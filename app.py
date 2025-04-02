import pickle
import pyodbc
import numpy as np
from vectorizer import tokenizer
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
clf = pickle.load(open("pkl/classifier.pkl", "rb"))
app.secret_key = 'supersecretkey'  # 用于会话管理
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, email, password, is_admin):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.is_admin = is_admin

def get_db_connection():
    server = 'JINYUYI'
    database = 'classdesign'
    driver = '{ODBC Driver 17 for SQL Server}'
    connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    return pyodbc.connect(connection_string)

def save_review(review, label, username):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO new_review (review, sentiment, review_date, username) VALUES (?, ?, CURRENT_TIMESTAMP, ?)",
                       (review, label, username))
        conn.commit()
    except Exception as e:
        flash(f"An error occurred while saving the review: {e}")
    finally:
        conn.close()

def set_admin(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET is_admin = 1 WHERE username = ?", (username,))
        conn.commit()
    except Exception as e:
        flash(f"An error occurred while setting admin: {e}")
    finally:
        conn.close()

# 设置 'jinyuyi' 为管理员
set_admin('jinyuyi')

class RegistrationForm(FlaskForm):
    username = StringField('Username', [Length(min=4, max=25)])
    email = StringField('Email Address', [Length(min=6, max=35)])
    password = PasswordField('New Password', [
        DataRequired(),
        EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')

class LoginForm(FlaskForm):
    username = StringField('Username', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])

class ReviewForm(FlaskForm):
    review = TextAreaField("", [DataRequired()])

class EditUserForm(FlaskForm):
    username = StringField('Username', [DataRequired()])
    email = StringField('Email', [DataRequired()])
    is_admin = BooleanField('Is Admin')

class EditReviewForm(FlaskForm):
    content = TextAreaField('Content', [DataRequired()])
    sentiment = StringField('Sentiment', [DataRequired()])

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = generate_password_hash(form.password.data)

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, email, password, is_admin) VALUES (?, ?, ?, 0)",
                           (username, email, password))
            conn.commit()
        except Exception as e:
            flash(f"An error occurred while registering: {e}")
        finally:
            conn.close()

        flash('Thanks for registering')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT user_id, username, email, password, is_admin FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
        except Exception as e:
            flash(f"An error occurred while logging in: {e}")
            user = None
        finally:
            conn.close()

        if user and check_password_hash(user[3], password):
            user_obj = User(id=user[0], username=user[1], email=user[2], password=user[3], is_admin=user[4])
            login_user(user_obj)
            flash('Logged in successfully.')
            return redirect(url_for('index'))
        else:
            flash('Invalid login credentials')
    return render_template('login.html', form=form)

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id, username, email, password, is_admin FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
    except Exception as e:
        flash(f"An error occurred while loading user: {e}")
        user = None
    finally:
        conn.close()
    if user:
        return User(id=user[0], username=user[1], email=user[2], password=user[3], is_admin=user[4])
    return None


def classify_review(review):
    label = {0: "negative", 1: "positive"}
    # tokenizer 返回的是list
    tokenized_review = tokenizer(review)

    # 确保传递给向量化器的数据是list
    X_transformed = tokenized_review

    # 确保 clf.predict 返回的是一个可以转换为整数的对象
    prediction = clf.predict(X_transformed)
    if isinstance(prediction, np.ndarray):
        prediction = prediction[0]  # 提取第一个元素
    Y = int(prediction)  # 转换为 Python int 类型

    label_Y = label[Y]
    proba = np.max(clf.predict_proba(X_transformed))
    return Y, label_Y, proba


@app.route("/")
@login_required
def index():
    form = ReviewForm()
    return render_template("index.html", form=form)

@app.route("/main", methods=["POST"])
@login_required
def main():
    form = ReviewForm()
    if form.validate_on_submit():
        review_text = form.review.data
        Y, label_Y, proba = classify_review(review_text)
        proba = float("%.4f" % proba) * 100
        return render_template("reviewform.html", review=review_text, Y=Y, label=label_Y, probability=proba)
    return render_template("index.html", form=form)

@app.route("/tanks", methods=["POST"])
@login_required
def tanks():
    btn_value = request.form["feedback_btn"]
    review = request.form["review"]
    label_temp = int(request.form["Y"])
    if btn_value == "Correct":
        label = label_temp
    else:
        label = 1 - label_temp
    save_review(review, label, current_user.username)  # 保存评论时传递用户名
    return render_template("tanks.html")

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.')
        return redirect(url_for('index'))

    return render_template('admin.html')

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.')
        return redirect(url_for('index'))

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id, username, email, is_admin FROM users")
        users = cursor.fetchall()
    except Exception as e:
        flash(f"An error occurred while fetching users: {e}")
        users = []
    finally:
        conn.close()

    return render_template('admin_users.html', users=users)

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('You do not have permission to perform this action.')
        return redirect(url_for('index'))

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
    except Exception as e:
        flash(f"An error occurred while deleting user: {e}")
    finally:
        conn.close()

    flash('User has been deleted.')
    return redirect(url_for('admin_users'))

@app.route('/admin/reviews')
@login_required
def view_reviews():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.')
        return redirect(url_for('index'))

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM new_review")
        reviews = cursor.fetchall()
    except Exception as e:
        flash(f"An error occurred while fetching reviews: {e}")
        reviews = []
    finally:
        conn.close()

    return render_template('reviews.html', reviews=reviews)

@app.route('/admin/delete_review/<int:review_id>', methods=['POST'])
@login_required
def delete_review(review_id):
    if not current_user.is_admin:
        flash('You do not have permission to perform this action.')
        return redirect(url_for('index'))

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM new_review WHERE review_id = ?", (review_id,))
        conn.commit()
    except Exception as e:
        flash(f"An error occurred while deleting review: {e}")
    finally:
        conn.close()

    flash('Review has been deleted.')
    return redirect(url_for('view_reviews'))

@app.route('/admin/model_info')
@login_required
def model_info():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.')
        return redirect(url_for('index'))

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM Model_Info")
        model_info = cursor.fetchall()
    except Exception as e:
        flash(f"An error occurred while fetching model info: {e}")
        model_info = []
    finally:
        conn.close()

    return render_template('model_info.html', model_info=model_info)

if __name__ == "__main__":
    app.debug = True
    app.run()

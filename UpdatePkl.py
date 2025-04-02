import pickle
import numpy as np
from vectorizer import tokenizer
import pyodbc
import pandas as pd

# 更新模型方法，每次更新10000条评论
def update_pkl(clf):
    # 建立连接
    server = 'JINYUYI'
    database = 'classdesign'
    driver = '{ODBC Driver 17 for SQL Server}'
    connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    conn = pyodbc.connect(connection_string)

    # 查询数据
    query = "SELECT * FROM new_review"
    df = pd.read_sql(query, conn)

    # 获取评论并确保其为字符串形式
    X = df['review'].astype(str)
    # 获取情感并确保其为整数形式并转化为NumPy数组
    Y = df['sentiment'].astype(int).values
    classes = np.array([0, 1])

    # 将评论应用tokenizer并将列表转换为字符串
    X_transformed = X.apply(lambda x: ' '.join(tokenizer(x)))

    # 将评论转成特征向量
    x_train = clf.named_steps['vect'].transform(X_transformed)

    # 检查Pipeline的步骤
    print(clf.named_steps)

    # 提取分类器
    classifier = clf.named_steps['clf']
    # 检查分类器是否支持partial_fit
    if hasattr(classifier, 'partial_fit'):
        # 更新模型
        classifier.partial_fit(x_train, Y, classes=classes)
    else:
        raise AttributeError(f"The classifier '{classifier}' does not support partial_fit")

    # 关闭连接
    conn.close()
    return None

if __name__ == "__main__":
    # 加载模型
    clf = pickle.load(open("pkl/classifier.pkl", "rb"))
    # 更新模型
    update_pkl(clf)
    # 保存模型
    pickle.dump(clf, open("pkl/classifier.pkl", "wb"), protocol=4)

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from nltk.stem.porter import PorterStemmer
import nltk
import pickle
import numpy as np

nltk.download("stopwords")
from nltk.corpus import stopwords

stops = stopwords.words("english")

# 提取词干获取单词的原型
def tokenizer_porter(text):
    porter = PorterStemmer()
    return ' '.join([porter.stem(word) for word in text.split()])

# 获取停用词
def remove_stopwords(text):
    return ' '.join([word for word in text.split() if word not in stops])

# 去除HTML标记符和标点符号
def remove_HTML_punctuation(text):
    text = re.sub('<[^>]*>', '', text)
    emoticons = re.findall('(?::|;|=)(?:-)?(?:\)|\(|D|P)', text)
    text = re.sub('[\W]+', ' ', text.lower()) + ''.join(emoticons).replace("-", "")
    return text

# 获取数据集
def get_X_Y():
    data = pd.read_excel("D:\\PyCharmFile\\comments\\data\\data.xlsx")
    np.random.seed(0)
    data = data.sample(frac=1).reset_index(drop=True)
    X = data["review"].apply(remove_HTML_punctuation)
    Y = data["sentiment"]
    return X, Y

# 设置网格参数
'''
vect__ngram_range:设置元组的数目
vect__stop_words:停用词
vect__tokenizer:提取词干，获取词的原型
clf__penalty:设置logistic回归正则化的方式
clf__C:设置正则化系数
'''
if __name__ == "__main__":
    tfidf = TfidfVectorizer(strip_accents=None, lowercase=False, preprocessor=None)
    param_grid = [{"vect__ngram_range": [(1, 1)],
                   "vect__stop_words": [stops, None],
                   "vect__tokenizer": [tokenizer_porter, None],
                   "clf__loss": ["log_loss"],
                   "clf__penalty": ["l1", "l2"],
                   "clf__alpha": [0.00001,0.0001, 0.001, 0.01]
                   }]
    lr_tfidf = Pipeline([("vect", tfidf), ("clf", SGDClassifier(random_state=0))])#这里，Pipeline对象包括两个步骤：vect: 使用TfidfVectorizer进行文本向量化；clf: 使用逻辑回归进行分类。
    gs_lr_tfidf = GridSearchCV(lr_tfidf, param_grid, scoring="accuracy", cv=5, verbose=1, n_jobs=-1)
    X, Y = get_X_Y()
    train_x, test_x, train_y, test_y = train_test_split(X, Y, test_size=0.1, random_state=0)
    gs_lr_tfidf.fit(train_x, train_y)# 训练模型
    # 获取网格搜索的最好参数
    print("Best parameter set:%s" % gs_lr_tfidf.best_params_)
    # 获取5折交叉验证在训练集上的准确率
    print("Best score:%.3f" % gs_lr_tfidf.best_score_)
    # 获取模型在测试集上的准确率
    print("Test Accuracy:%.3f" % gs_lr_tfidf.best_estimator_.score(test_x, test_y))

    pickle.dump(stops, open("stopwords.pkl", "wb"), protocol=4)
    pickle.dump(gs_lr_tfidf.best_estimator_, open("classifier.pkl", "wb"), protocol=4)

    model_info = {
        "Model": ["SGDClassifier"],
        "Best Parameters": [str(gs_lr_tfidf.best_params_)]
    }
    model_info_df = pd.DataFrame(model_info)

    try:
        model_info_df.to_excel("Model_Info.xlsx", index=False)
        print("模型信息成功存储到 Excel 文件中")
    except Exception as e:
        print(f"写入 Excel 文件时出现错误: {e}")

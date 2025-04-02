# -*- coding = utf-8 -*-
# @Time : 2024/5/19 18:39
# @Author: Vast
# @File: test.py
# @Software: PyCharm
import pickle

if __name__ == "__main__":
    # 加载分类模型
    clf = pickle.load(open("classifier.pkl", "rb"))

    X = 'i love it'
    X = vect.transform(review)



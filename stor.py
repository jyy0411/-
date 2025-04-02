import pandas as pd
from sqlalchemy import create_engine
import pyodbc

def get_data(file_path):
    # 读取Excel文件并返回DataFrame
    data = pd.read_excel(file_path)
    return data

def save_data_to_sql(data, server, database, table_name):
    # 创建数据库连接字符串
    connection_string = f'mssql+pyodbc://@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
    # 创建SQLAlchemy引擎
    engine = create_engine(connection_string)
    # 将DataFrame存入SQL Server数据库
    data.to_sql(name=table_name, con=engine, if_exists='replace', index=False)

def main():
    server = 'JINYUYI'  # 服务器名称或IP地址
    database = 'classdesign'  # 数据库名称
    table_name = 'row_review'  # 目标表名称

    # 读取数据
    file_path = "D:\\PyCharmFile\\comments\\data\\data.xlsx"
    data = get_data(file_path)

    # 保存数据到SQL Server数据库
    save_data_to_sql(data, server, database, table_name)

    print("Data successfully written to SQL Server database.")

    # 创建模型信息
    model_info = {
        "model": ["Logistic Regression"],
        "best parameters": ["{'vect__ngram_range': (1, 1), 'vect__stop_words': None, 'vect__tokenizer': None, 'clf__penalty': 'l2', 'clf__C': 1.0}"]
    }
    model_info_df = pd.DataFrame(model_info)

    # 将Model_Info表存储到SQL Server数据库
    model_info_table_name = 'model_info'
    save_data_to_sql(model_info_df, server, database, model_info_table_name)

    print("Model info successfully written to SQL Server database.")

if __name__ == "__main__":
    main()

import sqlite3
import pandas as pd
import pandas.io.sql
import configparser
import os
config = configparser.RawConfigParser()
config.read(r".\config\config.ini")

databaseUrl = r"dataSql.DB"
#config.get("database","database")
print(databaseUrl)
#databaseUrl = "/home/ly/Item/flask/dataSql.DB"
#print(databaseUrl)
conn = sqlite3.connect(databaseUrl)
cur = conn.cursor()
def insert(data):
    global conn
    data.to_sql('test',conn,index=False,if_exists='append')

def select_data(sql):
    global conn
    data = pd.read_sql(sql,conn)
    #data = data.drop(columns='index')
    return data

def to_excel():
    data = select_data("select * from test")
    data.to_excel(r".\test.xlsx",index=False)
    print("to_excel success")
def to_csv():
    data = select_data("select * from test")
    data.to_csv(r".\test.csv",index=False)
    print("to_csv success")

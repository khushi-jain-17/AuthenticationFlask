import psycopg2

conn = psycopg2.connect(database="flask_jwt",host="localhost",user="postgres",password="1719",port="5432")
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS users(id integer PRIMARY KEY,name varchar(100),email varchar(100) ,password varchar(100)); ''')

conn.commit()
cur.close()
conn.close()
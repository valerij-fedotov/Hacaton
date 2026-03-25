import psycopg2

conn = psycopg2.connect(
    dbname="dtp_analytics",
    user="postgres",
    password="123456",
    host="localhost",
    port=5432
)
cur = conn.cursor()
cur.execute("SELECT * FROM accidents;")
rows = cur.fetchall()
print("Таблица accidents:", rows)
cur.close()
conn.close()
import csv, sqlite3

SELECT = 'PRAGMA table_info("reviews_review");'
INSERT = 'INSERT INTO reviews_review ({}, {}, {}, {}, {}, {}) VALUES (?, ?, ?, ?, ?, ?);'


def connect_sql(con):
    try:
        cursor = con.cursor()
        print('Подключен к SQLite')
        cursor.execute(SELECT)
        records = cursor.fetchall()
        header = []
        for row in records:
            header.append(row[1])
        with open(
                'D:/Dev/api_yamdb/api_yamdb/static/data/review.csv',
                'r', encoding='utf-8') as fin:
            dr = csv.DictReader(fin)
            to_db = [
                (i[header[0]], i[header[1]],
                 i[header[2]], i[header[3]],
                 i[header[4]], i[header[5]]) for i in dr]
            print(header)
            print(to_db)
            cursor.executemany(
                INSERT.format(header[0], header[1], header[2],
                              header[3], header[4], header[5]), to_db)
        con.commit()
        con.close()
    except Exception as ex:
        print('Ошибка подключения')


my_con = sqlite3.connect('db.sqlite3')
connect_sql(my_con)

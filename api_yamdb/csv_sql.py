import csv, sqlite3

SELECT = 'PRAGMA table_info("reviews_comment");'
INSERT = 'INSERT INTO reviews_comment VALUES (?, ?, ?, ?, ?, ?);'


def connect_sql(con):
    try:
        cursor = con.cursor()
        print('Подключен к SQLite')
        cursor.execute(SELECT)
        records = cursor.fetchall()
        header = []
        for row in records:
            header.append(row[1])
        print(tuple(header))
        with open(
                'D:/Dev/14-05-22/api_yamdb/api_yamdb/static/data/comments.csv',
                'r', encoding='utf-8') as fin:
            dr = csv.DictReader(fin)
            to_db = []
            for i in dr:
                db = []
                for j in range(len(header)):
                    db.append(i[header[j]])
                to_db.append(tuple(db))
            cursor.executemany(INSERT, to_db)
            # cursor.executemany(
            #     INSERT.format(header[0], header[1], header[2], header[3], header[4], header[5], header[6], header[7]), to_db)
        con.commit()
        con.close()
    except Exception as ex:
        print('Ошибка подключения:', ex)


my_con = sqlite3.connect('db.sqlite3')
connect_sql(my_con)

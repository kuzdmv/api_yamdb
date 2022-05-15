import csv
import datetime as dt
import os
import sqlite3

con = sqlite3.connect('api_yamdb/db.sqlite3')
cur = con.cursor()
path = 'api_yamdb/static/data'

with open(os.path.join(path, 'category.csv'), 'r', encoding='utf-8') as data:
    reader = csv.DictReader(data)
    db = [(row['id'], row['name'], row['slug']) for row in reader]
    cur.executemany(
        'INSERT INTO reviews_category (id, name, slug) '
        'VALUES(?, ?, ?);', db
    )
    con.commit()

with open(os.path.join(path, 'comments.csv'), 'r', encoding='utf-8') as data:
    reader = csv.DictReader(data)
    db = [(
        row['id'], row['review_id'], row['text'], row['author'],
        row['pub_date']
    ) for row in reader]
    cur.executemany(
        'INSERT INTO reviews_comment '
        '(id, review_id, text, author_id, pub_date) '
        'VALUES(?, ?, ?, ?, ?);', db
    )
    con.commit()

with open(os.path.join(path, 'genre.csv'), 'r', encoding='utf-8') as data:
    reader = csv.DictReader(data)
    db = [(row['id'], row['name'], row['slug']) for row in reader]
    cur.executemany(
        'INSERT INTO reviews_genre (id, name, slug) '
        'VALUES(?, ?, ?);', db
    )
    con.commit()

with open(
    os.path.join(path, 'genre_title.csv'), 'r', encoding='utf-8'
) as data:
    reader = csv.DictReader(data)
    db = [(row['id'], row['title_id'], row['genre_id']) for row in reader]
    cur.executemany(
        'INSERT INTO reviews_title_genre (id, title_id, genre_id) '
        'VALUES(?, ?, ?);', db
    )
    con.commit()

with open(os.path.join(path, 'review.csv'), 'r', encoding='utf-8') as data:
    reader = csv.DictReader(data)
    db = [(
        row['id'], row['title_id'], row['text'], row['author'], row['score'],
        row['pub_date']
    ) for row in reader]
    cur.executemany(
        'INSERT INTO reviews_review '
        '(id, title_id, text, author_id, score, pub_date) '
        'VALUES(?, ?, ?, ?, ?, ?);', db
    )
    con.commit()

with open(os.path.join(path, 'titles.csv'), 'r', encoding='utf-8') as data:
    reader = csv.DictReader(data)
    db = [(
        row['id'], row['name'], row['year'], row['category']
    ) for row in reader]
    cur.executemany(
        'INSERT INTO reviews_title (id, name, year, category_id) '
        'VALUES(?, ?, ?, ?);', db
    )
    con.commit()

with open(os.path.join(path, 'users.csv'), 'r', encoding='utf-8') as data:
    reader = csv.DictReader(data)
    IS_STAFF = {'admin': True, 'user': False, 'moderator': False}
    db = [(
        row['id'], row['username'], row['email'], row['password'],
        row['role'], row['bio'], row['first_name'], row['last_name'], False,
        IS_STAFF[row['role']], True, dt.datetime.now()
    ) for row in reader]
    cur.executemany(
        'INSERT INTO reviews_user '
        '(id, username, email, password, role, bio, first_name, last_name, '
        'is_superuser, is_staff, is_active, date_joined) '
        'VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);', db
    )
    con.commit()

con.close()

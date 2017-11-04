import sqlite3 as lite
import codecs

creatdb_sql = 'create table Stars(' \
              's_id char(10) primary key not null,' \
              's_name varchar(10) not null,' \
              's_sex char(1),' \
              's_age int,' \
              's_typifies varchar(20),' \
              "check(s_sex='F' or s_sex='M')" \
              ")"
insert_sql = "insert into Stars VALUES ('{}','{}','{}',{},'{}')"
query_sql = "select * from Stars where s_sex='M'"
conn = lite.connect('Mystar.db')
cur = conn.cursor()
cur.execute(creatdb_sql)
cur.execute(insert_sql.format('1', '王菲', 'M', 50, '容易受伤的女人'))
cur.execute(insert_sql.format('2', '成龙', 'F', 50, '警察故事'))
cur.execute(insert_sql.format('3', '姚晨', 'M', 50, '武林外传'))
conn.commit()
with codecs.open("query.txt", 'w+', 'utf-8') as f:
    for row in cur.execute(query_sql):
        print(row)
        f.write(" ".join(map(str, row)))
        f.write('\n')
conn.close()

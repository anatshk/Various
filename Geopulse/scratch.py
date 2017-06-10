from task import DataBase

db = DataBase(dbname='temp', user='postgres', password='blahblah15')

# db.delete_table('table_one')
# db.create_table('table_one', id='SERIAL', num='integer', word='text')

# db.add_row('table_one', num=15, word='fish')
# db.add_row('table_one', word='cat')
# db.add_row('table_one', num=85)

result1 = db.query_table('table_one')
result2 = db.query_table('table_one', column_names='num')
result3 = db.query_table('table_one', query="num > 10", column_names=['_id', 'num'])
result4 = db.query_table('table_one', query="num < 50 AND word = \'fish\'")

db.close()


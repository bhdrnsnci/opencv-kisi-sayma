import sqlite3

# veri tabanı oluşturma     #### cdb
with sqlite3.connect("Counter.db") as cdb:
    cursor = cdb.cursor()

    # people:
    #   id
    #   dates
    #   numbers
    cursor.execute("create table people(id integer primary key autoincrement, year text, month text, day text, numbers int)")
    cursor.execute("insert into people(year, month, day, numbers) values('2021', '5', '25', 10)")

print("Veri tabanı oluşturuldu.")
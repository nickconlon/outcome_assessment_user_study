import sqlite3

DB_FILE = '/databases/flaskr.sqlite'
def cleanup():
    # Create a SQL connection to our SQLite database
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute('DELETE FROM user')
    con.commit()
    con.close()

    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute('DELETE FROM results')
    con.commit()
    con.close()

def dump():
    # Create a SQL connection to our SQLite database
    con = sqlite3.connect(DB_FILE)

    cur = con.cursor()

    # The result of a "cursor.execute" can be iterated over by row
    for row in cur.execute('SELECT * FROM user;'):
        print(row)
    for row in cur.execute('SELECT * FROM results;'):
        print(row)

    # Be sure to close the connection
    con.close()

def del_entry(id):
    # Create a SQL connection to our SQLite database
    con = sqlite3.connect(DB_FILE)

    cur = con.cursor()

    # The result of a "cursor.execute" can be iterated over by row
    cur.execute('DELETE FROM user where id=?', (id,))
    cur.execute('DELETE FROM results where user_id=?', (id,))
    con.commit()
    # Be sure to close the connection
    con.close()

if __name__ == "__main__":
    dump()
    #del_entry(1)
    #del_entry(2)
    #del_entry(5)
    #del_entry(6)
    #dump()
    #cleanup()
    #dump()
    pass

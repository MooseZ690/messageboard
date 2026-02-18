from flask import Flask, g, render_template
import logging
import sqlite3
DATABASE = 'database.db'

# initialize app
app = Flask(__name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.route("/")
def home():
    # home page - shows all messages committed as of present
    sql = """
        SELECT * FROM Messages;
        """
    results = query_db(sql)
    return render_template("home.html", results=results)

if __name__ == '__main__':
    app.run(debug=True)
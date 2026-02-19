from flask import Flask, g, render_template, request, redirect, url_for
import logging, sqlite3, datetime
from datetime import datetime

DATABASE = 'database.db'

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
        SELECT * FROM Messages
        ORDER BY time DESC
        """
    results = query_db(sql)
    return render_template("home.html", results=results)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/newpost", methods=['GET', 'POST'])
def newpost():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        user = request.form.get('user', '').strip()
        imageurl = request.form.get('imageurl', '').strip()

        if title and content and user:
            db = get_db()
            current_time = str(datetime.now().strftime("%H:%M:%S %d/%m/%Y")) #sets the date and time as a string

            user_ip = request.headers.get('X-Forwarded-For', request.remote_addr) #gets user's ip address
            user_ip = user_ip.split(',')[0].strip()

            time_ip = f"{current_time} (IP: {user_ip})" #appends ip address onto the time string to save space in the database
            db.execute(
                "INSERT INTO Messages (title, content, user, imageurl, time) VALUES (?, ?, ?, ?, ?)",
                (title, content, user, imageurl, time_ip)
            )
            db.commit()

        return redirect(url_for('home'))

    return render_template("newpost.html")


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
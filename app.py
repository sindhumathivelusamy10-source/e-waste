from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)   # ✅ FIRST create app

# your code here...

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

# DB CONNECT
def get_db():
    return sqlite3.connect("database.db")

# CREATE TABLE
def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS waste(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        item TEXT,
        qty INTEGER
    )
    """)
    conn.commit()
    conn.close()

init_db()

# LOGIN
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return redirect("/dashboard")
    return render_template("login.html")

# DASHBOARD
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if request.method == "POST":
        name = request.form["name"]
        item = request.form["item"]
        qty = request.form["qty"]

        if name == "" or item == "" or qty == "":
            return "<script>alert('Fill all fields');window.location='/dashboard'</script>"

        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO waste(name,item,qty) VALUES(?,?,?)", (name, item, qty))
        conn.commit()
        conn.close()

    return render_template("dashboard.html")

# RECORDS
@app.route("/records")
def records():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM waste")
    data = cur.fetchall()
    conn.close()
    return render_template("records.html", data=data)

# DELETE
@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM waste WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/records")

# EDIT
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        item = request.form["item"]
        qty = request.form["qty"]

        cur.execute("UPDATE waste SET name=?, item=?, qty=? WHERE id=?", (name, item, qty, id))
        conn.commit()
        conn.close()
        return redirect("/records")

    cur.execute("SELECT * FROM waste WHERE id=?", (id,))
    row = cur.fetchone()
    conn.close()

    return render_template("edit.html", row=row)

# GRAPH
@app.route("/graph")
def graph():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT item, SUM(qty) FROM waste GROUP BY item")
    data = cur.fetchall()
    conn.close()

    labels = [i[0] for i in data]
    values = [i[1] for i in data]

    return render_template("graph.html", labels=labels, values=values)

# MAP
@app.route("/map")
def map_view():
    item = request.args.get("item")
    return render_template("map.html", item=item)

# RUN
if __name__ == "__main__":
    app.run(debug=True)
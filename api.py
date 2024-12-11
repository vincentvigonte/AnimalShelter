from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from http import HTTPStatus

app = Flask(__name__)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "animal_shelter"

mysql = MySQL(app)

@app.route("/")
def hello_user():
    return "ANIMAL SHELTER API"

# Utility function to fetch a single row by ID
def fetch_one(query, params):
    cursor = mysql.connection.cursor()
    cursor.execute(query, params)
    result = cursor.fetchone()
    cursor.close()
    return result

# Utility function to fetch multiple rows
def fetch_all(query, params=None):
    cursor = mysql.connection.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    return results

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

#Crud for species
@app.route("/species", methods=["GET"])
def get_species():
    species = fetch_all("SELECT * FROM Species")
    if not species:
        return jsonify({"error": "No species found"}), HTTPStatus.NOT_FOUND
    species_data = [{"species_id": s[0], "species_name": s[1]} for s in species]
    return jsonify({"success": True, "data": species_data, "total": len(species_data)}), HTTPStatus.OK

@app.route("/species", methods=["POST"])
def create_species():
    data = request.get_json()
    species_name = data.get("species_name")
    if not species_name:
        return jsonify({"success": False, "error": "species_name is required"}), HTTPStatus.BAD_REQUEST

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO Species (species_name) VALUES (%s)", (species_name,))
    mysql.connection.commit()
    return jsonify({"success": True, "data": {"species_id": cursor.lastrowid, "species_name": species_name}}), HTTPStatus.CREATED

@app.route("/species/<int:species_id>", methods=["PUT"])
def update_species(species_id):
    data = request.get_json()
    species_name = data.get("species_name")

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE Species SET species_name = %s WHERE species_id = %s", (species_name, species_id))
    mysql.connection.commit()
    if cursor.rowcount == 0:
        return jsonify({"success": False, "error": "Species not found"}), HTTPStatus.NOT_FOUND
    return jsonify({"success": True, "message": "Species updated successfully"}), HTTPStatus.OK

@app.route("/species/<int:species_id>", methods=["DELETE"])
def delete_species(species_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM Species WHERE species_id = %s", (species_id,))
    mysql.connection.commit()
    if cursor.rowcount == 0:
        return jsonify({"success": False, "error": "Species not found"}), HTTPStatus.NOT_FOUND
    return jsonify({"success": True, "message": "Species deleted successfully"}), HTTPStatus.OK

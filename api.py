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

#Crud for pets
@app.route("/pets", methods=["GET"])
def get_pets():
    pets = fetch_all("SELECT * FROM Pet")
    pets_data = [{
        "pet_id": pet[0], "name": pet[1], "species_id": pet[2], "breed_name": pet[3], 
        "age": pet[4], "color": pet[5], "gender": pet[6], "adopted": pet[7], 
        "date_arrived": pet[8], "date_adopted": pet[9]
    } for pet in pets]
    return jsonify({"success": True, "data": pets_data, "total": len(pets_data)}), HTTPStatus.OK

@app.route("/pets", methods=["POST"])
def create_pet():
    data = request.get_json()
    name = data.get("name")
    species_id = data.get("species_id")
    breed_name = data.get("breed_name")
    age = data.get("age")
    color = data.get("color")
    gender = data.get("gender")
    date_arrived = data.get("date_arrived")

    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO Pet (name, species_id, breed_name, age, color, gender, date_arrived) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
        (name, species_id, breed_name, age, color, gender, date_arrived)
    )
    mysql.connection.commit()
    return jsonify({"success": True, "data": {"pet_id": cursor.lastrowid}}), HTTPStatus.CREATED

@app.route("/pets/<int:pet_id>", methods=["PUT"])
def update_pet(pet_id):
    data = request.get_json()
    name = data.get("name")
    species_id = data.get("species_id")
    breed_name = data.get("breed_name")
    age = data.get("age")
    color = data.get("color")
    gender = data.get("gender")

    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE Pet SET name = %s, species_id = %s, breed_name = %s, age = %s, color = %s, gender = %s WHERE pet_id = %s",
        (name, species_id, breed_name, age, color, gender, pet_id)
    )
    mysql.connection.commit()
    if cursor.rowcount == 0:
        return jsonify({"error": "Pet not found"}), HTTPStatus.NOT_FOUND
    return jsonify({"message": "Pet updated successfully"}), HTTPStatus.OK

@app.route("/pets/<int:pet_id>", methods=["DELETE"])
def delete_pet(pet_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM Pet WHERE pet_id = %s", (pet_id,))
    mysql.connection.commit()
    if cursor.rowcount == 0:
        return jsonify({"error": "Pet not found"}), HTTPStatus.NOT_FOUND
    return jsonify({"message": "Pet deleted successfully"}), HTTPStatus.OK

if __name__ == "__main__":
    app.run(debug=True)


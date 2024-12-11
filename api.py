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

#Crud for pet
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

#Crud for adoption
@app.route("/adoptions", methods=["GET"])
def get_adoptions():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Adoption")
    adoptions = cursor.fetchall()

    if not adoptions:
        return jsonify({"error": "No adoptions found"}), 404

    adoptions_list = [
        {
            "adoption_id": adoption[0],
            "pet_id": adoption[1],
            "first_name": adoption[2],
            "last_name": adoption[3],
            "address": adoption[4],
            "email": adoption[5],
            "phone": adoption[6],
            "adoption_date": adoption[7],
            "date_returned": adoption[8]
        }
        for adoption in adoptions
    ]

    return jsonify(adoptions_list), 200


@app.route("/adoptions", methods=["POST"])
def add_adoption():
    data = request.get_json()
    pet_id = data.get("pet_id")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    adoption_date = data.get("adoption_date")

    if not pet_id or not isinstance(pet_id, int):
        return jsonify({"error": "Pet ID is required and must be an integer"}), 400
    if not first_name or not isinstance(first_name, str):
        return jsonify({"error": "First name is required and must be a string"}), 400
    if not last_name or not isinstance(last_name, str):
        return jsonify({"error": "Last name is required and must be a string"}), 400
    if not adoption_date:
        return jsonify({"error": "Adoption date is required"}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO Adoption (pet_id, first_name, last_name, address, email, phone, adoption_date, date_returned) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (pet_id, first_name, last_name, data.get("address"), data.get("email"), data.get("phone"), adoption_date, data.get("date_returned")),
        )
        mysql.connection.commit()
        return jsonify({"message": "Adoption created successfully", "adoption_id": cursor.lastrowid}), 201
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500


@app.route("/adoptions/<int:adoption_id>", methods=["PUT"])
def update_adoption(adoption_id):
    data = request.get_json()
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    address = data.get("address")
    email = data.get("email")
    phone = data.get("phone")
    adoption_date = data.get("adoption_date")
    date_returned = data.get("date_returned")

    if not first_name or not isinstance(first_name, str):
        return jsonify({"error": "First name is required and must be a string"}), 400
    if not last_name or not isinstance(last_name, str):
        return jsonify({"error": "Last name is required and must be a string"}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "UPDATE Adoption SET first_name = %s, last_name = %s, address = %s, email = %s, phone = %s, adoption_date = %s, date_returned = %s WHERE adoption_id = %s",
            (first_name, last_name, address, email, phone, adoption_date, date_returned, adoption_id),
        )
        mysql.connection.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Adoption not found"}), 404
        return jsonify({"message": "Adoption updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500


@app.route("/adoptions/<int:adoption_id>", methods=["DELETE"])
def delete_adoption(adoption_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM Adoption WHERE adoption_id = %s", (adoption_id,))
        mysql.connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Adoption not found"}), 404

        return jsonify({"message": "Adoption deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

#Crud for medical record
@app.route("/medical_records", methods=["GET"])
def get_medical_records():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Medical_Record")
    records = cursor.fetchall()

    if not records:
        return jsonify({"error": "No medical records found"}), 404

    records_list = [
        {
            "treatment_id": record[0],
            "pet_id": record[1],
            "treatment_date": record[2],
            "treatment_details": record[3],
            "veterinarian": record[4]
        }
        for record in records
    ]

    return jsonify(records_list), 200


@app.route("/medical_records", methods=["POST"])
def add_medical_record():
    data = request.get_json()
    pet_id = data.get("pet_id")
    treatment_date = data.get("treatment_date")
    treatment_details = data.get("treatment_details")
    veterinarian = data.get("veterinarian")

    if not pet_id or not isinstance(pet_id, int):
        return jsonify({"error": "Pet ID is required and must be an integer"}), 400
    if not treatment_date:
        return jsonify({"error": "Treatment date is required"}), 400
    if not treatment_details or not isinstance(treatment_details, str):
        return jsonify({"error": "Treatment details are required and must be a string"}), 400
    if not veterinarian or not isinstance(veterinarian, str):
        return jsonify({"error": "Veterinarian name is required and must be a string"}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO Medical_Record (pet_id, treatment_date, treatment_details, veterinarian) VALUES (%s, %s, %s, %s)",
            (pet_id, treatment_date, treatment_details, veterinarian),
        )
        mysql.connection.commit()
        return jsonify({"message": "Medical record created successfully", "treatment_id": cursor.lastrowid}), 201
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500


@app.route("/medical_records/<int:treatment_id>", methods=["PUT"])
def update_medical_record(treatment_id):
    data = request.get_json()
    treatment_date = data.get("treatment_date")
    treatment_details = data.get("treatment_details")
    veterinarian = data.get("veterinarian")

    if not treatment_date:
        return jsonify({"error": "Treatment date is required"}), 400
    if not treatment_details or not isinstance(treatment_details, str):
        return jsonify({"error": "Treatment details are required and must be a string"}), 400
    if not veterinarian or not isinstance(veterinarian, str):
        return jsonify({"error": "Veterinarian name is required and must be a string"}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "UPDATE Medical_Record SET treatment_date = %s, treatment_details = %s, veterinarian = %s WHERE treatment_id = %s",
            (treatment_date, treatment_details, veterinarian, treatment_id),
        )
        mysql.connection.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Medical record not found"}), 404
        return jsonify({"message": "Medical record updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500


@app.route("/medical_records/<int:treatment_id>", methods=["DELETE"])
def delete_medical_record(treatment_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM Medical_Record WHERE treatment_id = %s", (treatment_id,))
        mysql.connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Medical record not found"}), 404

        return jsonify({"message": "Medical record deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)


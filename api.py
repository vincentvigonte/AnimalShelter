from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_httpauth import HTTPBasicAuth
from http import HTTPStatus
import jwt
import datetime
import json
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "animal_shelter" 
app.config["SECRET_KEY"] = "vincent7"

mysql = MySQL(app)
auth = HTTPBasicAuth()

USER_DATA_FILE = "users.json"

def load_users():
    try:
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_users(users):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(users, file)

users = load_users()

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users[username]['password'], password):
        return username

# Generate JWT
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username not in users or not check_password_hash(users[username]['password'], password):
        return jsonify({"error": "Invalid credentials"}), 401

    if 'token' not in users[username]:
        token = jwt.encode({
            "username": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, app.config["SECRET_KEY"], algorithm="HS256")
        users[username]['token'] = token
        save_users(users)
    else:
        token = users[username]['token']

    return jsonify({"token": token})

# Register a new user
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "users")  

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if username in users:
        return jsonify({"error": "User already exists"}), 400

    users[username] = {
        "password": generate_password_hash(password),
        "role": role
    }
    save_users(users)

    return jsonify({"message": "User registered successfully"}), 201

# JWT Token validation
def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            decoded_token = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            request.username = decoded_token["username"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)
    return wrapper

# Role-based access control
def role_required(required_roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            username = getattr(request, "username", None)
            user_role = users.get(username, {}).get("role")
            if not user_role or user_role not in required_roles:
                return jsonify({"error": "Access forbidden: insufficient permissions"}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator

@app.route("/")
def hello_world():
    style = """
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background: linear-gradient(135deg, #d1eaff, #a9d7f5);
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                color: #4b9cdd;
            }
            h1 {
                font-size: 50px;
                color: #4f8cc9;
                text-shadow: 3px 3px 8px rgba(0, 0, 0, 0.1);
                margin-bottom: 30px;
                text-align: center;
                animation: fadeIn 1.5s ease-out;
            }
            p {
                font-size: 22px;
                color: #5f9fcf;
                margin-bottom: 40px;
                text-align: center;
                animation: fadeIn 2s ease-out;
                font-weight: bold;
            }
            .link-container {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 20px;
            }
            a {
                font-size: 22px;
                color: #ffffff;
                text-decoration: none;
                background-color: #6fb6d8;
                padding: 15px 30px;
                margin: 10px;
                border-radius: 25px;
                transition: all 0.3s ease;
                box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.1);
                border: 2px solid #5c9cc3;
            }
            a:hover {
                background-color: #82c5e5;
                transform: scale(1.05);
                box-shadow: 0px 12px 20px rgba(0, 0, 0, 0.1);
            }
            a:active {
                transform: scale(1.03);
                background-color: #66aad1;
            }
            .icon {
                width: 40px;
                height: 40px;
                margin-right: 10px;
                vertical-align: middle;
            }
            @keyframes fadeIn {
                0% { opacity: 0; }
                100% { opacity: 1; }
            }
        </style>
    """
    
    # Define the links with animal-related names and icons
    no_token_routes = [
        {"name": "Home", "url": "/", "icon": "🏠"},
        {"name": "View Species", "url": "/species", "icon": "🐾"},
        {"name": "View Pet", "url": "/pets", "icon": "🐶"},
        {"name": "View Adoption", "url": "/adoptions", "icon": "💚"},
        {"name": "View Medical Record", "url": "/medical_records", "icon": "📋"},
    ]
    
    # Create the links with their respective icons
    no_token_links = "".join([f'<a href="{route["url"]}"><span class="icon">{route["icon"]}</span>{route["name"]}</a>' for route in no_token_routes])

    return f"""
        {style}
        <h1>Welcome to the Animal Shelter</h1>
        <p>Your one-stop destination to manage and view our beloved pets.</p>
        <div class="link-container">
            {no_token_links}
        </div>
    """

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



# CRUD for species

@app.route("/species", methods=["GET"])
def get_species():
    species = fetch_all("SELECT * FROM Species")
    if not species:
        return jsonify({"error": "No species found"}), HTTPStatus.NOT_FOUND
    species_data = [{"species_id": s[0], "species_name": s[1]} for s in species]
    return jsonify({"success": True, "data": species_data, "total": len(species_data)}), HTTPStatus.OK

@app.route("/species", methods=["POST"])
@token_required
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
@token_required
@role_required(["admin", "staff"])  #
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
@token_required
@role_required(["admin", "staff"]) 
def delete_species(species_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM Species WHERE species_id = %s", (species_id,))
    mysql.connection.commit()
    if cursor.rowcount == 0:
        return jsonify({"success": False, "error": "Species not found"}), HTTPStatus.NOT_FOUND
    return jsonify({"success": True, "message": "Species deleted successfully"}), HTTPStatus.OK

# CRUD for pets
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
@token_required
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
@token_required
@role_required(["admin", "staff"])
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
@token_required
@role_required(["admin", "staff"])
def delete_pet(pet_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM Pet WHERE pet_id = %s", (pet_id,))
    mysql.connection.commit()
    if cursor.rowcount == 0:
        return jsonify({"error": "Pet not found"}), HTTPStatus.NOT_FOUND
    return jsonify({"message": "Pet deleted successfully"}), HTTPStatus.OK

# CRUD for adoptions
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
@token_required
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
@token_required
@role_required(["admin", "staff"])
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
@token_required
@role_required(["admin", "staff"])
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

# CRUD for medical records
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
@token_required
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
@token_required
@role_required(["admin", "staff"])
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
@token_required
@role_required(["admin", "staff"])
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


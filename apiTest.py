import pytest
from api import app

@pytest.fixture
def mock_db(mocker):
    mock_conn = mocker.patch('flask_mysqldb.MySQL.connection')
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_cursor

#Species test
def test_get_species_empty(mock_db):
    mock_db.fetchall.return_value = [] 

    client = app.test_client()
    response = client.get('/species')
    
    assert response.status_code == 404
    assert b"No species found" in response.data

def test_get_species(mock_db):
    mock_db.fetchall.return_value = [(1, 'Dog'), (2, 'Cat')]
    
    client = app.test_client()
    response = client.get('/species')
    
    assert response.status_code == 200
    assert b"Dog" in response.data
    assert b"Cat" in response.data

def test_post_species_missing_field(mock_db):
    client = app.test_client()
    response = client.post('/species', json={})  
    
    assert response.status_code == 400
    assert b"species_name is required" in response.data

def test_post_species_success(mock_db):
    mock_db.lastrowid = 1 
    mock_db.rowcount = 1  
    
    client = app.test_client()
    response = client.post('/species', json={"species_name": "Rabbit"})
    
    assert response.status_code == 201
    assert b"Rabbit" in response.data
    assert b"species_id" in response.data

def test_put_species_not_found(mock_db):
    mock_db.rowcount = 0 
    
    client = app.test_client()
    response = client.put('/species/999', json={"species_name": "Updated Species"})
    
    assert response.status_code == 404
    assert b"Species not found" in response.data

def test_put_species_success(mock_db):
    mock_db.rowcount = 1 
    
    client = app.test_client()
    response = client.put('/species/1', json={"species_name": "Updated Species"})
    
    assert response.status_code == 200
    assert b"Species updated successfully" in response.data

def test_delete_species_not_found(mock_db):
    mock_db.rowcount = 0 
    
    client = app.test_client()
    response = client.delete('/species/999')
    
    assert response.status_code == 404
    assert b"Species not found" in response.data

def test_delete_species_success(mock_db):
    mock_db.rowcount = 1 
    
    client = app.test_client()
    response = client.delete('/species/1')
    
    assert response.status_code == 200
    assert b"Species deleted successfully" in response.data

#Pet test
def test_get_pets_empty(mock_db):
    mock_db.fetchall.return_value = []  
    
    client = app.test_client()
    response = client.get('/pets')
    
    assert response.status_code == 200
    assert b"total" in response.data
    assert b"0" in response.data 

def test_get_pets(mock_db):
    mock_db.fetchall.return_value = [
        (1, "Max", 1, "Golden Retriever", 3, "Golden", "Male", False, "2023-01-01", None),
        (2, "Bella", 2, "Persian Cat", 2, "White", "Female", True, "2023-01-05", "2023-03-01")
    ]
    
    client = app.test_client()
    response = client.get('/pets')
    
    assert response.status_code == 200
    assert b"Max" in response.data
    assert b"Bella" in response.data

def test_post_pet_missing_fields(mock_db):
    client = app.test_client()
    response = client.post('/pets', json={}) 
    
    assert response.status_code == 500

def test_post_pet_success(mock_db):
    mock_db.lastrowid = 1  
    
    client = app.test_client()
    response = client.post('/pets', json={
        "name": "Charlie",
        "species_id": 1,
        "breed_name": "Beagle",
        "age": 4,
        "color": "Brown",
        "gender": "Male",
        "date_arrived": "2024-01-01"
    })
    
    assert response.status_code == 201
    assert b"pet_id" in response.data

def test_put_pet_not_found(mock_db):
    mock_db.rowcount = 0 
    
    client = app.test_client()
    response = client.put('/pets/999', json={
        "name": "Updated Name",
        "species_id": 1,
        "breed_name": "Updated Breed",
        "age": 5,
        "color": "Updated Color",
        "gender": "Female"
    })
    
    assert response.status_code == 404
    assert b"Pet not found" in response.data

def test_put_pet_success(mock_db):
    mock_db.rowcount = 1 
    
    client = app.test_client()
    response = client.put('/pets/1', json={
        "name": "Updated Name",
        "species_id": 1,
        "breed_name": "Updated Breed",
        "age": 5,
        "color": "Updated Color",
        "gender": "Female"
    })
    
    assert response.status_code == 200
    assert b"Pet updated successfully" in response.data

def test_delete_pet_not_found(mock_db):
    mock_db.rowcount = 0 

    client = app.test_client()
    response = client.delete('/pets/999')
    
    assert response.status_code == 404
    assert b"Pet not found" in response.data

def test_delete_pet_success(mock_db):
    mock_db.rowcount = 1  

    client = app.test_client()
    response = client.delete('/pets/1')
    
    assert response.status_code == 200
    assert b"Pet deleted successfully" in response.data

#Adoption test
def test_get_adoptions_empty(mock_db):
    mock_db.fetchall.return_value = []  
    
    client = app.test_client()
    response = client.get('/adoptions')
    
    assert response.status_code == 404
    assert b"No adoptions found" in response.data

def test_get_adoptions(mock_db):
    mock_db.fetchall.return_value = [
        (1, 101, "John", "Doe", "123 Street", "john.doe@example.com", "1234567890", "2023-05-10", None),
        (2, 102, "Jane", "Smith", "456 Avenue", "jane.smith@example.com", "0987654321", "2023-06-15", "2023-07-01")
    ]
    
    client = app.test_client()
    response = client.get('/adoptions')
    
    assert response.status_code == 200
    assert b"John" in response.data
    assert b"Jane" in response.data

def test_post_adoption_missing_fields(mock_db):
    client = app.test_client()
    response = client.post('/adoptions', json={})
    
    assert response.status_code == 400
    assert b"Pet ID is required" in response.data

def test_post_adoption_success(mock_db):
    mock_db.lastrowid = 1  
    
    client = app.test_client()
    response = client.post('/adoptions', json={
        "pet_id": 101,
        "first_name": "John",
        "last_name": "Doe",
        "address": "123 Street",
        "email": "john.doe@example.com",
        "phone": "1234567890",
        "adoption_date": "2023-05-10"
    })
    
    assert response.status_code == 201
    assert b"Adoption created successfully" in response.data

def test_put_adoption_not_found(mock_db):
    mock_db.rowcount = 0  
    
    client = app.test_client()
    response = client.put('/adoptions/999', json={
        "first_name": "Updated",
        "last_name": "Name",
        "address": "Updated Address",
        "email": "updated@example.com",
        "phone": "9876543210",
        "adoption_date": "2023-08-10",
        "date_returned": "2023-09-01"
    })
    
    assert response.status_code == 404
    assert b"Adoption not found" in response.data

def test_put_adoption_success(mock_db):
    mock_db.rowcount = 1  
    
    client = app.test_client()
    response = client.put('/adoptions/1', json={
        "first_name": "Updated",
        "last_name": "Name",
        "address": "Updated Address",
        "email": "updated@example.com",
        "phone": "9876543210",
        "adoption_date": "2023-08-10",
        "date_returned": "2023-09-01"
    })
    
    assert response.status_code == 200
    assert b"Adoption updated successfully" in response.data

def test_delete_adoption_not_found(mock_db):
    mock_db.rowcount = 0 
    
    client = app.test_client()
    response = client.delete('/adoptions/999')
    
    assert response.status_code == 404
    assert b"Adoption not found" in response.data

def test_delete_adoption_success(mock_db):
    mock_db.rowcount = 1  
    
    client = app.test_client()
    response = client.delete('/adoptions/1')
    
    assert response.status_code == 200
    assert b"Adoption deleted successfully" in response.data

#Medical record test
def test_get_medical_records_empty(mock_db):
    mock_db.fetchall.return_value = [] 
    
    client = app.test_client()
    response = client.get('/medical_records')
    
    assert response.status_code == 404
    assert b"No medical records found" in response.data

def test_get_medical_records(mock_db):
    mock_db.fetchall.return_value = [
        (1, 101, "2023-05-10", "Vaccination", "Dr. Smith"),
        (2, 102, "2023-06-15", "Surgery", "Dr. Adams")
    ]
    
    client = app.test_client()
    response = client.get('/medical_records')
    
    assert response.status_code == 200
    assert b"Vaccination" in response.data
    assert b"Surgery" in response.data

def test_post_medical_record_missing_fields(mock_db):
    client = app.test_client()
    response = client.post('/medical_records', json={})  
    
    assert response.status_code == 400
    assert b"Pet ID is required" in response.data

def test_post_medical_record_success(mock_db):
    mock_db.lastrowid = 1 
    
    client = app.test_client()
    response = client.post('/medical_records', json={
        "pet_id": 101,
        "treatment_date": "2023-05-10",
        "treatment_details": "Vaccination",
        "veterinarian": "Dr. Smith"
    })
    
    assert response.status_code == 201
    assert b"Medical record created successfully" in response.data

def test_put_medical_record_not_found(mock_db):
    mock_db.rowcount = 0  
    
    client = app.test_client()
    response = client.put('/medical_records/999', json={
        "treatment_date": "2023-08-10",
        "treatment_details": "Updated treatment",
        "veterinarian": "Dr. Lee"
    })
    
    assert response.status_code == 404
    assert b"Medical record not found" in response.data

def test_put_medical_record_success(mock_db):
    mock_db.rowcount = 1 
    
    client = app.test_client()
    response = client.put('/medical_records/1', json={
        "treatment_date": "2023-08-10",
        "treatment_details": "Updated treatment",
        "veterinarian": "Dr. Lee"
    })
    
    assert response.status_code == 200
    assert b"Medical record updated successfully" in response.data

def test_delete_medical_record_not_found(mock_db):
    mock_db.rowcount = 0 
    
    client = app.test_client()
    response = client.delete('/medical_records/999')
    
    assert response.status_code == 404
    assert b"Medical record not found" in response.data

def test_delete_medical_record_success(mock_db):
    mock_db.rowcount = 1 
    
    client = app.test_client()
    response = client.delete('/medical_records/1')
    
    assert response.status_code == 200
    assert b"Medical record deleted successfully" in response.data

if __name__ == "__main__":
    pytest.main()
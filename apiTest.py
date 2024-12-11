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


if __name__ == "__main__":
    pytest.main()
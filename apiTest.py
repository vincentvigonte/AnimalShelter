import pytest
from api import app

@pytest.fixture
def mock_db(mocker):
    # Mock the database connection and cursor
    mock_conn = mocker.patch('flask_mysqldb.MySQL.connection')
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_cursor

def test_get_species_empty(mock_db):
    mock_db.fetchall.return_value = []  # Mock an empty result set
    
    client = app.test_client()
    response = client.get('/species')
    
    assert response.status_code == 404
    assert b"No species found" in response.data

def test_get_species(mock_db):
    # Mock a result set with one species
    mock_db.fetchall.return_value = [(1, 'Dog'), (2, 'Cat')]
    
    client = app.test_client()
    response = client.get('/species')
    
    assert response.status_code == 200
    assert b"Dog" in response.data
    assert b"Cat" in response.data

def test_post_species_missing_field(mock_db):
    client = app.test_client()
    response = client.post('/species', json={})  # Missing species_name
    
    assert response.status_code == 400
    assert b"species_name is required" in response.data

def test_post_species_success(mock_db):
    mock_db.lastrowid = 1  # Mock the ID of the last inserted row
    mock_db.rowcount = 1  # Mock successful row insertion
    
    client = app.test_client()
    response = client.post('/species', json={"species_name": "Rabbit"})
    
    assert response.status_code == 201
    assert b"Rabbit" in response.data
    assert b"species_id" in response.data

def test_put_species_not_found(mock_db):
    mock_db.rowcount = 0  # No rows updated
    
    client = app.test_client()
    response = client.put('/species/999', json={"species_name": "Updated Species"})
    
    assert response.status_code == 404
    assert b"Species not found" in response.data

def test_put_species_success(mock_db):
    mock_db.rowcount = 1  # Mock one row updated
    
    client = app.test_client()
    response = client.put('/species/1', json={"species_name": "Updated Species"})
    
    assert response.status_code == 200
    assert b"Species updated successfully" in response.data

def test_delete_species_not_found(mock_db):
    mock_db.rowcount = 0  # No rows deleted
    
    client = app.test_client()
    response = client.delete('/species/999')
    
    assert response.status_code == 404
    assert b"Species not found" in response.data

def test_delete_species_success(mock_db):
    mock_db.rowcount = 1  # Mock successful deletion
    
    client = app.test_client()
    response = client.delete('/species/1')
    
    assert response.status_code == 200
    assert b"Species deleted successfully" in response.data

if __name__ == "__main__":
    pytest.main()
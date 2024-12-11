# Animal Shelter API

## Description

A Flask-based REST API for managing pets, species, adoptions, and medical records in an animal shelter database.

## Installation

To install the required dependencies, run:

![alt text](finalHandsOnDrill\AnimalShelter\static\image\api_endpoints.png)

## Configuration

To configure the database:

    1. Upload the animal_shelter MySQL database to your server or local machine. 
    2. Update the database configuration in the Flask app with your database connection details.

Environment variables needed:

    > MYSQL_HOST: The host for the MySQL database (e.g., localhost or the IP address of the database server).
    > MYSQL_USER: MySQL username (e.g., root).
    > MYSQL_PASSWORD: MySQL password (e.g., root).
    > MYSQL_DB: Name of the database (e.g., animal_shelter).

## API Endpoints

![alt text](finalHandsOnDrill\AnimalShelter\static\image\requirements.png)

## Testing

To run the tests, ensure pytest and pytest-flask are installed, then run:

![alt text](finalHandsOnDrill/AnimalShelter/static/image/test.png)

## Example Usage

![alt text](finalHandsOnDrill\AnimalShelter\static\image\example.png)

## Git Commit Guidelines

Use conventional commits for clarity:

    > feat: add a new feature (e.g., feat: add species CRUD operations)
    > fix: resolve a bug or issue (e.g., fix: correct species retrieval error)
    > docs: update documentation (e.g., docs: update API documentation)
    > test: add or update tests (e.g., test: add mock tests for pet CRUD operations)
    > build: creating new file (e.g., build: initials files)


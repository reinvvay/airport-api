# Aiport API Service

Airport API Service is a Django-based RESTful API for managing airports, routes, crews, airplane types, airplanes, flights, orders, and tickets. The API provides endpoints to create, update, and retrieve essential airline-related data. It supports filtering, searching, and ordering of flights and other resources. Access permissions are configured so that only admins can modify data, while authenticated users have read-only access.

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation Git](#installation)
- [Run with Docker](#run-with-docker)

## Introduction

Airport API Service is designed to streamline the management of airline-related data and user interactions. Whether you’re developing an app for airport management, flight booking, or exploring Django REST APIs, this project provides a solid foundation.

### Features:
- JWT Authentication
- Email-Based Authentication
- Pagination for all pages
- API documentation with OpenAPI/Swagger
- CRUD operations for airports, routes, crews, airplane types, airplanes, flights, orders, and tickets
- Advanced filtering, searching, and ordering of flights

## Installation

1. Clone the repository:

   ```
   https://github.com/reinvvay/airport-api.git
   ```
2. Create .env file and define environmental variables following .env.sample:
   - On macOS and Linux:
   ```cp .env.sample .env```
   - On Windows:
   ```copy .env.sample .env```
3. Create a virtual environment::
   ```
   python -m venv .venv
   ```
4. Activate the virtual environment:

   - On macOS and Linux:
   ```source venv/bin/activate```
   - On Windows:
   ```venv\Scripts\activate```
5. Install project dependencies:
   ```
    pip install -r requirements.txt
   ```
6. Run database migrations:
    ```
    python manage.py makemigrations
    python manage.py migrate
    ```
   
## Run with Docker
Docker should be installed.
1. Pull docker container:
   ```
   docker pull reinvvay/airport-api:latest
   ```
2. Rull docker container
   ```
    docker-compose build
    docker-compose up
   ```
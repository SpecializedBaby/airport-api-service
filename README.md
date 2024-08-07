# Django API Project
## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Running with Docker](#running-with-docker)
- [Getting Access](#getting-access)
- [API Features](#api-features)
- [Environment Variables](#environment-variables)
- [License](#license)

## Overview
This project is a Django-based API that connects to a PostgreSQL database. It is Dockerized for easy setup and deployment. The API provides various endpoints for managing flights, routes, airports, and user authentication.

## Installation

### Cloning the Repository
First, clone the repository from GitHub:

```bash
git clone https://github.com/SpecializedBaby/airport-api-service.git
cd airport-api-service
```

#### Setting Up the Environment
Ensure you have Python 3.9 and Docker installed on your machine.

### Running with Docker
#### Build and Run Containers
To build and run the Docker containers, use Docker Compose:

```bash
docker-compose up --build
```
This command will:
- Build the Docker images for your application and PostgreSQL.
- Start the containers.
- Apply the necessary database migrations.

#### Create a Superuser
Create a superuser to access the Django admin interface:

```bash
docker-compose exec app python manage.py createsuperuser
```

## Getting Access
### Accessing the API
Once the containers are running, you can access the API at http://localhost:8000/.

### Accessing the Admin Interface
The Django admin interface is available at http://localhost:8000/admin/. Use the superuser credentials created earlier to log in.

## API Features
### User Authentication
- Register: POST /api/user/register/
- Login: POST /api/user/login/
- Manage User: GET /api/user/me/
### Airports
- List Airports: GET /api/airports/
- Retrieve Airport: GET /api/airports/{id}/
- Upload Image: POST /api/airports/{id}/upload-image/
### Routes
- List Routes: GET /api/routes/
- Retrieve Route: GET /api/routes/{id}/
### FLight
- List Flights: GET /api/flights/
- Retrieve Flight: GET /api/flights/{id}/

## Environment Variables
Ensure you have a .env file in the root of your project with the following variables:

```bash
SECRET_KEY=your_secret_key
DEBUG=1
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]
DATABASE_URL=postgres://your_db_user:your_db_password@db/your_db_name
```

## License
This project is licensed under the MIT License. See the LICENSE file for details.

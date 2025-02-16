# Blog API

## Overview
This is a RESTful API for a blog application built using Django REST Framework (DRF) with PostgreSQL as the database and JWT-based authentication.

## Technologies Used
- Django
- Django REST Framework
- PostgreSQL
- JWT Authentication

## Installation & Setup
1. Clone the repository:
   ```sh
   git clone <repo_url>
   cd <project_folder>
   ```
2. Create a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Apply migrations:
   ```sh
   python manage.py migrate
   ```
5. Run the development server:
   ```sh
   python manage.py runserver
   ```

## Authentication & Authorization
- Uses JWT authentication for secure API access.

## License
This project is open-source.

# Blog APP API

## Overview
This is a RESTful API for a blog application built using Django REST Framework (DRF) with PostgreSQL as the database and JWT-based authentication.

## Technologies Used
- Python (v3.13.1)
- Django (v5.1.6)
- Django REST Framework v(3.15.2)
- PostgreSQL (v17.4)
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
   pip insall -r requirements.txt
   ```
4. Apply migrations:
   ```sh
   python manage.py migrate
   ```
5. Run the development server:
   ```sh
   python manage.py runserver
   ```

## Features

- **Pre commit**: Integrated to code in structured manner.
- **Swagger Documentation**: Integrated Swagger documentation.
- **User Authentication**: Secure user authentication using JWT.
- **User Management**: Registration, login, and profile management.
- **Blog Posts**: CRUD operations for blog posts.
- **Categories & Tags**: Categorization of blog posts with tags.
- **Comments**: Users can comment on blog posts.
- **Upvote & Downvote**: Like and react to blog posts.
- **Search & Filtering**: Search and filter blog posts by categories, tags, or keywords.
- **Pagination**: Paginated API responses for better performance.
- **Permissions & Roles**: Role-based access control for users.
- **Admin Panel**: Django admin panel for managing users and content.

## Project Structure
```
blog/
│── config/
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── production.py
│   ├── __init__.py
│   ├── asgi.py
│   ├── urls.py
│   ├── wsgi.py
│── core/
│   ├── custom_auth/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── admins.py
│   │   ├── apps.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   ├── migrations/
│   ├── blog/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── admins.py
│   │   ├── apps.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│── manage.py
│── requirements.txt
│── .env
│── media/
│── static/
│── venv/
```

## Authentication & Authorization
- Uses JWT authentication for secure API access.

## Postman Documentation
https://web.postman.co/documentation/28689807-ad962446-0fc6-46bb-be4f-38d1ea248a0d/publish?workspaceId=8b4fc190-f4c7-450b-8e98-db77d27065d4#seo

## License
This project is open-source.

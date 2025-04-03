# User Task Management System

A secure web application with Role-Based Access Control (RBAC) that allows Managers to assign tasks to Users with deadlines, trigger notifications for missed deadlines, and automatically deactivate users after repeated failures.

## Features

### User Management
- CRUD operations for users with three roles: Admin, Manager, and User
- JWT authentication (register, login, logout)
- User deactivation after 5 failed tasks

### Role-Based Access
- **Admin**: Full access to all endpoints
- **Manager**: Assign tasks to users, view tasks, and receive notifications
- **User**: View assigned tasks, update task status

### Task Management
- Managers can assign tasks to users with deadlines
- Notifies Managers if a user misses a deadline
- Users who miss 5 tasks are automatically deactivated
- Managers can reactivate deactivated users

## Technical Stack

- Backend: Python 3.9 with Django 4.2.7 and Django REST Framework 3.14.0
- Authentication: JWT using djangorestframework-simplejwt
- Database: PostgreSQL

## Setup Instructions

### Prerequisites
- Python 3.8+
- PostgreSQL

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd user-task-management
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL:
   - Create a database called `usertaskdb`
   - Update database settings in `core/settings.py` if needed

5. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

8. To run the overdue task checker manually:
```bash
python manage.py check_overdue_tasks
```

## API Documentation

### Authentication Endpoints

#### Register a new user
- **URL**: `/api/users/register/`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "complex-password",
    "role": "USER"  // Can be ADMIN, MANAGER, or USER
  }
  ```
- **Response**: JWT tokens and user data

#### Login
- **URL**: `/api/users/login/`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "complex-password"
  }
  ```
- **Response**: JWT tokens and user data

#### Logout
- **URL**: `/api/users/logout/`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "refresh": "refresh-token"
  }
  ```

### User Management Endpoints

#### List/Create Users
- **URL**: `/api/users/`
- **Methods**: `GET`, `POST`
- **Authentication**: Required
- **Authorization**: Admin can see all users, Manager can see regular users
- **POST Request Body**:
  ```json
  {
    "email": "newuser@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "password": "complex-password",
    "role": "USER"
  }
  ```

#### Get/Update/Delete User
- **URL**: `/api/users/{user_id}/`
- **Methods**: `GET`, `PUT`, `DELETE`
- **Authentication**: Required
- **Authorization**: Admin can access any user, Manager can access only regular users, Users can access only themselves

#### Activate/Deactivate User
- **URL**: `/api/users/{user_id}/activation/`
- **Method**: `POST`
- **Authentication**: Required
- **Authorization**: Admin and Manager can activate/deactivate users
- **Request Body**:
  ```json
  {
    "is_active": true
  }
  ```

### Task Management Endpoints

#### List/Create Tasks
- **URL**: `/api/tasks/`
- **Methods**: `GET`, `POST`
- **Authentication**: Required
- **Authorization**: Admin can see all tasks, Manager can see tasks they assigned, Users can see only their tasks
- **POST Request Body**:
  ```json
  {
    "title": "Complete project report",
    "description": "Write a detailed report on the Q1 results",
    "assigned_to": 3,  // User ID
    "deadline": "2025-04-10T23:59:59Z",
    "status": "PENDING"
  }
  ```

#### Get/Update/Delete Task
- **URL**: `/api/tasks/{task_id}/`
- **Methods**: `GET`, `PUT`, `DELETE`
- **Authentication**: Required
- **Authorization**: Admin and Manager who assigned the task can perform all operations, Users can only update status

#### Check Overdue Tasks
- **URL**: `/api/tasks/overdue/`
- **Method**: `GET`
- **Authentication**: Required
- **Authorization**: Admin and Manager only

#### Mark Task as Failed
- **URL**: `/api/tasks/{task_id}/fail/`
- **Method**: `POST`
- **Authentication**: Required
- **Authorization**: Admin and Manager who assigned the task

### Notification Endpoints

#### List Notifications
- **URL**: `/api/notifications/`
- **Method**: `GET`
- **Authentication**: Required

#### Mark Notification as Read
- **URL**: `/api/notifications/{notification_id}/read/`
- **Method**: `POST`
- **Authentication**: Required

## Role-Based Permissions Summary

### Admin
- Full access to all endpoints
- Can create, view, update, and delete all users and tasks
- Can view all notifications directed to them

### Manager
- Can create and manage regular users
- Can create and manage tasks assigned by them
- Can view and mark their assigned tasks as failed
- Can activate/deactivate regular users
- Can view notifications directed to them

### User
- Can view and update their own profile
- Can view and update status of tasks assigned to them
- Can view notifications directed to them

## Periodic Tasks

To automatically check for overdue tasks, you can set up a cron job to run the management command:

```bash
# Run every hour
0 * * * * cd /path/to/project && /path/to/venv/bin/python manage.py check_overdue_tasks
```

## Testing

You can test the API endpoints using the provided Postman collection or with curl commands.

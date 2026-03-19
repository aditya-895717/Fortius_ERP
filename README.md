# Role-Based ERP System

A robust, enterprise-grade, role-based Employee Resource Planning (ERP) web application built from scratch with Python Django and Bootstrap 5.

## Features

- **Multi-Role Access Control**: Distinct roles for Admin, Human Resources (HR), and Technical Project Manager (TPM).
- **Admin Dashboard**: System overview, user management, and department management.
- **HR Workflows**: Complete modules for employee directory, attendance, leave, payroll (salary structures), recruitment (job openings & candidates), performance appraisals, training, grievances, and exit management.
- **TPM Workflows**: Comprehensive project management including tasks, milestones, risk register, issue tracker, client meetings, and project notes.
- **Modern UI**: Clean corporate theme built with Bootstrap 5 and Vanilla JavaScript.
- **Production Ready**: Modular Django setup ready for PostgreSQL (defaulting to SQLite for development).

## Installation and Setup

1. **Clone or Download the Repository**
   Ensure you are in the project root directory (`GTV_AI`).

2. **Create a Virtual Environment (Optional but Recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Database Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Seed the Database with Demo Data**
   The project includes a custom management command that sets up all roles, departments, demo users, and realistic data across all modules (projects, tasks, leave requests, etc.).
   ```bash
   python manage.py seed_data
   ```

6. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```
   Access the application at: `http://127.0.0.1:8000`

## Demo Credentials (from Seed Data)

- **Admin/Superuser**:
  - Username: `admin`
  - Password: `password123`
- **HR Manager**:
  - Username: `hr_user`
  - Password: `password123`
- **Technical Project Manager (TPM)**:
  - Username: `tpm_user`
  - Password: `password123`

*(Additional demo users like `john` (Engineering), `bob` (Finance) are also available with password `password123`).*

## Architecture & Tech Stack

- **Backend**: Python 3.10+, Django 5+
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Frontend**: HTML5, Vanilla JavaScript, Bootstrap 5.3+ (CDN), Bootstrap Icons
- **Key Django Features**: Class-based/Function-based views, ORM, Auth system, Decorators, Messages framework, Template inheritance, Partials.

## Folder Structure

- `erp_project/`: Main Django settings, WSGI, URLs.
- `accounts/`: User profiles, Authentication, Roles, Departments.
- `core/`: Dashboard routing, Notifications, Activity Logs, Global templates elements.
- `hr/`: Models and Views for all Human Resources workflows.
- `tpm/`: Models and Views for all Technical Project Management workflows.
- `templates/`: HTML templates broken down by app and partials.
- `static/`: Custom CSS (`custom.css`) and JavaScript (`main.js`).

## Next Steps for Production

1. Update `erp_project/settings.py` to use PostgreSQL.
2. Set `DEBUG = False`.
3. Configure `ALLOWED_HOSTS`.
4. Replace `SECRET_KEY` via environment variables.
5. Set up a web server like Gunicorn and Nginx/Apache.

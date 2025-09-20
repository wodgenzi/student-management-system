## Student Management System

A Django-based web application for managing student admissions, enrollments, and contacts. This project provides a simple interface for educational institutions to manage students, courses, enrollments, and contact information efficiently.

---

### Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Usage](#usage)
- [Sample Data](#sample-data)
- [Security Note](#security-note)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Features
- Student, Course, and Enrollment management
- User authentication (admin, student, teacher roles)
- Contact list integration (Google Contacts API)
- Dynamic search, filters, and modals in the UI
- Responsive design with a sidebar navigation

---

## Tech Stack
- **Backend:** Django 5.2+
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite (default, can be swapped)
- **Other:** Google Contacts API integration, Django Extensions

---

## Project Structure
```
stu-management-system/
├── accounts/      # User profiles, authentication, custom middleware
├── admissions/    # Core management: students, courses, enrollments
├── services/      # Google Contacts and other integrations
├── static/        # CSS, JavaScript, images (no real org logos)
├── templates/     # All HTML templates, including partials
└── stu-management-system/
    ├── settings.py    # Main Django settings
    ├── urls.py        # URL routing
    └── ...            # WSGI, ASGI, etc.
```

---

## Setup & Installation

### Requirements
- Python 3.8+
- Django 5.2+
- (Optional) Google API credentials for Contacts integration

### Installation Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/wodgenzi/student-management-system.git
   cd student-management-system
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables (see `.env.example`):
   - `DJANGO_SECRET_KEY` (required)
   - `DEBUG` (default: True for demo)
   - `GOOGLE_CREDENTIALS_PATH` (for Contacts, optional)
   - `GOOGLE_TOKEN_PATH` (for Contacts, optional)
4. Run migrations and create a superuser:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```
5. Start the development server:
   ```bash
   python manage.py runserver
   ```

---

## Usage
- Access the app at `http://localhost:8000/`
- Log in with the superuser or demo credentials
- Use the sidebar to navigate admissions, students, and dashboard
- Try adding/editing students, courses, and enrollments

---

## Sample Data
- The project uses placeholder/sample data for demonstration.
- No real organization or confidential data is included.
- To load demo data, you may use fixtures (if provided) or manually add via the UI.

---

## Security Note
- **Not for production use!**
- All secrets and credentials must be stored in environment variables.
- Remove any local credential/token files before sharing.
- DEBUG is set to True by default for demo purposes.

---

## License
MIT License. See [LICENSE](LICENSE) file.

---

## Acknowledgements
- Django framework
- Google Contacts API
- Community contributors

---

## To Do
- Dashboard with visual statistics
- UI tweaks
- 

---

For questions or suggestions, please open an issue or contact the author via GitHub.

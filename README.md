# Smart Attendance System

A comprehensive web-based attendance management system built with Flask and PostgreSQL, designed to streamline attendance tracking for educational institutions. The system provides separate portals for students and staff/lecturers with support for offline functionality and push notifications.

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Usage](#usage)
- [Database](#database)
- [Troubleshooting](#troubleshooting)

## ✨ Features

### Student Portal
- **Authentication**: Secure login and signup with email verification
- **Unit Registration**: Browse and enroll in available courses
- **Attendance Marking**: Mark attendance in active lessons with QR code support
- **Attendance Tracking**: View personal attendance history and records
- **Device Management**: Manage registered devices for push notifications
- **Profile Management**: Update personal profile information
- **Offline Support**: Access cached data when offline

### Staff/Lecturer Portal
- **Authentication**: Secure login and signup with email verification
- **Unit Management**: Create and manage courses/units
- **Class Sessions**: Start and manage active class sessions
- **Attendance Tracking**: View and manage student attendance records
- **Unit Reports**: Generate attendance reports for units
- **Student Management**: Manage enrolled students and restore deleted records
- **Push Notifications**: Send notifications to registered devices

### General Features
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Offline Functionality**: Service Worker for offline access to cached pages
- **Push Notifications**: Web push notifications for attendance alerts
- **Password Management**: Secure password reset via email
- **Email Notifications**: Email integration for alerts and notifications
- **Progressive Web App**: Installable as a web app

## 📁 Project Structure

```
smart_attendance_system/
├── app.py                          # Main Flask application entry point
├── config.py                       # Database configuration
├── requirements.txt                # Python dependencies
├── generate_vapid_keys.py          # Utility for generating VAPID keys
├── push_service.py                 # Push notification service
├── smart_attedance_sql_queries.sql # Database schema and queries
│
├── student_restAPI/                # Student REST API endpoints
│   ├── auth.py                     # Student authentication
│   ├── login.py                    # Student login
│   ├── active_lesson.py            # Active lesson endpoints
│   ├── classwork.py                # Classwork endpoints
│   ├── devices.py                  # Device management
│   ├── enroll.py                   # Unit enrollment
│   ├── exersice.py                 # Exercise endpoints
│   ├── forgotPassword.py           # Password recovery
│   ├── push_subscription.py        # Push notification subscriptions
│   ├── registered_units.py         # Registered units/dashboard
│   ├── Reset_password.py           # Password reset
│   └── units.py                    # Available units listing
│
├── staff_restApi/                  # Staff REST API endpoints
│   ├── auth.py                     # Staff authentication
│   ├── login.py                    # Staff login
│   ├── class_session.py            # Class session management
│   ├── lecturer_units.py           # Lecturer's units
│   ├── view_attendance.py          # Attendance viewing
│   ├── unit_report.py              # Unit attendance reports
│   ├── restore_student.py          # Student record restoration
│   ├── forgotPassword.py           # Password recovery
│   └── Reset_password.py           # Password reset
│
├── templates/                      # HTML templates
│   ├── index.html                  # Main landing page
│   ├── student_portal/             # Student templates
│   │   ├── login.html
│   │   ├── sign_up.html
│   │   ├── dashboard.html
│   │   ├── markAttendance.html
│   │   ├── Register_units.html
│   │   ├── viewAttendance.html
│   │   ├── myProfile.html
│   │   ├── forgot_password.html
│   │   ├── Reset_password.html
│   │   ├── onboarding.html
│   │   └── onb.html
│   └── staff_portal/               # Staff templates
│       ├── login.html
│       ├── sign_up.html
│       ├── dashboard.html
│       ├── manage_students.html
│       ├── viewAttendance.html
│       ├── myProfile.html
│       ├── forgot_password.html
│       ├── Reset_password.html
│       ├── test.html
│       └── test.html
│
└── static/                         # Static assets
    ├── manifest.json               # PWA manifest
    ├── sw.js                       # Service Worker for offline support
    ├── offline.html                # Offline fallback page
    ├── script.js                   # Global scripts
    ├── styles.css                  # Global styles
    ├── images/                     # Image assets
    ├── staff_portal/               # Staff portal assets
    │   ├── css/
    │   │   ├── dashboard.css
    │   │   ├── login.css
    │   │   ├── manage_students.css
    │   │   ├── myProfile.css
    │   │   └── sign_up.css
    │   └── js/
    │       ├── dashboard.js
    │       ├── login.js
    │       ├── sign_up.js
    │       └── viewAttendance.js
    └── student_portal/             # Student portal assets
        ├── css/
        │   ├── dashboard.css
        │   ├── login.css
        │   ├── myProfile.css
        │   ├── Register_units.css
        │   ├── sign_up.css
        │   └── forgot_password.css
        └── js/
            ├── dashboard.js
            ├── login.js
            ├── Register_units.js
            └── sign_up.js
```

## 🛠️ Tech Stack

### Backend
- **Framework**: Flask
- **Database**: PostgreSQL
- **Language**: Python 3.x
- **Email Service**: Flask-Mail (Gmail SMTP)
- **Push Notifications**: PyWebPush
- **Password Security**: itsdangerous

### Frontend
- **HTML5**
- **CSS3**
- **JavaScript (Vanilla)**
- **Service Workers** (Offline support)
- **Progressive Web App** (PWA)

### Database
- PostgreSQL with psycopg2 driver

## 📦 Prerequisites

- Python 3.7 or higher
- PostgreSQL 10 or higher
- pip (Python package manager)
- Git (optional)
- A Gmail account (for email notifications)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd smart_attendance_system
```

### 2. Create a Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up PostgreSQL Database

```bash
# Create a new PostgreSQL database
createdb attendance_db

# Import the schema
psql attendance_db < smart_attedance_sql_queries.sql
```

## ⚙️ Configuration

### 1. Create a `.env` File

Create a `.env` file in the root directory with the following variables:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=attendance_db
DB_USER=postgres
DB_PASSWORD=your-database-password

# Email Configuration (Gmail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@smartattendance.com

# Push Notification Keys (Generate using generate_vapid_keys.py)
VAPID_PUBLIC_KEY=your-vapid-public-key
VAPID_PRIVATE_KEY=your-vapid-private-key
VAPID_CLAIM_EMAIL=admin@smartattendance.com
```

### 2. Generate VAPID Keys for Push Notifications

```bash
python generate_vapid_keys.py
```

This will generate public and private VAPID keys. Copy these to your `.env` file.

### 3. Gmail App Password

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password at https://myaccount.google.com/apppasswords
3. Use this password in the `MAIL_PASSWORD` environment variable

## ▶️ Running the Application

### Development Mode

```bash
python app.py
```

The application will start at `http://localhost:5000`

### Production Mode

```bash
export FLASK_ENV=production
python app.py
```

## 📚 API Documentation

### Student API Endpoints

#### Authentication
- `POST /api/student/auth/signup` - Create new student account
- `POST /api/student/login` - Student login
- `POST /api/student/forgot-password` - Request password reset
- `POST /api/student/reset-password` - Reset password with token

#### Units & Enrollment
- `GET /api/student/units` - Get available units
- `GET /api/student/registered-units` - Get enrolled units
- `POST /api/student/enroll` - Enroll in a unit
- `GET /api/student/active-lesson` - Get current active lesson

#### Attendance
- `POST /api/student/mark-attendance` - Mark attendance
- `GET /api/student/view-attendance` - View attendance history

#### Device Management
- `POST /api/student/devices` - Register device for push notifications
- `GET /api/student/devices` - Get registered devices

### Staff API Endpoints

#### Authentication
- `POST /api/staff/auth/signup` - Create new staff account
- `POST /api/staff/login` - Staff login
- `POST /api/staff/forgot-password` - Request password reset
- `POST /api/staff/reset-password` - Reset password with token

#### Units & Classes
- `GET /api/staff/units` - Get lecturer's units
- `POST /api/staff/class-session/start` - Start a class session
- `GET /api/staff/class-session/active` - Get active sessions
- `POST /api/staff/class-session/end` - End a class session

#### Attendance Management
- `GET /api/staff/view-attendance` - View unit attendance
- `GET /api/staff/unit-report` - Generate attendance reports
- `POST /api/staff/manage-students` - Manage enrolled students

## 💻 Usage

### For Students

1. **Sign Up**: Navigate to the student portal and create an account
2. **Register Units**: Browse available units and enroll in courses
3. **Mark Attendance**: Join an active lesson and mark your attendance
4. **View Records**: Check your attendance history anytime
5. **Manage Profile**: Update your profile information

### For Staff/Lecturers

1. **Sign Up**: Navigate to the staff portal and create an account
2. **Manage Units**: Create and manage your courses
3. **Start Sessions**: Begin class sessions for attendance marking
4. **Track Attendance**: Monitor student attendance in real-time
5. **Generate Reports**: Create attendance reports for analysis

## 🗄️ Database

### Schema Overview

The database includes tables for:
- **Users**: Student and staff user accounts
- **Units**: Course/unit information
- **Enrollments**: Student unit registrations
- **Attendance**: Attendance records
- **Devices**: Push notification subscriptions
- **Sessions**: Active class sessions

Detailed schema available in `smart_attedance_sql_queries.sql`

## 🔧 Troubleshooting

### Common Issues

#### Database Connection Error
- Verify PostgreSQL is running
- Check database credentials in `.env` file
- Ensure database `attendance_db` exists

#### Email Not Sending
- Verify Gmail credentials are correct
- Check if 2FA is enabled and app password is used
- Verify `MAIL_*` settings in `.env`

#### Push Notifications Not Working
- Regenerate VAPID keys using `generate_vapid_keys.py`
- Verify keys are in `.env` file
- Check browser push notification permissions

#### Service Worker Issues
- Clear browser cache
- Check Service Worker status in browser DevTools
- Verify `sw.js` is being loaded correctly

### Enable Debug Mode

Set `DEBUG=True` in `.env` and restart the application for detailed error messages.

## 📝 License

This project is provided as-is for educational purposes.

## 👥 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📧 Support

For issues or questions, please contact the development team or open an issue in the repository.

---

**Last Updated**: May 2026
**Version**: 1.0

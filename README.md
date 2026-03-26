# 🚀 Placement Management System

## A Comprehensive Campus Recruitment Platform

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-black.svg)
![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Frontend](https://img.shields.io/badge/Frontend-40K+%20lines-purple.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)
![SQLite](https://img.shields.io/badge/SQLite-3.x-blue.svg)

---

## 📖 Overview

The **Placement Management System** is a full-stack, enterprise-grade web application designed to revolutionize campus recruitment processes. With **40,000+ lines of meticulously crafted frontend code**, this system provides a seamless bridge between companies, students, and placement coordinators, automating the entire placement lifecycle from drive creation to candidate selection.

---

## 🌟 Key Highlights

| Feature | Description |
|---------|-------------|
| **40,000+ Lines of Frontend Code** | Premium, production-ready UI/UX with custom animations |
| **Role-Based Access** | Student, Company, Admin, TPO dashboards with permissions |
| **Real-time Analytics** | Interactive charts and placement statistics using Chart.js |
| **Smart Application Tracking** | Automated eligibility filtering based on CGPA & branch |
| **Responsive Design** | Flawless experience across desktop, tablet, and mobile |
| **Modern Tech Stack** | Flask, SQLAlchemy, Bootstrap 5, Chart.js, AOS |

---

## ✨ Core Features

### 👨‍🎓 For Students
- 📝 **Profile Management** – Academic details, resume upload, skills section
- 🔍 **Browse Drives** – Filter by CGPA, branch, package, location
- ✅ **Smart Eligibility Check** – Automatic validation against drive criteria
- 📊 **Application Tracking** – Real-time status updates (Applied/Shortlisted/Selected/Rejected)
- 📈 **Personal Dashboard** – Application history and performance metrics

### 🏢 For Companies
- 🎯 **Drive Creation** – Post job opportunities with detailed requirements
- 📋 **Candidate Management** – View, filter, and shortlist applicants
- 📅 **Schedule Management** – Set deadlines and interview dates
- 👥 **Student Database** – Access eligible candidate pool
- 📊 **Analytics Dashboard** – Track application statistics and response rates

### 👑 For Administrators (TPO)
- ✅ **Drive Approval Workflow** – Verify and approve company drives
- 👤 **User Management** – Manage student and company accounts
- 📊 **Placement Statistics** – Comprehensive reports and analytics
- 🔔 **Notification System** – Broadcast announcements to all users
- 🏆 **Performance Tracking** – Monitor placement trends and metrics

---

## 🛠️ Technology Stack

### Frontend
| Technology | Details |
|------------|---------|
| **HTML5/CSS3** | Semantic markup, custom animations, responsive design |
| **Bootstrap 5** | Grid system, components, utilities |
| **JavaScript (ES6+)** | Dynamic interactions, form validation, API calls |
| **Chart.js** | Interactive data visualization |
| **AOS Library** | Scroll animations |
| **Font Awesome 6** | Icon library |
| **40,000+ Lines** | Custom CSS, 50+ templates, 30+ JavaScript modules |

### Backend
| Technology | Details |
|------------|---------|
| **Flask 3.0+** | Lightweight WSGI web framework |
| **Flask-SQLAlchemy** | ORM for database operations |
| **Flask-Login** | Authentication and session management |
| **Flask-WTF** | Form handling and CSRF protection |
| **Flask-Mail** | Email notifications |
| **Jinja2** | Template engine |

### Database
- **SQLite/PostgreSQL** – Production-ready database support
- **SQLAlchemy Migrations** – Version-controlled schema changes

### Security
- **Password Hashing** – bcrypt encryption
- **CSRF Protection** – Built-in token validation
- **Session Management** – Secure cookie handling
- **Input Validation** – Client and server-side validation

---

## 🚀 Installation Guide

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Virtual environment (recommended)

### Step-by-Step Setup

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/placement-management-system.git
cd placement-management-system
Create Virtual Environment

bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install Dependencies

bash
pip install -r requirements.txt
Configure Environment Variables
Create a .env file:

env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///placement.db
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
Initialize Database

bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
Run the Application

bash
python run.py
Access the Application
Open your browser and navigate to http://localhost:5000

📊 Database Schema
Table	Description
User	Authentication and user details
Student	Student profile, academic info
Company	Company profile and details
PlacementDrive	Drive details, requirements, dates
Application	Student applications with status
Notification	System notifications
Announcement	Admin announcements
🔐 User Roles & Permissions
Role	Permissions
Student	View drives, apply, track applications, update profile
Company	Create drives, view applicants, shortlist candidates
Admin (TPO)	Approve drives, manage users, view analytics
Super Admin	Full system access, role management
🎯 Module Highlights
📝 Create Placement Drive Module
Glass-morphism UI with animated backgrounds

Smart date management with calendar pickers

Real-time validation with character counter

CGPA range validation (0-10)

Branch eligibility with comma-separated inputs

Auto-adjustment of drive date based on deadline

📊 Analytics Dashboard
Interactive charts for placement statistics

Department-wise placement percentage

Company-wise hiring trends

Real-time data visualization

📋 Application Tracking
Status tracking (Applied → Shortlisted → Selected)

Interview schedule management

Offer letter generation

Automated email notifications

🎨 UI/UX Features
Glass-morphism Design – Modern, premium aesthetic

Animated Backgrounds – Gradient orbs with particle networks

Smooth Transitions – All interactive elements have hover effects

Responsive Layout – Optimized for all screen sizes

Loading Skeletons – Better perceived performance

Toast Notifications – Non-intrusive feedback messages

Dark/Light Mode – User preference support

📈 Performance Optimizations
Lazy Loading – Images load only when visible

Debounced Search – Reduced API calls

Pagination – Efficient data loading

Caching – Redis support for frequently accessed data

Minified Assets – CSS and JS compression

CDN Integration – Faster asset delivery

🧪 Testing
bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_models.py

# Run with coverage report
pytest --cov=app tests/
🤝 Contributing
Fork the repository

Create your feature branch (git checkout -b feature/AmazingFeature)

Commit your changes (git commit -m 'Add some AmazingFeature')

Push to the branch (git push origin feature/AmazingFeature)

Open a Pull Request

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
Flask – Lightweight and powerful web framework

Bootstrap – Responsive frontend toolkit

Chart.js – Beautiful data visualization

Font Awesome – Icon library

All Contributors – Who made this project possible

📞 Contact & Support
Project Maintainer: Your Name

Email: your.email@example.com

GitHub: github.com/yourusername

Issues: Report a bug

⭐ Show Your Support
If you found this project helpful, please give it a ⭐ on GitHub and share it with others!

Made with ❤️ for the campus placement community

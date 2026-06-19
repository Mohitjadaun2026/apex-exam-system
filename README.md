# APEX Online Examination System

An advanced, secure, and modern online examination platform featuring role-based dashboards, live quiz management, dynamic timers, and automated result generation.

---

## 🚀 Features

### 🔐 Role-Based Authentication
* **Admin Dashboard:** Full control over subjects, managing teachers, enrolling students, and monitoring complete system data.
* **Teacher Dashboard:** Create exams, manage specific subject questions, dynamically assign questions to papers, and view filtered class-wise performance results.
* **Student Dashboard:** View active exams, attempt real-time quizzes, see instantaneous pass/fail status and detailed scorecards.

### ⏱️ Core Examination Engine
* **Dynamic Timer:** Configurable overall exam duration along with question-level countdown timers.
* **Smart Question Assigner:** Seamlessly select and attach questions from the question bank to specific mock/test sessions.
* **Auto-Evaluation:** Instant score calculation, percentage breakdown, and automated Pass/Fail marking.

---

## 🛠️ Tech Stack

### Backend
* **Framework:** Django 
* **API Architecture:** Django REST Framework (DRF)
* **Database:** SQLite / MySQL / PostgreSQL compatible

### Frontend
* **Library:** React.js (Vite)
* **Routing:** React Router DOM
* **Styling:** Bootstrap 5 & Custom Modern CSS (Glassmorphic Components)
* **HTTP Client:** Axios (Interceptors handled for seamless routing)

---

## 📂 Project Structure

```text
apex-exam-system/
│
├── backend/               # Django REST API Source Code
│   ├── core/              # Main project configurations
│   ├── users/             # User Management (Admin, Teacher, Student)
│   ├── exams/             # Question Bank and Exam Management
│   └── results/           # Results processing & automated grading
│
└── frontend/              # React JS Application
    ├── src/
    │   ├── components/    # Reusable modern UI layouts
    │   ├── pages/         # Admin, Teacher, and Student views
    │   └── services/      # API configurations (Axios base instance)

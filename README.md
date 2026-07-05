# 🎓 College Website — Flask + SQLite

A complete college management web application built with **Flask** and **SQLite**.

---

## 📁 Project Structure

```
flask_college/
├── app.py                  ← Main Flask application (routes + DB logic)
├── college.db              ← SQLite database (auto-created on first run)
├── requirements.txt
├── templates/
│   ├── base.html           ← Shared layout (nav, footer, flash messages)
│   ├── _nav.html           ← Navigation partial
│   ├── index.html          ← Home page
│   ├── about.html          ← About Us page
│   ├── courses.html        ← Courses (loaded from DB)
│   ├── academics.html      ← Academics page
│   ├── admission.html      ← Online Application Form (saves to DB)
│   ├── contact.html        ← Contact form (saves to DB)
│   ├── login.html          ← Login page
│   ├── register.html       ← Registration page
│   ├── dashboard.html      ← Role-based dashboard
│   ├── admin_admissions.html ← Admin: manage applications
│   └── admin_messages.html   ← Admin: view contact messages
└── static/
    ├── css/
    │   ├── style.css       ← Main stylesheet
    │   └── login.css       ← Login page styles
    ├── images/             ← All college images
    └── js/                 ← (for future JS files)
```

---

## 🗄️ Database Models (SQLite)

| Table               | Description                            |
|---------------------|----------------------------------------|
| `users`             | Students, Faculty, Admins (with roles) |
| `courses`           | All courses (UG, PG, PhD)              |
| `admissions`        | Student application submissions        |
| `contact_messages`  | Messages from the contact form         |

---

## 🚀 How to Run

```bash
cd flask_college
pip install flask
python app.py
```

Then open: **http://localhost:5000**

---

## 🔐 Default Admin Login

| Field    | Value               |
|----------|---------------------|
| Email    | admin@college.com   |
| Password | admin123            |
| Role     | Admin               |

---

## ✅ Features

- **Home** — Hero, Courses overview, Campus gallery, Testimonials, CTA
- **About** — College history, Stats (35 yrs, NAAC A-grade, etc.)
- **Courses** — Dynamic from DB (UG / PG / PhD)
- **Academics** — Faculty cards + Syllabus table
- **Admission** — Full application form → saved to SQLite
- **Contact** — Contact form → saved to SQLite
- **Login / Register** — Role-based auth (Student / Faculty / Admin)
- **Dashboard** — Admin sees stats + recent apps; Student sees own apps
- **Admin Panel** — Approve/Reject applications, View messages


---

## 📌 Pages Map

| URL                     | Page                  |
|-------------------------|-----------------------|
| `/`                     | Home                  |
| `/about`                | About Us              |
| `/courses`              | Courses               |
| `/academics`            | Academics             |
| `/admission`            | Admission Form        |
| `/contact`              | Contact Us            |
| `/login`                | Login                 |
| `/register`             | Register              |
| `/dashboard`            | User Dashboard        |
| `/admin/admissions`     | Manage Applications   |
| `/admin/messages`       | View Contact Messages |
| `/api/login`            | JSON Login API        |

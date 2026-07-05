import sqlite3
import hashlib
import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash

app = Flask(__name__)
app.secret_key = "college_secret_key_2026"

DB_PATH = os.path.join(os.path.dirname(__file__), "college.db")

# ─────────────────────────────────────────────
# DATABASE SETUP
# ─────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    # Users table (students, faculty, admin)
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            email       TEXT UNIQUE NOT NULL,
            password    TEXT NOT NULL,
            role        TEXT NOT NULL CHECK(role IN ('student','faculty','admin')),
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Courses table
    c.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL UNIQUE,
            level       TEXT NOT NULL CHECK(level IN ('UG','PG','PhD')),
            stream      TEXT NOT NULL,
            duration    TEXT NOT NULL,
            fee         INTEGER NOT NULL
        )
    """)

    # Admissions / Applications table
    c.execute("""
        CREATE TABLE IF NOT EXISTS admissions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name   TEXT NOT NULL,
            email       TEXT NOT NULL,
            phone       TEXT NOT NULL,
            course_id   INTEGER NOT NULL,
            dob         TEXT NOT NULL,
            address     TEXT NOT NULL,
            status      TEXT DEFAULT 'Pending' CHECK(status IN ('Pending','Approved','Rejected')),
            applied_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(course_id) REFERENCES courses(id)
        )
    """)

    # Contact messages table
    c.execute("""
        CREATE TABLE IF NOT EXISTS contact_messages (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            email       TEXT NOT NULL,
            subject     TEXT NOT NULL,
            message     TEXT NOT NULL,
            received_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── Seed default admin ──
    admin_pw = hashlib.sha256("admin123".encode()).hexdigest()
    c.execute("""
        INSERT OR IGNORE INTO users (name, email, password, role)
        VALUES (?, ?, ?, ?)
    """, ("Admin User", "admin@college.com", admin_pw, "admin"))

    # ── Remove any existing duplicate courses (keep lowest id per name) ──
    c.execute("""
        DELETE FROM courses
        WHERE id NOT IN (
            SELECT MIN(id) FROM courses GROUP BY name
        )
    """)

    # ── Seed sample courses ──
    sample_courses = [
        ("BCom Regular",                    "UG",  "Commerce",   "3 Years", 25000),
        ("BCom Accountancy and Finance",     "UG",  "Commerce",   "3 Years", 30000),
        ("BCom Banking and Insurance",       "UG",  "Commerce",   "3 Years", 30000),
        ("BSc IT",                           "UG",  "Science",    "3 Years", 40000),
        ("BSc Computer Science",             "UG",  "Science",    "3 Years", 45000),
        ("BSc Data Science",                 "UG",  "Science",    "3 Years", 55000),
        ("BSc Artificial Intelligence",      "UG",  "Science",    "3 Years", 60000),
        ("BMS",                              "UG",  "Management", "3 Years", 40000),
        ("BAMMC",                            "UG",  "Arts/Media", "3 Years", 35000),
        ("BA Psychology",                    "UG",  "Arts",       "3 Years", 30000),
        ("MCom Accountancy",                 "PG",  "Commerce",   "2 Years", 35000),
        ("MCom Banking & Finance",           "PG",  "Commerce",   "2 Years", 40000),
        ("MSc IT",                           "PG",  "Science",    "2 Years", 50000),
        ("MSc Finance",                      "PG",  "Science",    "2 Years", 55000),
        ("PhD Business Management",          "PhD", "Commerce",   "3–6 Years", 75000),
        ("PhD Computer Science",             "PhD", "Science",    "3–6 Years", 80000),
        ("PhD Information Technology",       "PhD", "Science",    "3–6 Years", 80000),
        ("PhD Psychology",                   "PhD", "Arts",       "3–6 Years", 70000),
    ]
    c.executemany("""
        INSERT OR IGNORE INTO courses (name, level, stream, duration, fee)
        VALUES (?, ?, ?, ?, ?)
    """, sample_courses)

    conn.commit()
    conn.close()
    print("✅ Database initialised.")


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def login_required(role=None):
    """Decorator factory for route protection."""
    from functools import wraps
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in first.", "error")
                return redirect(url_for("login"))
            if role and session.get("role") != role:
                flash("Access denied.", "error")
                return redirect(url_for("index"))
            return f(*args, **kwargs)
        return wrapper
    return decorator


# ─────────────────────────────────────────────
# PUBLIC ROUTES
# ─────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/courses")
def courses():
    conn = get_db()
    all_courses = conn.execute(
        "SELECT * FROM courses GROUP BY name ORDER BY level, name"
    ).fetchall()
    conn.close()
    return render_template("courses.html", courses=all_courses)

@app.route("/academics")
def academics():
    return render_template("academics.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name    = request.form.get("name", "").strip()
        email   = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()

        if not all([name, email, subject, message]):
            flash("All fields are required.", "error")
            return redirect(url_for("contact"))

        conn = get_db()
        conn.execute("""
            INSERT INTO contact_messages (name, email, subject, message)
            VALUES (?, ?, ?, ?)
        """, (name, email, subject, message))
        conn.commit()
        conn.close()
        flash("Message sent successfully! We'll get back to you soon.", "success")
        return redirect(url_for("contact"))

    return render_template("contact.html")

@app.route("/admission", methods=["GET", "POST"])
def admission():
    conn = get_db()
    courses_list = conn.execute(
        "SELECT * FROM courses GROUP BY name ORDER BY level, name"
    ).fetchall()

    if request.method == "POST":
        full_name  = request.form.get("full_name", "").strip()
        email      = request.form.get("email", "").strip()
        phone      = request.form.get("phone", "").strip()
        course_id  = request.form.get("course_id")
        dob        = request.form.get("dob", "").strip()
        address    = request.form.get("address", "").strip()

        if not all([full_name, email, phone, course_id, dob, address]):
            flash("All fields are required.", "error")
            conn.close()
            return render_template("admission.html", courses=courses_list)

        conn.execute("""
            INSERT INTO admissions (full_name, email, phone, course_id, dob, address)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (full_name, email, phone, int(course_id), dob, address))
        conn.commit()
        conn.close()
        flash("Application submitted successfully! We will contact you soon.", "success")
        return redirect(url_for("admission"))

    conn.close()
    return render_template("admission.html", courses=courses_list)


# ─────────────────────────────────────────────
# AUTH ROUTES
# ─────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        # Support both JSON (from original login.html JS) and form POST
        if request.is_json:
            data     = request.get_json()
            email    = data.get("email", "")
            password = data.get("password", "")
            role     = data.get("role", "")
        else:
            email    = request.form.get("email", "")
            password = request.form.get("password", "")
            role     = request.form.get("role", "")

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE email=? AND password=? AND role=?",
            (email, hash_pw(password), role)
        ).fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["name"]    = user["name"]
            session["role"]    = user["role"]
            if request.is_json:
                return jsonify({"status": "success", "message": f"Welcome, {user['name']}!"})
            return redirect(url_for("dashboard"))
        else:
            if request.is_json:
                return jsonify({"status": "error", "message": "Invalid credentials."})
            flash("Invalid email, password, or role.", "error")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        role     = request.form.get("role", "student")

        if not all([name, email, password]):
            flash("All fields are required.", "error")
            return render_template("register.html")

        conn = get_db()
        try:
            conn.execute("""
                INSERT INTO users (name, email, password, role)
                VALUES (?, ?, ?, ?)
            """, (name, email, hash_pw(password), role))
            conn.commit()
            flash("Account created! Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Email already registered.", "error")
        finally:
            conn.close()

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))


# ─────────────────────────────────────────────
# DASHBOARD (after login)
# ─────────────────────────────────────────────

@app.route("/dashboard")
@login_required()
def dashboard():
    conn = get_db()
    role = session["role"]
    data = {}

    if role == "admin":
        data["total_users"]       = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        data["total_admissions"]  = conn.execute("SELECT COUNT(*) FROM admissions").fetchone()[0]
        data["pending"]           = conn.execute("SELECT COUNT(*) FROM admissions WHERE status='Pending'").fetchone()[0]
        data["messages"]          = conn.execute("SELECT COUNT(*) FROM contact_messages").fetchone()[0]
        data["recent_admissions"] = conn.execute("""
            SELECT a.full_name, a.email, c.name as course, a.status, a.applied_at
            FROM admissions a JOIN courses c ON a.course_id = c.id
            ORDER BY a.applied_at DESC LIMIT 5
        """).fetchall()

    elif role == "student":
        data["my_applications"] = conn.execute("""
            SELECT a.full_name, c.name as course, a.status, a.applied_at
            FROM admissions a JOIN courses c ON a.course_id = c.id
            WHERE a.email = ?
            ORDER BY a.applied_at DESC
        """, (conn.execute("SELECT email FROM users WHERE id=?", (session["user_id"],)).fetchone()["email"],)).fetchall()

    conn.close()
    return render_template("dashboard.html", role=role, data=data)


# Admin: view all admissions
@app.route("/admin/admissions")
@login_required(role="admin")
def admin_admissions():
    conn = get_db()
    admissions = conn.execute("""
        SELECT a.id, a.full_name, a.email, a.phone, c.name as course,
               a.status, a.applied_at
        FROM admissions a JOIN courses c ON a.course_id = c.id
        ORDER BY a.applied_at DESC
    """).fetchall()
    conn.close()
    return render_template("admin_admissions.html", admissions=admissions)


# Admin: update admission status
@app.route("/admin/admissions/<int:app_id>/status", methods=["POST"])
@login_required(role="admin")
def update_admission_status(app_id):
    new_status = request.form.get("status")
    if new_status in ("Approved", "Rejected", "Pending"):
        conn = get_db()
        conn.execute("UPDATE admissions SET status=? WHERE id=?", (new_status, app_id))
        conn.commit()
        conn.close()
        flash(f"Application #{app_id} marked as {new_status}.", "success")
    return redirect(url_for("admin_admissions"))


# Admin: contact messages
@app.route("/admin/messages")
@login_required(role="admin")
def admin_messages():
    conn = get_db()
    messages = conn.execute(
        "SELECT * FROM contact_messages ORDER BY received_at DESC"
    ).fetchall()
    conn.close()
    return render_template("admin_messages.html", messages=messages)


# ─────────────────────────────────────────────
# API ENDPOINT (for original JS login)
# ─────────────────────────────────────────────

@app.route("/api/login", methods=["POST"])
def api_login():
    data     = request.get_json(force=True)
    email    = data.get("email", "")
    password = data.get("password", "")
    role     = data.get("role", "")

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE email=? AND password=? AND role=?",
        (email, hash_pw(password), role)
    ).fetchone()
    conn.close()

    if user:
        session["user_id"] = user["id"]
        session["name"]    = user["name"]
        session["role"]    = user["role"]
        return jsonify({"status": "success", "message": f"Welcome, {user['name']}!"})
    return jsonify({"status": "error", "message": "Invalid credentials."})


# ─────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)

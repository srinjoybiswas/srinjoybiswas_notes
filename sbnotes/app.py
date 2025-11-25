from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, flash
import os, json, uuid, random, string, datetime
from functools import wraps
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "super-secret-key-change-this"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOAD_NOTES = os.path.join(BASE_DIR, "uploads", "notes")
UPLOAD_SYLLABUS = os.path.join(BASE_DIR, "uploads", "syllabus")

os.makedirs(UPLOAD_NOTES, exist_ok=True)
os.makedirs(UPLOAD_SYLLABUS, exist_ok=True)

ADMIN_EMAIL = "srinjoy@admin.sbnotes"
ADMIN_PASSWORD = "bca_123"

# ------------------ EMAIL CONFIG ------------------
# Replace with your Gmail (safe to share)
GMAIL_EMAIL = "bcacoding25.28@gmail.com"

# Replace with your Gmail APP PASSWORD (NOT Gmail login password!)
# Example format: abcd efgh ijkl mnop
GMAIL_APP_PASSWORD = "ttfv unfv fizl cjvn"


def send_credentials_email(to_email, user_id, password):
    subject = "Your SB Notes Login Details"
    body = f"""
Hello {to_email},

Your SB Notes login details are:

Login ID: {user_id}
Password: {password}

Use these to log in at SB Notes.

Regards,
SB Notes Admin
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = GMAIL_EMAIL
    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print("Error sending email:", e)


# ------------------ HELPERS ------------------

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_json(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def generate_password(length=8):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))

def find_user_by_email(email):
    data = load_json("users.json") or {"users": []}
    for u in data["users"]:
        if u["email"].lower() == email.lower():
            return u
    return None

def find_user_by_userid(user_id):
    data = load_json("users.json") or {"users": []}
    for u in data["users"]:
        if u["user_id"].lower() == user_id.lower():
            return u
    return None

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return wrapper

# ------------------ ROUTES ------------------

@app.route("/")
def index():
    return render_template("index.html")

# ------------------ USER REGISTER ------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        surname = request.form.get("surname", "").strip()
        mobile = request.form.get("mobile", "").strip()
        email = request.form.get("email", "").strip()

        if not (name and surname and mobile and email):
            flash("All fields are required.", "error")
            return redirect(url_for("register"))

        users_data = load_json("users.json") or {"users": []}

        existing = find_user_by_email(email)
        if existing:
            send_credentials_email(existing["email"], existing["user_id"], existing["password"])
            flash("You are already registered. Login details sent again.", "info")
            return redirect(url_for("login"))

        user_id = f"{name}.{surname}@sbnotes.log"
        password = generate_password()

        new_user = {
            "id": str(uuid.uuid4()),
            "name": name,
            "surname": surname,
            "mobile": mobile,
            "email": email,
            "user_id": user_id,
            "password": password,
            "created_at": datetime.datetime.now().isoformat()
        }

        users_data["users"].append(new_user)
        save_json("users.json", users_data)

        send_credentials_email(email, user_id, password)
        flash("Registration successful! Check your email.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

# ------------------ USER LOGIN ------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form.get("user_id", "").strip()
        password = request.form.get("password", "").strip()

        user = find_user_by_userid(user_id)
        if not user or user["password"] != password:
            flash("Invalid login ID or password.", "error")
            return redirect(url_for("login"))

        session["user_id"] = user["user_id"]
        session["name"] = user["name"]
        session["surname"] = user["surname"]
        session["email"] = user["email"]

        flash(f"Welcome {user['name']}!", "success")
        return redirect(url_for("user_dashboard"))

    return render_template("login.html")

# ------------------ USER FORGOT ID ------------------

@app.route("/forgot-id", methods=["GET", "POST"])
def forgot_id():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        user = find_user_by_email(email)
        if not user:
            flash("This email is not registered.", "error")
            return redirect(url_for("forgot_id"))

        send_credentials_email(user["email"], user["user_id"], user["password"])
        flash("Login details sent to your email.", "success")
        return redirect(url_for("login"))

    return render_template("forgot_id.html")

# ------------------ USER LOGOUT ------------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# ------------------ USER DASHBOARD ------------------

@app.route("/user/dashboard")
@login_required
def user_dashboard():
    departments = load_json("departments.json").get("departments", [])
    notes = load_json("notes.json").get("notes", [])
    return render_template("user_dashboard.html", departments=departments, notes=notes)

# ------------------ READ NOTE ------------------

@app.route("/read/<note_id>")
@login_required
def read_note(note_id):
    notes_data = load_json("notes.json").get("notes", [])
    note = next((n for n in notes_data if n["id"] == note_id), None)
    if not note:
        flash("Note not found.", "error")
        return redirect(url_for("user_dashboard"))

    return render_template("read_note.html", note=note)

# ------------------ ADMIN LOGIN ------------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid admin credentials.", "error")
            return redirect(url_for("admin_login"))

    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("index"))

# ------------------ ADMIN DASHBOARD ------------------

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    departments = load_json("departments.json").get("departments", [])
    notes = load_json("notes.json").get("notes", [])
    return render_template("admin_dashboard.html", departments=departments, notes=notes)

# ------------------ ADMIN DEPARTMENTS ------------------

@app.route("/admin/departments", methods=["GET", "POST"])
@admin_required
def admin_departments():
    data = load_json("departments.json") or {"departments": []}

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add_dept":
            dept_id = request.form.get("dept_id").strip()
            name = request.form.get("name").strip()
            if dept_id and name:
                data["departments"].append({"id": dept_id, "name": name, "semesters": []})

        elif action == "delete_dept":
            dept_id = request.form.get("dept_id")
            data["departments"] = [d for d in data["departments"] if d["id"] != dept_id]

        save_json("departments.json", data)
        return redirect(url_for("admin_departments"))

    return render_template("admin_departments.html", data=data)

# ------------------ ADMIN SEMESTERS ------------------

@app.route("/admin/semesters", methods=["POST"])
@admin_required
def admin_semesters():
    data = load_json("departments.json") or {"departments": []}
    dept_id = request.form.get("dept_id")
    action = request.form.get("action")

    dept = next((d for d in data["departments"] if d["id"] == dept_id), None)
    if not dept:
        return redirect(url_for("admin_departments"))

    if action == "add_sem":
        sem_id = request.form.get("sem_id").strip()
        sem_name = request.form.get("sem_name").strip()
        if sem_id and sem_name:
            dept["semesters"].append({
                "id": sem_id, "name": sem_name,
                "subjects": [], "syllabus_pdf": ""
            })

    elif action == "delete_sem":
        sem_id = request.form.get("sem_id")
        dept["semesters"] = [s for s in dept["semesters"] if s["id"] != sem_id]

    save_json("departments.json", data)
    return redirect(url_for("admin_departments"))

# ------------------ ADMIN SUBJECTS ------------------

@app.route("/admin/subjects", methods=["POST"])
@admin_required
def admin_subjects():
    data = load_json("departments.json") or {"departments": []}
    dept_id = request.form.get("dept_id")
    sem_id = request.form.get("sem_id")
    action = request.form.get("action")

    dept = next((d for d in data["departments"] if d["id"] == dept_id), None)
    if not dept:
        return redirect(url_for("admin_departments"))

    sem = next((s for s in dept["semesters"] if s["id"] == sem_id), None)
    if not sem:
        return redirect(url_for("admin_departments"))

    if action == "add_subject":
        sub_id = request.form.get("sub_id").strip()
        sub_name = request.form.get("sub_name").strip()
        if sub_id and sub_name:
            sem["subjects"].append({"id": sub_id, "name": sub_name})

    elif action == "delete_subject":
        sub_id = request.form.get("sub_id")
        sem["subjects"] = [s for s in sem["subjects"] if s["id"] != sub_id]

    save_json("departments.json", data)
    return redirect(url_for("admin_departments"))

# ------------------ ADMIN SYLLABUS ------------------

@app.route("/admin/syllabus", methods=["POST"])
@admin_required
def admin_syllabus():
    data = load_json("departments.json") or {"departments": []}
    dept_id = request.form.get("dept_id")
    sem_id = request.form.get("sem_id")
    file = request.files.get("syllabus_pdf")

    dept = next((d for d in data["departments"] if d["id"] == dept_id), None)
    if not dept or not file:
        return redirect(url_for("admin_departments"))

    sem = next((s for s in dept["semesters"] if s["id"] == sem_id), None)
    if not sem:
        return redirect(url_for("admin_departments"))

    filename = f"{dept_id}_{sem_id}_syllabus.pdf"
    filepath = os.path.join(UPLOAD_SYLLABUS, filename)
    file.save(filepath)
    sem["syllabus_pdf"] = f"/uploads/syllabus/{filename}"

    save_json("departments.json", data)
    return redirect(url_for("admin_departments"))

# ------------------ ADMIN NOTES ------------------

@app.route("/admin/notes", methods=["GET", "POST"])
@admin_required
def admin_notes():
    departments = load_json("departments.json").get("departments", [])
    notes_data = load_json("notes.json") or {"notes": []}

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add_note":
            dept_id = request.form.get("dept_id")
            sem_id = request.form.get("sem_id")
            sub_id = request.form.get("sub_id")
            title = request.form.get("title")
            file = request.files.get("note_pdf")

            if file and dept_id and sem_id and sub_id and title:
                note_id = str(uuid.uuid4())
                filename = f"{note_id}.pdf"
                filepath = os.path.join(UPLOAD_NOTES, filename)
                file.save(filepath)

                notes_data["notes"].append({
                    "id": note_id,
                    "dept_id": dept_id,
                    "semester_id": sem_id,
                    "subject_id": sub_id,
                    "title": title,
                    "file_path": f"/uploads/notes/{filename}",
                    "uploaded_at": datetime.datetime.now().isoformat()
                })

        elif action == "delete_note":
            note_id = request.form.get("note_id")
            notes_data["notes"] = [n for n in notes_data["notes"] if n["id"] != note_id]

        save_json("notes.json", notes_data)
        return redirect(url_for("admin_notes"))

    return render_template("admin_notes.html", departments=departments, notes=notes_data["notes"])

# ------------------ SECURE FILE SERVING ------------------

@app.route("/uploads/<path:folder>/<path:filename>")
@login_required
def serve_upload(folder, filename):
    if folder == "notes":
        return send_from_directory(UPLOAD_NOTES, filename)
    elif folder == "syllabus":
        return send_from_directory(UPLOAD_SYLLABUS, filename)
    else:
        return "Not found", 404

# ------------------ RUN APP ------------------

if __name__ == "__main__":
    app.run(debug=True)


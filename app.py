import os
import sqlite3
from datetime import datetime
from flask import Flask, request, redirect, url_for, session, render_template_string, flash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "devdesk_public.db")

app = Flask(__name__)
app.secret_key = os.environ.get("DEVDESK_SECRET", "devdesk-local-language-session-key")

TEXT = {
    "en": {
        "brand": "DevDesk", "tagline": "Your workspace, organized.",
        "dashboard": "Dashboard", "projects": "Projects",
        "tasks": "Tasks", "notes": "Notes", "overview": "Overview",
        "welcome": "Your workspace, organized.",
        "subtitle": "Manage projects, tasks and notes in one simple workspace.",
        "new_project": "New project", "project_name": "Project name",
        "description": "Description", "add_project": "Create project",
        "your_projects": "Your projects", "no_projects": "No projects yet.",
        "add_task": "Add task", "task_title": "Task title",
        "select_project": "Choose project", "due_date": "Due date",
        "create_task": "Create task", "your_tasks": "Your tasks",
        "no_tasks": "No tasks yet.", "completed": "Completed",
        "open": "Open", "add_note": "Add note", "note_title": "Note title",
        "note_body": "Write your note...", "save_note": "Save note",
        "your_notes": "Your notes", "no_notes": "No notes yet.",
        "delete": "Delete", "confirm": "Are you sure?",
        "created": "Created", "status": "Status", "actions": "Actions",
        "language": "فارسی", "all": "All", "back": "Back to dashboard",
        "footer": "Open-source project workspace",
        "project_created": "Project created.",
        "task_created": "Task created.", "note_created": "Note saved.",
        "required": "Please fill in the required fields.",
        "invalid": "Invalid request."
    },
    "fa": {
        "brand": "دِو‌دِسک", "tagline": "فضای کاری منظم شما",
        "dashboard": "داشبورد", "projects": "پروژه‌ها",
        "tasks": "کارها", "notes": "یادداشت‌ها", "overview": "نمای کلی",
        "welcome": "فضای کاری منظم شما",
        "subtitle": "پروژه‌ها، کارها و یادداشت‌هایتان را در یک محیط ساده مدیریت کنید.",
        "new_project": "پروژه جدید", "project_name": "نام پروژه",
        "description": "توضیحات", "add_project": "ایجاد پروژه",
        "your_projects": "پروژه‌های شما", "no_projects": "هنوز پروژه‌ای ندارید.",
        "add_task": "افزودن کار", "task_title": "عنوان کار",
        "select_project": "انتخاب پروژه", "due_date": "مهلت انجام",
        "create_task": "ایجاد کار", "your_tasks": "کارهای شما",
        "no_tasks": "هنوز کاری ثبت نشده است.", "completed": "انجام‌شده",
        "open": "باز", "add_note": "افزودن یادداشت", "note_title": "عنوان یادداشت",
        "note_body": "یادداشت خود را بنویسید...", "save_note": "ذخیره یادداشت",
        "your_notes": "یادداشت‌های شما", "no_notes": "هنوز یادداشتی ندارید.",
        "delete": "حذف", "confirm": "آیا مطمئن هستید؟",
        "created": "ایجاد شده", "status": "وضعیت", "actions": "عملیات",
        "language": "English", "all": "همه", "back": "بازگشت به داشبورد",
        "footer": "فضای کاری متن‌باز",
        "project_created": "پروژه ایجاد شد.",
        "task_created": "کار ایجاد شد.", "note_created": "یادداشت ذخیره شد.",
        "required": "لطفاً فیلدهای ضروری را تکمیل کنید.",
        "invalid": "درخواست نامعتبر است."
    }
}

def tr(key):
    lang = session.get("lang", "en")
    return TEXT.get(lang, TEXT["en"]).get(key, key)

app.jinja_env.globals["tr"] = tr

def connect():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with connect() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                title TEXT NOT NULL,
                due_date TEXT NOT NULL DEFAULT '',
                done INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY(project_id) REFERENCES projects(id)
                    ON DELETE SET NULL
            );
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                body TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            );
        """)
        db.execute("PRAGMA foreign_keys = ON")

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

PAGE = r"""
<!doctype html>
<html lang="{{ 'fa' if session.get('lang','en') == 'fa' else 'en' }}"
      dir="{{ 'rtl' if session.get('lang','en') == 'fa' else 'ltr' }}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ title }} · DevDesk</title>
<style>
:root{font-family:Inter,"Segoe UI",Tahoma,Arial,sans-serif;color:#e9edf5;
background:#0b1020;color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;min-height:100vh;background:radial-gradient(ellipse at top,#172343,#0b1020 58%)}
a{color:inherit;text-decoration:none}
button,input,textarea,select{font:inherit}
button,.btn{border:0;border-radius:10px;padding:10px 14px;cursor:pointer;
background:#6479f5;color:white;display:inline-flex;align-items:center;justify-content:center;gap:7px}
button:hover,.btn:hover{filter:brightness(1.12)}
.btn.secondary{background:#252f48;color:#e9edf5}
.btn.danger{background:#753849}
input,textarea,select{width:100%;border:1px solid #303b56;background:#10182b;
color:#f4f6fc;padding:11px;border-radius:10px;outline:none}
input:focus,textarea:focus,select:focus{border-color:#8290ff}
textarea{min-height:95px;resize:vertical}
label{display:block;font-size:13px;color:#b8c3d9;margin-bottom:7px}
.shell{max-width:1120px;margin:auto;padding:24px}
header{display:flex;justify-content:space-between;align-items:center;gap:18px;
margin-bottom:30px;flex-wrap:wrap}
.brand{font-size:21px;font-weight:800;letter-spacing:-.5px}
.brand span{color:#8e9aff}
nav{display:flex;gap:7px;flex-wrap:wrap}
nav a{padding:9px 12px;color:#bac5dc;border-radius:9px}
nav a:hover,nav a.active{background:#202b46;color:white}
.hero{padding:30px;border:1px solid #293550;border-radius:20px;
background:linear-gradient(120deg,#1b2948,#141c30);margin-bottom:23px}
.hero h1{margin:0 0 9px;font-size:clamp(27px,4vw,40px)}
.hero p{color:#b4c0d7;line-height:1.8;margin:0}
.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:15px;margin:18px 0}
.card{border:1px solid #293550;background:#131b2d;border-radius:16px;padding:19px;min-width:0}
.stat{font-size:30px;font-weight:800;margin-top:10px}
.muted{color:#9eabc4;font-size:13px}
.section-head{display:flex;justify-content:space-between;align-items:center;gap:12px;
margin:28px 0 14px;flex-wrap:wrap}
.section-head h2{font-size:20px;margin:0}
.list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:13px}
.item-title{font-size:17px;font-weight:700;margin:0 0 8px;overflow-wrap:anywhere}
.item-desc{color:#aab7d0;white-space:pre-wrap;line-height:1.7;overflow-wrap:anywhere}
.form-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.field{margin-bottom:14px}
.wide{grid-column:1/-1}
.inline{display:inline}
.actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}
.task{display:flex;gap:12px;align-items:flex-start}
.task .item-title{flex:1}
.badge{display:inline-block;padding:5px 8px;border-radius:8px;
background:#263353;color:#cbd4ff;font-size:12px}
.badge.done{background:#173e34;color:#a5f1d5}
.flash{padding:12px 14px;border-radius:10px;background:#26375b;margin-bottom:12px}
.empty{color:#aab7d0;text-align:center;padding:25px}
footer{border-top:1px solid #27314a;margin-top:35px;padding:20px 0;color:#8290aa;
font-size:12px;display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap}
@media(max-width:700px){.shell{padding:15px}.grid{grid-template-columns:repeat(2,minmax(0,1fr))}
.list,.form-grid{grid-template-columns:1fr}.hero{padding:22px}.wide{grid-column:auto}}
@media(max-width:420px){.grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="shell">
<header>
<a class="brand" href="{{ url_for('dashboard') }}"><span>◆</span> DevDesk</a>
<nav>
<a class="{{ 'active' if active=='dashboard' else '' }}" href="{{ url_for('dashboard') }}">{{ tr('dashboard') }}</a>
<a class="{{ 'active' if active=='projects' else '' }}" href="{{ url_for('projects') }}">{{ tr('projects') }}</a>
<a class="{{ 'active' if active=='tasks' else '' }}" href="{{ url_for('tasks') }}">{{ tr('tasks') }}</a>
<a class="{{ 'active' if active=='notes' else '' }}" href="{{ url_for('notes') }}">{{ tr('notes') }}</a>
<a class="btn secondary" href="{{ url_for('language', code='fa' if session.get('lang','en') == 'en' else 'en') }}">{{ tr('language') }}</a>
</nav>
</header>
{% for message in get_flashed_messages() %}<div class="flash">{{ message }}</div>{% endfor %}
{{ content|safe }}
<footer><span>DevDesk · {{ tr('footer') }}</span><span>Flask + SQLite</span></footer>
</div>
<script>
document.querySelectorAll("form[data-confirm]").forEach(function(form){
  form.addEventListener("submit",function(event){
    if(!confirm(form.dataset.confirm)){event.preventDefault();}
  });
});
</script>
</body></html>
"""

def page(title, content, active):
    return render_template_string(PAGE, title=title, content=content, active=active)

@app.get("/language/<code>")
def language(code):
    if code in ("en", "fa"):
        session["lang"] = code
    return redirect(request.referrer if request.referrer and request.host in request.referrer else url_for("dashboard"))

@app.get("/")
def dashboard():
    with connect() as db:
        project_count = db.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
        task_count = db.execute("SELECT COUNT(*) FROM tasks WHERE done=0").fetchone()[0]
        note_count = db.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
        projects = db.execute("SELECT * FROM projects ORDER BY id DESC LIMIT 6").fetchall()
        tasks = db.execute("""
            SELECT tasks.*, projects.name AS project_name
            FROM tasks LEFT JOIN projects ON projects.id=tasks.project_id
            ORDER BY tasks.done ASC, tasks.id DESC LIMIT 6
        """).fetchall()
    content = render_template_string("""
    <section class="hero"><h1>{{ tr('welcome') }}</h1><p>{{ tr('subtitle') }}</p></section>
    <div class="grid">
      <a class="card" href="{{ url_for('projects') }}"><div class="muted">{{ tr('projects') }}</div><div class="stat">{{ pc }}</div></a>
      <a class="card" href="{{ url_for('tasks') }}"><div class="muted">{{ tr('tasks') }}</div><div class="stat">{{ tc }}</div></a>
      <a class="card" href="{{ url_for('notes') }}"><div class="muted">{{ tr('notes') }}</div><div class="stat">{{ nc }}</div></a>
    </div>
    <div class="section-head"><h2>{{ tr('your_projects') }}</h2><a class="btn" href="{{ url_for('projects') }}">{{ tr('new_project') }} +</a></div>
    <div class="list">{% for p in projects %}
      <article class="card"><h3 class="item-title">{{ p.name }}</h3><p class="item-desc">{{ p.description or '' }}</p>
      <div class="muted">{{ tr('created') }}: {{ p.created_at }}</div></article>
    {% else %}<article class="card empty">{{ tr('no_projects') }}</article>{% endfor %}</div>
    <div class="section-head"><h2>{{ tr('your_tasks') }}</h2><a class="btn secondary" href="{{ url_for('tasks') }}">{{ tr('tasks') }} →</a></div>
    <div class="list">{% for t in tasks %}
      <article class="card"><div class="task"><div><div class="item-title">{{ t.title }}</div>
      <div class="muted">{{ t.project_name or tr('all') }}{% if t.due_date %} · {{ t.due_date }}{% endif %}</div></div>
      <span class="badge {{ 'done' if t.done else '' }}">{{ tr('completed') if t.done else tr('open') }}</span></div></article>
    {% else %}<article class="card empty">{{ tr('no_tasks') }}</article>{% endfor %}</div>
    """, pc=project_count, tc=task_count, nc=note_count, projects=projects, tasks=tasks)
    return page(tr("dashboard"), content, "dashboard")

@app.route("/projects", methods=["GET", "POST"])
def projects():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        if not name:
            flash(tr("required"))
        else:
            with connect() as db:
                db.execute("INSERT INTO projects(name,description,created_at) VALUES(?,?,?)",
                           (name, description, now()))
            flash(tr("project_created"))
        return redirect(url_for("projects"))
    with connect() as db:
        rows = db.execute("SELECT * FROM projects ORDER BY id DESC").fetchall()
    content = render_template_string("""
    <section class="hero"><h1>{{ tr('projects') }}</h1><p>{{ tr('subtitle') }}</p></section>
    <section class="card"><h2>{{ tr('new_project') }}</h2>
    <form method="post"><div class="form-grid">
    <div class="field"><label>{{ tr('project_name') }}</label><input name="name" required maxlength="160"></div>
    <div class="field"><label>{{ tr('description') }}</label><input name="description" maxlength="500"></div>
    </div><button>{{ tr('add_project') }}</button></form></section>
    <div class="section-head"><h2>{{ tr('your_projects') }}</h2></div>
    <div class="list">{% for p in rows %}<article class="card">
    <h3 class="item-title">{{ p.name }}</h3><p class="item-desc">{{ p.description }}</p>
    <div class="muted">{{ tr('created') }}: {{ p.created_at }}</div>
    <form class="actions" method="post" action="{{ url_for('delete_project', project_id=p.id) }}" data-confirm="{{ tr('confirm') }}">
    <button class="danger">{{ tr('delete') }}</button></form></article>
    {% else %}<article class="card empty">{{ tr('no_projects') }}</article>{% endfor %}</div>
    """, rows=rows)
    return page(tr("projects"), content, "projects")

@app.post("/projects/<int:project_id>/delete")
def delete_project(project_id):
    with connect() as db:
        db.execute("UPDATE tasks SET project_id=NULL WHERE project_id=?", (project_id,))
        db.execute("DELETE FROM projects WHERE id=?", (project_id,))
    return redirect(url_for("projects"))

@app.route("/tasks", methods=["GET", "POST"])
def tasks():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        due = request.form.get("due_date", "").strip()
        project_raw = request.form.get("project_id", "")
        project_id = int(project_raw) if project_raw.isdigit() else None
        if not title:
            flash(tr("required"))
        else:
            with connect() as db:
                db.execute("INSERT INTO tasks(project_id,title,due_date,created_at) VALUES(?,?,?,?)",
                           (project_id, title, due, now()))
            flash(tr("task_created"))
        return redirect(url_for("tasks"))
    with connect() as db:
        projects_rows = db.execute("SELECT id,name FROM projects ORDER BY name").fetchall()
        rows = db.execute("""SELECT tasks.*, projects.name AS project_name
          FROM tasks LEFT JOIN projects ON projects.id=tasks.project_id
          ORDER BY tasks.done ASC,tasks.id DESC""").fetchall()
    content = render_template_string("""
    <section class="hero"><h1>{{ tr('tasks') }}</h1></section>
    <section class="card"><h2>{{ tr('add_task') }}</h2><form method="post"><div class="form-grid">
    <div class="field"><label>{{ tr('task_title') }}</label><input name="title" required maxlength="200"></div>
    <div class="field"><label>{{ tr('select_project') }}</label><select name="project_id"><option value="">{{ tr('all') }}</option>
    {% for p in projects_rows %}<option value="{{ p.id }}">{{ p.name }}</option>{% endfor %}</select></div>
    <div class="field"><label>{{ tr('due_date') }}</label><input type="date" name="due_date"></div>
    </div><button>{{ tr('create_task') }}</button></form></section>
    <div class="section-head"><h2>{{ tr('your_tasks') }}</h2></div>
    <div class="list">{% for t in rows %}<article class="card"><div class="task">
    <div style="flex:1"><h3 class="item-title">{{ t.title }}</h3><div class="muted">{{ t.project_name or tr('all') }}{% if t.due_date %} · {{ t.due_date }}{% endif %}</div>
    <span class="badge {{ 'done' if t.done else '' }}">{{ tr('completed') if t.done else tr('open') }}</span></div></div>
    <div class="actions"><form method="post" action="{{ url_for('toggle_task', task_id=t.id) }}"><button class="secondary">{{ tr('open') if t.done else tr('completed') }}</button></form>
    <form method="post" action="{{ url_for('delete_task', task_id=t.id) }}" data-confirm="{{ tr('confirm') }}"><button class="danger">{{ tr('delete') }}</button></form></div>
    </article>{% else %}<article class="card empty">{{ tr('no_tasks') }}</article>{% endfor %}</div>
    """, projects_rows=projects_rows, rows=rows)
    return page(tr("tasks"), content, "tasks")

@app.post("/tasks/<int:task_id>/toggle")
def toggle_task(task_id):
    with connect() as db:
        db.execute("UPDATE tasks SET done=CASE WHEN done=0 THEN 1 ELSE 0 END WHERE id=?", (task_id,))
    return redirect(url_for("tasks"))

@app.post("/tasks/<int:task_id>/delete")
def delete_task(task_id):
    with connect() as db:
        db.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    return redirect(url_for("tasks"))

@app.route("/notes", methods=["GET", "POST"])
def notes():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        body = request.form.get("body", "").strip()
        if not title:
            flash(tr("required"))
        else:
            with connect() as db:
                db.execute("INSERT INTO notes(title,body,created_at) VALUES(?,?,?)",
                           (title, body, now()))
            flash(tr("note_created"))
        return redirect(url_for("notes"))
    with connect() as db:
        rows = db.execute("SELECT * FROM notes ORDER BY id DESC").fetchall()
    content = render_template_string("""
    <section class="hero"><h1>{{ tr('notes') }}</h1></section>
    <section class="card"><h2>{{ tr('add_note') }}</h2><form method="post">
    <div class="field"><label>{{ tr('note_title') }}</label><input name="title" required maxlength="200"></div>
    <div class="field"><label>{{ tr('note_body') }}</label><textarea name="body" rows="4"></textarea></div>
    <button>{{ tr('save_note') }}</button></form></section>
    <div class="section-head"><h2>{{ tr('your_notes') }}</h2></div>
    <div class="list">{% for n in rows %}<article class="card"><h3 class="item-title">{{ n.title }}</h3>
    <p class="item-desc">{{ n.body }}</p><div class="muted">{{ tr('created') }}: {{ n.created_at }}</div>
    <form class="actions" method="post" action="{{ url_for('delete_note', note_id=n.id) }}" data-confirm="{{ tr('confirm') }}">
    <button class="danger">{{ tr('delete') }}</button></form></article>
    {% else %}<article class="card empty">{{ tr('no_notes') }}</article>{% endfor %}</div>
    """, rows=rows)
    return page(tr("notes"), content, "notes")

@app.post("/notes/<int:note_id>/delete")
def delete_note(note_id):
    with connect() as db:
        db.execute("DELETE FROM notes WHERE id=?", (note_id,))
    return redirect(url_for("notes"))

@app.errorhandler(404)
def not_found(error):
    return page("404", '<section class="hero"><h1>404</h1><a class="btn" href="/">Home</a></section>', "" ), 404

if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=False)
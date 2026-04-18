from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# ====================== Configuration ======================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key-todo-app'

# Création automatique du dossier instance
instance_path = os.path.join(app.root_path, 'instance')
os.makedirs(instance_path, exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "todos.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ====================== Modèle ======================
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default="À Faire")
    progress = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Task {self.title}>"

# Création de la base de données
with app.app_context():
    db.create_all()

# ====================== Routes ======================
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()

        if title:
            new_task = Task(title=title, description=description if description else None)
            db.session.add(new_task)
            db.session.commit()
            flash("Tâche ajoutée avec succès !", "success")

        return redirect(url_for("index"))

    # Récupération des tâches
    todo_tasks = Task.query.filter_by(status="À Faire").order_by(Task.created_at.desc()).all()
    in_progress_tasks = Task.query.filter_by(status="En Cours").order_by(Task.created_at.desc()).all()
    done_tasks = Task.query.filter_by(status="Terminées").order_by(Task.created_at.desc()).all()

    return render_template("index.html", 
                           todo_tasks=todo_tasks,
                           in_progress_tasks=in_progress_tasks,
                           done_tasks=done_tasks)

@app.route("/toggle/<int:task_id>")
def toggle(task_id):
    task = Task.query.get_or_404(task_id)
    
    if task.status == "À Faire":
        task.status = "En Cours"
        task.progress = 50
    elif task.status == "En Cours":
        task.status = "Terminées"
        task.progress = 100
    else:
        task.status = "À Faire"
        task.progress = 0
    
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/delete/<int:task_id>")
def delete(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash("Tâche supprimée", "danger")
    return redirect(url_for("index"))

@app.route("/delete/all")
def delete_all():
    Task.query.delete()
    db.session.commit()
    flash("Toutes les tâches ont été supprimées", "danger")
    return redirect(url_for("index"))

@app.route("/update/<int:task_id>", methods=["POST"])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()

    if title:
        task.title = title
        task.description = description if description else None
        db.session.commit()
        flash("Tâche mise à jour", "success")

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)

from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    redirect,
    url_for
)
import os
import logging

from database import (
    get_db_connection,
    create_database,
    add_sample_data
)


# --------------------------------------------------
# FLASK CONFIGURATION
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR,
    static_url_path="/static"
)

app.logger.setLevel(logging.INFO)


# --------------------------------------------------
# DATABASE INITIALIZATION
# --------------------------------------------------

# DATABASE_URL set aana Neon PostgreSQL use aagum.
# DATABASE_URL illa na local SQLite use aagum.
create_database()
add_sample_data()


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("dashboard.html")


# --------------------------------------------------
# CLIENTS PAGE
# --------------------------------------------------

@app.route("/clients")
def clients_page():
    connection = get_db_connection()

    try:
        clients = connection.execute(
            "SELECT * FROM clients ORDER BY id DESC"
        ).fetchall()

        return render_template(
            "clients.html",
            clients=clients
        )

    finally:
        connection.close()


# --------------------------------------------------
# ADD CLIENT
# --------------------------------------------------

@app.route("/clients/add", methods=["POST"])
def add_client():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    company = request.form.get("company", "").strip()

    if not name:
        return "Client name is required.", 400

    connection = get_db_connection()

    try:
        connection.execute(
            """
            INSERT INTO clients (name, email, phone, company)
            VALUES (?, ?, ?, ?)
            """,
            (name, email, phone, company)
        )

        connection.commit()

    finally:
        connection.close()

    return redirect(url_for("clients_page"))


# --------------------------------------------------
# EDIT CLIENT
# --------------------------------------------------

@app.route(
    "/clients/edit/<int:client_id>",
    methods=["GET", "POST"]
)
def edit_client(client_id):
    connection = get_db_connection()

    try:
        client = connection.execute(
            "SELECT * FROM clients WHERE id = ?",
            (client_id,)
        ).fetchone()

        if client is None:
            return "Client not found.", 404

        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            phone = request.form.get("phone", "").strip()
            company = request.form.get("company", "").strip()

            if not name:
                return "Client name is required.", 400

            connection.execute(
                """
                UPDATE clients
                SET name = ?,
                    email = ?,
                    phone = ?,
                    company = ?
                WHERE id = ?
                """,
                (name, email, phone, company, client_id)
            )

            connection.commit()
            return redirect(url_for("clients_page"))

        return render_template(
            "edit_client.html",
            client=client
        )

    finally:
        connection.close()


# --------------------------------------------------
# DELETE CLIENT
# --------------------------------------------------

@app.route(
    "/clients/delete/<int:client_id>",
    methods=["POST"]
)
def delete_client(client_id):
    connection = get_db_connection()

    try:
        client = connection.execute(
            "SELECT id FROM clients WHERE id = ?",
            (client_id,)
        ).fetchone()

        if client is None:
            return "Client not found.", 404

        project = connection.execute(
            """
            SELECT id
            FROM projects
            WHERE client_id = ?
            LIMIT 1
            """,
            (client_id,)
        ).fetchone()

        if project:
            return (
                "This client has projects linked to them. "
                "You cannot delete this client yet.",
                400
            )

        connection.execute(
            "DELETE FROM clients WHERE id = ?",
            (client_id,)
        )

        connection.commit()

    finally:
        connection.close()

    return redirect(url_for("clients_page"))


# --------------------------------------------------
# PROJECTS PAGE
# --------------------------------------------------

@app.route("/projects")
def projects_page():
    connection = get_db_connection()

    try:
        projects = connection.execute(
            """
            SELECT
                projects.*,
                clients.name AS client_name
            FROM projects
            LEFT JOIN clients
                ON projects.client_id = clients.id
            ORDER BY projects.id DESC
            """
        ).fetchall()

        clients = connection.execute(
            """
            SELECT id, name
            FROM clients
            ORDER BY name
            """
        ).fetchall()

        return render_template(
            "projects.html",
            projects=projects,
            clients=clients
        )

    finally:
        connection.close()


# --------------------------------------------------
# ADD PROJECT
# --------------------------------------------------

@app.route("/projects/add", methods=["POST"])
def add_project():
    project_name = request.form.get(
        "project_name", ""
    ).strip()

    client_id = request.form.get("client_id", type=int)
    budget_text = request.form.get("budget", "0").strip()
    status = request.form.get("status", "Active").strip()
    deadline = request.form.get("deadline", "").strip()

    if not project_name:
        return "Project name is required.", 400

    if not client_id:
        return "Please select a client.", 400

    try:
        budget = float(budget_text)

        if budget < 0:
            return "Budget cannot be negative.", 400

    except ValueError:
        return "Please enter a valid budget.", 400

    if status not in ["Active", "Completed", "On Hold"]:
        return "Invalid project status.", 400

    connection = get_db_connection()

    try:
        client = connection.execute(
            "SELECT id FROM clients WHERE id = ?",
            (client_id,)
        ).fetchone()

        if client is None:
            return "Selected client was not found.", 400

        connection.execute(
            """
            INSERT INTO projects
                (project_name, client_id, budget, status, deadline)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                project_name,
                client_id,
                budget,
                status,
                deadline or None
            )
        )

        connection.commit()

    finally:
        connection.close()

    return redirect(url_for("projects_page"))


# --------------------------------------------------
# EDIT PROJECT
# --------------------------------------------------

@app.route(
    "/projects/edit/<int:project_id>",
    methods=["GET", "POST"]
)
def edit_project(project_id):
    connection = get_db_connection()

    try:
        project = connection.execute(
            "SELECT * FROM projects WHERE id = ?",
            (project_id,)
        ).fetchone()

        if project is None:
            return "Project not found.", 404

        clients = connection.execute(
            "SELECT id, name FROM clients ORDER BY name"
        ).fetchall()

        if request.method == "POST":
            project_name = request.form.get(
                "project_name", ""
            ).strip()

            client_id = request.form.get("client_id", type=int)
            budget_text = request.form.get("budget", "0").strip()
            status = request.form.get("status", "").strip()
            deadline = request.form.get("deadline", "").strip()

            if not project_name:
                return "Project name is required.", 400

            if not client_id:
                return "Please select a client.", 400

            if status not in ["Active", "Completed", "On Hold"]:
                return "Invalid project status.", 400

            try:
                budget = float(budget_text)

                if budget < 0:
                    return "Budget cannot be negative.", 400

            except ValueError:
                return "Please enter a valid budget.", 400

            client = connection.execute(
                "SELECT id FROM clients WHERE id = ?",
                (client_id,)
            ).fetchone()

            if client is None:
                return "Selected client was not found.", 400

            connection.execute(
                """
                UPDATE projects
                SET project_name = ?,
                    client_id = ?,
                    budget = ?,
                    status = ?,
                    deadline = ?
                WHERE id = ?
                """,
                (
                    project_name,
                    client_id,
                    budget,
                    status,
                    deadline or None,
                    project_id
                )
            )

            connection.commit()
            return redirect(url_for("projects_page"))

        return render_template(
            "edit_project.html",
            project=project,
            clients=clients
        )

    finally:
        connection.close()


# --------------------------------------------------
# DELETE PROJECT
# --------------------------------------------------

@app.route(
    "/projects/delete/<int:project_id>",
    methods=["POST"]
)
def delete_project(project_id):
    connection = get_db_connection()

    try:
        project = connection.execute(
            "SELECT id FROM projects WHERE id = ?",
            (project_id,)
        ).fetchone()

        if project is None:
            return "Project not found.", 404

        connection.execute(
            "DELETE FROM projects WHERE id = ?",
            (project_id,)
        )

        connection.commit()

    finally:
        connection.close()

    return redirect(url_for("projects_page"))


# --------------------------------------------------
# DASHBOARD DATA API
# --------------------------------------------------

@app.route("/api/dashboard")
def dashboard_api():
    connection = get_db_connection()

    try:
        total_clients = connection.execute(
            "SELECT COUNT(*) FROM clients"
        ).fetchone()[0]

        total_projects = connection.execute(
            "SELECT COUNT(*) FROM projects"
        ).fetchone()[0]

        active_projects = connection.execute(
            """
            SELECT COUNT(*)
            FROM projects
            WHERE LOWER(status) = 'active'
            """
        ).fetchone()[0]

        completed_projects = connection.execute(
            """
            SELECT COUNT(*)
            FROM projects
            WHERE LOWER(status) = 'completed'
            """
        ).fetchone()[0]

        total_budget = connection.execute(
            """
            SELECT COALESCE(SUM(budget), 0)
            FROM projects
            """
        ).fetchone()[0]

        recent_projects = connection.execute(
            """
            SELECT
                projects.*,
                clients.name AS client_name
            FROM projects
            LEFT JOIN clients
                ON projects.client_id = clients.id
            ORDER BY projects.id DESC
            LIMIT 5
            """
        ).fetchall()

        return jsonify({
            "total_clients": total_clients,
            "total_projects": total_projects,
            "active_projects": active_projects,
            "completed_projects": completed_projects,
            "total_budget": total_budget,
            "recent_projects": [
                dict(row) for row in recent_projects
            ]
        })

    except Exception:
        app.logger.exception("Dashboard database error")

        return jsonify({
            "error": "Dashboard data could not be loaded."
        }), 500

    finally:
        connection.close()


# --------------------------------------------------
# START APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)

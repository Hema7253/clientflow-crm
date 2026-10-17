
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "database.db")


def get_db_connection():
    """Connect to the SQLite database."""
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_database():
    """Create the clients and projects tables if they do not exist."""
    connection = get_db_connection()

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                company TEXT
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                client_id INTEGER NOT NULL,
                budget REAL DEFAULT 0,
                status TEXT DEFAULT 'Active',
                deadline TEXT,
                FOREIGN KEY (client_id)
                    REFERENCES clients(id)
                    ON DELETE RESTRICT
            )
        """)

        connection.commit()
        print("Database and tables are ready!")

    finally:
        connection.close()


def add_sample_data():
    """
    Add demo data only when both tables are empty.
    Existing client and project records are preserved.
    """
    connection = get_db_connection()

    try:
        client_count = connection.execute(
            "SELECT COUNT(*) FROM clients"
        ).fetchone()[0]

        project_count = connection.execute(
            "SELECT COUNT(*) FROM projects"
        ).fetchone()[0]

        # Avoid adding duplicate demo data
        if client_count > 0 or project_count > 0:
            print("Existing data found. Sample data not added.")
            return

        cursor = connection.execute("""
            INSERT INTO clients (name, email, phone, company)
            VALUES (?, ?, ?, ?)
        """, (
            "Ananya Sharma",
            "ananya@example.com",
            "9876543210",
            "Bright Solutions"
        ))

        client_id = cursor.lastrowid

        connection.executemany("""
            INSERT INTO projects
                (project_name, client_id, budget, status, deadline)
            VALUES (?, ?, ?, ?, ?)
        """, [
            (
                "Business Website",
                client_id,
                25000,
                "Active",
                "2026-11-30"
            ),
            (
                "CRM Dashboard",
                client_id,
                15000,
                "Completed",
                "2026-10-30"
            )
        ])

        connection.commit()
        print("Demo client and projects added successfully!")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    create_database()
    add_sample_data()

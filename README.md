
# ClientFlow CRM

A simple Client Relationship Management (CRM) and Project Management web application built using Python, Flask, SQLite, HTML, CSS, and JavaScript.

## Features

### Dashboard
- Total client count
- Total project count
- Active and completed project statistics
- Total project budget
- Recent projects overview

### Client Management
- Add new clients
- View client details
- Edit client information
- Delete clients without linked projects

### Project Management
- Add projects and assign clients
- View project details
- Edit project information
- Delete projects with confirmation
- Manage project budgets, deadlines, and statuses

### Search and Filters
- Search by project name or client name
- Filter projects by client
- Filter by Active, Completed, or On Hold status

## Technologies Used

- Python
- Flask
- SQLite
- HTML5
- CSS3
- JavaScript
- Jinja2 Templates

## Project Structure

```text
CLIENTFLOW CRM/
├── app.py
├── database.py
├── requirements.txt
├── .gitignore
├── templates/
│   ├── dashboard.html
│   ├── clients.html
│   ├── edit_client.html
│   ├── projects.html
│   └── edit_project.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── script.js
```

The SQLite database is created locally when the application initializes. The database file is excluded from Git tracking.

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd "CLIENTFLOW CRM"
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your actual repository URL.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the application

```bash
python app.py
```

### 6. Open in your browser

```text
http://127.0.0.1:5000
```

## Database

This application uses SQLite for local data storage. Demo records are created only when the database is empty.

## Future Improvements

- User authentication
- Improved form validation and error messages
- Production deployment
- Persistent database storage for the deployed application

## Author

ClientFlow CRM — Portfolio Project

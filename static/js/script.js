
const money = (amount) =>
    new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 2
    }).format(Number(amount) || 0);

function showMessage(message, error = false) {
    const element = document.getElementById("message");
    element.textContent = message;
    element.className = error ? "message error" : "message";
}

function getField(row, names) {
    const key = Object.keys(row).find(
        name => names.includes(name.toLowerCase())
    );
    return key ? row[key] : "—";
}

async function loadDashboard() {
    const button = document.getElementById("refreshBtn");
    button.disabled = true;
    showMessage("Loading dashboard data...");

    try {
        const response = await fetch("/api/dashboard");
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Unable to load dashboard");
        }

        document.getElementById("totalClients").textContent =
            data.total_clients;

        document.getElementById("totalProjects").textContent =
            data.total_projects;

        document.getElementById("activeProjects").textContent =
            data.active_projects;

        document.getElementById("completedProjects").textContent =
            data.completed_projects;

        document.getElementById("totalBudget").textContent =
            money(data.total_budget);

        const table = document.getElementById("projectsTable");
        table.replaceChildren();

        if (!data.recent_projects || data.recent_projects.length === 0) {
            const row = document.createElement("tr");
            const cell = document.createElement("td");

            cell.colSpan = 4;
            cell.className = "empty";
            cell.textContent = "No projects found in your database yet.";

            row.appendChild(cell);
            table.appendChild(row);
        } else {
            data.recent_projects.forEach(project => {
                const row = document.createElement("tr");

                const values = [
                    getField(project, ["project_name", "name", "title"]),
                    project.client_name || "Unknown Client",
                    getField(project, ["status"]),
                    getField(project, ["budget", "amount", "project_budget"])
                ];

                values.forEach((value, index) => {
                    const cell = document.createElement("td");

                    if (index === 2) {
                        const badge = document.createElement("span");
                        badge.className =
                            "status " +
                            String(value).toLowerCase().replace(/\s+/g, "-");
                        badge.textContent = value;
                        cell.appendChild(badge);
                    } else {
                        cell.textContent =
                            index === 3 && value !== "—"
                                ? money(value)
                                : value;
                    }

                    row.appendChild(cell);
                });

                table.appendChild(row);
            });
        }

        showMessage("Dashboard updated successfully.");
    } catch (error) {
        console.error("Dashboard error:", error);
        showMessage("Dashboard error: " + error.message, true);
    } finally {
        button.disabled = false;
    }
}

document.getElementById("refreshBtn").addEventListener(
    "click",
    loadDashboard
);

loadDashboard();

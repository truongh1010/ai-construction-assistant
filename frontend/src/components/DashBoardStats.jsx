function DashboardStats({ issues }) {
    const total = issues.length;

    const open = issues.filter((issue) => issue.status === "Open").length;

    const inProgress = issues.filter(
        (issue) => issue.status === "In progress"
    ).length;

    const resolved = issues.filter((issue) => issue.status === "Resolved").length;

    const highUrgency = issues.filter((issue) => {
        const urgency = issue.analysis.urgency.toLowerCase();
        return urgency === "high" || urgency === "critical";
    }).length;

    return (
        <div className="stats-grid">
            <div className="stat-card">
                <p>Total Issues</p>
                <h3>{total}</h3>
            </div>

            <div className="stat-card">
                <p>Open</p>
                <h3>{open}</h3>
            </div>

            <div className="stat-card">
                <p>In Progress</p>
                <h3>{inProgress}</h3>
            </div>

            <div className="stat-card">
                <p>Resolved</p>
                <h3>{resolved}</h3>
            </div>

            <div className="stat-card">
                <p>High/Critical</p>
                <h3>{highUrgency}</h3>
            </div>
        </div>
    );
}

export default DashboardStats;

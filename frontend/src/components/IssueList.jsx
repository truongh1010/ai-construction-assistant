import { useState } from "react";
import { deleteIssue, updateIssueStatus, reanalyzeIssue, updateIssue } from "../api/issues";

function IssueList({ issues, onIssueDeleted }) {
    const [error, setError] = useState("");
    const [statusFilter, setStatusFilter] = useState("All")
    const [searchTerm, setSearchTerm] = useState("")
    const [sortBy, setSortBy] = useState("Newest")
    const [reanalyzingId, setReanalyzingId] = useState(null)
    const [editingId, setEditingId] = useState(null);
    const [editForm, setEditForm] = useState({
        title: "",
        description: "",
        project_name: "",
        location: "",
    });

    const filteredIssues = issues.filter((issue) => {
        const matchesStatus =
            statusFilter === "All" || issue.status === statusFilter;

        const searchText = `
            ${issue.title}
            ${issue.description}
            ${issue.project_name || ""}
            ${issue.location || ""}
            ${issue.status}
            ${issue.analysis.category}
            ${issue.analysis.urgency}
            ${issue.analysis.trade}
            ${issue.analysis.summary}
        `.toLowerCase();

        const matchesSearch = searchText.includes(searchTerm.toLowerCase());

        return matchesStatus && matchesSearch;
    });

    const urgencyRank = {
        Critical: 4,
        High: 3,
        Medium: 2,
        Low: 1,
    };

    const statusRank = {
        Open: 3,
        "In Progress": 2,
        Resolved: 1,
    };

    const sortedIssues = [...filteredIssues].sort((a, b) => {
        if (sortBy === "Newest") {
            return b.id - a.id;
        }

        if (sortBy === "Oldest") {
            return a.id - b.id;
        }

        if (sortBy === "Urgency") {
            return (
                (urgencyRank[b.analysis.urgency] || 0) -
                (urgencyRank[a.analysis.urgency] || 0)
            );
        }

        if (sortBy === "Status") {
            return (statusRank[b.status] || 0) - (statusRank[a.status] || 0);
        }

        return 0;
    });

    async function handleReanalyze(issueId) {
        try {
            setReanalyzingId(issueId)
            await reanalyzeIssue(issueId)
            onIssueDeleted()
        } catch (err) {
            console.error(err)
            setError("Failed to reanalyze issue.")
        } finally {
            setReanalyzingId(null)
        }
    }

    async function handleDelete(issueId) {
        try {
            await deleteIssue(issueId);
            onIssueDeleted();
        } catch (err) {
            console.error(err);
            setError("Failed to delete issue.");
        }
    }

    async function handleStatusChange(issueId, newStatus) {
        try {
            await updateIssueStatus(issueId, newStatus)
            onIssueDeleted()
        } catch (err) {
            console.error(err)
            setError("Failed to update issue status")
        }
    }

    function startEditing(issue) {
        setEditingId(issue.id);
        setEditForm({
            title: issue.title,
            description: issue.description,
            project_name: issue.project_name || "",
            location: issue.location || "",
        });
    }

    function cancelEditing() {
        setEditingId(null);
        setEditForm({
            title: "",
            description: "",
            project_name: "",
            location: "",
        });
    }

    function handleEditChange(event) {
        const { name, value } = event.target;

        setEditForm((prev) => ({
            ...prev,
            [name]: value,
        }));
    }

    async function handleSaveEdit(issueId) {
        try {
            await updateIssue(issueId, editForm);
            setEditingId(null);
            onIssueDeleted();
        } catch (err) {
            console.error(err);
            setError("Failed to update issue.");
        }
    }

    return (
        <div>
            <h2>Saved Issues</h2>

            <input
                className="search-input"
                type="text"
                placeholder="Search issues by title, trade, location, status..."
                value={searchTerm}
                onChange={(event) => setSearchTerm(event.target.value)}
            />

            <div className="sort-row">
                <label>Sort by</label>
                <select value={sortBy} onChange={(event) => setSortBy(event.target.value)}>
                    <option value="Newest">Newest</option>
                    <option value="Oldest">Oldest</option>
                    <option value="Urgency">Urgency</option>
                    <option value="Status">Status</option>
                </select>
            </div>

            <div className="filter-row">
                {["All", "Open", "In progress", "Resolved"].map((status) => (
                    <button
                        key={status}
                        className={statusFilter === status ? "filter-button active" : "filter-button"}
                        onClick={() => setStatusFilter(status)}
                    >
                        {status}
                    </button>
                ))}
            </div>

            {error && <p>{error}</p>}

            {sortedIssues.length === 0 ? (
                <p>No saved issues yet.</p>
            ) : (
                sortedIssues.map((issue) => (
                    <div className="issue-card" key={issue.id}>
                        {editingId === issue.id ? (
                            <div className="edit-form">
                                <label>Title</label>
                                <input
                                    type="text"
                                    name="title"
                                    value={editForm.title}
                                    onChange={handleEditChange}
                                />

                                <label>Description</label>
                                <textarea
                                    name="description"
                                    value={editForm.description}
                                    onChange={handleEditChange}
                                />

                                <label>Project Name</label>
                                <input
                                    type="text"
                                    name="project_name"
                                    value={editForm.project_name}
                                    onChange={handleEditChange}
                                />

                                <label>Location</label>
                                <input
                                    type="text"
                                    name="location"
                                    value={editForm.location}
                                    onChange={handleEditChange}
                                />

                                <div className="card-actions">
                                    <button onClick={() => handleSaveEdit(issue.id)}>Save Changes</button>

                                    <button className="secondary-button" onClick={cancelEditing}>
                                        Cancel
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <>
                                <h3>{issue.title}</h3>

                                <p className="issue-description">{issue.description}</p>

                                <p>
                                    <strong>Project:</strong> {issue.project_name || "N/A"}
                                </p>

                                <p>
                                    <strong>Location:</strong> {issue.location || "N/A"}
                                </p>
                            </>
                        )}

                        <div className="badges">
                            <span className="badge">{issue.analysis.category}</span>
                            <span className={`badge ${issue.analysis.urgency.toLowerCase()}`}>
                                {issue.analysis.urgency}
                            </span>
                            <span className="badge">{issue.analysis.trade}</span>
                        </div>

                        <div className="status-row">
                            <label>Status</label>
                            <select
                                value={issue.status}
                                onChange={(event) => handleStatusChange(issue.id, event.target.value)}
                            >
                                <option value="Open">Open</option>
                                <option value="In progress">In progress</option>
                                <option value="Resolved">Resolved</option>
                            </select>
                        </div>

                        <p>
                            <strong>Summary:</strong> {issue.analysis.summary}
                        </p>

                        <div className="analysis-section">
                            <h4>Next Steps</h4>
                            <ul>
                                {issue.analysis.next_steps.map((step, index) => (
                                    <li key={index}>{step}</li>
                                ))}
                            </ul>
                        </div>

                        <div className="analysis-section">
                            <h4>Recommended Tasks</h4>

                            {issue.analysis.tasks.map((task, index) => (
                                <div className="task-item" key={index}>
                                    <p>
                                        <strong>{task.title}</strong>
                                    </p>
                                    <p>Assigned to: {task.assigned_to}</p>
                                    <p>Priority: {task.priority}</p>
                                </div>
                            ))}
                        </div>
                        <div className="card-actions">
                            <button
                                className="secondary-button"
                                onClick={() => startEditing(issue)}
                            >
                                Edit
                            </button>
                            <button
                                className="secondary-button"
                                onClick={() => handleReanalyze(issue.id)}
                                disabled={reanalyzingId === issue.id}
                            >
                                {reanalyzingId === issue.id ? "Reanalyzing..." : "Reanalyze"}
                            </button>

                            <button onClick={() => handleDelete(issue.id)}>
                                Delete
                            </button>
                        </div>
                    </div>
                ))
            )}
        </div>
    );
}

export default IssueList;

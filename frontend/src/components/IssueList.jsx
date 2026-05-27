import { useState } from "react";
import { deleteIssue, updateIssueStatus } from "../api/issues";

function IssueList({ issues, onIssueDeleted }) {
    const [error, setError] = useState("");

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

    return (
        <div>
            <h2>Saved Issues</h2>

            {error && <p>{error}</p>}

            {issues.length === 0 ? (
                <p>No saved issues yet.</p>
            ) : (
                issues.map((issue) => (
                    <div className="issue-card" key={issue.id}>
                        <h3>{issue.title}</h3>
                        <p className="issue-description">{issue.description}</p>

                        <p>
                            <strong>Project:</strong> {issue.project_name || "N/A"}
                        </p>

                        <p>
                            <strong>Location:</strong> {issue.location || "N/A"}
                        </p>

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

                        <button onClick={() => handleDelete(issue.id)}>
                            Delete
                        </button>
                    </div>
                ))
            )}
        </div>
    );
}

export default IssueList;

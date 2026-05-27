import { useEffect, useState } from "react";
import { getIssues, deleteIssue } from "../api/issues";

function IssueList() {
  const [issues, setIssues] = useState([]);
  const [error, setError] = useState("");

  async function loadIssues() {
    try {
      const data = await getIssues();
      setIssues(data);
    } catch (err) {
      console.error(err);
      setError("Failed to load issues.");
    }
  }

  async function handleDelete(issueId) {
    try {
      await deleteIssue(issueId);
      loadIssues();
    } catch (err) {
      console.error(err);
      setError("Failed to delete issue.");
    }
  }

  useEffect(() => {
    loadIssues();
  }, []);

  return (
    <div>
      <h2>Saved Issues</h2>

      {error && <p>{error}</p>}

      {issues.length === 0 ? (
        <p>No saved issues yet.</p>
      ) : (
        issues.map((issue) => (
          <div key={issue.id}>
            <h3>{issue.title}</h3>
            <p>{issue.description}</p>

            <p>
              <strong>Project:</strong> {issue.project_name || "N/A"}
            </p>

            <p>
              <strong>Location:</strong> {issue.location || "N/A"}
            </p>

            <p>
              <strong>Category:</strong> {issue.analysis.category}
            </p>

            <p>
              <strong>Urgency:</strong> {issue.analysis.urgency}
            </p>

            <p>
              <strong>Trade:</strong> {issue.analysis.trade}
            </p>

            <button onClick={() => handleDelete(issue.id)}>
              Delete
            </button>

            <hr />
          </div>
        ))
      )}
    </div>
  );
}

export default IssueList;
import { useEffect, useState } from "react";
import IssueForm from "./components/IssueForm";
import IssueList from "./components/IssueList";
import { getIssues } from "./api/issues";

function App() {
  const [issues, setIssues] = useState([]);

  async function loadIssues() {
    try {
      const data = await getIssues();
      setIssues(data);
    } catch (err) {
      console.error("Failed to load issues:", err);
    }
  }

  useEffect(() => {
    loadIssues();
  }, []);

  return (
    <div>
      <h1>AI Construction Assistant</h1>

      <IssueForm onIssueCreated={loadIssues} />

      <IssueList issues={issues} onIssueDeleted={loadIssues} />
    </div>
  );
}

export default App;
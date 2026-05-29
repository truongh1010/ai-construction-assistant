import { useEffect, useState } from "react";
import IssueForm from "./components/IssueForm";
import IssueList from "./components/IssueList";
import { getIssues } from "./api/issues";
import DashboardStats from "./components/DashBoardStats";
import "./App.css";

function App() {
    const [issues, setIssues] = useState([]);
    const [statusFilter, setStatusFilter] = useState("All");
    const [searchTerm, setSearchTerm] = useState("");

    async function loadIssues() {
        try {
            const data = await getIssues({
                status: statusFilter,
                search: searchTerm,
            });
            
            setIssues(data);
        } catch (err) {
            console.error("Failed to load issues:", err);
        }
    }

    useEffect(() => {
        loadIssues();
    }, [statusFilter, searchTerm]);

    return (
        <div className="app">
            <header className="app-header">
                <div>
                    <p className="eyebrow">AI Construction Assistant</p>
                    <h1>Construction Issue Dashboard</h1>
                    <p className="subtitle">
                        Submit project issues, classify them, generate next steps, and track saved records.
                    </p>
                </div>
            </header>

            <DashboardStats issues={issues}/>

            <main className="dashboard">
                <section className="panel">
                    <IssueForm onIssueCreated={loadIssues}/>
                </section>

                <section className="panel">
                <IssueList
                    issues={issues}
                    onIssueDeleted={loadIssues}
                    statusFilter={statusFilter}
                    setStatusFilter={setStatusFilter}
                    searchTerm={searchTerm}
                    setSearchTerm={setSearchTerm}
                />
                </section>
            </main>
        </div>
    );
}

export default App;

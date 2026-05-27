import { useState } from "react";
import { createIssue } from "../api/issues";

function IssueForm({ onIssueCreated }) {
    const [formData, setFormData] = useState({
        title: "",
        description: "",
        project_name: "",
        location: "",
    });

    const [result, setResult] = useState(null);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    function handleChange(event) {
        const { name, value } = event.target;

        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }));
    }

    async function handleSubmit(event) {
        event.preventDefault();

        setLoading(true);
        setError("");
        setResult(null);

        try {
            const savedIssue = await createIssue(formData);
            setResult(savedIssue);

            onIssueCreated();

            setFormData({
                title: "",
                description: "",
                project_name: "",
                location: "",
            });
        } catch (err) {
            console.error(err);
            setError("Something went wrong while submitting the issue.");
        } finally {
            setLoading(false);
        }
    }

    return (
        <div>
            <h2>Submit Construction Issue</h2>

            <form onSubmit={handleSubmit}>
                <div>
                    <label>Issue Title</label>
                    <input
                        type="text"
                        name="title"
                        value={formData.title}
                        onChange={handleChange}
                        placeholder="Water leaking in bathroom"
                        required
                    />
                </div>

                <div>
                    <label>Description</label>
                    <textarea
                        name="description"
                        value={formData.description}
                        onChange={handleChange}
                        placeholder="Describe the issue..."
                        required
                    />
                </div>

                <div>
                    <label>Project Name</label>
                    <input
                        type="text"
                        name="project_name"
                        value={formData.project_name}
                        onChange={handleChange}
                        placeholder="Apartment Renovation"
                    />
                </div>

                <div>
                    <label>Location</label>
                    <input
                        type="text"
                        name="location"
                        value={formData.location}
                        onChange={handleChange}
                        placeholder="Second floor bathroom"
                    />
                </div>

                <button type="submit" disabled={loading}>
                    {loading ? "Analyzing..." : "Submit Issue"}
                </button>
            </form>

            {error && <p>{error}</p>}

            {result && (
                <div className="result-box">
                    <h3>AI Analysis Result</h3>

                    <p>
                        <strong>Category:</strong> {result.analysis.category}
                    </p>

                    <p>
                        <strong>Urgency:</strong> {result.analysis.urgency}
                    </p>

                    <p>
                        <strong>Trade:</strong> {result.analysis.trade}
                    </p>

                    <p>
                        <strong>Summary:</strong> {result.analysis.summary}
                    </p>

                    <h4>Next Steps</h4>
                    <ul>
                        {result.analysis.next_steps.map((step, index) => (
                            <li key={index}>{step}</li>
                        ))}
                    </ul>

                    <h4>Recommended Tasks</h4>
                    <ul>
                        {result.analysis.tasks.map((task, index) => (
                            <li key={index}>
                                {task.title} — {task.assigned_to} — {task.priority}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

export default IssueForm;

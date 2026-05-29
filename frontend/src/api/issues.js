import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000";

export async function createIssue(issueData) {
    const response = await axios.post(`${API_BASE_URL}/issues`, issueData);
    return response.data;
}

export async function getIssues(filters = {}) {
    const params = {};
  
    if (filters.status && filters.status !== "All") {
        params.status = filters.status;
    }
  
    if (filters.search && filters.search.trim() !== "") {
        params.search = filters.search;
    }
  
    const response = await axios.get(`${API_BASE_URL}/issues`, { params });
    return response.data;
}

export async function getIssueById(issueId) {
    const response = await axios.get(`${API_BASE_URL}/issues/${issueId}`);
    return response.data;
}

export async function deleteIssue(issueId) {
    const response = await axios.delete(`${API_BASE_URL}/issues/${issueId}`);
    return response.data;
}

export async function updateIssueStatus(issueId, status) {
    const response = await axios.patch(`${API_BASE_URL}/issues/${issueId}/status`, {
        status
    })

    return response.data
}

export async function reanalyzeIssue(issueId) {
    const response = await axios.post(`${API_BASE_URL}/issues/${issueId}/reanalyze`);
    return response.data;
  }

export async function updateIssue(issueId, issueData) {
    const response = await axios.put(`${API_BASE_URL}/issues/${issueId}`, issueData);
    return response.data;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function handleResponse(response) {
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    const message = payload.message || `Request failed with status ${response.status}`;
    throw new Error(message);
  }
  return response.json();
}

export async function fetchPortfolio() {
  const response = await fetch(`${API_BASE}/portfolio`);
  return handleResponse(response);
}

export async function importTransactionsCsv(file) {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`${API_BASE}/imports/transactions`, {
    method: "POST",
    body: formData
  });
  return handleResponse(response);
}

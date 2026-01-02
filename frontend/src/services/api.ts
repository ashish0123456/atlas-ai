const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function queryAI(question: string) {
    const response = await fetch(`${API_BASE}/query`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
    });

    if(!response.ok){
        throw new Error("Failed to fetch response");
    }

    return response.json();
}
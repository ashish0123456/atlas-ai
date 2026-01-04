const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export interface ApiError {
    detail: string;
    trace_id?: string;
}

class ApiClient {
    private apiKey: string | null = null;

    setApiKey(key: string | null) {
        this.apiKey = key;
        if (key) {
            localStorage.setItem("api_key", key);
        } else {
            localStorage.removeItem("api_key");
        }
    }

    getApiKey(): string | null {
        if (!this.apiKey) {
            this.apiKey = localStorage.getItem("api_key");
        }
        return this.apiKey;
    }

    private getHeaders(): HeadersInit {
        const headers: HeadersInit = {
            "Content-Type": "application/json",
        };
        
        const apiKey = this.getApiKey();
        if (apiKey) {
            headers["X-API-Key"] = apiKey;
        }
        
        return headers;
    }

    private async handleResponse<T>(response: Response): Promise<T> {
        if (!response.ok) {
            let error: ApiError;
            try {
                const errorData = await response.json();
                error = {
                    detail: errorData.detail || errorData.error || `HTTP ${response.status}: ${response.statusText}`,
                    trace_id: errorData.trace_id
                };
            } catch {
                // If response is not JSON, try to get text
                try {
                    const text = await response.text();
                    error = {
                        detail: text || `HTTP ${response.status}: ${response.statusText}`,
                    };
                } catch {
                    error = {
                        detail: `HTTP ${response.status}: ${response.statusText}`,
                    };
                }
            }
            throw error;
        }
        return response.json();
    }

    async queryAI(question: string): Promise<{ answer: string; contexts?: any[] }> {
        const response = await fetch(`${API_BASE}/api/v1/query`, {
            method: "POST",
            headers: this.getHeaders(),
            body: JSON.stringify({ question }),
        });

        return this.handleResponse(response);
    }

    queryAIStream(
        question: string,
        onProgress: (stage: string, message: string, data?: any) => void,
        onComplete: (result: any) => void,
        onError: (error: string) => void
    ): () => void {
        const headers = this.getHeaders();
        const headers_all = {...headers, "Accept" : "text/event-stream" };
        
        // Create EventSource for SSE
        const url = `${API_BASE}/api/v1/query/stream`;
        // const eventSource = new EventSource(url, {
        //     withCredentials: false
        // });

        // Send question via POST (EventSource only supports GET, so we use a workaround)
        // For proper SSE with POST, we need to use fetch with ReadableStream
        const abortController = new AbortController();
        
        fetch(url, {
            method: "POST",
            headers: headers_all,
            body: JSON.stringify({ question }),
            signal: abortController.signal
        }).then(async (response) => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const reader = response.body?.getReader();
            const decoder = new TextDecoder();

            if (!reader) {
                throw new Error("Response body is not readable");
            }

            let buffer = "";

            while (true) {
                const { done, value } = await reader.read();
                
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split("\n\n");
                buffer = lines.pop() || "";

                for (const line of lines) {
                    if (line.startsWith("data: ")) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            
                            if (data.type === "progress") {
                                onProgress(data.stage, data.message, data);
                            } else if (data.type === "complete") {
                                onComplete(data.result);
                                return;
                            } else if (data.type === "error") {
                                onError(data.message);
                                return;
                            }
                        } catch (e) {
                            console.error("Failed to parse SSE data:", e);
                        }
                    }
                }
            }
        }).catch((error) => {
            if (error.name !== "AbortError") {
                onError(error.message);
            }
        });

        // Return cleanup function
        return () => {
            abortController.abort();
        };
    }

    async uploadDocument(file: File): Promise<{ document_id: string; title: string; status: string }> {
        const formData = new FormData();
        formData.append("file", file);

        const headers: HeadersInit = {};
        const apiKey = this.getApiKey();
        if (apiKey) {
            headers["X-API-Key"] = apiKey;
        }
        // Don't set Content-Type header - let browser set it with boundary for FormData

        try {
            const response = await fetch(`${API_BASE}/api/v1/documents/upload`, {
                method: "POST",
                headers,
                body: formData,
            });

            // Log response for debugging
            if (!response.ok) {
                console.error("Upload failed:", response.status, response.statusText);
            }

            return this.handleResponse(response);
        } catch (error) {
            console.error("Upload error details:", error);
            // Network error (CORS, connection refused, etc.)
            if (error instanceof TypeError && error.message.includes("fetch")) {
                throw {
                    detail: `Failed to connect to server. Please check if the backend is running at ${API_BASE}. Error: ${error.message}`
                } as ApiError;
            }
            throw error;
        }
    }

    async healthCheck(): Promise<{ status: string; service: string }> {
        const response = await fetch(`${API_BASE}/api/v1/health`, {
            method: "GET",
        });

        return this.handleResponse(response);
    }
}

export const apiClient = new ApiClient();

// Legacy exports for backward compatibility
export async function queryAI(question: string) {
    return apiClient.queryAI(question);
}

export interface QueryRequest {
    question: string;
    metadata?: Record<string, any>;
}

export interface QueryResponse {
    answer: string;
    confidence?: number;
    contexts?: ContextItem[];
}

export interface ContextItem {
    content: string;
    document_id?: string;
    chunk_index?: number;
    file_path?: string;
    metadata?: Record<string, any>;
}

export interface DocumentResponse {
    document_id: string;
    title: string;
    status: string;
}

export interface HealthResponse {
    status: string;
    service: string;
    version?: string;
    vector_store?: string;
    document_storage?: string;
}

export interface ApiError {
    detail: string;
    trace_id?: string;
}

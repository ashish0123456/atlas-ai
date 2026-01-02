export interface QueryRequest {
    question: string
}

export interface QueryResponse {
    answer: string;
    contexts?: {
         content: string;
         metadata?: Record<string, any>;
    }[];
}
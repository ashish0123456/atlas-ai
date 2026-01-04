import { useState, useEffect } from "react";
import { apiClient } from "../services/api";
import type { ApiError } from "../services/api";

interface Document {
    document_id: string;
    title: string;
    status: string;
}

interface ProgressStage {
    stage: string;
    message: string;
    timestamp: number;
}

export default function Home() {
    const [question, setQuestion] = useState("");
    const [answer, setAnswer] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [apiKey, setApiKey] = useState<string>("");
    const [showApiKeyInput, setShowApiKeyInput] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [uploadError, setUploadError] = useState<string | null>(null);
    const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
    const [documents, setDocuments] = useState<Document[]>([]);
    const [progress, setProgress] = useState<ProgressStage[]>([]);
    const [currentStage, setCurrentStage] = useState<string | null>(null);

    useEffect(() => {
        // Load API key from localStorage
        const savedKey = apiClient.getApiKey();
        if (savedKey) {
            setApiKey(savedKey);
        }
    }, []);

    const handleApiKeySubmit = () => {
        if (apiKey.trim()) {
            apiClient.setApiKey(apiKey.trim());
            setShowApiKeyInput(false);
            setError(null);
        }
    };

    const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        setUploading(true);
        setUploadError(null);
        setUploadSuccess(null);

        try {
            // Validate file type
            const fileExt = file.name.toLowerCase().split('.').pop();
            if (!['pdf', 'txt', 'md'].includes(fileExt || '')) {
                setUploadError(`Invalid file type. Please upload a PDF, TXT, or MD file.`);
                return;
            }

            // Validate file size (10MB)
            if (file.size > 10 * 1024 * 1024) {
                setUploadError(`File too large. Maximum size is 10MB. Your file is ${(file.size / 1024 / 1024).toFixed(2)}MB.`);
                return;
            }

            const result = await apiClient.uploadDocument(file);
            setUploadSuccess(`Document "${result.title}" uploaded successfully!`);
            setDocuments((prev) => [result, ...prev]);
            
            // Clear success message after 5 seconds
            setTimeout(() => setUploadSuccess(null), 5000);
        } catch (err) {
            console.error("Upload error:", err);
            const apiError = err as ApiError;
            let errorMessage = "Failed to upload document";
            
            if (apiError.detail) {
                errorMessage = apiError.detail;
            } else if (err instanceof TypeError && err.message.includes("fetch")) {
                errorMessage = `Cannot connect to server. Please check if the backend is running at ${import.meta.env.VITE_API_BASE || "http://localhost:8000"}`;
            } else if (err instanceof Error) {
                errorMessage = err.message;
            }
            
            setUploadError(errorMessage);
        } finally {
            setUploading(false);
            // Reset file input
            event.target.value = "";
        }
    };

    const handleSubmit = async () => {
        if (!question.trim()) {
            setError("Please enter a question");
            return;
        }

        setLoading(true);
        setAnswer(null);
        setError(null);
        setProgress([]);
        setCurrentStage(null);

        // Use streaming API for real-time progress
        const cleanup = apiClient.queryAIStream(
            question.trim(),
            (stage, message, data) => {
                setCurrentStage(stage);
                setProgress((prev) => [
                    ...prev,
                    { stage, message, timestamp: Date.now() }
                ]);
            },
            (result) => {
                setAnswer(result.answer);
                setCurrentStage("complete");
                setLoading(false);
            },
            (errorMsg) => {
                setError(errorMsg);
                setCurrentStage("error");
                setLoading(false);
            }
        );

        // Store cleanup function (could be used to cancel if needed)
        // For now, it will be called automatically when stream completes
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
            handleSubmit();
        }
    };

    const getStageLabel = (stage: string): string => {
        const labels: Record<string, string> = {
            starting: "Starting...",
            planning: "Planning",
            retrieving: "Retrieving Context",
            verifying: "Verifying",
            evaluating: "Evaluating",
            refining: "Refining",
            complete: "Ready!"
        };
        return labels[stage] || stage;
    };

    return (
        <div className="min-h-screen" style={{ minHeight: '100vh' }}>
            <div className="container mx-auto px-4 py-8 max-w-4xl" style={{ maxWidth: '896px', margin: '0 auto', padding: '2rem 1rem' }}>
                {/* Header */}
                <div className="text-center mb-10">
                    <h1 className="text-5xl font-bold text-white mb-3 drop-shadow-lg">
                        Atlas AI
                    </h1>
                    <p className="text-white/90 text-lg">
                        Upload documents and ask questions powered by RAG
                    </p>
                </div>

                {/* API Key Section */}
                <div className="bg-white/95 backdrop-blur-sm rounded-xl shadow-xl p-6 mb-6 border border-white/20">
                    <div className="flex items-center justify-between">
                        <div>
                            <h2 className="text-lg font-semibold text-gray-800 mb-1">
                                API Key
                            </h2>
                            <p className="text-sm text-gray-600">
                                {apiClient.getApiKey()
                                    ? "API key is configured"
                                    : "Configure your API key to start querying"}
                            </p>
                        </div>
                        <button
                            onClick={() => {
                                if (apiClient.getApiKey()) {
                                    apiClient.setApiKey(null);
                                    setApiKey("");
                                }
                                setShowApiKeyInput(!showApiKeyInput);
                            }}
                            className="px-4 py-2 bg-indigo-100 hover:bg-indigo-200 rounded-lg text-sm font-medium text-indigo-700 transition-colors"
                        >
                            {apiClient.getApiKey() ? "Change" : "Set API Key"}
                        </button>
                    </div>
                    {showApiKeyInput && (
                        <div className="mt-4 flex gap-2">
                            <input
                                type="password"
                                value={apiKey}
                                onChange={(e) => setApiKey(e.target.value)}
                                placeholder="Enter your API key"
                                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                                onKeyPress={(e) => {
                                    if (e.key === "Enter") handleApiKeySubmit();
                                }}
                            />
                            <button
                                onClick={handleApiKeySubmit}
                                className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 transition-all shadow-md hover:shadow-lg"
                            >
                                Save
                            </button>
                        </div>
                    )}
                </div>

                {/* Document Upload Section */}
                <div className="bg-white/95 backdrop-blur-sm rounded-xl shadow-xl p-6 mb-6 border border-white/20">
                    <h2 className="text-lg font-semibold text-gray-800 mb-4">
                        Upload Document
                    </h2>
                    <div className="border-2 border-dashed border-indigo-300 rounded-xl p-8 text-center hover:border-indigo-500 hover:bg-indigo-50/50 transition-all duration-200 bg-indigo-50/30">
                        <input
                            type="file"
                            id="file-upload"
                            accept=".pdf,.txt,.md"
                            onChange={handleFileUpload}
                            disabled={uploading}
                            className="hidden"
                        />
                        <label
                            htmlFor="file-upload"
                            className="cursor-pointer flex flex-col items-center justify-center"
                        >
                            <svg
                                className="w-12 h-12 text-indigo-500 mb-4"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                                style={{ width: '48px', height: '48px', maxWidth: '48px', maxHeight: '48px', flexShrink: 0 }}
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                                />
                            </svg>
                            <span className="text-gray-700 font-medium text-base">
                                {uploading ? "Uploading..." : "Click to upload or drag and drop"}
                            </span>
                            <span className="text-sm text-gray-500 mt-2">
                                PDF, TXT, or MD (max 10MB)
                            </span>
                        </label>
                    </div>
                    {uploadError && (
                        <div className="mt-4 p-3 bg-red-50 border-l-4 border-red-500 rounded-lg text-red-700 text-sm shadow-sm">
                            {uploadError}
                        </div>
                    )}
                    {uploadSuccess && (
                        <div className="mt-4 p-3 bg-emerald-50 border-l-4 border-emerald-500 rounded-lg text-emerald-700 text-sm shadow-sm">
                            {uploadSuccess}
                        </div>
                    )}
                </div>

                {/* Query Section */}
                <div className="bg-white/95 backdrop-blur-sm rounded-xl shadow-xl p-6 mb-6 border border-white/20">
                    <h2 className="text-lg font-semibold text-gray-800 mb-4">
                        Ask a Question
                    </h2>
                    <div className="space-y-4">
                        <textarea
                            className="w-full border border-gray-300 rounded-xl p-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none transition-all"
                            rows={4}
                            placeholder="Ask a question based on your uploaded documents..."
                            value={question}
                            onChange={(e) => setQuestion(e.target.value)}
                            onKeyDown={handleKeyPress}
                            disabled={loading}
                        />
                        <div className="flex items-center justify-between">
                            <p className="text-sm text-gray-500">
                                Press Ctrl+Enter (Cmd+Enter on Mac) to submit
                            </p>
                            <button
                                onClick={handleSubmit}
                                disabled={loading || !question.trim()}
                                className="px-6 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:from-indigo-700 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all font-medium shadow-md hover:shadow-lg disabled:shadow-none"
                            >
                                {loading ? (
                                    <span className="flex items-center gap-2">
                                        <svg
                                            className="animate-spin h-4 w-4"
                                            xmlns="http://www.w3.org/2000/svg"
                                            fill="none"
                                            viewBox="0 0 24 24"
                                        >
                                            <circle
                                                className="opacity-25"
                                                cx="12"
                                                cy="12"
                                                r="10"
                                                stroke="currentColor"
                                                strokeWidth="4"
                                            />
                                            <path
                                                className="opacity-75"
                                                fill="currentColor"
                                                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                            />
                                        </svg>
                                        Processing...
                                    </span>
                                ) : (
                                    "Ask"
                                )}
                            </button>
                        </div>
                    </div>

                    {/* Progress Indicator */}
                    {loading && currentStage && (
                        <div className="mt-4 p-4 bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-xl">
                            <div className="flex items-center gap-2 mb-2">
                                <div className="w-2 h-2 bg-indigo-500 rounded-full animate-pulse"></div>
                                <span className="text-sm font-medium text-indigo-700">
                                    {getStageLabel(currentStage)}
                                </span>
                            </div>
                            <div className="space-y-1">
                                {progress.slice(-3).map((p, idx) => (
                                    <div key={idx} className="text-xs text-indigo-600 flex items-center gap-2">
                                        <span className="w-1 h-1 bg-indigo-400 rounded-full"></span>
                                        {p.message}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {error && (
                        <div className="mt-4 p-4 bg-red-50 border-l-4 border-red-500 rounded-lg text-red-700 shadow-sm">
                            <p className="font-medium">Error</p>
                            <p className="text-sm mt-1">{error}</p>
                        </div>
                    )}

                    {answer && (
                        <div className="mt-6 p-5 bg-gradient-to-br from-indigo-50 to-purple-50 border border-indigo-200 rounded-xl shadow-sm">
                            <h3 className="font-semibold text-indigo-900 mb-2 flex items-center gap-2">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                Answer
                            </h3>
                            <p className="text-gray-800 whitespace-pre-wrap leading-relaxed">
                                {answer}
                            </p>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="text-center text-sm text-white/80 mt-8">
                    Powered by open-source LLMs and RAG architecture
                </div>
            </div>
        </div>
    );
}

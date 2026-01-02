import { useState } from "react";
import { queryAI } from "../services/api";

export default function Home() {
    const [question, setQuestion] = useState("");
    const [answer, setAnswer] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async () => {
        setLoading(true);
        setAnswer(null);
        setError(null);

        try {
            const res = await queryAI(question);
            setAnswer(res.answer);
        } catch (error) {
            setError("Something went wrong");
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="min-h-screen bg-gray-100 flex items-center justify-center">
            <div className="bg-white shadow-lg rounded-xl p-6 w-full max-w-2xl">
                <h1 className="text-2xl font-semibold mb-4">
                    AI Knowledge Assistant
                </h1>

                <textarea
                    className="w-full border rounded-md p-2 mb-4"
                    rows={4}
                    placeholder="Ask a question..."
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                />

                <button
                    onClick={handleSubmit}
                    disabled={loading}
                    className="bg-black text-white px-4 py-2 rounded-md"
                >
                    {loading ? "Thinking..." : "Ask"}
                </button>

                {error && (
                    <p className="text-red-500 mt-4">{error}</p>
                )}

                {answer && (
                    <div>
                        <h2 className="font-medium mb-2">Answer</h2>
                        <p className="whitespace-pre-wrap">{answer}</p>
                    </div>
                )}
            </div>
        </div>
    );
}
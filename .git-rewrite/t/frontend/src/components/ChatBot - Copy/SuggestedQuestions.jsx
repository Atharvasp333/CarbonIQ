export default function SuggestedQuestions({ onQuestionClick }) {
  const questions = [
    "How can I reduce office energy usage?",
    "What increases carbon footprint the most?",
    "How to reduce AC emissions?"
  ];

  return (
    <div className="px-4 py-2 border-t border-gray-200 bg-gray-50">
      <p className="text-xs text-gray-600 mb-2 font-medium">Suggested questions:</p>
      <div className="space-y-1">
        {questions.map((question, idx) => (
          <button
            key={idx}
            onClick={() => onQuestionClick(question)}
            className="w-full text-left text-xs bg-white hover:bg-primary/10 text-gray-700 px-3 py-2 rounded-lg border border-gray-200 hover:border-primary transition-colors"
          >
            💡 {question}
          </button>
        ))}
      </div>
    </div>
  );
}

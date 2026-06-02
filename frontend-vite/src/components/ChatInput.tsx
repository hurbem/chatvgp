import { useState } from "react";

interface ChatInputProps {
  onSend: (pergunta: string) => void;
  isLoading?: boolean;
}

export function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [input, setInput] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      onSend(input);
      setInput("");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Ex: Preciso de um encanador"
        disabled={isLoading}
        className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:border-blue-500"
      />
      <button
        type="submit"
        disabled={isLoading || !input.trim()}
        className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400"
      >
        {isLoading ? "Buscando..." : "Buscar"}
      </button>
    </form>
  );
}

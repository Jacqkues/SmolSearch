"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Message { fromBot: boolean; text: string; }

export function ChatBox() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg: Message = { fromBot: false, text: input };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/research", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: input ,max_iteration:1}),
      });

      if (!res.ok) throw new Error(`Erreur ${res.status}`);

      const data = await res.json();
      console.log(data)
      const botMsg: Message = { fromBot: true, text: data.answer };
      setMessages((m) => [...m, botMsg]);
    } catch (err) {
      console.error(err);
      setMessages((m) => [
        ...m,
        { fromBot: true, text: "❌ Erreur lors de la requête." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-full bg-white shadow-lg rounded-lg overflow-hidden w-full">
      <div className="flex-grow overflow-auto p-4 space-y-2">
      {messages.map((msg, i) => (
          <div
            key={i}
            className={`${msg.fromBot ? "text-left" : "text-right"}`}
          >
            <div
              className={`inline-block px-3 py-2 rounded-lg whitespace-pre-wrap break-words ${
                msg.fromBot ? "bg-gray-200" : "bg-blue-500 text-white"
              }`}
            >
             <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.text}</ReactMarkdown>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <Spinner size={32} />
          </div>
        )}
      </div>

      <div className="p-4 border-t">
        <div className="flex items-center space-x-2">
          <Input
            type="text"
            placeholder="Écrire un message…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKey}
            className="flex-grow"
          />

          <Button onClick={sendMessage} disabled={loading}>
            Search
          </Button>
        </div>
      </div>
    </div>
  );
}
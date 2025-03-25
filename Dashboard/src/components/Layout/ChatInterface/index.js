import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import './ChatInterface.css';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: "user", text: input };
    setMessages([...messages, userMessage]); 

    setInput(""); // Clear input field

    try {
      //AWS-hosted Flask endpoint here
      const response = await fetch("https://wzmyg3e4e5ywcr3jkqbot46a6u0prbsy.lambda-url.us-east-1.on.aws/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: input}),
      });

      const data = await response.json();
      const botMessage = { sender: "assistant", text: data.response };
      setMessages((prevMessages) => [...prevMessages, botMessage]);
    } catch (error) {
      console.error("Error fetching response:", error);
    }
  };

  const handleAddMessage = async () => {
    if (!input.trim()) return;
    
    try {
      // AWS-hosted Flask endpoint here for saving to S3
      const response = await fetch("https://wzmyg3e4e5ywcr3jkqbot46a6u0prbsy.lambda-url.us-east-1.on.aws/save-to-s3", { 
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: input }),
      });
  
      const data = await response.json();
      if (response.ok) {
        alert(`Message saved to S3! File: ${data.file}`);
      } else {
        alert("Error saving message: " + data.error);
      }
    } catch (error) {
      console.error("Error saving message:", error);
      alert("Error saving message.");
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-box">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`}>
           {msg.sender === "assistant" ? (
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.text}</ReactMarkdown>
            ) : (
              <span>{msg.text}</span>
            )}
          </div>
        ))}
      </div>
      <div className="input-area">
        <input
          type="text"
          placeholder="Type your prompt..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
        />
        <button onClick={handleSendMessage}>Send</button>
        <button onClick={handleAddMessage}>Add</button>
      </div>
    </div>
  );
};

export default ChatInterface;

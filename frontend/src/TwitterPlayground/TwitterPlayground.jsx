import React, { useState, useRef, useEffect } from "react";
import { FiImage, FiSmile, FiMapPin, FiBarChart2 } from "react-icons/fi";
import { FaHeart, FaRetweet, FaComment, FaShare } from "react-icons/fa";
import "./TwitterPlayground.css";

const TwitterPlayground = () => {
  const [text, setText] = useState("");
  const [charLimit, setCharLimit] = useState(280);
  const [thread, setThread] = useState([]); // Thread of replies
  const [loadingAction, setLoadingAction] = useState(""); // Track loading state
  const [selectedPersona, setSelectedPersona] = useState(null); // For dropdown
  const textareaRef = useRef(null); // Reference for the textarea

  const personas = [
    "Elon Musk",
    "Steve Jobs",
    "Albert Einstein",
    "Oprah Winfrey",
    "William Shakespeare",
  ];

  // Adjust textarea height dynamically
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto"; // Reset height
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`; // Adjust to content
    }
  }, [text]);

  const handleAction = (action, persona = null) => {
    if (!text.trim()) {
      alert("Please enter some text to perform an action.");
      return;
    }

    setLoadingAction(action); // Set button's loading state
    setTimeout(() => {
      const response = generateSampleResponse(action, persona); // Simulated API response
      setThread((prev) => [
        ...prev,
        {
          action: persona ? `${action} (${persona})` : action,
          response,
          username: "TweetVichar",
          handle: "@tweetvichar",
          timestamp: "Just now",
        },
      ]); // Add response to thread
      setLoadingAction(""); // Reset loading state
    }, 1500);
  };

  const generateSampleResponse = (action, persona) => {
    if (persona) {
      return `In the perspective of ${persona}: "${text} might change the world!"`;
    }

    switch (action) {
      case "Analyze":
        return `This tweet contains ${text.split(" ").length} words and ${
          text.length
        } characters.`;
      case "Meme":
        return "This text could definitely become a trending meme! 😂";
      case "Translate":
        return "Translated: Hola, Mundo! (Spanish)";
      case "Summarize":
        return "Summary: You've made your point clear and concise.";
      default:
        return "Some default response.";
    }
  };

  return (
    <div className="twitter-playground">
      {/* Input Section */}
      <div className="input-section">
        <img
          src="https://abs.twimg.com/sticky/default_profile_images/default_profile_400x400.png"
          alt="Profile"
          className="profile-picture"
        />
        <textarea
          ref={textareaRef}
          placeholder="What's happening?"
          value={text}
          onChange={(e) => setText(e.target.value)}
          maxLength={charLimit}
          className="tweet-input"
        />
      </div>

      {/* Toolbar */}
      <div className="toolbar">
        <FiImage className="toolbar-icon" title="Add Image" />
        <FiSmile className="toolbar-icon" title="Add Emoji" />
        <FiBarChart2 className="toolbar-icon" title="Poll" />
        <FiMapPin className="toolbar-icon" title="Add Location" />
        <span
          className={`char-counter ${
            charLimit - text.length <= 20 ? "warning" : ""
          }`}
        >
          {charLimit - text.length}
        </span>
      </div>

      {/* Divider */}
      <div className="divider" />

      {/* Action Buttons */}
      <div className="action-buttons">
        {/* Dropdown Button */}
        <div className="dropdown">
          <button
            className="action-btn"
            disabled={loadingAction.startsWith("How would")}
          >
            {loadingAction.startsWith("How would")
              ? "Loading..."
              : "How would they react?"}
          </button>
          <div className="dropdown-content">
            {personas.map((persona) => (
              <div
                key={persona}
                className="dropdown-item"
                onClick={() => handleAction("How would they react", persona)}
              >
                {persona}
              </div>
            ))}
          </div>
        </div>
        <button
          className="action-btn"
          onClick={() => handleAction("Analyze")}
          disabled={loadingAction === "Analyze"}
        >
          {loadingAction === "Sentiment Analyzer"
            ? "Loading..."
            : "Sentiment Analyzer"}
        </button>
        <button
          className="action-btn"
          onClick={() => handleAction("Meme")}
          disabled={loadingAction === "Meme"}
        >
          {loadingAction === "Meme" ? "Loading..." : "Create a meme"}
        </button>
        <button
          className="action-btn"
          onClick={() => handleAction("Summarize")}
          disabled={loadingAction === "Summarize"}
        >
          {loadingAction === "Simplify the tweet"
            ? "Loading..."
            : "Simplify the tweet"}
        </button>
        <button
          className="action-btn"
          onClick={() => handleAction("Summarize")}
          disabled={loadingAction === "Summarize"}
        >
          {loadingAction === "Check facts" ? "Loading..." : "Check facts"}
        </button>
        <button
          className="action-btn"
          onClick={() => handleAction("Summarize")}
          disabled={loadingAction === "Summarize"}
        >
          {loadingAction === "Viral threads generator"
            ? "Loading..."
            : "Viral threads generator"}
        </button>
      </div>

      {/* Thread Section */}
      <div className="thread-section">
        {thread.map((item, index) => (
          <div key={index} className="thread-item">
            <img
              src="https://abs.twimg.com/sticky/default_profile_images/default_profile_400x400.png"
              alt="Profile"
              className="thread-profile-picture"
            />
            <div className="thread-content">
              <div className="thread-header">
                <span className="thread-username">{item.username}</span>
                <span className="thread-handle">{item.handle}</span>
                <span className="thread-timestamp">· {item.timestamp}</span>
              </div>
              <div className="thread-text">{item.response}</div>
              <div className="thread-actions">
                <FaComment className="thread-action-icon" />
                <FaRetweet className="thread-action-icon" />
                <FaHeart className="thread-action-icon" />
                <FaShare className="thread-action-icon" />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TwitterPlayground;

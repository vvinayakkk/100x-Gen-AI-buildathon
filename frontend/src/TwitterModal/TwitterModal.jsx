import React, { useState } from "react";
import "./TwitterModal.css";

const TwitterModal = () => {
  const [showModal, setShowModal] = useState(true); // State for modal visibility

  const handleCloseModal = () => {
    setShowModal(false);
  };

  return (
    <>
      {showModal && (
        <div className="twitter-modal-overlay">
          <div className="twitter-modal animated-modal">
            <div className="modal-header">
              <img
                src="logo-white.png"
                alt="Twitter Logo"
                className="modal-logo"
              />
              <h2>
                Welcome to Your <br />
                Twitter Playground - TweetVichar
              </h2>
            </div>
            <div className="modal-body">
              <p>
                🚀 Experience the power of <b>AI-enhanced Twitter tools</b> to
                create, analyze, and optimize your tweets. This simulation is
                designed to replicate real Twitter interactions seamlessly.
              </p>
              <p>
                ✨ Built for innovation and creativity, you can perform
                sentiment analysis, meme generation, and more. Dive in and
                explore!
              </p>
              <div className="highlight-box">
                <strong>💡 Reminder:</strong> This is a simulation with no
                actual Twitter API integration, ensuring a free and immersive
                experience.
              </div>
            </div>
            <div className="modal-footer">
              <button className="okay-btn" onClick={handleCloseModal}>
                Let's Get Started
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default TwitterModal;

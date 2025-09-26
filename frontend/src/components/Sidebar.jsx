import React from "react";
import { FaPlus, FaSun, FaMoon, FaComments } from "react-icons/fa";

function Sidebar({ darkMode, setDarkMode }) {
  return (
    <div className="sidebar">
      <h2 className="logo">AI Chat</h2>
      <div className="chat-list">
        <p><FaComments /> General Chat</p>
        <p><FaComments /> Project Ideas</p>
        <p><FaComments /> Coding Help</p>
      </div>
      <div className="sidebar-footer">
        <button><FaPlus /> New Chat</button>
        <button onClick={() => setDarkMode(!darkMode)}>
          {darkMode ? <FaSun /> : <FaMoon />}
        </button>
      </div>
    </div>
  );
}

export default Sidebar;

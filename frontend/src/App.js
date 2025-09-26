import React, { useState } from "react";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import "./App.css";

function App() {
  const [darkMode, setDarkMode] = useState(true);

  return (
    <div className={`app ${darkMode ? "dark" : "light"}`}>
      <Sidebar darkMode={darkMode} setDarkMode={setDarkMode} />
      <ChatWindow />
    </div>
  );
}

export default App;

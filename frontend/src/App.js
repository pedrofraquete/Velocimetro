import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import PrayerSystem from "./components/PrayerSystem";
import AdminApp from "./components/AdminApp";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<PrayerSystem />} />
          <Route path="/admin" element={<AdminApp />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
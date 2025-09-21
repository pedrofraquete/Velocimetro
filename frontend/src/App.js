import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import PrayerSystem from "./components/PrayerSystem";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<PrayerSystem />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
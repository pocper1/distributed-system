import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import { Navigation } from "./components/navigation";
import { Team } from "./components/TeamList";
import { Login } from "./components/Login";
import { Register } from "./components/Register";
import { LandingPage } from "./components/LandingPage";

import SmoothScroll from "smooth-scroll";
import "./App.css";
export const scroll = new SmoothScroll('a[href*="#"]', {
    speed: 1000,
    speedAsDuration: true,
});

const App = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [userName, setUserName] = useState("");

    const handleLogin = name => {
        setIsLoggedIn(true);
        setUserName(name); // 設定使用者名稱
    };

    const handleLogout = () => {
        setIsLoggedIn(false);
        setUserName(""); // 清空使用者名稱
    };

    return (
        <Router>
            <Navigation isLoggedIn={isLoggedIn} userName={userName} onLogout={handleLogout} />
            <div id="page-content">
                <Routes>
                    <Route path="/" element={<LandingPage />} />
                    <Route path="/login" element={<Login onLogin={name => handleLogin(name)} />} />
                    <Route path="/register" element={<Register />} />
                    <Route path="/team" element={<Team />} />
                </Routes>
            </div>
        </Router>
    );
};

export default App;

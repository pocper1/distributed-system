import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import { LandingPage } from "./components/LandingPage";
import { Navigation } from "./components/navigation";

// Users
import { Login } from "./components/User/Login";
import { Register } from "./components/User/Register";
import { UserInfo } from "./components/User/Info";

// Teams
import { TeamList } from "./components/Team/TeamList";
import { CreateTeam } from "./components/Team/CreateTeam";

// Events
import { EventList } from "./components/Event/EventList";

// Admins
import { CreateEvent } from "./components/Admin/CreateEvent";

import SmoothScroll from "smooth-scroll";
import "./App.css";

// Smooth Scroll 設定
export const scroll = new SmoothScroll('a[href*="#"]', {
    speed: 1000,
    speedAsDuration: true,
});

const App = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [userName, setUserName] = useState("");

    // 使用 useEffect 檢查 localStorage，並初始化登入狀態
    useEffect(() => {
        const storedUserName = localStorage.getItem("userName");
        if (storedUserName) {
            setIsLoggedIn(true);
            setUserName(storedUserName);
        }
    }, []);

    const handleLogout = () => {
        localStorage.removeItem("userName"); // 清除 userName
        setIsLoggedIn(false);
        setUserName("");
    };

    return (
        <Router>
            <Navigation isLoggedIn={isLoggedIn} userName={userName} onLogout={handleLogout} />
            <div id="page-content">
                <Routes>
                    <Route path="/" element={<LandingPage />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route path="/user/info" element={<UserInfo />} />
                    <Route path="/team/list" element={<TeamList />} />
                    <Route path="/team/create" element={<CreateTeam />} />
                    <Route path="/event/list" element={<EventList />} />
                    <Route path="/event/create" element={<CreateEvent />} />
                </Routes>
            </div>
        </Router>
    );
};

export default App;
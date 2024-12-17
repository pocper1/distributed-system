import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";

import { LandingPage } from "./components/LandingPage";
import { Navigation } from "./components/navigation";

// Users
import { Login } from "./components/User/Login";
import { Register } from "./components/User/Register";
import { UserInfo } from "./components/User/Info";

// Events
import { CheckIn } from "./components/Event/CheckIn";
import { Ranking } from "./components/Event/Ranking";

// Teams
import { TeamList } from "./components/Team/TeamList";
import { CreateTeam } from "./components/Team/CreateTeam";
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

    // 登入處理
    const handleLogin = name => {
        setIsLoggedIn(true);
        setUserName(name);
    };

    // 登出處理
    const handleLogout = () => {
        setIsLoggedIn(false);
        setUserName("");
    };

    return (
        <AuthProvider>
            <Router>
                <Navigation isLoggedIn={isLoggedIn} userName={userName} onLogout={handleLogout} />
                <div id="page-content">
                    <Routes>
                        <Route path="/" element={<LandingPage />} />

                        {/* User Routes */}
                        <Route path="/login" element={<Login onLogin={handleLogin} />} />
                        <Route path="/register" element={<Register />} />
                        <Route path="/user/info" element={<UserInfo />} />

                        {/* Team Routes */}
                        <Route path="/team/list" element={<TeamList />} />
                        <Route path="/team/create" element={<CreateTeam />} />

                        {/* Event Routes */}
                        <Route path="/event/ranking" element={<Ranking />} />
                        <Route path="/event/checkin" element={<CheckIn />} />
                        <Route path="/event/list" element={<EventList />} />

                        {/* Admin Routes */}
                        <Route path="/event/create" element={<CreateEvent />} />
                    </Routes>
                </div>
            </Router>
        </AuthProvider>
    );
};

export default App;

import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, useNavigate } from "react-router-dom";

// Import your components
import { LandingPage } from "./components/LandingPage";
import { Navigation } from "./components/navigation";
import { Login } from "./components/User/Login";
import { Register } from "./components/User/Register";
import { UserInfo } from "./components/User/Info";
import { TeamList } from "./components/Team/TeamList";
import { CreateTeam } from "./components/Team/CreateTeam";
import { EventList } from "./components/Event/EventList";
import { EventDetail } from "./components/Event/EventDetail";
import { CreateEvent } from "./components/Admin/CreateEvent";
import { Upload } from "./components/Event/Upload";
import { UploadList } from "./components/Event/UploadList";
import { EventRanking } from "./components/Event/EventRanking";

import SmoothScroll from "smooth-scroll";
import "./App.css";

export const scroll = new SmoothScroll('a[href*="#"]', {
    speed: 1000,
    speedAsDuration: true,
});

const App = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [userName, setUserName] = useState("");

    useEffect(() => {
        const storedUserName = localStorage.getItem("userName");
        if (storedUserName) {
            setIsLoggedIn(true);
            setUserName(storedUserName);
        }
    }, []);

    const handleLogout = async () => {
        try {
            const response = await fetch(`${process.env.REACT_APP_API_URL}/api/user/logout`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
            });

            const data = await response.json();

            if (data.message === "Logout successful") {
                localStorage.removeItem("userId");
                localStorage.removeItem("userName");
                localStorage.removeItem("isSuperadmin");
                localStorage.removeItem("isLogin");

                // Navigate after logout
                window.location.href = "/";
            } else {
                alert("登出失敗");
            }
        } catch (err) {
            console.error("登出錯誤:", err.message);
            alert("登出時發生錯誤");
        }
    };

    return (
        <Router>
            <Navigation isLoggedIn={isLoggedIn} userName={userName} onLogout={handleLogout} />
            <div id="page-content">
                <Routes>
                    <Route path="/" element={<LandingPage />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route path="/user/info/:userId" element={<UserInfo />} />
                    <Route path="/team/list" element={<TeamList />} />
                    <Route path="/event/list" element={<EventList />} />
                    <Route path="/event/create" element={<CreateEvent />} />
                    <Route path="/event/:eventId" element={<EventDetail />} />
                    <Route path="/event/:eventId/team/create" element={<CreateTeam />} />
                    <Route path="/event/:eventId/upload" element={<Upload />} />
                    <Route path="/event/:eventId/uploadList" element={<UploadList />} />
                    <Route path="/event/:eventId/ranking" element={<EventRanking />} />
                </Routes>
            </div>
        </Router>
    );
};

export default App;

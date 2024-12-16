import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./components/Home";

import UserRegister from "./components/User/UserRegister";
import UserLogin from "./components/User/UserLogin";
import UserCheckin from "./components/User/UserCheckin";

import TeamCreate from "./components/Team/TeamCreate";
import TeamMembers from "./components/Team/TeamMembers";
import UpdateScore from "./components/Team/UpdateScore";
import Ranking from "./components/Team/Ranking";

function App() {
    return (
        <Router>
            <Navbar />
            <div className="container mt-4">
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/user/register" element={<UserRegister />} />
                    <Route path="/user/login" element={<UserLogin />} />
                    <Route path="/team/create" element={<TeamCreate />} />
                    <Route path="/team/:teamId/members" element={<TeamMembers />} />
                    <Route path="/checkin" element={<UserCheckin />} />
                    <Route path="/score/update" element={<UpdateScore />} />
                    <Route path="/ranking" element={<Ranking />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;

import React, { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";

export const EventDetail = () => {
    const [event, setEvent] = useState(null);
    const [teams, setTeams] = useState([]);
    const [currentTime, setCurrentTime] = useState(new Date());
    const [userTeams, setUserTeams] = useState([]); // 用來儲存使用者加入的隊伍
    const { eventId } = useParams(); // 從 URL 中獲取 eventId
    const navigate = useNavigate();

    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentTime(new Date());
        }, 1000); // 每秒更新一次時間

        return () => clearInterval(interval); // 組件卸載時清除計時器
    }, []);

    useEffect(() => {
        const fetchEventDetails = async () => {
            const response = await fetch(`${process.env.REACT_APP_API_URL}/api/event/${eventId}`);
            const data = await response.json();
            setEvent(data);
        };

        const fetchTeams = async () => {
            const response = await fetch(`${process.env.REACT_APP_API_URL}/api/event/${eventId}/teams`);
            const data = await response.json();
            setTeams(data.teams || []);
        };

        const fetchUserTeams = async () => {
            try {
                const userId = localStorage.getItem("userId");
                const isLogin = localStorage.getItem("isLogin");

                if (!userId || isLogin !== "true") {
                    throw new Error("User is not logged in or no userId found");
                }

                const response = await fetch(`${process.env.REACT_APP_API_URL}/api/user/${userId}/teams`);

                if (!response.ok) {
                    throw new Error(`Error fetching teams: ${response.status} ${response.statusText}`);
                }

                const data = await response.json();

                // 檢查資料結構是否正確
                if (!data.teams || !Array.isArray(data.teams)) {
                    throw new Error("Invalid response format");
                }

                if (data.teams.length === 0) {
                    console.warn("No teams found for this user");
                    setUserTeams([]);
                } else {
                    setUserTeams(data.teams);
                }
            } catch (err) {
                console.error("Error fetching user teams:", err.message);
                setUserTeams([]); // 避免狀態未定義
            }
        };

        fetchEventDetails();
        fetchTeams();
        fetchUserTeams();
    }, [eventId]); // 當 eventId 改變時重新發送請求

    const isEventActive = () => {
        if (!event) return false;
        const startTime = new Date(event.start_time);
        const endTime = new Date(event.end_time);
        return currentTime >= startTime && currentTime <= endTime;
    };

    // 檢查使用者是否已經在這個隊伍
    const isUserInTeam = teamId => {
        return userTeams.some(team => team.id === teamId);
    };

    const handleJoinTeam = async teamId => {
        const userId = localStorage.getItem("userId");
        console.log("UserId from localStorage:", userId); // 調試

        if (!userId) {
            alert("使用者未登入，無法加入隊伍！");
            return;
        }

        try {
            const response = await fetch(`${process.env.REACT_APP_API_URL}/api/event/${eventId}/teams/join`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    user_id: userId,
                    team_id: teamId,
                }),
            });

            if (!response.ok) {
                throw new Error("加入隊伍失敗");
            }

            alert("成功加入隊伍！");
            // 更新隊伍狀態或其他操作
        } catch (err) {
            console.error(err.message);
            alert("加入隊伍時發生錯誤！");
        }
    };

    const getTimeDifference = () => {
        if (!event || !event.end_time) return "尚未設定";
        const endTime = new Date(event.end_time);
        const diffMs = endTime - currentTime; // 計算毫秒差
        if (diffMs <= 0) return "已結束";

        // 轉換毫秒為時分秒
        const hours = Math.floor(diffMs / (1000 * 60 * 60));
        const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diffMs % (1000 * 60)) / 1000);

        return `${hours} 小時 ${minutes} 分鐘 ${seconds} 秒`;
    };

    if (!event) return <div>載入中...</div>;

    return (
        <div className="container mt-5">
            <h2 className="text-center">{event.name}</h2>
            <p className="text-center">{event.description}</p>
            <div>
                <h5>目前時間: {currentTime.toLocaleString()}</h5>
                <h5>開始時間: {event.start_time ? new Date(event.start_time).toLocaleString() : "尚未設定"}</h5>
                <h5>結束時間: {event.end_time ? new Date(event.end_time).toLocaleString() : "尚未設定"}</h5>
                <h5>剩餘時間: {getTimeDifference()}</h5>
            </div>

            <div className="mt-4">
                <button className="btn btn-success" onClick={() => navigate(`/event/${eventId}/team/create`)} disabled={!isEventActive()}>
                    新增隊伍
                </button>
                <button className="btn btn-warning" onClick={() => navigate(`/event/${eventId}/upload`)} disabled={!isEventActive()}>
                    上傳資料
                </button>
            </div>

            <div className="mt-4">
                <h4>目前報名的隊伍</h4>

                <table className="table table-bordered text-center">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>隊伍名稱</th>
                            <th>隊伍成員數</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        {teams.length > 0 ? (
                            teams.map((team, index) => (
                                <tr key={team.id}>
                                    <td>{index + 1}</td>
                                    <td>{team.name}</td>
                                    <td>{team.members.length}</td>
                                    <td>
                                        {/* 判斷使用者是否已加入隊伍 */}
                                        {isUserInTeam(team.id) ? (
                                            <span className="text-success">已加入</span>
                                        ) : (
                                            <button
                                                className="btn btn-primary btn-sm"
                                                onClick={() => handleJoinTeam(team.id)}
                                                disabled={!isEventActive()} // 禁用按鈕，若活動不在時間範圍內
                                            >
                                                加入隊伍
                                            </button>
                                        )}
                                    </td>
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan="4">目前沒有隊伍報名</td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

import React, { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext"; // 從 AuthContext 取得登入資訊
import { useNavigate } from "react-router-dom";

export const LandingPage = () => {
    const { username, authToken, logout } = useAuth(); // 從 AuthContext 取得登入資訊與方法
    const [teamCount, setTeamCount] = useState(0);
    const [postCount, setPostCount] = useState(0);
    const [deadline, setDeadline] = useState("");
    const [eventList, setEventList] = useState([]);
    const [isSuperuser, setIsSuperuser] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchData = async () => {
            try {
                // 從後端獲取統計數據
                const statsResponse = await fetch(`${process.env.REACT_APP_API_URL}/api/stats`, {
                    headers: { Authorization: `Bearer ${authToken}` },
                });
                const statsData = await statsResponse.json();
                setTeamCount(statsData.team_count);
                setPostCount(statsData.post_count);
                setDeadline(statsData.deadline);

                // 獲取活動列表
                const eventsResponse = await fetch(`${process.env.REACT_APP_API_URL}/api/event/all`, {
                    headers: { Authorization: `Bearer ${authToken}` },
                });
                const eventsData = await eventsResponse.json();
                setEventList(eventsData.events || []);
            } catch (error) {
                console.error("Error fetching data:", error);
            }
        };

        if (authToken) {
            fetchData();
        }
    }, [authToken]);

    useEffect(() => {
        // 檢查是否為超級用戶 (此邏輯根據需求修改)
        if (authToken && username === "admin") {
            setIsSuperuser(true);
        }
    }, [authToken, username]);

    const handleLogout = () => {
        logout(); // 調用 Context 的 logout 方法
        navigate("/"); // 導向首頁
    };

    return (
        <div className="container mt-5">
            <h1 className="text-center">歡迎來到行銷活動</h1>
            <p className="text-center">
                透過揪團、打卡、分享，快速提升品牌知名度！立即加入我們的活動，體驗全新的互動方式，並贏取豐厚獎勵。
            </p>

            {/* 統計數據 */}
            <div className="stats mt-4 text-center">
                <h3>活動統計</h3>
                <ul className="list-unstyled">
                    <li>團隊數量：<strong>{teamCount}</strong></li>
                    <li>貼文數量：<strong>{postCount}</strong></li>
                    <li>截止時間：<strong>{deadline}</strong></li>
                </ul>
            </div>

            {/* 按鈕區塊 */}
            <div className="text-center mt-4">
                {authToken ? (
                    <>
                        <button onClick={() => navigate("/ranking")} className="btn btn-success mx-2">排名</button>
                        <button onClick={() => navigate("/teams")} className="btn btn-info mx-2">團隊列表</button>
                        <button onClick={() => navigate("/checkin")} className="btn btn-warning mx-2">打卡</button>
                        <button onClick={handleLogout} className="btn btn-danger mx-2">登出</button>
                        {isSuperuser && (
                            <button onClick={() => navigate("/create-event")} className="btn btn-primary mx-2">
                                創建活動
                            </button>
                        )}
                    </>
                ) : (
                    <>
                        <button onClick={() => navigate("/register")} className="btn btn-primary mx-2">立即註冊</button>
                        <button onClick={() => navigate("/login")} className="btn btn-secondary mx-2">登入</button>
                    </>
                )}
            </div>

            {/* 活動列表 */}
            <div className="event-list mt-5">
                <h3>活動列表</h3>
                <table className="table table-bordered text-center">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>活動名稱</th>
                            <th>開始時間</th>
                            <th>結束時間</th>
                            <th>描述</th>
                        </tr>
                    </thead>
                    <tbody>
                        {eventList.length > 0 ? (
                            eventList.map((event, index) => (
                                <tr key={event.id}>
                                    <td>{index + 1}</td>
                                    <td>{event.name}</td>
                                    <td>{event.start_time}</td>
                                    <td>{event.end_time}</td>
                                    <td>{event.description}</td>
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan="5">目前沒有活動</td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};
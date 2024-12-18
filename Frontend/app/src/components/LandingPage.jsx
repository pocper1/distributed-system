import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

export const LandingPage = () => {
    const [teamCount, setTeamCount] = useState(0);
    const [postCount, setPostCount] = useState(0);
    const [deadline, setDeadline] = useState("");
    const [eventList, setEventList] = useState([]);
    const [isSuperuser, setIsSuperuser] = useState(false);
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    const navigate = useNavigate();

    // 用來格式化日期
    const formatDate = dateString => {
        const date = new Date(dateString);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, "0"); // 月份從0開始，需要加1
        const day = String(date.getDate()).padStart(2, "0");
        const hours = String(date.getHours()).padStart(2, "0");
        const minutes = String(date.getMinutes()).padStart(2, "0");
        const seconds = String(date.getSeconds()).padStart(2, "0");

        return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    };

    useEffect(() => {
        const fetchData = async () => {
            try {
                const eventsResponse = await fetch(`${process.env.REACT_APP_API_URL}/api/event/all`, {
                    method: "GET",
                });

                if (!eventsResponse.ok) throw new Error("無法獲取活動列表");

                const eventsData = await eventsResponse.json();
                // 排序活動列表，根據 end_time 進行排序（時間較近的排在最上面）
                const sortedEvents = eventsData.events.sort((a, b) => new Date(b.end_time) - new Date(a.end_time));
                setEventList(sortedEvents);
            } catch (error) {
                console.error("Error fetching data:", error.message);
            }
        };

        fetchData();
    }, []);

    useEffect(() => {
        const storedUserName = localStorage.getItem("userName");
        if (storedUserName) {
            setIsLoggedIn(true);
        }

        // checkSuperuser();
    }, []);

    const handleLogout = async () => {
        try {
            await fetch(`${process.env.REACT_APP_API_URL}/api/user/logout`, {
                method: "POST",
                credentials: "include",
            });
            localStorage.removeItem("userName");
            setIsLoggedIn(false);
            navigate("/");
        } catch (error) {
            console.error("登出失敗:", error.message);
        }
    };

    return (
        <div className="container mt-5">
            <h1 className="text-center">歡迎來到行銷活動</h1>
            <p className="text-center">透過揪團、打卡、分享，快速提升品牌知名度！立即加入我們的活動，體驗全新的互動方式，並贏取豐厚獎勳。</p>

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
                            <th>詳細資訊</th>
                        </tr>
                    </thead>
                    <tbody>
                        {eventList.length > 0 ? (
                            eventList.map((event, index) => (
                                <tr key={event.id}>
                                    <td>{index + 1}</td>
                                    <td>{event.name}</td>
                                    <td>{formatDate(event.start_time)}</td>
                                    <td>{formatDate(event.end_time)}</td>
                                    <td>
                                        <button className="btn btn-info me-2" onClick={() => navigate(`/event/${event.id}`)}>
                                            詳細資訊
                                        </button>
                                        <button className="btn btn-warning" onClick={() => navigate(`/event/${event.id}/ranking`)}>
                                            排名
                                        </button>
                                    </td>
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

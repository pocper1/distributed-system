import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export const EventList = ({ authToken }) => {
    const [eventList, setEventList] = useState([]); // 活動列表
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
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
            setIsLoading(true);
            setError(null);

            try {
                const eventsResponse = await fetch(`${process.env.REACT_APP_API_URL}/api/event/all`, {
                    method: "GET",
                });

                if (!eventsResponse.ok) throw new Error("無法獲取活動列表");

                const eventsData = await eventsResponse.json();

                // 排序活動列表，根據 `end_time` 排序（時間較近的排在最上面）
                const sortedEvents = eventsData.events.sort((a, b) => new Date(b.end_time) - new Date(a.end_time));
                setEventList(sortedEvents);
            } catch (err) {
                console.error("Error fetching events:", err.message);
                setError(err.message);
            } finally {
                setIsLoading(false);
            }
        };

        fetchData();
    }, []);

    return (
        <div className="container mt-5">
            <h3>活動列表</h3>
            {error && <div className="alert alert-danger">{error}</div>}
            {isLoading ? (
                <p>資料加載中...</p>
            ) : (
                <div className="event-list mt-5">
                    <table className="table table-bordered text-center">
                        <thead>
                            <tr>
                                <th>ID</th> {/* 將 # 改為 ID */}
                                <th>活動名稱</th>
                                <th>開始時間</th>
                                <th>結束時間</th>
                                <th>詳細資訊</th>
                            </tr>
                        </thead>
                        <tbody>
                            {eventList.length > 0 ? (
                                eventList.map(event => (
                                    <tr key={event.id}>
                                        <td>{event.id}</td> {/* 顯示活動的 ID */}
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
            )}
        </div>
    );
};
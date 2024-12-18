import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

export const LandingPage = () => {
    const [eventList, setEventList] = useState([]);
    const navigate = useNavigate();

    // 日期格式化
    const formatDate = dateString => {
        const date = new Date(dateString);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, "0");
        const day = String(date.getDate()).padStart(2, "0");
        const hours = String(date.getHours()).padStart(2, "0");
        const minutes = String(date.getMinutes()).padStart(2, "0");

        return `${year}-${month}-${day} ${hours}:${minutes}`;
    };

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch(`${process.env.REACT_APP_API_URL}/api/event/all`, {
                    method: "GET",
                });

                if (!response.ok) throw new Error("無法獲取活動列表");

                const data = await response.json();
                const sortedEvents = data.events.sort((a, b) => new Date(b.end_time) - new Date(a.end_time));
                setEventList(sortedEvents);
            } catch (error) {
                console.error("Error fetching data:", error.message);
            }
        };

        fetchData();
    }, []);

    return (
        <div className="container mt-5">
            <div className="text-center">
                <h1>歡迎來到行銷活動</h1>
                <p className="lead">透過揪團、打卡、分享，快速提升品牌知名度！立即加入我們的活動，體驗全新的互動方式，並贏取豐厚獎勳。</p>
            </div>

            <div className="mt-5">
                <h3 className="text-center">活動列表</h3>
                <table className="table table-striped table-hover text-center mt-4">
                    <thead className="table-dark">
                        <tr>
                            <th>ID</th>
                            <th>活動名稱</th>
                            <th>開始時間</th>
                            <th>結束時間</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        {eventList.length > 0 ? (
                            eventList.map(event => (
                                <tr key={event.id}>
                                    <td>{event.id}</td>
                                    <td>{event.name}</td>
                                    <td>{formatDate(event.start_time)}</td>
                                    <td>{formatDate(event.end_time)}</td>
                                    <td>
                                        <button className="btn btn-info btn-sm me-2" onClick={() => navigate(`/event/${event.id}`)}>
                                            詳細資訊
                                        </button>
                                        <button className="btn btn-warning btn-sm" onClick={() => navigate(`/event/${event.id}/ranking`)}>
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

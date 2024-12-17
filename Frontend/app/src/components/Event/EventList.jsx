import React, { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext"; // 從 AuthContext 取得登入資訊

export const EventList = () => {
    const [eventList, setEventList] = useState([]); // 活動列表
    const [userEvents, setUserEvents] = useState([]); // 使用者已加入的活動
    const [isLoading, setIsLoading] = useState(false);

    const { authToken } = useAuth(); // 從 AuthContext 取得 authToken

    // 取得活動列表與使用者已加入的活動
    useEffect(() => {
        const fetchData = async () => {
            try {
                setIsLoading(true);

                // 獲取所有活動
                const eventsResponse = await fetch(`${process.env.REACT_APP_API_URL}/api/events`, {
                    headers: {
                        Authorization: `Bearer ${authToken}`,
                    },
                });
                const eventsData = await eventsResponse.json();
                setEventList(eventsData.events || []);

                // 獲取使用者已加入的活動
                const userEventsResponse = await fetch(`${process.env.REACT_APP_API_URL}/api/user/events`, {
                    headers: {
                        Authorization: `Bearer ${authToken}`,
                    },
                });
                const userEventsData = await userEventsResponse.json();
                setUserEvents(userEventsData.events || []);
            } catch (error) {
                console.error("Error fetching event data:", error);
            } finally {
                setIsLoading(false);
            }
        };

        if (authToken) {
            fetchData();
        }
    }, [authToken]);

    // 加入活動功能
    const handleAddEvent = async eventId => {
        try {
            const response = await fetch(`${process.env.REACT_APP_API_URL}/api/events/join`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${authToken}`,
                },
                body: JSON.stringify({ event_id: eventId }),
            });

            if (response.ok) {
                alert("成功加入活動！");
                setUserEvents(prev => [...prev, eventId]); // 更新加入的活動列表
            } else {
                const errorData = await response.json();
                alert(`加入失敗: ${errorData.detail}`);
            }
        } catch (error) {
            console.error("Error adding event:", error);
            alert("加入活動時發生錯誤！");
        }
    };

    // 檢查活動是否已加入
    const isEventJoined = eventId => userEvents.includes(eventId);

    return (
        <div className="container mt-5">
            <h3>活動列表</h3>
            {isLoading ? (
                <p>資料加載中...</p>
            ) : (
                <table className="table table-striped table-bordered">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>活動名稱</th>
                            <th>開始時間</th>
                            <th>結束時間</th>
                            <th>描述</th>
                            <th>操作</th>
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
                                    <td>
                                        {isEventJoined(event.id) ? (
                                            <span className="text-success">已加入</span>
                                        ) : (
                                            <button className="btn btn-primary btn-sm" onClick={() => handleAddEvent(event.id)}>
                                                加入
                                            </button>
                                        )}
                                    </td>
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan="6" className="text-center">
                                    暫無活動資訊
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            )}
        </div>
    );
};

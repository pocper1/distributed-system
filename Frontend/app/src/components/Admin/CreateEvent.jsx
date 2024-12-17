import React, { useState } from "react";

export const CreateEvent = () => {
    const [eventName, setEventName] = useState(""); // 活動名稱
    const [eventDescription, setEventDescription] = useState(""); // 活動描述
    const [startTime, setStartTime] = useState(""); // 活動開始時間
    const [endTime, setEndTime] = useState(""); // 活動結束時間
    const [loading, setLoading] = useState(false); // 處理上傳的狀態

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!eventName || !eventDescription || !startTime || !endTime) {
            alert("請輸入所有必填欄位！");
            return;
        }

        if (new Date(startTime) >= new Date(endTime)) {
            alert("開始時間必須早於結束時間！");
            return;
        }

        const payload = {
            name: eventName,
            description: eventDescription,
            start_time: startTime,
            end_time: endTime,
        };

        try {
            setLoading(true);
            const response = await fetch("/api/event/create", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            });

            if (response.ok) {
                alert("活動創建成功！");
                setEventName(""); // 清空輸入
                setEventDescription("");
                setStartTime("");
                setEndTime("");
            } else {
                const data = await response.json();
                alert(`創建失敗: ${data.detail || "請稍後再試！"}`);
            }
        } catch (error) {
            console.error("Event creation failed:", error);
            alert("創建活動時發生錯誤！");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div id="create-event" className="container">
            <h2>創建活動</h2>
            <form onSubmit={handleSubmit}>
                {/* 活動名稱 */}
                <div className="form-group">
                    <label htmlFor="eventName">活動名稱:</label>
                    <input
                        type="text"
                        id="eventName"
                        className="form-control"
                        value={eventName}
                        onChange={(e) => setEventName(e.target.value)}
                        required
                    />
                </div>

                {/* 活動描述 */}
                <div className="form-group">
                    <label htmlFor="eventDescription">活動描述:</label>
                    <textarea
                        id="eventDescription"
                        className="form-control"
                        rows="4"
                        value={eventDescription}
                        onChange={(e) => setEventDescription(e.target.value)}
                        required
                    ></textarea>
                </div>

                {/* 活動開始時間 */}
                <div className="form-group">
                    <label htmlFor="startTime">活動開始時間:</label>
                    <input
                        type="datetime-local"
                        id="startTime"
                        className="form-control"
                        value={startTime}
                        onChange={(e) => setStartTime(e.target.value)}
                        required
                    />
                </div>

                {/* 活動結束時間 */}
                <div className="form-group">
                    <label htmlFor="endTime">活動結束時間:</label>
                    <input
                        type="datetime-local"
                        id="endTime"
                        className="form-control"
                        value={endTime}
                        onChange={(e) => setEndTime(e.target.value)}
                        required
                    />
                </div>

                {/* 提交按鈕 */}
                <button type="submit" className="btn btn-primary" disabled={loading}>
                    {loading ? "創建中..." : "創建活動"}
                </button>
            </form>
        </div>
    );
};
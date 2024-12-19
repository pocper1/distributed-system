import React, { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

export const CreateTeam = () => {
    const [teamName, setTeamName] = useState(""); // 團隊名稱
    const [teamDescription, setTeamDescription] = useState(""); // 團隊描述
    const [loading, setLoading] = useState(false); // 處理上傳的狀態
    const [errorMessage, setErrorMessage] = useState(""); // 錯誤訊息
    const navigate = useNavigate(); // 初始化 navigate
    const { eventId } = useParams(); // 從 URL 參數獲取 eventId

    const handleSubmit = async e => {
        e.preventDefault();
        setErrorMessage(""); // 清空之前的錯誤訊息

        if (!teamName || !teamDescription) {
            setErrorMessage("請輸入團隊名稱和描述！");
            return;
        }

        const payload = {
            name: teamName,
            description: teamDescription,
        };

        try {
            setLoading(true);
            const response = await fetch(`${process.env.REACT_APP_API_URL}/api/event/${eventId}/team/create`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            });

            if (response.ok) {
                const data = await response.json();
                alert("團隊創建成功！");
                setTeamName(""); // 清空輸入
                setTeamDescription("");

                // 自動導向到 /event/${eventId}
                navigate(`/event/${eventId}`);
            } else {
                const data = await response.json();
                setErrorMessage(`創建失敗: ${data.detail || "請稍後再試！"}`);
            }
        } catch (error) {
            console.error("Team creation failed:", error);
            setErrorMessage("創建團隊時發生錯誤，請檢查網路或聯繫管理員！");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div id="create-team" className="container">
            <h2>創建團隊</h2>
            {errorMessage && <div className="alert alert-danger">{errorMessage}</div>} {/* 錯誤訊息顯示 */}
            <form onSubmit={handleSubmit}>
                {/* 團隊名稱輸入 */}
                <div className="form-group">
                    <label htmlFor="teamName">團隊名稱:</label>
                    <input
                        type="text"
                        id="teamName"
                        className="form-control"
                        value={teamName}
                        onChange={e => setTeamName(e.target.value)}
                        required
                    />
                </div>

                {/* 團隊描述輸入 */}
                <div className="form-group">
                    <label htmlFor="teamDescription">團隊描述:</label>
                    <textarea
                        id="teamDescription"
                        className="form-control"
                        rows="4"
                        value={teamDescription}
                        onChange={e => setTeamDescription(e.target.value)}
                        required
                    ></textarea>
                </div>

                {/* 提交按鈕 */}
                <button type="submit" className="btn btn-primary" disabled={loading}>
                    {loading ? "創建中..." : "創建團隊"}
                </button>
            </form>
        </div>
    );
};
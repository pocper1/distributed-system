import React, { useEffect, useState } from "react";

export const UserInfo = ({ userName }) => {
    const [userInfo, setUserInfo] = useState({}); // 使用者資訊狀態
    const [loading, setLoading] = useState(true); // 載入狀態
    const [error, setError] = useState(null); // 錯誤狀態

    useEffect(() => {
        const fetchUserInfo = async () => {
            try {
                // 從後端 API 獲取使用者資訊
                const response = await fetch(`${process.env.REACT_APP_API_URL}/api/user/info`, {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    credentials: "include", // 確保發送 cookies（如使用 Session 或 JWT）
                });

                if (!response.ok) {
                    throw new Error("無法獲取使用者資訊");
                }

                const data = await response.json();
                setUserInfo(data);
                setLoading(false);
            } catch (err) {
                console.error(err);
                setError(err.message);
                setLoading(false);
            }
        };

        fetchUserInfo();
    }, []);

    if (loading) {
        return <div className="text-center">載入中...</div>;
    }

    if (error) {
        return <div className="alert alert-danger text-center">{error}</div>;
    }

    return (
        <div className="container mt-5">
            <h2 className="text-center mb-4">使用者資訊</h2>
            <div className="card shadow-sm mx-auto" style={{ maxWidth: "500px" }}>
                <div className="card-body">
                    <h5 className="card-title text-center mb-3">歡迎回來, {userName || userInfo.username}</h5>
                    <ul className="list-group list-group-flush">
                        <li className="list-group-item">
                            <strong>使用者名稱：</strong> {userInfo.username || "N/A"}
                        </li>
                        <li className="list-group-item">
                            <strong>Email：</strong> {userInfo.email || "N/A"}
                        </li>
                        <li className="list-group-item">
                            <strong>加入時間：</strong> {userInfo.created_at || "N/A"}
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    );
};
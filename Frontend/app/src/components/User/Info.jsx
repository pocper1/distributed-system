import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

export const UserInfo = () => {
    const [userInfo, setUserInfo] = useState(null);
    const [userTeams, setUserTeams] = useState([]); // 新增狀態來儲存使用者的隊伍
    const [error, setError] = useState(null);
    const { userId } = useParams(); // 從 URL 中獲取 userId

    useEffect(() => {
        const fetchUserInfo = async () => {
            try {
                const response = await fetch(`${process.env.REACT_APP_API_URL}/api/user/${userId}/info`, {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                    },
                });

                if (!response.ok) {
                    throw new Error("無法獲取用戶資料");
                }

                const data = await response.json();
                setUserInfo(data); // 設置用戶資料
            } catch (err) {
                setError(err.message); // 設置錯誤信息
            }
        };

        const fetchUserTeams = async () => {
            try {
                const response = await fetch(`${process.env.REACT_APP_API_URL}/api/user/${userId}/teams`, {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                    },
                });

                if (!response.ok) {
                    throw new Error("無法獲取隊伍資料");
                }

                const data = await response.json();
                setUserTeams(data.teams || []); // 設置隊伍資料
            } catch (err) {
                setError(err.message); // 設置錯誤信息
            }
        };

        fetchUserInfo();
        fetchUserTeams();
    }, [userId]); // 當 userId 改變時重新加載資料

    if (error) {
        return <div>錯誤: {error}</div>;
    }

    if (!userInfo || userTeams.length === 0) {
        return <div>載入中...</div>;
    }

    return (
        <div className="container mt-5">
            <h2>用戶資料</h2>
            <div className="card">
                <div className="card-body">
                    <h5 className="card-title">用戶名: {userInfo.username}</h5>
                    <p className="card-text">電子郵件: {userInfo.email}</p>
                    <p className="card-text">管理員: {userInfo.is_superadmin ? "是" : "否"}</p>
                    <p className="card-text">註冊時間: {new Date(userInfo.created_at).toLocaleString()}</p>
                </div>
            </div>

            <h3 className="mt-4">已加入隊伍</h3>
            {userTeams.length > 0 ? (
                <ul>
                    {userTeams.map(team => (
                        <li key={team.id}>{team.name}</li> // 顯示隊伍名稱
                    ))}
                </ul>
            ) : (
                <p>此用戶尚未加入任何隊伍。</p>
            )}
        </div>
    );
};

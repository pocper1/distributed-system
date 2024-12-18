import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

export const UserInfo = () => {
    const [userInfo, setUserInfo] = useState(null);
    const [userTeams, setUserTeams] = useState([]);
    const [error, setError] = useState(null);
    const { userId } = useParams();

    useEffect(() => {
        const fetchUserInfo = async () => {
            try {
                const response = await fetch(`${process.env.REACT_APP_API_URL}/api/user/${userId}/info`, {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                    },
                });

                if (!response.ok) throw new Error("無法獲取用戶資料");

                const data = await response.json();
                setUserInfo(data);
            } catch (err) {
                setError(err.message);
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

                if (!response.ok) throw new Error("無法獲取隊伍資料");

                const data = await response.json();
                setUserTeams(data.teams || []);
            } catch (err) {
                setError(err.message);
            }
        };

        fetchUserInfo();
        fetchUserTeams();
    }, [userId]);

    if (error) {
        return <div className="alert alert-danger">錯誤: {error}</div>;
    }

    if (!userInfo || userTeams.length === 0) {
        return <div className="text-center">載入中...</div>;
    }

    return (
        <div className="container mt-5">
            <div className="text-center">
                <h2>用戶資料</h2>
            </div>

            <div className="card mt-4">
                <div className="card-body">
                    <h5 className="card-title">用戶名: {userInfo.username}</h5>
                    <p className="card-text">電子郵件: {userInfo.email}</p>
                    <p className="card-text">管理員: {userInfo.is_superadmin ? "是" : "否"}</p>
                    <p className="card-text">註冊時間: {new Date(userInfo.created_at).toLocaleString()}</p>
                </div>
            </div>

            <div className="mt-5">
                <h3>已加入的隊伍</h3>
                {userTeams.length > 0 ? (
                    <ul className="list-group">
                        {userTeams.map(team => (
                            <li className="list-group-item" key={team.id}>
                                {team.name}
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p className="text-muted">此用戶尚未加入任何隊伍。</p>
                )}
            </div>
        </div>
    );
};

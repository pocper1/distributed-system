import React, { useEffect, useState } from "react";

export const Ranking = () => {
    const [rankings, setRankings] = useState([]); // 儲存排名資訊
    const [loading, setLoading] = useState(true); // 載入狀態
    const [error, setError] = useState(null); // 錯誤狀態

    useEffect(() => {
        // 從後端 API 獲取排名資料
        const fetchRankings = async () => {
            try {
                const response = await fetch(`${process.env.REACT_APP_API_URL}/api/ranking`);
                if (!response.ok) {
                    throw new Error("無法獲取排名資訊，請稍後再試！");
                }
                const data = await response.json();
                setRankings(data.rankings); // 假設返回的結構: { rankings: [{ team_id, team_name, total_score }] }
                setLoading(false);
            } catch (err) {
                console.error("Error fetching rankings:", err);
                setError(err.message);
                setLoading(false);
            }
        };

        fetchRankings();
    }, []);

    return (
        <div className="container mt-5">
            <h2 className="text-center mb-4">團隊排名</h2>

            {/* 錯誤處理 */}
            {error && <div className="alert alert-danger text-center">{error}</div>}

            {/* 載入中狀態 */}
            {loading ? (
                <div className="text-center">載入中...</div>
            ) : (
                <div className="table-responsive">
                    <table className="table table-striped table-bordered">
                        <thead className="thead-dark">
                            <tr>
                                <th>排名</th>
                                <th>團隊名稱</th>
                                <th>總積分</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rankings.length > 0 ? (
                                rankings.map((team, index) => (
                                    <tr key={team.team_id}>
                                        <td>{index + 1}</td>
                                        <td>{team.team_name}</td>
                                        <td>{team.total_score}</td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="3" className="text-center">
                                        目前沒有排名資訊。
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};
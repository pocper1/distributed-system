import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

export const EventRanking = () => {
    const { eventId } = useParams(); // 獲取活動 ID
    const [rankingList, setRankingList] = useState([]); // 排名列表
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchRankings = async () => {
            setIsLoading(true);
            setError(null);

            try {
                const response = await fetch(`${process.env.REACT_APP_API_URL}/api/event/${eventId}/ranking`);

                if (!response.ok) throw new Error("無法獲取排名數據");
                const data = await response.json();

                // 假設後端已排序，直接使用返回的數據
                setRankingList(data.rankings || []);
            } catch (err) {
                console.error("Error fetching rankings:", err.message);
                setError(err.message);
            } finally {
                setIsLoading(false);
            }
        };

        fetchRankings();
    }, [eventId]);

    return (
        <div className="container mt-5">
            <h3>活動排名</h3>
            {error && <div className="alert alert-danger">{error}</div>}
            {isLoading ? (
                <p>資料加載中...</p>
            ) : (
                <div className="ranking-list mt-4">
                    <table className="table table-bordered text-center">
                        <thead>
                            <tr>
                                <th>排名</th>
                                <th>隊伍名稱</th>
                                <th>分數</th>
                                <th>隊伍人數</th> {/* 新增隊伍人數欄位 */}
                            </tr>
                        </thead>
                        <tbody>
                            {rankingList.length > 0 ? (
                                rankingList.map((rank, index) => (
                                    <tr key={rank.team_id}>
                                        <td>{index + 1}</td>
                                        <td>{rank.team_name}</td>
                                        <td>{rank.score}</td>
                                        <td>{rank.team_size}</td> {/* 顯示隊伍人數 */}
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="4">尚未有排名數據</td> {/* 更新 colspan */}
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};
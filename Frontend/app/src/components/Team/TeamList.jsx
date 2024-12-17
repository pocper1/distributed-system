import React, { useState, useEffect } from "react";

export const TeamList = () => {
    const [teams, setTeams] = useState([]);
    const [isLoggedIn, setIsLoggedIn] = useState(false); // 模擬登入狀態

    useEffect(() => {
        // 模擬 API 呼叫，取得 Teams 資料
        const fetchTeams = async () => {
            try {
                const response = await fetch("/api/teams"); // 替換為後端 API URL
                const data = await response.json();
                setTeams(data.teams); // 假設返回格式為 { teams: [{ id, name, members_count, posts_count }] }
            } catch (error) {
                console.error("Failed to fetch teams:", error);
            }
        };

        fetchTeams();
    }, []);

    return (
        <div id="team" className="text-center">
            <div className="container">
                <div className="col-md-8 col-md-offset-2 section-title">
                    <h2>團隊資訊</h2>
                    <p>顯示各團隊的數量、人數與 Po 文數量。</p>
                </div>

                {isLoggedIn ? (
                    <div className="table-responsive">
                        {teams.length > 0 ? (
                            <table className="table table-striped table-bordered">
                                <thead className="thead-dark">
                                    <tr>
                                        <th>#</th>
                                        <th>團隊名稱</th>
                                        <th>人數</th>
                                        <th>Po 文數量</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {teams.map((team, index) => (
                                        <tr key={team.id}>
                                            <td>{index + 1}</td>
                                            <td>{team.name}</td>
                                            <td>{team.members_count}</td>
                                            <td>{team.posts_count}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        ) : (
                            <p>載入中...</p>
                        )}
                    </div>
                ) : (
                    <div className="not-logged-in">
                        <p>請先登入以查看團隊資訊！</p>
                        <a href="/login" className="btn btn-primary">
                            登入
                        </a>
                    </div>
                )}
            </div>
        </div>
    );
};

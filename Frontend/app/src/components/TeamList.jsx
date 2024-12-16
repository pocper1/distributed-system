import React, { useState, useEffect } from "react";

export const Team = () => {
  const [rankings, setRankings] = useState([]);
  const [isLoggedIn, setIsLoggedIn] = useState(false); // 登入狀態模擬

  useEffect(() => {
    // 模擬 API 呼叫，取得排名資料
    const fetchRankings = async () => {
      try {
        const response = await fetch("/api/rankings"); // 替換為後端 API URL
        const data = await response.json();
        setRankings(data);
      } catch (error) {
        console.error("Failed to fetch rankings:", error);
      }
    };

    fetchRankings();
  }, []);

  return (
    <div id="team" className="text-center">
      <div className="container">
        <div className="col-md-8 col-md-offset-2 section-title">
          <h2>即時團隊積分排行</h2>
          <p>
            根據團隊人數、默契及新會員數動態更新排名。
          </p>
        </div>
        {isLoggedIn ? (
          <div id="rankings" className="row">
            {rankings.length > 0 ? (
              rankings.slice(0, 20).map((team, index) => (
                <div key={team.id} className="col-md-3 col-sm-6 team">
                  <div className="thumbnail">
                    <div className="caption">
                      <h4>#{index + 1} - {team.name}</h4>
                      <p>積分: {team.score}</p>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              "載入中..."
            )}
          </div>
        ) : (
          <div className="not-logged-in">
            <p>請先登入以查看團隊排名！</p>
            <a href="/login" className="btn btn-primary">登入</a>
          </div>
        )}
      </div>
    </div>
  );
};
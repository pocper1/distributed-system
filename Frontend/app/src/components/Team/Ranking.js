import React, { useState, useEffect } from "react";

function Ranking() {
    const [rankings, setRankings] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchRankings = async () => {
            try {
                const response = await fetch("/api/ranking");
                const data = await response.json();
                if (response.ok) {
                    setRankings(data.rankings);
                } else {
                    setRankings([]);
                }
            } catch (error) {
                console.error("Failed to fetch rankings", error);
                setRankings([]);
            } finally {
                setLoading(false);
            }
        };

        fetchRankings();
    }, []);

    return (
        <div>
            <h2>Team Rankings</h2>
            {loading ? (
                <p>Loading rankings...</p>
            ) : rankings.length > 0 ? (
                <table className="table table-striped">
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Team ID</th>
                            <th>Score</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rankings.map((rank, index) => (
                            <tr key={rank[0]}>
                                <td>{index + 1}</td>
                                <td>{rank[0]}</td>
                                <td>{rank[1]}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            ) : (
                <p>No rankings available.</p>
            )}
        </div>
    );
}

export default Ranking;

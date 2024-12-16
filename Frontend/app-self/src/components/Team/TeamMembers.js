import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

function TeamMembers() {
    const { teamId } = useParams(); // Get teamId from the route parameter
    const [members, setMembers] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchMembers = async () => {
            try {
                const response = await fetch(`/api/team/${teamId}/members`);
                const data = await response.json();
                if (response.ok) {
                    setMembers(data.members);
                } else {
                    setMembers([]);
                }
            } catch (error) {
                console.error("Failed to fetch team members", error);
                setMembers([]);
            } finally {
                setLoading(false);
            }
        };

        fetchMembers();
    }, [teamId]);

    return (
        <div>
            <h2>Team Members</h2>
            {loading ? (
                <p>Loading members...</p>
            ) : members.length > 0 ? (
                <ul className="list-group">
                    {members.map((member, index) => (
                        <li key={index} className="list-group-item">
                            {member}
                        </li>
                    ))}
                </ul>
            ) : (
                <p>No members found for this team.</p>
            )}
        </div>
    );
}

export default TeamMembers;

import React, { useState } from "react";

export const Upload = () => {
    const [teamId, setTeamId] = useState("");

    const handleUpload = async () => {
        const payload = {
            teamId,
            timestamp: new Date().toISOString(),
        };
        try {
            const response = await fetch("/api/upload", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            });
            if (response.ok) {
                alert("打卡資料上傳成功！");
            } else {
                alert("上傳失敗，請稍後再試！");
            }
        } catch (error) {
            console.error("Upload failed:", error);
        }
    };

    return (
        <div id="upload" className="text-center">
            <div className="container">
                <h2>上傳打卡資料</h2>
                <div className="form-group">
                    <label htmlFor="teamId">團隊 ID:</label>
                    <input type="text" id="teamId" className="form-control" value={teamId} onChange={e => setTeamId(e.target.value)} />
                </div>
                <button className="btn btn-primary" onClick={handleUpload}>
                    上傳
                </button>
            </div>
        </div>
    );
};

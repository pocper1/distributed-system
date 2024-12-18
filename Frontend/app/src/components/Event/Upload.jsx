import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

export const Upload = () => {
    const { eventId } = useParams(); // 從 URL 取得 eventId
    const [comment, setComment] = useState("");
    const [photo, setPhoto] = useState("");

    // 處理圖片選擇
    const handlePhotoChange = e => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
                setPhoto(reader.result.split(",")[1]); // 轉換為 Base64 字串
            };
            reader.readAsDataURL(file);
        }
    };

    // 上傳資料
    const handleUpload = async () => {
        const userId = localStorage.getItem("userId");
        if (!userId) {
            alert("請先登入系統！");
            return;
        }

        const payload = {
            user_id: userId, // 傳送使用者 ID 給後端
            created_at: new Date().toISOString(),
            comment: comment,
            photo: photo, // Base64 編碼圖片
        };

        try {
            const response = await fetch(`/api/event/${eventId}/upload`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            });

            if (response.ok) {
                alert("打卡資料已成功上傳至所有隊伍！");
                setComment("");
                setPhoto("");
            } else {
                alert("打卡資料上傳失敗，請稍後重試！");
            }
        } catch (error) {
            console.error("Upload failed:", error);
            alert("上傳時發生錯誤，請稍後再試！");
        }
    };

    return (
        <div id="upload" className="text-center">
            <div className="container">
                <h2>上傳打卡資料</h2>
                <div className="form-group">
                    <label htmlFor="comment">備註:</label>
                    <textarea id="comment" className="form-control" rows="3" value={comment} onChange={e => setComment(e.target.value)}></textarea>
                </div>
                <div className="form-group">
                    <label htmlFor="photo">上傳照片:</label>
                    <input type="file" id="photo" className="form-control" accept="image/*" onChange={handlePhotoChange} />
                </div>
                <button className="btn btn-primary" onClick={handleUpload}>
                    上傳
                </button>
            </div>
        </div>
    );
};

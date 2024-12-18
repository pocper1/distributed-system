import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

export const UploadList = () => {
    const { eventId } = useParams(); // 獲取 eventId
    const [event, setEvent] = useState(null); // 活動詳情
    const [uploads, setUploads] = useState([]); // 上傳數據列表

    // 獲取活動詳情
    useEffect(() => {
        const fetchEventDetails = async () => {
            try {
                const response = await fetch(`${process.env.REACT_APP_API_URL}/api/event/${eventId}`);
                const data = await response.json();
                setEvent(data);
            } catch (error) {
                console.error("Error fetching event details:", error);
            }
        };

        // 獲取活動的所有上傳數據
        const fetchUploads = async () => {
            try {
                const response = await fetch(`${process.env.REACT_APP_API_URL}/api/event/${eventId}/upload/list`);
                const data = await response.json();

                // 按 created_at 降序排序並限制為最近 20 筆
                const sortedUploads = (data.uploads || []).sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 20);
                setUploads(sortedUploads);
            } catch (error) {
                console.error("Error fetching uploads:", error);
            }
        };

        fetchEventDetails();
        fetchUploads();
    }, [eventId]); // 當 eventId 改變時重新獲取數據

    // 如果活動資料尚未加載完成
    if (!event) return <div>載入中...</div>;

    return (
        <div className="container mt-5">
            <h2 className="text-center">{event.name}</h2>
            <p className="text-center">{event.description}</p>

            {/* 顯示上傳的資料 */}
            <div className="mt-4">
                <h4>上傳的資料 (最近 20 筆)</h4>
                {uploads.length > 0 ? (
                    <div className="uploads">
                        {uploads.map((upload, index) => (
                            <div key={index} className="upload-item mb-4">
                                <p>
                                    <strong>留言：</strong>
                                    {upload.comment || "無留言"}
                                </p>
                                {upload.photo_url && <img src={upload.photo_url} alt="Uploaded" style={{ maxWidth: "300px", maxHeight: "300px" }} />}
                                <p>
                                    <strong>上傳時間：</strong>
                                    {new Date(upload.created_at).toLocaleString()}
                                </p>
                                <hr />
                            </div>
                        ))}
                    </div>
                ) : (
                    <p>尚未有任何上傳資料。</p>
                )}
            </div>
        </div>
    );
};

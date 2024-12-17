import React, { useState } from "react";
import axios from "axios";

export const CheckIn = () => {
    const [text, setText] = useState(""); // Textarea 的內容
    const [image, setImage] = useState(null); // 圖片檔案
    const [preview, setPreview] = useState(null); // 圖片預覽

    // 處理 Textarea 變更
    const handleTextChange = e => {
        setText(e.target.value);
    };

    // 處理圖片上傳
    const handleImageChange = e => {
        const file = e.target.files[0];
        if (file) {
            setImage(file);
            setPreview(URL.createObjectURL(file)); // 預覽圖片
        }
    };

    // 提交資料到後端
    const handleSubmit = async e => {
        e.preventDefault();
        if (!image || !text) {
            alert("請輸入文字並選擇圖片！");
            return;
        }

        // 使用 FormData 來傳送圖片和文字
        const formData = new FormData();
        formData.append("text", text);
        formData.append("image", image);

        try {
            const response = await axios.post(
                "http://localhost:8000/upload", // 修改為後端 API 的 URL
                formData,
                {
                    headers: {
                        "Content-Type": "multipart/form-data",
                    },
                }
            );
            alert("上傳成功！");
            console.log("Server response:", response.data);
        } catch (error) {
            console.error("上傳失敗:", error);
            alert("上傳失敗，請稍後再試。");
        }
    };

    return (
        <div className="upload-container">
            <h2>文字與圖片上傳</h2>
            <form onSubmit={handleSubmit}>
                {/* Textarea */}
                <div className="form-group">
                    <label htmlFor="text">內容：</label>
                    <textarea id="text" rows="5" cols="50" value={text} onChange={handleTextChange} placeholder="請輸入您的內容..." required></textarea>
                </div>

                {/* File Input */}
                <div className="form-group">
                    <label htmlFor="image">上傳圖片：</label>
                    <input type="file" id="image" accept="image/*" onChange={handleImageChange} required />
                </div>

                {/* 圖片預覽 */}
                {preview && (
                    <div className="image-preview">
                        <p>圖片預覽：</p>
                        <img src={preview} alt="預覽圖片" style={{ maxWidth: "300px", marginTop: "10px" }} />
                    </div>
                )}

                {/* Submit Button */}
                <button type="submit" className="btn btn-primary">
                    上傳
                </button>
            </form>
        </div>
    );
};

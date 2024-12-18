import React from "react";
import { useNavigate } from "react-router-dom";

export const Logout = () => {
    const navigate = useNavigate();

    const handleLogout = () => {
        // 刪除 localStorage 中的使用者資料
        localStorage.removeItem("userId");
        localStorage.removeItem("userName");
        localStorage.removeItem("isSuperadmin");
        localStorage.removeItem("isLogin");

        // 跳轉到登入頁面
        navigate("/"); // 或者跳轉到首頁 "/"，根據需要調整
    };

    return (
        <div className="container mt-5">
            <h2>登出</h2>
            <p>確定要登出嗎？</p>
            <button className="btn btn-danger" onClick={handleLogout}>
                登出
            </button>
        </div>
    );
};

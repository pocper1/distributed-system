import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext"; // 假設有 AuthContext 管理登入狀態

export const Login = () => {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState(null);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const navigate = useNavigate(); // 初始化 navigate
    const { login } = useAuth(); // 從 AuthContext 取得 login 方法

    // 處理提交表單
    const handleSubmit = async e => {
        e.preventDefault();
        setError(null); // 清空錯誤訊息
        setIsSubmitting(true);

        try {
            const response = await fetch(`${process.env.REACT_APP_API_URL}/api/user/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                // 判斷伺服器返回的錯誤訊息
                const errorMessage = Array.isArray(errorData.detail) ? errorData.detail.map(item => `${item.msg} (Field: ${item.loc[1]})`).join(", ") : errorData.detail || "登入失敗，請稍後再試";

                throw new Error(errorMessage);
            }

            const data = await response.json();
            console.log("Login success:", data);

            // 調用 Context 保存登入狀態
            login(data.auth_token, data.username);
            alert("登入成功！");

            // 重導向首頁
            navigate("/");
        } catch (err) {
            console.error("Login error:", err.message);
            setError(err.message); // 設置錯誤訊息
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div id="login" className="container">
            <div className="row justify-content-center mt-5">
                <div className="col-md-6">
                    <div className="form-container">
                        <h2 className="text-center">登入</h2>
                        {/* 顯示錯誤訊息 */}
                        {error && <div className="alert alert-danger">{error}</div>}
                        <form onSubmit={handleSubmit}>
                            <div className="form-group">
                                <label htmlFor="email">Email:</label>
                                <input type="email" id="email" className="form-control" value={email} onChange={e => setEmail(e.target.value)} required />
                            </div>
                            <div className="form-group mt-3">
                                <label htmlFor="password">Password:</label>
                                <input type="password" id="password" className="form-control" value={password} onChange={e => setPassword(e.target.value)} required />
                            </div>
                            <button type="submit" className="btn btn-primary w-100 mt-4" disabled={isSubmitting}>
                                {isSubmitting ? "登入中..." : "登入"}
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
};

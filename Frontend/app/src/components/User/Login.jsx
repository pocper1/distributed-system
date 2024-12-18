import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

export const Login = () => {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState(null);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async e => {
        e.preventDefault();
        setError(null);
        setIsSubmitting(true);

        try {
            const response = await fetch(`${process.env.REACT_APP_API_URL}/api/user/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "登入失敗");
            }

            const data = await response.json();
            console.log("Login success:", data);

            // 儲存 userId, userName 和 isSuperadmin 到 localStorage
            localStorage.setItem("userId", data.user_id); // 儲存 userId
            localStorage.setItem("userName", data.username);
            localStorage.setItem("isSuperadmin", data.is_superadmin);
            localStorage.setItem("isLogin", data.is_login);

            // 登入成功，導向首頁
            alert("登入成功！");
            navigate("/"); // 重導向首頁
        } catch (err) {
            console.error("Login error:", err.message);
            setError(err.message);
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="container mt-5">
            <h2 className="text-center">登入</h2>
            {error && <div className="alert alert-danger">{error}</div>}
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="email">Email</label>
                    <input type="email" id="email" className="form-control" value={email} onChange={e => setEmail(e.target.value)} required />
                </div>
                <div className="form-group mt-3">
                    <label htmlFor="password">Password</label>
                    <input type="password" id="password" className="form-control" value={password} onChange={e => setPassword(e.target.value)} required />
                </div>
                <button type="submit" className="btn btn-primary w-100 mt-4" disabled={isSubmitting}>
                    {isSubmitting ? "登入中..." : "登入"}
                </button>
            </form>
        </div>
    );
};

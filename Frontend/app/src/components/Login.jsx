import React, { useState } from "react";

export const Login = ({ onLogin }) => {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const handleSubmit = (e) => {
        e.preventDefault();
        const mockUserName = email.split("@")[0]; // 假設使用 Email 的名稱作為使用者名稱
        console.log("Login data:", { email, password });
        alert("登入成功！");
        onLogin(mockUserName); // 傳遞使用者名稱給父元件
    };

    return (
        <div id="login" className="container">
            <div className="row">
                <div className="col-md-6 col-md-offset-3">
                    <div className="form-container">
                        <h2>Login</h2>
                        <form onSubmit={handleSubmit}>
                            <div className="form-group">
                                <label htmlFor="email">Email:</label>
                                <input
                                    type="email"
                                    id="email"
                                    className="form-control"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label htmlFor="password">Password:</label>
                                <input
                                    type="password"
                                    id="password"
                                    className="form-control"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                />
                            </div>
                            <button type="submit" className="btn btn-primary">
                                Login
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
};
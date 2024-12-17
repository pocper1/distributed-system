import React, { useState } from "react";

export const Register = () => {
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [error, setError] = useState(null); // 用於顯示錯誤訊息
    const [success, setSuccess] = useState(null); // 用於顯示成功訊息

    const handleSubmit = async e => {
        e.preventDefault();
        setError(null); // 清除前一次錯誤
        setSuccess(null);

        if (password !== confirmPassword) {
            setError("密碼不一致！");
            return;
        }

        try {
            const response = await fetch(`${process.env.REACT_APP_API_URL}/api/user/register`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    username: name,
                    email: email,
                    password: password,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();

                // Check if errorData.detail is an array before using .map
                const errorMessage = Array.isArray(errorData.detail) ? errorData.detail.map(item => `${item.msg} (Field: ${item.loc[1]})`).join(", ") : errorData.detail || "註冊失敗，請稍後再試";

                throw new Error(errorMessage);
            }

            const data = await response.json();
            setSuccess(data.message || "註冊成功！");
            console.log("Register success:", data);
        } catch (err) {
            console.error("Register error:", err);
            setError(err.message || "註冊時發生錯誤，請稍後再試");
        }
    };

    return (
        <div id="register" className="container">
            <div className="row">
                <div className="col-md-6 col-md-offset-3">
                    <div className="form-container">
                        <h2>Register</h2>

                        {/* 錯誤訊息 */}
                        {error && <div className="alert alert-danger">{error}</div>}

                        {/* 成功訊息 */}
                        {success && <div className="alert alert-success">{success}</div>}

                        <form onSubmit={handleSubmit}>
                            <div className="form-group">
                                <label htmlFor="name">Name:</label>
                                <input type="text" id="name" className="form-control" value={name} onChange={e => setName(e.target.value)} required />
                            </div>
                            <div className="form-group">
                                <label htmlFor="email">Email:</label>
                                <input type="email" id="email" className="form-control" value={email} onChange={e => setEmail(e.target.value)} required />
                            </div>
                            <div className="form-group">
                                <label htmlFor="password">Password:</label>
                                <input type="password" id="password" className="form-control" value={password} onChange={e => setPassword(e.target.value)} required />
                            </div>
                            <div className="form-group">
                                <label htmlFor="confirmPassword">Confirm Password:</label>
                                <input type="password" id="confirmPassword" className="form-control" value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} required />
                            </div>
                            <button type="submit" className="btn btn-primary">
                                Register
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
};

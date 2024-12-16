import React, { useState } from "react";

export const Register = () => {
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");

    const handleSubmit = e => {
        e.preventDefault();
        if (password !== confirmPassword) {
            alert("密碼不一致！");
            return;
        }
        // 模擬提交到後端
        console.log("Register data:", { name, email, password });
        alert("註冊成功！");
    };

    return (
        <div id="register" className="container">
            <div className="row">
                <div className="col-md-6 col-md-offset-3">
                    <div className="form-container">
                        <h2>Register</h2>
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

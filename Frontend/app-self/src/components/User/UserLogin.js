import React, { useState } from "react";

function UserLogin() {
    const [form, setForm] = useState({ email: "", password: "" });
    const [loginMessage, setLoginMessage] = useState("");

    const handleChange = e => {
        setForm({ ...form, [e.target.name]: e.target.value });
    };

    const handleSubmit = async e => {
        e.preventDefault();
        try {
            const response = await fetch("/api/user/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(form),
            });
            const data = await response.json();
            if (response.ok) {
                setLoginMessage(`Login successful! User ID: ${data.user_id}`);
            } else {
                setLoginMessage(data.detail || "Login failed");
            }
        } catch (error) {
            setLoginMessage("An error occurred during login");
        }
    };

    return (
        <div>
            <h2>User Login</h2>
            <form onSubmit={handleSubmit}>
                <div className="mb-3">
                    <label htmlFor="email" className="form-label">
                        Email
                    </label>
                    <input type="email" name="email" className="form-control" value={form.email} onChange={handleChange} required />
                </div>
                <div className="mb-3">
                    <label htmlFor="password" className="form-label">
                        Password
                    </label>
                    <input type="password" name="password" className="form-control" value={form.password} onChange={handleChange} required />
                </div>
                <button type="submit" className="btn btn-primary">
                    Login
                </button>
            </form>
            {loginMessage && <p className="mt-3">{loginMessage}</p>}
        </div>
    );
}

export default UserLogin;

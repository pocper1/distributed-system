import React, { useState } from "react";

function UserCheckin() {
    const [form, setForm] = useState({ user_id: "" });
    const [message, setMessage] = useState("");

    const handleChange = e => {
        setForm({ ...form, [e.target.name]: e.target.value });
    };

    const handleSubmit = async e => {
        e.preventDefault();
        try {
            const response = await fetch("/api/checkin", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(form),
            });
            const data = await response.json();
            if (response.ok) {
                setMessage(data.message);
            } else {
                setMessage(data.detail || "Check-in failed");
            }
        } catch (error) {
            setMessage("An error occurred during check-in");
        }
    };

    return (
        <div>
            <h2>User Check-in</h2>
            <form onSubmit={handleSubmit}>
                <div className="mb-3">
                    <label htmlFor="user_id" className="form-label">
                        User ID
                    </label>
                    <input type="text" name="user_id" className="form-control" value={form.user_id} onChange={handleChange} required />
                </div>
                <button type="submit" className="btn btn-primary">
                    Check-in
                </button>
            </form>
            {message && <p className="mt-3">{message}</p>}
        </div>
    );
}

export default UserCheckin;

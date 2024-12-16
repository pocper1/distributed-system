import React, { useState } from "react";

function UpdateScore() {
    const [form, setForm] = useState({ user_id: "", value: "" });
    const [message, setMessage] = useState("");

    const handleChange = e => {
        setForm({ ...form, [e.target.name]: e.target.value });
    };

    const handleSubmit = async e => {
        e.preventDefault();
        try {
            const response = await fetch("/api/score/update", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(form),
            });
            const data = await response.json();
            if (response.ok) {
                setMessage(data.message);
            } else {
                setMessage(data.detail || "Score update failed");
            }
        } catch (error) {
            setMessage("An error occurred while updating the score");
        }
    };

    return (
        <div>
            <h2>Update Score</h2>
            <form onSubmit={handleSubmit}>
                <div className="mb-3">
                    <label htmlFor="user_id" className="form-label">
                        User ID
                    </label>
                    <input type="text" name="user_id" className="form-control" value={form.user_id} onChange={handleChange} required />
                </div>
                <div className="mb-3">
                    <label htmlFor="value" className="form-label">
                        Score Value
                    </label>
                    <input type="number" name="value" className="form-control" value={form.value} onChange={handleChange} required />
                </div>
                <button type="submit" className="btn btn-primary">
                    Update Score
                </button>
            </form>
            {message && <p className="mt-3">{message}</p>}
        </div>
    );
}

export default UpdateScore;

import React, { useState } from "react";

function TeamCreate() {
    const [form, setForm] = useState({ name: "", description: "" });
    const [createMessage, setCreateMessage] = useState("");

    const handleChange = e => {
        setForm({ ...form, [e.target.name]: e.target.value });
    };

    const handleSubmit = async e => {
        e.preventDefault();
        try {
            const response = await fetch("/api/team/create", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(form),
            });
            const data = await response.json();
            if (response.ok) {
                setCreateMessage(`Team created successfully! Team ID: ${data.team_id}`);
            } else {
                setCreateMessage(data.detail || "Team creation failed");
            }
        } catch (error) {
            setCreateMessage("An error occurred while creating the team");
        }
    };

    return (
        <div>
            <h2>Create Team</h2>
            <form onSubmit={handleSubmit}>
                <div className="mb-3">
                    <label htmlFor="name" className="form-label">
                        Team Name
                    </label>
                    <input type="text" name="name" className="form-control" value={form.name} onChange={handleChange} required />
                </div>
                <div className="mb-3">
                    <label htmlFor="description" className="form-label">
                        Description
                    </label>
                    <textarea name="description" className="form-control" value={form.description} onChange={handleChange} required></textarea>
                </div>
                <button type="submit" className="btn btn-primary">
                    Create
                </button>
            </form>
            {createMessage && <p className="mt-3">{createMessage}</p>}
        </div>
    );
}

export default TeamCreate;

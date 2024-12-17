import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Dropdown, Nav, Navbar, Container } from "react-bootstrap";

export const Navigation = ({ onLogout }) => {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [userName, setUserName] = useState("");

    useEffect(() => {
        const checkUserName = () => {
            const storedUserName = localStorage.getItem("userName");
            if (storedUserName) {
                setIsLoggedIn(true);
                setUserName(storedUserName);
            } else {
                setIsLoggedIn(false);
                setUserName("");
            }
        };

        // Initial check
        checkUserName();

        // Set an interval to check the localStorage for changes
        const interval = setInterval(checkUserName, 1000);

        // Clean up the interval on component unmount
        return () => clearInterval(interval);
    }, []);

    const handleLogout = () => {
        localStorage.removeItem("userName");
        setIsLoggedIn(false);
        setUserName("");
        if (onLogout) {
            onLogout();
        }
    };

    return (
        <Navbar bg="light" expand="lg" fixed="top">
            <Container>
                <Navbar.Brand as={Link} to="/">行銷活動</Navbar.Brand>
                <Navbar.Toggle aria-controls="basic-navbar-nav" />
                <Navbar.Collapse id="basic-navbar-nav">
                    <Nav className="ms-auto">
                        {isLoggedIn ? (
                            <>
                                <Nav.Link as={Link} to="/event/list">活動列表</Nav.Link>
                                <Dropdown>
                                    <Dropdown.Toggle variant="light" id="dropdown-user-info">
                                        {userName || "用戶"}
                                    </Dropdown.Toggle>
                                    <Dropdown.Menu>
                                        <Dropdown.Item as={Link} to="/user/info">個人資料</Dropdown.Item>
                                        <Dropdown.Item onClick={handleLogout} style={{ cursor: "pointer" }}>
                                            登出
                                        </Dropdown.Item>
                                    </Dropdown.Menu>
                                </Dropdown>
                            </>
                        ) : (
                            <>
                                <Nav.Link as={Link} to="/login">登入</Nav.Link>
                                <Nav.Link as={Link} to="/register">註冊</Nav.Link>
                            </>
                        )}
                    </Nav>
                </Navbar.Collapse>
            </Container>
        </Navbar>
    );
};
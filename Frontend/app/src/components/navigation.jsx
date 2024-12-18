import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Dropdown, Nav, Navbar, Container } from "react-bootstrap";

export const Navigation = ({ onLogout }) => {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [userName, setUserName] = useState("");
    const [isSuperuser, setIsSuperuser] = useState(false); // 新增 isSuperuser 狀態

    useEffect(() => {
        const checkUserName = () => {
            const storedUserName = localStorage.getItem("userName");
            const superadmin = localStorage.getItem("isSuperadmin");

            if (storedUserName) {
                setIsLoggedIn(true);
                setUserName(storedUserName);
                setIsSuperuser(superadmin === "true"); // 根據 localStorage 設定 isSuperuser
            } else {
                setIsLoggedIn(false);
            }
        };

        // 初始檢查
        checkUserName();

        // 設定定時器定期檢查 localStorage 變化
        const interval = setInterval(checkUserName, 1000);

        // 清理定時器
        return () => clearInterval(interval);
    }, []);

    const handleLogout = () => {
        localStorage.removeItem("userName");
        localStorage.removeItem("isSuperadmin");
        setIsLoggedIn(false);
        setIsSuperuser(false);
        setUserName("");
        if (onLogout) {
            onLogout();
        }
    };

    const userId = localStorage.getItem("userId");  // 獲取 userId

    return (
        <Navbar bg="light" expand="lg" fixed="top">
            <Container>
                <Navbar.Brand as={Link} to="/">
                    行銷活動
                </Navbar.Brand>
                <Navbar.Toggle aria-controls="basic-navbar-nav" />
                <Navbar.Collapse id="basic-navbar-nav">
                    <Nav className="ms-auto">
                        {isLoggedIn ? (
                            <>
                                <Nav.Link as={Link} to="/event/list">
                                    活動列表
                                </Nav.Link>
                                {isSuperuser && (
                                    <Nav.Link as={Link} to="/create-event">
                                        創建活動
                                    </Nav.Link> // 只有超級管理員顯示此按鈕
                                )}
                                <Dropdown>
                                    <Dropdown.Toggle variant="light" id="dropdown-user-info">
                                        {userName || "用戶"}
                                    </Dropdown.Toggle>
                                    <Dropdown.Menu>
                                        <Dropdown.Item as={Link} to={`/user/info/${userId}`}>
                                            個人資料
                                        </Dropdown.Item>
                                        <Dropdown.Item onClick={handleLogout} style={{ cursor: "pointer" }}>
                                            登出
                                        </Dropdown.Item>
                                    </Dropdown.Menu>
                                </Dropdown>
                            </>
                        ) : (
                            <>
                                <Nav.Link as={Link} to="/login">
                                    登入
                                </Nav.Link>
                                <Nav.Link as={Link} to="/register">
                                    註冊
                                </Nav.Link>
                            </>
                        )}
                    </Nav>
                </Navbar.Collapse>
            </Container>
        </Navbar>
    );
};
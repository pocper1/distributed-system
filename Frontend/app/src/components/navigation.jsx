import React from "react";
import { Link } from "react-router-dom";
import { Dropdown, Nav, Navbar, Container } from "react-bootstrap";

export const Navigation = ({ isLoggedIn, userName, onLogout }) => {
    return (
        <Navbar bg="light" expand="lg" fixed="top">
            <Container>
                {/* Navbar Brand */}
                <Navbar.Brand as={Link} to="/">
                    行銷活動
                </Navbar.Brand>
                <Navbar.Toggle aria-controls="basic-navbar-nav" />
                <Navbar.Collapse id="basic-navbar-nav">
                    <Nav className="ms-auto">
                        {isLoggedIn ? (
                            <>
                                {/* Event List */}
                                <Nav.Link as={Link} to="/event/list">
                                    活動列表
                                </Nav.Link>

                                {/* User Info Dropdown */}
                                <Dropdown>
                                    <Dropdown.Toggle variant="light" id="dropdown-user-info">
                                        {userName}
                                    </Dropdown.Toggle>
                                    <Dropdown.Menu>
                                        <Dropdown.Item as={Link} to="/user/info">
                                            個人資料
                                        </Dropdown.Item>
                                        <Dropdown.Item onClick={onLogout} style={{ cursor: "pointer" }}>
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
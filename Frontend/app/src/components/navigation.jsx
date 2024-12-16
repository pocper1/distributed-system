import React from "react";
import { Link } from "react-router-dom";

export const Navigation = ({ isLoggedIn, userName, onLogout }) => {
    return (
        <nav id="menu" className="navbar navbar-default navbar-fixed-top">
            <div className="container">
                <div className="navbar-header">
                    <button
                        type="button"
                        className="navbar-toggle collapsed"
                        data-toggle="collapse"
                        data-target="#bs-example-navbar-collapse-1"
                    >
                        {" "}
                        <span className="sr-only">Toggle navigation</span>{" "}
                        <span className="icon-bar"></span>{" "}
                        <span className="icon-bar"></span>{" "}
                        <span className="icon-bar"></span>{" "}
                    </button>
                    <Link className="navbar-brand page-scroll" to="/">
                        行銷活動
                    </Link>
                </div>

                <div
                    className="collapse navbar-collapse"
                    id="bs-example-navbar-collapse-1"
                >
                    <ul className="nav navbar-nav navbar-right">
                        {isLoggedIn ? (
                            <>
                                {/* 使用者名稱 */}
                                <li>
                                    <button className="btn btn-link navbar-btn">
                                        Hi, {userName}
                                    </button>
                                </li>

                                {/* User Status */}
                                <li>
                                    <Link to="/user-status" className="page-scroll">
                                        User Status
                                    </Link>
                                </li>

                                {/* User Info */}
                                <li>
                                    <Link to="/user-info" className="page-scroll">
                                        User Info
                                    </Link>
                                </li>

                                {/* Team Info */}
                                <li>
                                    <Link to="/team-info" className="page-scroll">
                                        Team Info
                                    </Link>
                                </li>

                                {/* Logout */}
                                <li>
                                    <button
                                        className="btn btn-link navbar-btn page-scroll"
                                        onClick={onLogout}
                                    >
                                        Logout
                                    </button>
                                </li>
                            </>
                        ) : (
                            <>
                                <li>
                                    <Link to="/login" className="page-scroll">
                                        Login
                                    </Link>
                                </li>
                                <li>
                                    <Link to="/register" className="page-scroll">
                                        Register
                                    </Link>
                                </li>
                            </>
                        )}
                    </ul>
                </div>
            </div>
        </nav>
    );
};
import React, { createContext, useState, useContext } from "react";

// 建立 Context
const AuthContext = createContext();

// 提供者元件 (供應全局狀態)
export const AuthProvider = ({ children }) => {
    const [authToken, setAuthToken] = useState(null);
    const [username, setUsername] = useState(null);

    const login = (token, user) => {
        setAuthToken(token);
        setUsername(user);
    };

    const logout = () => {
        setAuthToken(null);
        setUsername(null);
    };

    return <AuthContext.Provider value={{ authToken, username, login, logout }}>{children}</AuthContext.Provider>;
};

// 建立一個 Hook 來方便使用 AuthContext
export const useAuth = () => {
    return useContext(AuthContext);
};

import React from "react";

export const LandingPage = () => {
    return (
        <div id="landing-page" className="container">
            <div className="row">
                <div className="col-md-12 text-center">
                    <h1>歡迎來到行銷活動</h1>
                    <p>
                        透過揪團、打卡、分享，快速提升品牌知名度！立即加入我們的活動，
                        體驗全新的互動方式，並贏取豐厚獎勵。
                    </p>
                    <a href="/register" className="btn btn-primary btn-lg">
                        立即註冊
                    </a>
                    <a href="/login" className="btn btn-secondary btn-lg" style={{ marginLeft: "10px" }}>
                        登入
                    </a>
                </div>
            </div>
        </div>
    );
};
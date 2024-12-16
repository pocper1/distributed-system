import React from "react";

export const Header = (props) => {
  return (
    <header id="header">
      <div className="intro">
        <div className="overlay">
          <div className="container">
            <div className="row">
              <div className="col-md-8 col-md-offset-2 intro-text">
                <h1>
                  {props.data ? props.data.title : "Loading"}
                  <span></span>
                </h1>
                <p>{props.data ? props.data.paragraph : "Loading"}</p>
                <div className="header-buttons">
                  <a href="#team" className="btn btn-custom btn-lg page-scroll">
                    Team
                  </a>
                  <a
                    href="#register"
                    className="btn btn-custom btn-lg page-scroll"
                  >
                    Register
                  </a>
                  <a href="#login" className="btn btn-custom btn-lg page-scroll">
                    Login
                  </a>
                  <a
                    href="#ranking"
                    className="btn btn-custom btn-lg page-scroll"
                  >
                    積分排行
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
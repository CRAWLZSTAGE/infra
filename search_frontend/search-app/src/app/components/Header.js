import React from "react";

export const Header = (props) => {
    return (
        <nav className="navbar navbar-default">
            <div className="container">
                <div className="navbar-header">
                    <ul className="nav navbar-nav">
                        <li><a href="http://crawlz.me">Home</a></li>
                        <li><a href="http://crawlz.me/stats">Settings</a></li>
                        <li><a href="https://github.com/crawlzstage">Github</a></li>
                    </ul>
                </div>
            </div>
        </nav>
    );
}
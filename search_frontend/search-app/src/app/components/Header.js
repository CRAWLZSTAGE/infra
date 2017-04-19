import React from "react";

const headerItemStyle = {
  "padding-left": "30px"
};

export const Header = (props) => {
    return (
        <nav className="navbar navbar-default">
            <div className="container">
                <div className="navbar-header">
                    <ul className="nav navbar-nav">
                        <li><a href="https://crawlz.me" style={headerItemStyle}>Home</a></li>
                        <li><a href="https://rabbitmq.crawlz.me" style={headerItemStyle}>RabbitMQ</a></li>
                        <li><a href="https://prometheus.crawlz.me" style={headerItemStyle}>Prometheus</a></li>
                        <li><a href="https://grafana.crawlz.me" style={headerItemStyle}>Grafana</a></li>
                        <li><a href="https://github.com/crawlz" style={headerItemStyle}>Github</a></li>
                    </ul>
                </div>
            </div>
        </nav>
    );
}


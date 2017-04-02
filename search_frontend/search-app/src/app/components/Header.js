import React from "react";

export const Header = (props) => {
    return (
        <nav className="navbar navbar-default">
            <div className="container">
                <div className="navbar-header">
                    <ul className="nav navbar-nav">
                        <li><a href="https://crawlz.me">Home</a></li>
                        <li><a href="https://rabbitmq.crawlz.me">RabbitMQ</a></li>
                        <li><a href="https://prometheus.crawlz.me">Prometheus</a></li>
                        <li><a href="https://grafana.crawlz.me">Grafana</a></li>
                        <li><a href="https://github.com/crawlz">Github</a></li>
                    </ul>
                </div>
            </div>
        </nav>
    );
}
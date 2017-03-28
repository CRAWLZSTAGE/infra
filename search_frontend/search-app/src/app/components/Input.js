import React from "react";

export class Input extends React.Component {
    constructor(props) {
        super(props);

        this.state = {inputValue: 'Input Query Here'};
    }

    queryBackend(event) {
        var component = this; //required in promise
        fetch('http://backend.crawlz.me/api/fastSearch/' + event.target.value, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
          }
        }).then(function(response) {
            response.json().then(function(json) {
                component.props.setSettingsHandler(json);
            });
        });
        this.setState({inputValue: event.target.value});
    }

    keyUp(event){
        if (event.key == 'Enter'){
            var component = this; //required in promise
            fetch('http://backend.crawlz.me/api/search/' + event.target.value, {
              method: 'GET',
              headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
              }
            }).then(function(response) {
                response.json().then(function(json) {
                    component.props.setSettingsHandler(json);
                });
            });
        }
    }

    render() {
        return (
            <div className="col-xs-10 col-xs-offset-1 form-group row">
                <input className="form-control" value={this.state.inputValue} type="search" 
                    onChange={this.queryBackend.bind(this)}
                    onKeyDown={this.keyUp.bind(this)} 
                    id="searchInput" rows="1">
                </input>
            </div>
        );
    }
}
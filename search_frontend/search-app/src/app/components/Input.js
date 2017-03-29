import React from "react";
import 'whatwg-fetch'; // safari does not have "fetch" function -> http://stackoverflow.com/questions/35830202/fetch-not-defined-in-safari-referenceerror-cant-find-variable-fetch

export class Input extends React.Component {
    constructor(props) {
        super(props);

        this.state = {inputValue: 'Input Query Here'};
    }

    queryBackend(event) {
        var component = this; //required in promise
        if (event.target.value == ""){
            this.setState({inputValue: event.target.value});
            component.props.setSettingsHandler({});
            return
        }
        fetch('https://backend.crawlz.me/api/fastSearch/' + event.target.value, {
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
            if (event.target.value == ""){
                this.setState({inputValue: event.target.value});
                component.props.setSettingsHandler({});
                return
            }
            var locationTrailer = ""
            if (localStorage.lat && localStorage.lon){
                locationTrailer = locationTrailer + "?lat=" + String(localStorage.lat) + "&lon=" + String(localStorage.lon)
            }
            fetch('https://backend.crawlz.me/api/search/' + event.target.value + locationTrailer, {
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
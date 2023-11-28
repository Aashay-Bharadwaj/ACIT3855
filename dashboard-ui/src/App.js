import logo from './logo.png';
import './App.css';
import HealthStats from './components/HealthStats'
import EndpointAudit from './components/EndpointAudit'
import AppStats from './components/AppStats'

function App() {

    const endpoints = ["inventory-item", "standard-order"]

    const rendered_endpoints = endpoints.map((endpoint) => {
        return <EndpointAudit key={endpoint} endpoint={endpoint}/>
    })
    return (
        <div className="App">
            <img src={logo} className="App-logo" alt="logo" height="250px" width="300px"/>
            <div>
                <AppStats/>
                <h1>Audit Endpoints</h1>
                {rendered_endpoints}
                <h1>Health</h1>
                <HealthStats/>
            </div>
        </div>
    );

}



export default App;

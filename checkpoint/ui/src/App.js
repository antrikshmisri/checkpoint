import React from "react";
import { HashRouter as Router, Switch, Route } from "react-router-dom";
import { Toaster } from "react-hot-toast"
import { eel } from "./eel.js";
import Splash from "./routes/Splash";
import Home from "./routes/Home";

function App() {
  eel.set_host("http://localhost:8888");
  return (
    <Router>
      <div className="App">
        <Switch>
          <Route path="/" exact component={Splash} />
          <Route path="/home" exact component={Home} />
        </Switch>
      </div>
      <Toaster />
    </Router>
  );
}
export default App;

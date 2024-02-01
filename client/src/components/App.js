import React, { useState, useEffect } from "react";
import { Switch, Route } from "react-router-dom";
import Article from "./Article";
import Header from "./Header";
import Home from "./Home";
import Login from "./Login";

function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Check session on component mount
    fetch("/check_session")
      .then((response) => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error("User not authenticated");
        }
      })
      .then((user) => setUser(user))
      .catch((error) => {
        // Handle unauthorized or session check failure
        console.error("Session check failed:", error);
        setUser(null);
      });
  }, []);

  function handleLogin(username) {
    // Perform login request
    fetch("/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username }),
    })
      .then((response) => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error("Login failed");
        }
      })
      .then((user) => setUser(user))
      .catch((error) => {
        // Handle login failure
        console.error("Login failed:", error);
        setUser(null);
      });
  }

  function handleLogout() {
    // Perform logout request
    fetch("/logout", {
      method: "DELETE",
    })
      .then(() => setUser(null))
      .catch((error) => {
        // Handle logout failure
        console.error("Logout failed:", error);
      });
  }

  return (
    <div className="App">
      <Header user={user} onLogout={handleLogout} />
      <Switch>
        <Route exact path="/articles/:id">
          <Article />
        </Route>
        <Route exact path="/login">
          <Login onLogin={handleLogin} />
        </Route>
        <Route exact path="/">
          <Home />
        </Route>
      </Switch>
    </div>
  );
}

export default App;

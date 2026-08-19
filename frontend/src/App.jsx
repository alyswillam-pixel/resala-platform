import React, { useState } from "react";
import Login from "./pages/Login";
import Home from "./pages/home";

function App() {
  const [currentPage, setCurrentPage] = useState("login"); // "login" | "home"
  const [userAuth, setUserAuth] = useState(null);

  const handleLoginSuccess = (authData) => {
    setUserAuth(authData);
    setCurrentPage("home");
  };

  if (currentPage === "login") {
    return (
      <Login
        onLoginSuccess={handleLoginSuccess}
        onBackToHome={() => setCurrentPage("home")}
      />
    );
  }

  return (
    <Home
      userAuth={userAuth}
      onNavigateToLogin={() => setCurrentPage("login")}
    />
  );
}

export default App;
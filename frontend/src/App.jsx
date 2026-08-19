import { useState } from "react";
import LoginForm from "./pages/LoginForm";
import Home from "./pages/home";

function App() {
  const [currentPage, setCurrentPage] = useState("login");
  const [userAuth, setUserAuth] = useState(null);

  const handleLoginSuccess = (authData) => {
    setUserAuth(authData);
    setCurrentPage("home");
  };

  if (currentPage === "login") {
    return (
      <LoginForm
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

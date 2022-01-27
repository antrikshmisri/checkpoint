import React from "react";
import About from "./components/About";
import CTA from "./components/CTA";
import Footer from "./components/Footer";
import Header from "./components/Header";
import Navigation from "./components/Navigation";

function App() {
  return (
    <React.Fragment>
      <nav>
        <Navigation />
      </nav>
      <header>
        <Header />
      </header>
      <main>
        <About />
        <CTA />
      </main>
      <footer>
        <Footer />
      </footer>
    </React.Fragment>
  );
}

export default App;

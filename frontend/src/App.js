import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Identify from "./pages/Identify";
import Explore from "./pages/Explore";
import About from "./pages/About";
import "./App.css";

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/identify" element={<Identify />} />
        <Route path="/explore" element={<Explore />} />
        <Route path="/about" element={<About />} />
      </Routes>
    </BrowserRouter>
  );
}
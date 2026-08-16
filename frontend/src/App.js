import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Identify from "./pages/Identify";
import Explore from "./pages/Explore";
import Map from "./pages/Map";
import MonumentDetail from "./pages/MonumentDetail";
import About from "./pages/About";
import "./App.css";
import AR from "./pages/AR";
import './mobile.css';
export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/identify" element={<Identify />} />
        <Route path="/explore" element={<Explore />} />
        <Route path="/map" element={<Map />} />
        <Route path="/monument/:id" element={<MonumentDetail />} />
        <Route path="/about" element={<About />} />
        <Route path="/ar" element={<AR />} />
      </Routes>
    </BrowserRouter>
  );
}

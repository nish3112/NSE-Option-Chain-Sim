import React, { useState } from "react";
import "./navbar.css";
import {
  FaGithub,
  FaLinkedin,
  FaReadme,
  FaWrench
} from "react-icons/fa";
import logo from "./assets/NSE.png";
import overlayImage from "./assets/overlayImage.png"; // Import the overlay image

import { NavLink } from "react-router-dom";

const Navbar = () => {
  const [showOverlay, setShowOverlay] = useState(false);
  const [showMediaIcons, setShowMediaIcons] = useState(false);

  const handleOverlayToggle = () => {
    setShowOverlay(!showOverlay);
  };

  const handleOverlayClose = () => {
    setShowOverlay(false);
  };

  return (
    <>
      <nav className="main-nav">
        <div className="logo">
          <img src={logo} alt="Logo" />
        </div>

        <div
          className={
            showMediaIcons ? "menu-link mobile-menu-link" : "menu-link"
          }>
          <ul>
            <li>
              <NavLink to="/" className="active-link">Market Data</NavLink>
            </li>
            <li>
              <NavLink to="https://drive.google.com/file/d/1stqKPE552GgK6_DBi6_OU5c6MDHNvJ-o/view?usp=sharing">Resume</NavLink>
            </li>
            <li>
              <NavLink to="mailto:tnishith9123@gmail.com">Contact</NavLink>
            </li>
          </ul>
        </div>

        {/* 3rd social media links */}
        <div className="social-media">
           <ul className="social-media-desktop">
             <li>
               <a
                href="https://github.com/nish3112/">
                <FaGithub className="github" />
              </a>
            </li>
            <li>
              <a
                href="https://www.linkedin.com/in/nishith-thakker/">
                <FaLinkedin className="linkedin" />
              </a>
            </li>
            <li>
              <a
                href="">
                <FaReadme className="caution" />
              </a>
            </li>
            <li>
              <div className="wrench-icon" onClick={handleOverlayToggle}>
                <FaWrench className="working" />
              </div>
            </li>
          </ul>
        </div>
      </nav>

      {/* Wrench icon in the navbar */}
      

      {/* Overlay */}
      {showOverlay && (
        <div className="overlay-background" onClick={handleOverlayClose}>
          <img src={overlayImage} alt="Overlay" className="overlay-image" />
        </div>
      )}

      {/* ... rest of your content ... */}
    </>
  );
};

export default Navbar;

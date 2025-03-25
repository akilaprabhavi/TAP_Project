import React from 'react';
import './sidenav.css';
import logo from "../../../assets/images/logo.png"; 

const SideNav = ({ menuItems, allCategoryChange }) => {
    return (
      <div id="sidebar" className="sidenav">
        <div className="sidebar-header">
          <div className="logo-container">
            <img src={logo} alt="Logo" className="sidebar-logo" />
          </div>
          <p className="custom-header m-0">Attack Lens</p>
          <p className="fst-normal m-0">Cyber Threat Intelligence at Your Fingertips</p>
        </div>
        <nav className="navbar p-0">
          <ul className="navbar-item">
            {menuItems.map((menuItem, index) => (
              <li key={index}>
                <a href={menuItem.link}>{menuItem.label}</a>
              </li>
            ))}
          </ul>
        </nav>
      </div>
    );
};
  
export default SideNav;
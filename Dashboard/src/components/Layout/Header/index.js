import React, { useState } from 'react';
import './header.css'

function Header() {
  const [isSidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    setSidebarOpen(!isSidebarOpen);
  };

  return (
    <div className="header-class">
      <div className="col-sm-12 col-12">
        <div className="header-sidenav">
          <button className="menu-button navbar-toggler" type="button" data-bs-toggle="offcanvas" data-bs-target="#sidebar" onClick={toggleSidebar}>
            <i className="fas fa-bars"></i>
          </button>
        </div>
        <div className="header-nav">
          <div className="col-sm-12 col-12 hn-center d-flex justify-content-end">
            <i class="fas fa-search"></i>
            <div class="w3-dropdown-hover w3-right">
              <button class="w3-button"><i class="far fa-user"></i></button>
              <div class="w3-dropdown-content w3-bar-block w3-border" style={{right:0}}>
                <a href="#" class="w3-bar-item w3-button">Email Subscriptions</a>
                <a href="#" class="w3-bar-item w3-button">Profile</a>
                <a href="#" class="w3-bar-item w3-button">Saved Articles</a>
                <a href="#" class="w3-bar-item w3-button">Sign Out</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
  );
}

export default Header;

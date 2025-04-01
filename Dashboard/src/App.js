import React, { Component } from "react";
import Header from './components/Layout/Header'; 
import SideNav from "./components/Layout/SideNav";
import Content from "./components/Layout/Content";
import './App.css';
import Fullpage from "./components/Layout/FullPage";
import { FaHome, FaChartLine, FaCog, FaHistory } from "react-icons/fa";
import { AiOutlineSchedule } from "react-icons/ai";
import { MdAddToPhotos } from "react-icons/md";
 
class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      isAllCategory: false,
    };
  }

  menuItems = [
      { label: <><FaHome /> Dashboard</>, link: '/' },
      { label: <><MdAddToPhotos /> Daily Updates</>, link: '/dailyUpdates' },
      { label: <><AiOutlineSchedule /> Attack Vectors</>,link: '/attackVectors' },
      { label: <><FaHistory /> History</>, link: '/history' },
      { label: <><FaChartLine /> Analytics</>, link: '/analytics' },
      { label: <><FaCog /> Settings</>, link: '/settings' },
    ];

  toggleCategory = () => {
    this.setState((prevState) => ({
      isAllCategory: !prevState.isAllCategory,
    }));
  };
  
  render() {
    const { isAllCategory } = this.state;

    return (
      isAllCategory ? (
        <Fullpage onCloseButtonClick={this.toggleCategory} />
      ) : (
        <div>
          <Header />
          <SideNav menuItems={this.menuItems} allCategoryChange={this.toggleCategory} />
          <Content />          
        </div>
      )
    );
  }
}

export default App;
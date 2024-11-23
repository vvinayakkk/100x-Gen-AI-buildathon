import React from "react";
import "./SideHug.css";
import TwitterPlayground from "../TwitterPlayground/TwitterPlayground";

const SideHug = () => {
  return (
    <div className="sidehug_container">
      <div className="left_sidehug">
        <img className="twitter_logo" src="logo-white.png" alt="twitter logo" />
      </div>
      <div className="right_sidehug">
        <div className="twitter-playground-wrapper">
          <TwitterPlayground />
        </div>
      </div>
    </div>
  );
};

export default SideHug;

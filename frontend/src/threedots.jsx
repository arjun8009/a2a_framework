
import React from 'react';
import CircularProgress from "@mui/material/CircularProgress";
import './threedotsstyle.css'


function ThreeDotsAnimation() {

  return (
    <div className="dots-container" style={{display: 'flex',alignItems: 'center'}}>
      <div className="dots" >
        <div className="dot"></div>
        <div className="dot"></div>
        <div className="dot"></div>
      </div>
    </div>
  );
}

export default ThreeDotsAnimation;
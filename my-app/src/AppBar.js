import React from 'react';

const AppBar = () => {
  return (
    <div style={appBarStyle}>
      <h1 style={{ margin: 0, color: 'white' }}>OMR Reviewer</h1>
    </div>
  );
};

const appBarStyle = {
  backgroundColor: '#2196F3', // You can change the background color to your preference
  padding: '10px',
  textAlign: 'center',
  position: 'fixed',
  top: 0,
  left: 0,
  width: '100%',
  zIndex: 1000, // Ensure the app bar appears above other content
};

export default AppBar;

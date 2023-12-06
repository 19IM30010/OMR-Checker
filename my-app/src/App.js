import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
// import OMRForm from './OMRForm';
import OMRAns from './OMRAns';
import ResultPage from './ResultPage';
import AppBar from './AppBar'; // Import the AppBar component

function App() {
  return (
    <Router>
      <div>
        {/* Add the AppBar component */}
        <AppBar />
        <br></br>
        <br></br>
        <br></br>
        <br></br>

        {/* Define your routes */}
        <Routes>
          {/* <Route path="/" element={<OMRForm />} /> */}
          <Route path="/" element={<OMRAns />} />
          <Route path="/result" element={<ResultPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

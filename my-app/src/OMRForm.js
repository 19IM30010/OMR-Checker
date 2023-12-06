import logo from './logo.svg';
import './App.css';
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';


const OMRForm = () => {
  const [numQuestions, setNumQuestions] = useState(0);
  const navigate = useNavigate();
  const [formData, setFormData] = useState(null);
  const [questionsPerBox, setQuestionsPerBox] = useState(0);
  const [numBoxes, setNumBoxes] = useState(0);
  const [omrTemplate, setOMRTemplate] = useState(null);

  useEffect(() => {
    if (formData) {
      console.log(formData);
      navigate('/result', { state: { formData } });
    }
  }, [formData, navigate]);

  const handleFormSubmit = (e) => {
    e.preventDefault();

    // Process the form data as needed
    const data = {
      numQuestions,
      questionsPerBox,
      numBoxes,
      omrTemplate,
    };

    // Set the formData state
    setFormData(data);
  };

  return (
    <div className="omr-form-container">
      <div className="omr-form-card">
        <h1>OMR Form</h1>
        <form onSubmit={handleFormSubmit}>
          <div>
            <label htmlFor="numQuestions" className="omr-question">No. of Questions</label>
            <input
              type="number"
              className="omr-box"
              id="numQuestions"
              value={numQuestions}
              onChange={(e) => setNumQuestions(e.target.value)}
              required
            />
          </div>

          <div>
            <label htmlFor="questionsPerBox" className="omr-question">Questions per Box</label>
            <input
              type="number"
              className="omr-box"
              id="questionsPerBox"
              value={questionsPerBox}
              onChange={(e) => setQuestionsPerBox(e.target.value)}
              required
            />
          </div>

          <div>
            <label htmlFor="numBoxes" className="omr-question">No. of Boxes</label>
            <input
              className="omr-box"
              type="number"
              id="numBoxes"
              value={numBoxes}
              onChange={(e) => setNumBoxes(e.target.value)}
              required
            />
          </div>

          <div>
            <label htmlFor="omrTemplate" className="omr-question">Upload the OMR Template</label>
            <input
              className="omr-box"
              type="file"
              id="omrTemplate"
              onChange={(e) => setOMRTemplate(e.target.files[0])}
              accept="image/*"
              required
            />
          </div>

          <button type="submit" className="omr-submit-button">Submit</button>
        </form>
      </div>
    </div>
  );
};

export default OMRForm;


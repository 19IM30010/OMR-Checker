// StudentResult.js

import React from 'react';
import './OMRAns.css';

const StudentResult = ({ resultDict, images }) => {
  // Assuming resultDict is an object with question numbers as keys and an object as values
  // The table columns are "Question No.", "Correct Answer", "Written Answer"
  const tableData = Object.entries(resultDict).map(([questionNo, { Correct_ans, Written_ans }]) => ({
    questionNo,
    correctAnswer: Correct_ans,
    writtenAnswer: Written_ans,
  }));

  // Assuming images is an array of image URLs
//   const firstImage = images[0];

  return (
    <div className="result-container">
      <div className="image-container">
      {images.length > 0 && (
        <img
        src={URL.createObjectURL(images[0])}  // Assuming images is a FileList object
        alt="OMR Image"
        className="omr-image"
        style={{
          width: '40vw', // 40% of the viewport width
          height: '100vh', // 40% of the viewport height
          objectFit: 'cover', // This property ensures the image maintains its aspect ratio
        }}
      />
      )}
      </div>
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Question No.</th>
              <th>Correct Answer</th>
              <th>Written Answer</th>
            </tr>
          </thead>
          <tbody>
            {tableData.map((rowData) => (
              <tr key={rowData.questionNo}>
                <td>{rowData.questionNo}</td>
                <td>{rowData.correctAnswer}</td>
                <td>{rowData.writtenAnswer}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default StudentResult;

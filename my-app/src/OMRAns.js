import React, { useState, useEffect } from 'react';
import './OMRAns.css'; // Import your CSS file
import Modal from 'react-modal'; // Import the Modal component
import StudentResult from './StudentResult';
/* index.css or your main CSS file */
// import 'react-modal/style/react-modal.css';


const OMRAns = () => {
  const [images, setImages] = useState([]);
  const [csvFile, setCsvFile] = useState(null);
  const [uniqueIds, setUniqueIds] = useState([]);
  const [selectedUniqueId, setSelectedUniqueId] = useState('');
  const [resultDict, setResultDict] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const openModal = () => {
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };

  useEffect(() => {
    // Fetch unique IDs from the backend API endpoint
    const fetchUniqueIds = async () => {
      try {
        const response = await fetch('http://localhost:5000/getUniqueIds'); // Replace with your actual API endpoint
        if (response.ok) {
          const data = await response.json();
          setUniqueIds(data.uniqueIds);
        } else {
          console.error('Failed to fetch unique IDs');
        }
      } catch (error) {
        console.error('Error fetching unique IDs:', error);
      }
    };

    fetchUniqueIds();
  }, []);

  const handleImageChange = (e) => {
    const selectedImages = Array.from(e.target.files);
    setImages(selectedImages);
  };

  const handleCsvFileChange = (e) => {
    const selectedCsvFile = e.target.files[0];
    setCsvFile(selectedCsvFile);
  };

  const handleUniqueIdChange = (e) => {
    setSelectedUniqueId(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
  
    // Use FormData to handle file uploads
    const formData = new FormData();
    images.forEach((image, index) => {
      formData.append('image', image);
    });
    formData.append('csvFile', csvFile);
    formData.append('uniqueId', selectedUniqueId);
  
    try {
      // Make a request to your backend service to process images
      const response = await fetch('http://localhost:5000/', {
        method: 'POST',
        body: formData,
      });
  
      if (response.ok) {
        // const resultDict = await response.json();
        const resultData = await response.json();
        console.log(resultData);
        setResultDict(resultData);
        openModal();
      } else {
        console.error('Image processing failed.');
      }
    } catch (error) {
      console.error('Error submitting form:', error);
    }
  };
  
  return (
    <div className="card-container">
      <div className="card">
        <form onSubmit={handleSubmit}>
          <h1>Answer Sheet Upload</h1>
          <label htmlFor="image" className="label">
            Select Images:
          </label>
          <input type="file" id="image" accept="image/*" multiple onChange={handleImageChange} className="input" />
          <br />
          <label htmlFor="csvFile" className="label">
            Select CSV File:
          </label>
          <input type="file" id="csvFile" accept=".csv" onChange={handleCsvFileChange} className="input" />
          <br />
          <label htmlFor="uniqueId" className="label">
            Select OMR Template ID:
          </label>
          <select id="uniqueId" onChange={handleUniqueIdChange} value={selectedUniqueId} className="input">
            <option value="" disabled>Select an OMR Template ID</option>
            {uniqueIds.map((id) => (
              <option key={id} value={id}>{id}</option>
            ))}
          </select>
          <br />
          <button type="submit" className="submit-button">
            Submit
          </button>
        </form>
      </div>
      {/* Modal */}
      <Modal
        isOpen={isModalOpen}
        onRequestClose={closeModal}
        contentLabel="Result Modal"
        className="result-modal"
        overlayClassName="modal-overlay"
      >
        {/* Close button */}
        <button className="close-button" onClick={closeModal}>
          Close
        </button>

        {/* Conditionally render the StudentResult component in the modal */}
        {resultDict && <StudentResult resultDict={resultDict} images={images} />}
      </Modal>
    </div>
  );
};

export default OMRAns;

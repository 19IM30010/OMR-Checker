import React, { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';

const ResultPage = () => {
  const location = useLocation();
  const formData = location.state && location.state.formData;
  const [localFormData, setLocalFormData] = useState(null);
  const canvasRef = useRef(null);
  const upperCanvasRef = useRef(null);
  const zoom = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [startX, setStartX] = useState(0);
  const [startY, setStartY] = useState(0);
  const [endX, setEndX] = useState(0);
  const [endY, setEndY] = useState(0);
  const [boxes, setBoxes] = useState([]);
  const [box1, setBox1] = useState(null);

  const sendFormDataToBackend = async () => {
    try {
      const formattedBoxes = boxes.reduce((acc, box, index) => {
        const formattedBox = {
          [`box${index + 1}`]: {
            x1: box.x1,
            y1: box.y1,
            width: box.width,
            height: box.height,
          },
        };
        return { ...acc, ...formattedBox };
      }, {});
      const formData = new FormData();
      formData.append('omrTemplate', localFormData.omrTemplate);
      formData.append('formData', JSON.stringify(localFormData));
      formData.append('boxesData', JSON.stringify(formattedBoxes));

      const response = await fetch('http://localhost:5000/submitFormData', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        console.log('Data successfully sent to the backend');
      } else {
        console.error('Failed to send data to the backend');
      }
    } catch (error) {
      console.error('Error sending data to the backend:', error);
    }
  };

  useEffect(() => {
    setLocalFormData(formData);

    if (formData && formData.omrTemplate && canvasRef.current) {
      const imageUrl = URL.createObjectURL(formData.omrTemplate);
      drawImageOnCanvas(imageUrl);
      setBoxes(Array.from({ length: formData.numBoxes }, () => ({ x1: 0, y1: 0, width: 0, height: 0 })));
    }
  }, [formData]);

  useEffect(() => {
    const canvash = upperCanvasRef.current;

    if (!canvash) {
      console.error('Upper canvas reference is null.');
      return;
    }

    const ctxh = canvash.getContext('2d');
    canvash.width = canvasRef.current.width;
    canvash.height = canvasRef.current.height;

    if (!ctxh) {
      console.error('2D context is null.');
      return;
    }

    const draw = () => {
      ctxh.clearRect(0, 0, canvash.width, canvash.height);

      if (isDrawing) {
        ctxh.strokeStyle = '#1079BF';
        ctxh.lineWidth = 2;

        const width = endX - startX;
        const height = endY - startY;

        ctxh.strokeRect(startX, startY, width, height);
      } else if (startX !== endX) {
        ctxh.strokeStyle = '#1079BF';
        ctxh.lineWidth = 2;

        const width = endX - startX;
        const height = endY - startY;

        ctxh.strokeRect(startX, startY, width, height);
        const box = {
          x1: startX,
          y1: startY,
          width: width,
          height: height,
        };
        setBox1(box);
        console.log(box);
      }
    };

    draw(); // Call the draw function immediately

  }, [isDrawing, startX, startY, endX, endY, upperCanvasRef]);

  const drawImageOnCanvas = (imageUrl) => {
    const canvas = canvasRef.current;

    if (!canvas) {
      return;
    }

    const context = canvas.getContext('2d');

    const img = new Image();
    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;
      context.clearRect(0, 0, canvas.width, canvas.height);
      context.drawImage(img, 0, 0, canvas.width, canvas.height);
      const canvash = upperCanvasRef.current;
      canvash.width = canvasRef.current.width;
      canvash.height = canvasRef.current.height;
    };

    img.onerror = (error) => {
      console.error('Error loading image:', error);
    };

    img.src = imageUrl;
  };

  const handleMouseDown = (event) => {
    const { offsetX, offsetY } = event.nativeEvent;
    setIsDrawing(true);
    setStartX(offsetX);
    setStartY(offsetY);
    setEndX(offsetX);
    setEndY(offsetY);
  };

  const handleMouseMove = (event) => {
    if (!isDrawing) return;

    const { offsetX, offsetY } = event.nativeEvent;
    setEndX(offsetX);
    setEndY(offsetY);
  };

  const handleMouseUp = (event) => {
    const { offsetX, offsetY } = event.nativeEvent;
    setIsDrawing(false);
    setEndX(offsetX);
    setEndY(offsetY);
  };

  const loadImage = () => {
    if (formData && formData.omrTemplate && canvasRef.current) {
      const imageUrl = URL.createObjectURL(formData.omrTemplate);
      drawImageOnCanvas(imageUrl);
    }
  };

  const handleEdit = (index) => {
    const updatedBoxes = [...boxes]; // Create a copy of the boxes array
    updatedBoxes[index].x1 = box1.x1;
    updatedBoxes[index].y1 = box1.y1;
    updatedBoxes[index].height = box1.height;
    updatedBoxes[index].width = box1.width;
    setBoxes(updatedBoxes); // Update the boxes state with the modified array
  };
  


  return (
    <div style={{ display: 'flex' }}>
    <div style={{ flex: 1, marginRight: '20px' }}>
        <div id="zoom" ref={zoom} className="card2">
          <button onClick={loadImage}>Load Image</button>
          {/* <button onClick={() => setIsDrawing(!isDrawing)}>
            {isDrawing ? 'Stop Drawing' : 'Start Drawing'}
          </button> */}
          <br></br>
          <canvas
            id="canvas"
            ref={canvasRef}
          ></canvas>
          <canvas
            id="canvasx"
            ref={upperCanvasRef}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
          ></canvas>
        </div>
      </div>

      <div style={{ flex: 1, overflowX: 'auto' }} className="table-container">
        <button onClick={sendFormDataToBackend}>Send Data to Backend</button>
        {localFormData && (
          <table>
            <thead>
              <tr>
                <th>Box</th>
                <th>Edit</th>
                <th>x1</th>
                <th>y1</th>
                <th>width</th>
                <th>height</th>
              </tr>
            </thead>
            <tbody>
              {boxes.map((box, index) => (
                <tr key={index}>
                  <td>Box {index + 1}</td>
                  <td>
                    <button className="edit-button" onClick={() => handleEdit(index)}>Edit</button>
                  </td>
                  <td>{box.x1}</td>
                  <td>{box.y1}</td>
                  <td>{box.width}</td>
                  <td>{box.height}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default ResultPage;

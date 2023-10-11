import logo from './logo.svg';
import React, { useState } from 'react';
import './FormulaInput.css'; 

function FormulaInput() {
  const [tags, setTags] = useState(['']); // Initial tag

  const addTag = () => {
    setTags([...tags, '']); // Add a new empty tag
  };

  const handleTagChange = (index, value) => {
    const updatedTags = [...tags];
    updatedTags[index] = value;
    setTags(updatedTags);
  };

  const deleteTag = (index) => {
    const updatedTags = [...tags];
    updatedTags.splice(index, 1);
    setTags(updatedTags);
  };

  const calculateFormula = () => {
    const formula = tags.join(' '); // Combine tags into a single string
    // You can add code here to calculate the formula if needed
    alert(`Formula: ${formula}`);
  };

  const addOperation = (operation) => {
    const updatedTags = [...tags, operation];
    setTags(updatedTags);
  };

  return (
    <div className="formula-input">
      <div className="tag-container">
        {tags.map((tag, index) => (
          <div key={index} className="tag">
            <input
              type="text"
              value={tag}
              onChange={(e) => handleTagChange(index, e.target.value)}
            />
            {tags.length > 1 && (
              <button onClick={() => deleteTag(index)}>Delete</button>
            )}
          </div>
        ))}
      </div>
      <div className="operation-buttons">
        <button onClick={() => addOperation('+')}>+</button>
        <button onClick={() => addOperation('-')}>-</button>
        <button onClick={() => addOperation('*')}>*</button>
        <button onClick={() => addOperation('/')}>/</button>
        <button onClick={() => addOperation('^')}>^</button>
        <button onClick={() => addOperation('(')}>(</button>
        <button onClick={() => addOperation(')')}>)</button>
      </div>
      <button className="add-button" onClick={addTag}>
        Add Tag
      </button>
      <button className="calculate-button" onClick={calculateFormula}>
        Calculate
      </button>
    </div>
  );
}


export default FormulaInput;


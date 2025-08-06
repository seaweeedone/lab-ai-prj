import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import Editor from '@monaco-editor/react';

const CodeCreate: React.FC = () => {
  const [newCodeName, setNewCodeName] = useState<string>('');
  const [newCodeContent, setNewCodeContent] = useState<string>('# Enter your Python code here');
  const navigate = useNavigate();

  const handleCreateCode = async () => {
    try {
      await axios.post('http://localhost:8000/codes', {
        name: newCodeName,
        content: newCodeContent,
      });
      alert('Code created successfully!');
      navigate('/');
    } catch (error) {
      console.error('Error creating code:', error);
      alert('Failed to create code.');
    }
  };

  return (
    <div className="card">
      <div className="card-header">Create New Code</div>
      <div className="card-body">
        <div className="mb-3">
          <label htmlFor="newCodeName" className="form-label">Code Name</label>
          <input
            type="text"
            className="form-control"
            id="newCodeName"
            value={newCodeName}
            onChange={(e) => setNewCodeName(e.target.value)}
          />
        </div>
        <div className="mb-3">
          <label htmlFor="newCodeContent" className="form-label">Code Content</label>
          <Editor
            height="60vh" // Fixed height
            language="python"
            theme="vs-dark"
            value={newCodeContent}
            onChange={(value) => setNewCodeContent(value || '')}
          />
        </div>
        <button className="btn btn-primary me-2" onClick={handleCreateCode}>Create</button>
        <button className="btn btn-secondary" onClick={() => navigate('/')}>Cancel</button>
      </div>
    </div>
  );
};

export default CodeCreate;

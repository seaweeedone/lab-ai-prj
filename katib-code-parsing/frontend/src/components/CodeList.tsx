import React, { useEffect, useState, useMemo } from 'react';
import axios from 'axios';
import { Link, useNavigate } from 'react-router-dom';

interface Code {
  id: number;
  name: string;
  created_at: string;
  updated_at: string;
  versions: CodeVersion[];
}

interface CodeVersion {
  id: number;
  version: number;
  content: string;
  created_at: string;
}

const CodeList: React.FC = () => {
  const [codes, setCodes] = useState<Code[]>([]);
  const [selectedCodes, setSelectedCodes] = useState<number[]>([]);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchCodes();
  }, []);

  const fetchCodes = async () => {
    try {
      const response = await axios.get<Code[]>('http://localhost:8000/codes');
      setCodes(response.data);
    } catch (error) {
      console.error('Error fetching codes:', error);
    }
  };

  const handleCheckboxChange = (codeId: number) => {
    setSelectedCodes((prevSelectedCodes) =>
      prevSelectedCodes.includes(codeId)
        ? prevSelectedCodes.filter((id) => id !== codeId)
        : [...prevSelectedCodes, codeId]
    );
  };

  const handleDeleteSelectedCodes = async () => {
    if (selectedCodes.length === 0) {
      alert('Please select at least one code to delete.');
      return;
    }
    if (!window.confirm(`Are you sure you want to delete ${selectedCodes.length} selected codes?`)) {
      return;
    }

    try {
      await Promise.all(
        selectedCodes.map((id) => axios.delete(`http://localhost:8000/codes/${id}`))
      );
      setSelectedCodes([]); // Clear selection
      fetchCodes(); // Refresh the list
      alert('Selected codes deleted successfully!');
    } catch (error) {
      console.error('Error deleting selected codes:', error);
      alert('Failed to delete selected codes.');
    }
  };

  const filteredCodes = useMemo(() => {
    return codes.filter((code) =>
      code.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [codes, searchTerm]);

  return (
    <div className="card">
      <div className="card-body">
        <div className="d-flex justify-content-between mb-3">
          <input
            type="text"
            className="form-control w-50"
            placeholder="Search codes..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <div>
            <button
              className="btn btn-danger me-2"
              onClick={handleDeleteSelectedCodes}
              disabled={selectedCodes.length === 0}
            >
              Delete Selected ({selectedCodes.length})
            </button>
            <button className="btn btn-primary" onClick={() => navigate('/create')}>
              + NEW CODE
            </button>
          </div>
        </div>

        <table className="table table-hover">
          <thead>
            <tr>
              <th style={{ width: '5%' }}></th>
              <th>Name</th>
              <th>Latest Version</th>
              <th>Created</th>
              <th>Updated</th>
            </tr>
          </thead>
          <tbody>
            {filteredCodes.map((code) => (
              <tr key={code.id}>
                <td>
                  <input
                    className="form-check-input"
                    type="checkbox"
                    checked={selectedCodes.includes(code.id)}
                    onChange={() => handleCheckboxChange(code.id)}
                  />
                </td>
                <td>
                  <Link to={`/codes/${code.id}`}>{code.name}</Link>
                </td>
                <td>{code.versions.length > 0 ? code.versions[code.versions.length - 1].version : 'N/A'}</td>
                <td>{new Date(code.created_at).toLocaleString()}</td>
                <td>{new Date(code.updated_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default CodeList;

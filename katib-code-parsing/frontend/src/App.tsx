import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import CodeList from './components/CodeList';
import CodeDetail from './components/CodeDetail';
import CodeCreate from './components/CodeCreate';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app-container">
        <div className="sidebar">
          <div className="sidebar-header">
            <Link to="/" className="sidebar-brand">ML Code Parser</Link>
          </div>
          <ul className="nav flex-column">
            <li className="nav-item">
              <Link className="nav-link active" to="/">
                <i className="bi bi-file-earmark-code me-2"></i>
                ML Codes
              </Link>
            </li>
          </ul>
        </div>
        <div className="main-content">
          <header className="header">
            <div className="header-title">Codes</div>
          </header>
          <div className="content-body">
            <Routes>
              <Route path="/" element={<CodeList />} />
              <Route path="/create" element={<CodeCreate />} />
              <Route path="/codes/:id" element={<CodeDetail />} />
            </Routes>
          </div>
        </div>
      </div>
    </Router>
  );
}

export default App;
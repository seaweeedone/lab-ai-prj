import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';
import Editor, { OnMount } from '@monaco-editor/react';
import VersionDiffModal from './VersionDiffModal';

// --- Interfaces (no changes) ---
interface Code { id: number; name: string; created_at: string; updated_at: string; versions: CodeVersion[]; }
interface CodeVersion { id: number; version: number; content: string; created_at: string; parsing_results: ParsingResult[]; }
interface ParsingResult { id: number; code_version_id: number; name: string; created_at: string; versions: ParsingResultVersion[]; }
interface ParsedContent { name: string; framework: string; metric: string[]; parameter: string; model_block: string; data_block: string; }
interface ParsingResultVersion { id: number; version: number; content: ParsedContent; created_at: string; }

// --- Debounce Utility (Removed as it's no longer needed for editor height) ---

const CodeDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const codeId = Number(id);

  const [code, setCode] = useState<Code | null>(null);
  const [selectedVersion, setSelectedVersion] = useState<CodeVersion | null>(null);
  const [codeContent, setCodeContent] = useState<string>('');
  const [editorHeight, setEditorHeight] = useState<string>('60vh'); // Initial height
  const [isEditingCodeName, setIsEditingCodeName] = useState<boolean>(false);
  const [newCodeName, setNewCodeName] = useState<string>('');
  const [selectedParsingResult, setSelectedParsingResult] = useState<ParsingResult | null>(null);
  const [selectedParsingResultVersion, setSelectedParsingResultVersion] = useState<ParsingResultVersion | null>(null);
  const [isEditingParsingResultContent, setIsEditingParsingResultContent] = useState<boolean>(false);
  const [newParsingResultContent, setNewParsingResultContent] = useState<string>('');
  const [isDiffModalOpen, setIsDiffModalOpen] = useState<boolean>(false);

  // --- Data Fetching and State Management ---
  useEffect(() => {
    fetchCodeDetail();
  }, [codeId]);

  useEffect(() => {
    const handler = setTimeout(() => {
      const lines = codeContent.split('\n').length;
      const newHeight = Math.max(300, lines * 19 + 20) + 'px'; // Minimum 300px, 19px per line + 20px buffer
      setEditorHeight(newHeight);
    }, 100); // Debounce by 100ms

    return () => {
      clearTimeout(handler);
    };
  }, [codeContent]);

  const fetchCodeDetail = async (versionToSelect?: number) => {
    try {
      const response = await axios.get<Code>(`http://localhost:8000/codes/${codeId}`);
      const fetchedCode = response.data;
      setCode(fetchedCode);

      if (fetchedCode.versions.length > 0) {
        const versionId = versionToSelect ?? fetchedCode.versions[fetchedCode.versions.length - 1].id;
        const version = fetchedCode.versions.find(v => v.id === versionId) ?? fetchedCode.versions[0];
        updateStateForVersion(version);
      }
    } catch (error) {
      console.error('Error fetching code detail:', error);
    }
  };

  const updateStateForVersion = (version: CodeVersion) => {
    setSelectedVersion(version);
    setCodeContent(version.content);

    if (version.parsing_results.length > 0) {
      const latestParsingResult = version.parsing_results[version.parsing_results.length - 1];
      setSelectedParsingResult(latestParsingResult);
      if (latestParsingResult.versions.length > 0) {
        const latestParsingResultVersion = latestParsingResult.versions[latestParsingResult.versions.length - 1];
        setSelectedParsingResultVersion(latestParsingResultVersion);
        setNewParsingResultContent(JSON.stringify(latestParsingResultVersion.content, null, 2));
      } else {
        setSelectedParsingResultVersion(null);
        setNewParsingResultContent('');
      }
    } else {
      setSelectedParsingResult(null);
      setSelectedParsingResultVersion(null);
      setNewParsingResultContent('');
    }
  };

  const handleVersionChange = (versionId: number) => {
    if (!code) return;
    const version = code.versions.find(v => v.id === versionId);
    if (version) {
      updateStateForVersion(version);
    }
  };

  // --- API Handlers ---
  const handleSaveNewVersion = async () => {
    if (!codeId || !codeContent) return;
    try {
      await axios.post(`http://localhost:8000/codes/${codeId}/versions`, { content: codeContent });
      await fetchCodeDetail(selectedVersion?.id);
      alert('New version saved successfully!');
    } catch (error) { console.error('Error saving new version:', error); }
  };

  const handleParseCode = async () => {
    if (!selectedVersion) return;
    const parsingResultName = `Parsing Result v${selectedVersion.parsing_results.length + 1}`;
    try {
      await axios.post(`http://localhost:8000/parsing/code-versions/${selectedVersion.id}`, { name: parsingResultName });
      await fetchCodeDetail(selectedVersion.id);
      alert('Code parsed successfully!');
    } catch (error) { console.error('Error parsing code:', error); }
  };

  const handleUpdateCodeName = async () => {
    if (!codeId || !newCodeName) return;
    try {
      await axios.put(`http://localhost:8000/codes/${codeId}`, { name: newCodeName });
      setIsEditingCodeName(false);
      await fetchCodeDetail(selectedVersion?.id);
    } catch (error) { console.error('Error updating code name:', error); }
  };

  const handleSaveParsingResultVersion = async () => {
    if (!selectedParsingResult || !newParsingResultContent) return;
    try {
      const content = JSON.parse(newParsingResultContent);
      await axios.post(`http://localhost:8000/parsing/results/${selectedParsingResult.id}/versions`, { content });
      setIsEditingParsingResultContent(false);
      await fetchCodeDetail(selectedVersion?.id);
      alert('Parsing result version saved successfully!');
    } catch (error) { console.error('Error saving parsing result version:', error); }
  };

  // --- Editor Height Management (Fixed Height) ---
  const handleEditorMount: OnMount = (editor, monaco) => {
    // No dynamic height adjustment, fixed height is set in JSX
  };

  if (!code) { return <div>Loading...</div>; }

  return (
    <>
      <div className="card">
        <div className="card-header d-flex justify-content-between align-items-center">
          {isEditingCodeName ? (
            <div className="input-group w-50">
              <input type="text" className="form-control" value={newCodeName} onChange={(e) => setNewCodeName(e.target.value)} />
              <button className="btn btn-primary" onClick={handleUpdateCodeName}>Save</button>
              <button className="btn btn-secondary" onClick={() => setIsEditingCodeName(false)}>Cancel</button>
            </div>
          ) : (
            <h4 onClick={() => { setIsEditingCodeName(true); setNewCodeName(code.name); }}>{code.name}</h4>
          )}
        </div>
        <div className="card-body">
          <div className="row">
            {/* --- Original Code Column --- */}
            <div className="col-md-6">
              <div className="d-flex justify-content-between align-items-center mb-3">
                <h5>Original Code</h5>
                <div>
                  <button className="btn btn-primary btn-sm me-2" onClick={handleSaveNewVersion}>Save Version</button>
                  <button className="btn btn-primary btn-sm me-2" onClick={handleParseCode}>Parse</button>
                  <button className="btn btn-secondary btn-sm" onClick={() => setIsDiffModalOpen(true)}>Compare</button>
                </div>
              </div>
              <div className="mb-3">
                <label htmlFor="codeVersionSelect" className="form-label">Select Version</label>
                <select className="form-select" id="codeVersionSelect" value={selectedVersion?.id || ''} onChange={(e) => handleVersionChange(Number(e.target.value))}>
                  {code.versions.map((v) => <option key={v.id} value={v.id}>Version {v.version} ({new Date(v.created_at).toLocaleString()})</option>)}
                </select>
              </div>
              <Editor
                
                height={editorHeight}
                language="python"
                theme="vs-dark"
                value={codeContent}
                onChange={(v) => setCodeContent(v || '')}
                options={{ scrollBeyondLastLine: false, minimap: { enabled: false } }}
              />
            </div>

            {/* --- Parsed Code Column --- */}
            <div className="col-md-6">
              <div className="d-flex justify-content-between align-items-center mb-3">
                <h5>Parsed Result</h5>
                 <div style={{ height: '31px' }}></div> {/* Spacer for alignment */}
              </div>
              {selectedVersion && selectedVersion.parsing_results.length > 0 ? (
                <div className="mb-3">
                  <label htmlFor="parsingResultSelect" className="form-label">Select Result</label>
                  <select className="form-select" id="parsingResultSelect" value={selectedParsingResult?.id || ''} onChange={(e) => {
                    const resultId = Number(e.target.value);
                    const result = selectedVersion.parsing_results.find(pr => pr.id === resultId);
                    if (result) {
                      setSelectedParsingResult(result);
                      if (result.versions.length > 0) {
                        const latestVersion = result.versions[result.versions.length - 1];
                        setSelectedParsingResultVersion(latestVersion);
                        setNewParsingResultContent(JSON.stringify(latestVersion.content, null, 2));
                      } else {
                        setSelectedParsingResultVersion(null);
                        setNewParsingResultContent('');
                      }
                    }
                  }}>
                    {selectedVersion.parsing_results.map((r) => <option key={r.id} value={r.id}>{r.name} ({new Date(r.created_at).toLocaleString()})</option>)}
                  </select>
                </div>
              ) : (
                <div className="mb-3"><label className="form-label">&nbsp;</label><div style={{height: '38px'}}></div></div>
              )}

              {selectedParsingResult && selectedParsingResultVersion ? (
                <div onClick={() => setIsEditingParsingResultContent(true)} style={{ cursor: 'pointer' }}>
                  {isEditingParsingResultContent ? (
                    <>
                      <Editor height="45vh" language="json" theme="vs-dark" value={newParsingResultContent} onChange={(v) => setNewParsingResultContent(v || '')} />
                      <div className="mt-2">
                        <button className="btn btn-primary btn-sm me-2" onClick={(e) => { e.stopPropagation(); handleSaveParsingResultVersion(); }}>Save</button>
                        <button className="btn btn-secondary btn-sm" onClick={(e) => { e.stopPropagation(); setIsEditingParsingResultContent(false); }}>Cancel</button>
                      </div>
                    </>
                  ) : (
                    <div style={{ minHeight: '50vh' }}>
                      <h5>Framework:</h5>
                      <pre className="bg-light p-2 rounded">{selectedParsingResultVersion.content.framework ?? 'N/A'}</pre>

                      <h5>Metric:</h5>
                      <pre className="bg-light p-2 rounded">{selectedParsingResultVersion.content.metric ? JSON.stringify(selectedParsingResultVersion.content.metric, null, 2) : 'N/A'}</pre>

                      <h5>Parameter:</h5>
                      <pre className="bg-light p-2 rounded">{selectedParsingResultVersion.content.parameter}</pre>

                      <h5>Model Block:</h5>
                      <pre className="bg-light p-2 rounded">{selectedParsingResultVersion.content.model_block}</pre>

                      <h5>Data Block:</h5>
                      <pre className="bg-light p-2 rounded">{selectedParsingResultVersion.content.data_block}</pre>
                    </div>
                  )}
                </div>
              ) : (
                <p>No parsing results available for this version.</p>
              )}
            </div>
          </div>
        </div>
      </div>
      {code && <VersionDiffModal isOpen={isDiffModalOpen} onClose={() => setIsDiffModalOpen(false)} versions={code.versions} />}
    </>
  );
};

export default CodeDetail;

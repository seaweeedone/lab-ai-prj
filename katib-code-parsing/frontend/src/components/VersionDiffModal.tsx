import React, { useState, useEffect } from 'react';
import ReactDiffViewer from 'react-diff-viewer-continued';

interface CodeVersion {
  id: number;
  version: number;
  content: string;
}

interface VersionDiffModalProps {
  isOpen: boolean;
  onClose: () => void;
  versions: CodeVersion[];
}

const VersionDiffModal: React.FC<VersionDiffModalProps> = ({ isOpen, onClose, versions }) => {
  const [oldVersionId, setOldVersionId] = useState<number | null>(null);
  const [newVersionId, setNewVersionId] = useState<number | null>(null);
  const [oldCode, setOldCode] = useState<string>('');
  const [newCode, setNewCode] = useState<string>('');

  useEffect(() => {
    if (versions.length >= 2) {
      setOldVersionId(versions[versions.length - 2].id);
      setNewVersionId(versions[versions.length - 1].id);
    } else if (versions.length === 1) {
      setOldVersionId(versions[0].id);
      setNewVersionId(versions[0].id);
    }
  }, [versions]);

  useEffect(() => {
    const oldV = versions.find(v => v.id === oldVersionId);
    setOldCode(oldV ? oldV.content : '');
  }, [oldVersionId, versions]);

  useEffect(() => {
    const newV = versions.find(v => v.id === newVersionId);
    setNewCode(newV ? newV.content : '');
  }, [newVersionId, versions]);

  if (!isOpen) return null;

  return (
    <div className="modal show d-block" tabIndex={-1} style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
      <div className="modal-dialog modal-xl">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">Compare Code Versions</h5>
            <button type="button" className="btn-close" onClick={onClose}></button>
          </div>
          <div className="modal-body">
            <div className="row mb-3">
              <div className="col">
                <label className="form-label">Old Version</label>
                <select className="form-select" value={oldVersionId || ''} onChange={e => setOldVersionId(Number(e.target.value))}>
                  {versions.map(v => <option key={v.id} value={v.id}>Version {v.version}</option>)}
                </select>
              </div>
              <div className="col">
                <label className="form-label">New Version</label>
                <select className="form-select" value={newVersionId || ''} onChange={e => setNewVersionId(Number(e.target.value))}>
                  {versions.map(v => <option key={v.id} value={v.id}>Version {v.version}</option>)}
                </select>
              </div>
            </div>
            <ReactDiffViewer oldValue={oldCode} newValue={newCode} splitView={true} useDarkTheme={true} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default VersionDiffModal;

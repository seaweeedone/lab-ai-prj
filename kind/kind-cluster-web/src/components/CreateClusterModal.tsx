import React, { useState } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, TextField, CircularProgress, Alert, Box, Typography } from '@mui/material';
import axiosInstance from '@/lib/axios';
import { ClusterCreateRequest, TaskResponse } from '@/types/cluster';
import useSWR from 'swr';
import { fetcher } from '@/lib/axios';

interface CreateClusterModalProps {
  open: boolean;
  onClose: () => void;
  onClusterCreated: () => void;
}

export default function CreateClusterModal({ open, onClose, onClusterCreated }: CreateClusterModalProps) {
  const [clusterName, setClusterName] = useState('');
  const [nodeVersion, setNodeVersion] = useState('');
  const [numWorkers, setNumWorkers] = useState<number | ''>('');
  const [config, setConfig] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [taskId, setTaskId] = useState<string | null>(null);

  const { data: taskStatus, error: taskError } = useSWR<TaskResponse>(
    taskId ? `/tasks/${taskId}` : null,
    fetcher,
    { refreshInterval: 3000 } // Poll every 3 seconds
  );

  React.useEffect(() => {
    if (taskStatus) {
      if (taskStatus.status === 'completed') {
        setLoading(false);
        onClusterCreated();
        onClose();
        alert(`Cluster creation completed: ${taskStatus.result}`);
      } else if (taskStatus.status === 'failed') {
        setLoading(false);
        setError(`Cluster creation failed: ${taskStatus.result}`);
      }
    }
  }, [taskStatus, onClusterCreated, onClose]);

  const handleSubmit = async () => {
    setError(null);
    setLoading(true);
    setTaskId(null);

    const requestBody: ClusterCreateRequest = {
      cluster_name: clusterName,
    };

    if (nodeVersion) {
      requestBody.node_version = nodeVersion;
    }
    if (numWorkers !== '') {
      requestBody.num_workers = Number(numWorkers);
    }
    if (config) {
      requestBody.config = config;
    }

    try {
      const response = await axiosInstance.post<TaskResponse>('/clusters', requestBody);
      setTaskId(response.data.task_id);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An unexpected error occurred.');
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="md">
      <DialogTitle>Create New Cluster</DialogTitle>
      <DialogContent>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {taskId && taskStatus && (
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography>Task ID: {taskId}</Typography>
            <Typography>Status: {taskStatus.status}</Typography>
            {taskStatus.result && <Typography>Result: {taskStatus.result}</Typography>}
            {taskStatus.status === 'in_progress' && <CircularProgress size={20} sx={{ ml: 2 }} />}
          </Alert>
        )}
        <TextField
          autoFocus
          margin="dense"
          label="Cluster Name"
          type="text"
          fullWidth
          variant="outlined"
          value={clusterName}
          onChange={(e) => setClusterName(e.target.value)}
          sx={{ mb: 2 }}
          disabled={loading}
        />
        <TextField
          margin="dense"
          label="Node Version (e.g., 1.27.3)"
          type="text"
          fullWidth
          variant="outlined"
          value={nodeVersion}
          onChange={(e) => setNodeVersion(e.target.value)}
          sx={{ mb: 2 }}
          disabled={loading}
        />
        <TextField
          margin="dense"
          label="Number of Worker Nodes"
          type="number"
          fullWidth
          variant="outlined"
          value={numWorkers}
          onChange={(e) => setNumWorkers(e.target.value === '' ? '' : Number(e.target.value))}
          sx={{ mb: 2 }}
          disabled={loading}
          inputProps={{ min: 0 }}
        />
        <TextField
          margin="dense"
          label="Kind Config YAML (Optional)"
          type="text"
          fullWidth
          multiline
          rows={6}
          variant="outlined"
          value={config}
          onChange={(e) => setConfig(e.target.value)}
          disabled={loading}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>Cancel</Button>
        <Button onClick={handleSubmit} disabled={loading || !clusterName} variant="contained">
          {loading ? <CircularProgress size={24} /> : 'Create'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

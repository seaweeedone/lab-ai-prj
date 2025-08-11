import { Box, Typography, CircularProgress, Alert, Button, FormControlLabel, Checkbox } from '@mui/material';
import { useParams } from 'next/navigation';
import React, { useEffect, useRef, useState } from 'react';
import axiosInstance from '@/lib/axios';

export default function PodLogsPage() {
  const params = useParams();
  const clusterName = params.clusterName as string;
  const podName = params.podName as string;
  const [logs, setLogs] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [follow, setFollow] = useState(true);
  const logContainerRef = useRef<HTMLDivElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  const namespace = 'default'; // TODO: Make dynamic if needed

  const handleDownloadLogs = () => {
    const logContent = logs.join('\n');
    const blob = new Blob([logContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${podName}-logs.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const fetchLogs = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    setLoading(true);
    setLogs([]);
    setError(null);

    const url = `/clusters/${clusterName}/pods/${podName}/logs?namespace=${namespace}&follow=${follow}`;
    eventSourceRef.current = new EventSource(axiosInstance.defaults.baseURL + url);

    eventSourceRef.current.onmessage = (event) => {
      setLogs((prevLogs) => [...prevLogs, event.data]);
      setLoading(false);
    };

    eventSourceRef.current.onerror = (err) => {
      console.error('EventSource failed:', err);
      setError('Failed to stream logs. Check if the pod exists and is running.');
      setLoading(false);
      eventSourceRef.current?.close();
    };
  };

  useEffect(() => {
    fetchLogs();

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, [clusterName, podName, namespace, follow]);

  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Logs for Pod: {podName}</Typography>
      <FormControlLabel
        control={<Checkbox checked={follow} onChange={(e) => setFollow(e.target.checked)} />}
        label="Follow logs"
      />
      <Button onClick={fetchLogs} variant="outlined" sx={{ ml: 2 }}>Refresh Logs</Button>
      <Button onClick={handleDownloadLogs} variant="outlined" sx={{ ml: 2 }}>Download Logs</Button>
      
      {loading && <CircularProgress sx={{ mt: 2 }} />}
      {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}

      <Box
        ref={logContainerRef}
        sx={{
          mt: 2,
          p: 2,
          backgroundColor: '#1e1e1e',
          color: '#f0f0f0',
          fontFamily: 'monospace',
          whiteSpace: 'pre-wrap',
          maxHeight: '600px',
          overflowY: 'auto',
          borderRadius: '4px',
        }}
      >
        {logs.map((line, index) => (
          <div key={index}>{line}</div>
        ))}
      </Box>
    </Box>
  );
}

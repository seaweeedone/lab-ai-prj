'use client';

import useSWR from 'swr';
import axiosInstance, { fetcher } from '@/lib/axios';
import { Box, Card, CardContent, Typography, Grid, CircularProgress, Alert, Button } from '@mui/material';
import Add from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import CreateClusterModal from '@/components/CreateClusterModal';
import { Cluster } from '@/types/cluster';
import { useState } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions } from '@mui/material';
import Link from 'next/link';

export default function HomePage() {
  const { data: clusters, error, mutate } = useSWR<Cluster[]>('/clusters', fetcher);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [clusterToDelete, setClusterToDelete] = useState<string | null>(null);

  const handleOpenModal = () => setIsModalOpen(true);
  const handleCloseModal = () => setIsModalOpen(false);
  const handleClusterCreated = () => {
    mutate(); // Re-fetch clusters after creation
  };

  const handleDeleteCluster = (clusterName: string) => {
    setClusterToDelete(clusterName);
    setIsDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (clusterToDelete) {
      try {
        await axiosInstance.delete(`/clusters/${clusterToDelete}`);
        mutate(); // Re-fetch clusters after deletion
        alert(`Cluster '${clusterToDelete}' deleted successfully.`);
      } catch (err: any) {
        alert(`Failed to delete cluster '${clusterToDelete}': ${err.response?.data?.detail || err.message}`);
      }
    }
    setIsDeleteDialogOpen(false);
    setClusterToDelete(null);
  };

  const handleCancelDelete = () => {
    setIsDeleteDialogOpen(false);
    setClusterToDelete(null);
  };

  if (error) return <Alert severity="error">Failed to load clusters.</Alert>;
  if (!clusters) return <CircularProgress />;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4">Clusters</Typography>
        <Button variant="contained" startIcon={<Add />} onClick={handleOpenModal}>
          Create Cluster
        </Button>
      </Box>
      <Grid container spacing={3}>
        {clusters.map((cluster) => (
          <Grid item xs={12} sm={6} md={4} key={cluster.name}>
            <Card>
              <CardContent>
                <Typography variant="h6" component={Link} href={`/clusters/${cluster.name}`} sx={{ cursor: 'pointer', textDecoration: 'none', color: 'inherit' }}>
                  {cluster.name}
                </Typography>
                {/* 클러스터 상태 등 추가 정보 표시 가능 */}
                <Button 
                  variant="outlined" 
                  color="error" 
                  size="small" 
                  sx={{ mt: 2 }}
                  startIcon={<DeleteIcon />}
                  onClick={() => handleDeleteCluster(cluster.name)}
                >
                  Delete
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
      <CreateClusterModal
        open={isModalOpen}
        onClose={handleCloseModal}
        onClusterCreated={handleClusterCreated}
      />

      <Dialog
        open={isDeleteDialogOpen}
        onClose={handleCancelDelete}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">
          {"Confirm Deletion"}
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            Are you sure you want to delete cluster '{clusterToDelete}'? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCancelDelete}>Cancel</Button>
          <Button onClick={handleConfirmDelete} autoFocus color="error">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

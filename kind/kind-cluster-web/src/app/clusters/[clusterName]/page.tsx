'use client';

import { Box, Typography, CircularProgress, Alert, Card, CardContent, Grid } from '@mui/material';
import { useParams } from 'next/navigation';
import useSWR from 'swr';
import { fetcher } from '@/lib/axios';
import { ClusterDetailsResponse } from '@/types/cluster';
import Link from 'next/link';

export default function ClusterDetailPage() {
  const params = useParams();
  const clusterName = params.clusterName as string;

  const { data, error } = useSWR<ClusterDetailsResponse>(
    `/clusters/${clusterName}/details`,
    fetcher
  );

  if (error) return <Alert severity="error">Failed to load cluster details.</Alert>;
  if (!data) return <CircularProgress />;

  const { node_count, pod_summary, service_count, deployment_count } = data;

  const resourceCards = [
    { title: 'Nodes', count: node_count, path: `/clusters/${clusterName}/nodes` },
    { title: 'Pods', count: `${pod_summary.running} Running, ${pod_summary.succeeded} Succeeded, ${pod_summary.pending} Pending, ${pod_summary.failed} Failed`, path: `/clusters/${clusterName}/pods` },
    { title: 'Services', count: service_count, path: `/clusters/${clusterName}/services` },
    { title: 'Deployments', count: deployment_count, path: `/clusters/${clusterName}/deployments` },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Cluster: {clusterName}
      </Typography>
      <Grid container spacing={3}>
        {resourceCards.map((card) => (
          <Grid item xs={12} sm={6} key={card.title}>
            <Card component={Link} href={card.path} sx={{ textDecoration: 'none', cursor: 'pointer' }}>
              <CardContent>
                <Typography variant="h6">{card.title}</Typography>
                <Typography color="text.secondary">{card.count}</Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
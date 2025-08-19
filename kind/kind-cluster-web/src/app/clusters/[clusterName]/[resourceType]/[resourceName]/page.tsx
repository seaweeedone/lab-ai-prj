'use client';

import { Box, Typography, CircularProgress, Alert, Paper, Tabs, Tab } from '@mui/material';
import { useParams } from 'next/navigation';
import useSWR from 'swr';
import { fetcher } from '@/lib/axios';
import YamlView from '@/components/YamlView';
import { useState } from 'react';
import Link from 'next/link';

export default function ResourceDetailPage() {
  const params = useParams();
  const clusterName = params.clusterName as string;
  const resourceType = params.resourceType as string;
  const resourceName = params.resourceName as string;
  const [tabValue, setTabValue] = useState(0);

  const { data, error } = useSWR(
    `/clusters/${clusterName}/${resourceType}/${resourceName}`,
    fetcher
  );

  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  if (error) return <Alert severity="error">Failed to load {resourceType} details.</Alert>;
  if (!data) return <CircularProgress />;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        {resourceType.slice(0, -1)}: {resourceName}
      </Typography>
      <Typography variant="h6" gutterBottom>
        Cluster: {clusterName}
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleChange} aria-label="resource details tabs">
          <Tab label="Details" />
          <Tab label="YAML" />
          {resourceType === 'pods' && <Tab label="Logs" />}
        </Tabs>
      </Box>

      {tabValue === 0 && (
        <Paper sx={{ p: 2, mt: 2 }}>
          {Object.entries(data).map(([key, value]) => (
            <Box key={key} sx={{ mb: 2 }}>
              <Typography variant="h6" component="h3" gutterBottom>
                {key.charAt(0).toUpperCase() + key.slice(1)}
              </Typography>
              <pre>{JSON.stringify(value, null, 2)}</pre>
            </Box>
          ))}
        </Paper>
      )}
      {tabValue === 1 && (
        <Paper sx={{ p: 2, mt: 2 }}>
          <YamlView data={data} />
        </Paper>
      )}
      {tabValue === 2 && resourceType === 'pods' && (
        <Paper sx={{ p: 2, mt: 2 }}>
          <Link href={`/clusters/${clusterName}/pods/${resourceName}/logs`}>
            View Logs
          </Link>
        </Paper>
      )}
    </Box>
  );
}
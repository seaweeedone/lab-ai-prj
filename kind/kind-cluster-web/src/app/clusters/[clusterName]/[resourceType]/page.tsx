'use client';

import { Box, Typography, CircularProgress, Alert, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Checkbox, FormControlLabel } from '@mui/material';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import useSWR from 'swr';
import { fetcher } from '@/lib/axios';
import { useState } from 'react';

interface ResourceData {
  apiVersion: string;
  items: any[];
}

export default function ResourceListPage() {
  const params = useParams();
  const clusterName = params.clusterName as string;
  const resourceType = params.resourceType as string;
  const [allNamespaces, setAllNamespaces] = useState(true);

  const { data, error } = useSWR<ResourceData>(
    resourceType === 'pods' ? `/clusters/${clusterName}/${resourceType}?all_namespaces=${allNamespaces}` : `/clusters/${clusterName}/${resourceType}`,
    fetcher
  );

  if (error) return <Alert severity="error">Failed to load {resourceType}.</Alert>;
  if (!data) return <CircularProgress />;

  const items = data.items || [];

  if (items.length === 0) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>{resourceType.charAt(0).toUpperCase() + resourceType.slice(1)} in {clusterName}</Typography>
        {resourceType === 'pods' && (
          <FormControlLabel
            control={<Checkbox checked={allNamespaces} onChange={(e) => setAllNamespaces(e.target.checked)} />}
            label="All Namespaces"
          />
        )}
        <Alert severity="info">No {resourceType} found.</Alert>
      </Box>
    );
  }

  // Dynamically determine table headers based on the first item
  const headers = Object.keys(items[0].metadata || {}).concat(Object.keys(items[0].spec || {})).concat(Object.keys(items[0].status || {}));
  const uniqueHeaders = Array.from(new Set(headers));

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4" gutterBottom>{resourceType.charAt(0).toUpperCase() + resourceType.slice(1)} in {clusterName}</Typography>
        {resourceType === 'pods' && (
          <FormControlLabel
            control={<Checkbox checked={allNamespaces} onChange={(e) => setAllNamespaces(e.target.checked)} />}
            label="All Namespaces"
          />
        )}
      </Box>
      <TableContainer component={Paper}>
        <Table sx={{ minWidth: 650 }} aria-label="simple table">
          <TableHead>
            <TableRow>
              {allNamespaces && <TableCell>Namespace</TableCell>}
              <TableCell>Name</TableCell>
              {uniqueHeaders.map((header) => (
                <TableCell key={header}>{header.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {items.map((item) => (
              <TableRow
                key={item.metadata.uid}
                sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
              >
                {allNamespaces && <TableCell>{item.metadata.namespace}</TableCell>}
                <TableCell component="th" scope="row">
                  <Typography component={Link} href={`/clusters/${clusterName}/${resourceType}/${item.metadata.name}?namespace=${item.metadata.namespace}`} sx={{ cursor: 'pointer', fontWeight: 'bold', textDecoration: 'none', color: 'inherit' }}>
                    {item.metadata.name}
                  </Typography>
                </TableCell>
                {uniqueHeaders.map((header) => (
                  <TableCell key={`${item.metadata.uid}-${header}`}>
                    {(() => {
                      const value = item.metadata[header] || item.spec[header] || item.status[header] || '-';
                      return typeof value === 'object' ? JSON.stringify(value) : value;
                    })()}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}
import React from 'react';
import YAML from 'yaml';
import { Box } from '@mui/material';

interface YamlViewProps {
  data: any;
}

export default function YamlView({ data }: YamlViewProps) {
  const yamlString = YAML.stringify(data);

  return (
    <Box
      component="pre"
      sx={{
        backgroundColor: '#f4f4f4',
        padding: '16px',
        borderRadius: '4px',
        overflowX: 'auto',
        whiteSpace: 'pre-wrap',
        wordBreak: 'break-all',
      }}
    >
      <code>{yamlString}</code>
    </Box>
  );
}

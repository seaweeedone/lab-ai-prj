import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ['@mui/material', '@mui/system', '@mui/icons-material', '@mui/styled-engine-sc'],
  /* config options here */
};

export default nextConfig;
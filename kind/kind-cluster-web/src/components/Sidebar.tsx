'use client';

import * as React from 'react';
import Drawer from '@mui/material/Drawer';
import Toolbar from '@mui/material/Toolbar';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Home from '@mui/icons-material/Home';
import Dns from '@mui/icons-material/Dns';
import Apps from '@mui/icons-material/Apps';
import Storage from '@mui/icons-material/Storage';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import useClusterStore from '@/hooks/useClusterStore';

const drawerWidth = 240;

export default function Sidebar() {
  const pathname = usePathname();
  const { selectedCluster, setSelectedCluster } = useClusterStore();

  // Extract clusterName from pathname if available
  React.useEffect(() => {
    const pathParts = pathname.split('/');
    if (pathParts[1] === 'clusters' && pathParts[2]) {
      setSelectedCluster(decodeURIComponent(pathParts[2]));
    } else {
      setSelectedCluster(null);
    }
  }, [pathname, setSelectedCluster]);

  const menuItems = [
    { text: 'Clusters', icon: <Home />, path: '/' },
    { text: 'Nodes', icon: <Dns />, path: selectedCluster ? `/clusters/${selectedCluster}/nodes` : '#' },
    { text: 'Pods', icon: <Apps />, path: selectedCluster ? `/clusters/${selectedCluster}/pods` : '#' },
    { text: 'Services', icon: <Storage />, path: selectedCluster ? `/clusters/${selectedCluster}/services` : '#' },
    { text: 'Deployments', icon: <Apps />, path: selectedCluster ? `/clusters/${selectedCluster}/deployments` : '#' },
  ];

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
      }}
    >
      <Toolbar />
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton component={Link} href={item.path} disabled={item.path === '#'}>
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Drawer>
  );
}
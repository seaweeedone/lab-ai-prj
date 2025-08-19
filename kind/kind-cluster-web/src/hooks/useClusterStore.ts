import { create } from 'zustand';

interface ClusterState {
  selectedCluster: string | null;
  setSelectedCluster: (clusterName: string | null) => void;
}

const useClusterStore = create<ClusterState>((set) => ({
  selectedCluster: null,
  setSelectedCluster: (clusterName) => set({ selectedCluster: clusterName }),
}));

export default useClusterStore;

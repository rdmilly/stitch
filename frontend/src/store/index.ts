import { create } from 'zustand';

interface User {
  id: string;
  email: string;
  name: string;
  avatar_url?: string;
}

interface AuthState {
  token: string | null;
  user: User | null;
  setToken: (token: string | null) => void;
  setUser: (user: User | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: typeof window !== 'undefined' ? localStorage.getItem('token') : null,
  user: null,
  setToken: (token) => {
    if (token) localStorage.setItem('token', token);
    else localStorage.removeItem('token');
    set({ token });
  },
  setUser: (user) => set({ user }),
  logout: () => {
    localStorage.removeItem('token');
    set({ token: null, user: null });
  }
}));

interface Campaign {
  id: string;
  name: string;
  description?: string;
  post_count: number;
}

interface Post {
  id: string;
  platform: string;
  content: string;
  scheduled_for?: string;
  status: string;
}

interface CampaignState {
  campaigns: Campaign[];
  currentCampaign: any | null;
  selectedPost: Post | null;
  setCampaigns: (campaigns: Campaign[]) => void;
  setCurrentCampaign: (campaign: any) => void;
  setSelectedPost: (post: Post | null) => void;
}

export const useCampaignStore = create<CampaignState>((set) => ({
  campaigns: [],
  currentCampaign: null,
  selectedPost: null,
  setCampaigns: (campaigns) => set({ campaigns }),
  setCurrentCampaign: (campaign) => set({ currentCampaign: campaign }),
  setSelectedPost: (post) => set({ selectedPost: post })
}));

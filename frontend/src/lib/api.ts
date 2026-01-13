import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
});

export const getToken = () => typeof window !== 'undefined' ? localStorage.getItem('token') : null;

export const authApi = {
  getLinkedInUrl: () => api.get('/api/auth/linkedin').then(r => r.data),
  getMe: (token: string) => api.get(`/api/auth/me?token=${token}`).then(r => r.data),
  getConnections: (token: string) => api.get(`/api/auth/connections?token=${token}`).then(r => r.data)
};

export const campaignApi = {
  list: (token: string) => api.get(`/api/campaigns?token=${token}`).then(r => r.data),
  get: (id: string, token: string) => api.get(`/api/campaigns/${id}?token=${token}`).then(r => r.data),
  create: (data: any, token: string) => api.post(`/api/campaigns?token=${token}`, data).then(r => r.data),
  generate: (id: string, data: any, token: string) => api.post(`/api/campaigns/${id}/generate?token=${token}`, data).then(r => r.data),
  updatePost: (cid: string, pid: string, data: any, token: string) => api.patch(`/api/campaigns/${cid}/posts/${pid}?token=${token}`, data).then(r => r.data),
  approvePost: (cid: string, pid: string, token: string) => api.post(`/api/campaigns/${cid}/posts/${pid}/approve?token=${token}`).then(r => r.data),
  publishPost: (cid: string, pid: string, token: string) => api.post(`/api/campaigns/${cid}/posts/${pid}/publish?token=${token}`).then(r => r.data),
  regeneratePost: (cid: string, pid: string, instruction: string, token: string) => api.post(`/api/campaigns/${cid}/posts/${pid}/regenerate?token=${token}&instruction=${encodeURIComponent(instruction)}`).then(r => r.data)
};

export default api;

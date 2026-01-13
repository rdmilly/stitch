'use client';
import { useEffect, useState } from 'react';
import { Linkedin, Plus, Sparkles, Calendar, Check, Send, RefreshCw, LogOut, ChevronRight } from 'lucide-react';
import { useAuthStore, useCampaignStore } from '@/store';
import { authApi, campaignApi } from '@/lib/api';
import { format } from 'date-fns';

export default function Dashboard() {
  const { token, user, setToken, setUser, logout } = useAuthStore();
  const { campaigns, currentCampaign, selectedPost, setCampaigns, setCurrentCampaign, setSelectedPost } = useCampaignStore();
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [showNewCampaign, setShowNewCampaign] = useState(false);
  const [newCampaign, setNewCampaign] = useState({ name: '', business_name: '', industry: '', goals: '' });

  useEffect(() => {
    const init = async () => {
      const storedToken = localStorage.getItem('token');
      if (storedToken) {
        setToken(storedToken);
        try {
          const userData = await authApi.getMe(storedToken);
          setUser(userData);
          const campaignData = await campaignApi.list(storedToken);
          setCampaigns(campaignData);
        } catch (e) {
          logout();
        }
      }
      setLoading(false);
    };
    init();
  }, []);

  const handleLogin = async () => {
    const { url } = await authApi.getLinkedInUrl();
    window.location.href = url;
  };

  const handleCreateCampaign = async () => {
    if (!token || !newCampaign.name) return;
    const campaign = await campaignApi.create({ name: newCampaign.name, platforms: ['linkedin'] }, token);
    setGenerating(true);
    await campaignApi.generate(campaign.id, {
      business_name: newCampaign.business_name || newCampaign.name,
      industry: newCampaign.industry || 'General',
      goals: newCampaign.goals || 'Increase engagement',
      weeks: 4,
      posts_per_week: 3
    }, token);
    setGenerating(false);
    const updated = await campaignApi.list(token);
    setCampaigns(updated);
    const full = await campaignApi.get(campaign.id, token);
    setCurrentCampaign(full);
    setShowNewCampaign(false);
    setNewCampaign({ name: '', business_name: '', industry: '', goals: '' });
  };

  const loadCampaign = async (id: string) => {
    if (!token) return;
    const campaign = await campaignApi.get(id, token);
    setCurrentCampaign(campaign);
    setSelectedPost(null);
  };

  const handleApprove = async (postId: string) => {
    if (!token || !currentCampaign) return;
    await campaignApi.approvePost(currentCampaign.id, postId, token);
    const updated = await campaignApi.get(currentCampaign.id, token);
    setCurrentCampaign(updated);
  };

  const handlePublish = async (postId: string) => {
    if (!token || !currentCampaign) return;
    try {
      await campaignApi.publishPost(currentCampaign.id, postId, token);
      const updated = await campaignApi.get(currentCampaign.id, token);
      setCurrentCampaign(updated);
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Failed to publish');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0f0f17]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand"></div>
      </div>
    );
  }

  if (!token || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0f0f17]">
        <div className="text-center">
          <h1 className="text-4xl font-bold mb-2 gradient-text">Content Forge</h1>
          <p className="text-gray-400 mb-8">AI-powered social media campaigns</p>
          <button
            onClick={handleLogin}
            className="flex items-center gap-3 px-6 py-3 bg-[#0077b5] hover:bg-[#006399] rounded-lg font-medium transition mx-auto"
          >
            <Linkedin size={20} />
            Sign in with LinkedIn
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0f0f17] flex">
      {/* Sidebar */}
      <div className="w-64 bg-surface-dark border-r border-gray-800 p-4 flex flex-col">
        <div className="flex items-center gap-2 mb-8">
          <Sparkles className="text-brand" size={24} />
          <span className="text-xl font-bold gradient-text">Content Forge</span>
        </div>
        
        <button
          onClick={() => setShowNewCampaign(true)}
          className="flex items-center gap-2 px-4 py-2 bg-brand hover:bg-brand-dark rounded-lg mb-4 transition"
        >
          <Plus size={18} /> New Campaign
        </button>
        
        <div className="flex-1 overflow-y-auto">
          <p className="text-xs text-gray-500 uppercase mb-2">Campaigns</p>
          {campaigns.map((c) => (
            <button
              key={c.id}
              onClick={() => loadCampaign(c.id)}
              className={`w-full text-left px-3 py-2 rounded-lg mb-1 transition ${currentCampaign?.id === c.id ? 'bg-surface text-white' : 'hover:bg-surface-light text-gray-400'}`}
            >
              <div className="font-medium truncate">{c.name}</div>
              <div className="text-xs text-gray-500">{c.post_count} posts</div>
            </button>
          ))}
        </div>
        
        <div className="border-t border-gray-800 pt-4 mt-4">
          <div className="flex items-center gap-3 mb-3">
            {user.avatar_url && <img src={user.avatar_url} className="w-8 h-8 rounded-full" />}
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium truncate">{user.name}</div>
              <div className="text-xs text-gray-500 truncate">{user.email}</div>
            </div>
          </div>
          <button onClick={logout} className="flex items-center gap-2 text-gray-400 hover:text-white text-sm">
            <LogOut size={16} /> Sign out
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-6 overflow-y-auto">
        {showNewCampaign ? (
          <div className="max-w-xl mx-auto">
            <h2 className="text-2xl font-bold mb-6">Create Campaign</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Campaign Name</label>
                <input
                  value={newCampaign.name}
                  onChange={(e) => setNewCampaign({ ...newCampaign, name: e.target.value })}
                  className="w-full px-4 py-2 bg-surface border border-gray-700 rounded-lg focus:border-brand outline-none"
                  placeholder="Q1 2026 Launch"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Business Name</label>
                <input
                  value={newCampaign.business_name}
                  onChange={(e) => setNewCampaign({ ...newCampaign, business_name: e.target.value })}
                  className="w-full px-4 py-2 bg-surface border border-gray-700 rounded-lg focus:border-brand outline-none"
                  placeholder="MW Development"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Industry</label>
                <input
                  value={newCampaign.industry}
                  onChange={(e) => setNewCampaign({ ...newCampaign, industry: e.target.value })}
                  className="w-full px-4 py-2 bg-surface border border-gray-700 rounded-lg focus:border-brand outline-none"
                  placeholder="AI & Automation Consulting"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Goals</label>
                <input
                  value={newCampaign.goals}
                  onChange={(e) => setNewCampaign({ ...newCampaign, goals: e.target.value })}
                  className="w-full px-4 py-2 bg-surface border border-gray-700 rounded-lg focus:border-brand outline-none"
                  placeholder="Build thought leadership, generate leads"
                />
              </div>
              <div className="flex gap-3 pt-4">
                <button
                  onClick={() => setShowNewCampaign(false)}
                  className="px-4 py-2 border border-gray-700 rounded-lg hover:bg-surface-light transition"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreateCampaign}
                  disabled={!newCampaign.name || generating}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-brand hover:bg-brand-dark rounded-lg transition disabled:opacity-50"
                >
                  {generating ? (
                    <><RefreshCw size={18} className="animate-spin" /> Generating...</>
                  ) : (
                    <><Sparkles size={18} /> Create & Generate Posts</>
                  )}
                </button>
              </div>
            </div>
          </div>
        ) : currentCampaign ? (
          <div>
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold">{currentCampaign.name}</h2>
                <p className="text-gray-400">{currentCampaign.posts?.length || 0} posts</p>
              </div>
            </div>
            
            <div className="grid gap-4">
              {currentCampaign.posts?.map((post: any) => (
                <div
                  key={post.id}
                  onClick={() => setSelectedPost(post)}
                  className={`p-4 bg-surface rounded-lg border cursor-pointer transition ${selectedPost?.id === post.id ? 'border-brand' : 'border-gray-800 hover:border-gray-700'}`}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <Linkedin size={16} className="text-[#0077b5]" />
                        <span className={`px-2 py-0.5 rounded text-xs ${post.status === 'published' ? 'bg-green-500/20 text-green-400' : post.status === 'approved' ? 'bg-blue-500/20 text-blue-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
                          {post.status}
                        </span>
                        {post.scheduled_for && (
                          <span className="text-xs text-gray-500 flex items-center gap-1">
                            <Calendar size={12} />
                            {format(new Date(post.scheduled_for), 'MMM d, h:mm a')}
                          </span>
                        )}
                      </div>
                      <p className="text-gray-300 line-clamp-2">{post.content}</p>
                    </div>
                    <div className="flex gap-2">
                      {post.status === 'pending' && (
                        <button
                          onClick={(e) => { e.stopPropagation(); handleApprove(post.id); }}
                          className="p-2 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-lg transition"
                          title="Approve"
                        >
                          <Check size={16} />
                        </button>
                      )}
                      {post.status === 'approved' && (
                        <button
                          onClick={(e) => { e.stopPropagation(); handlePublish(post.id); }}
                          className="p-2 bg-brand/20 hover:bg-brand/30 text-brand-light rounded-lg transition"
                          title="Publish Now"
                        >
                          <Send size={16} />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <Sparkles size={48} className="text-gray-600 mb-4" />
            <h2 className="text-xl font-medium mb-2">Welcome to Content Forge</h2>
            <p className="text-gray-400 mb-6">Create your first campaign to get started</p>
            <button
              onClick={() => setShowNewCampaign(true)}
              className="flex items-center gap-2 px-4 py-2 bg-brand hover:bg-brand-dark rounded-lg transition"
            >
              <Plus size={18} /> Create Campaign
            </button>
          </div>
        )}
      </div>

      {/* Detail Panel */}
      {selectedPost && (
        <div className="w-96 bg-surface-dark border-l border-gray-800 p-6 overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold">Post Details</h3>
            <button onClick={() => setSelectedPost(null)} className="text-gray-400 hover:text-white">
              ×
            </button>
          </div>
          
          <div className="mb-4">
            <span className={`px-2 py-1 rounded text-xs ${selectedPost.status === 'published' ? 'bg-green-500/20 text-green-400' : selectedPost.status === 'approved' ? 'bg-blue-500/20 text-blue-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
              {selectedPost.status}
            </span>
          </div>
          
          {selectedPost.scheduled_for && (
            <div className="flex items-center gap-2 text-sm text-gray-400 mb-4">
              <Calendar size={14} />
              {format(new Date(selectedPost.scheduled_for), 'EEEE, MMMM d, yyyy h:mm a')}
            </div>
          )}
          
          <div className="bg-surface p-4 rounded-lg mb-4">
            <p className="whitespace-pre-wrap">{selectedPost.content}</p>
          </div>
          
          <div className="space-y-2">
            {selectedPost.status === 'pending' && (
              <button
                onClick={() => handleApprove(selectedPost.id)}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-lg transition"
              >
                <Check size={18} /> Approve Post
              </button>
            )}
            {selectedPost.status === 'approved' && (
              <button
                onClick={() => handlePublish(selectedPost.id)}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-brand hover:bg-brand-dark rounded-lg transition"
              >
                <Send size={18} /> Publish to LinkedIn
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

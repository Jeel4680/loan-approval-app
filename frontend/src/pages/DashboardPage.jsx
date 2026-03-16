import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getMyApplications } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { PlusCircle, LogOut, Clock, CheckCircle, XCircle } from 'lucide-react';

const statusConfig = {
  approved: { color: 'text-emerald-400', bg: 'rgba(16,185,129,0.1)', border: 'rgba(16,185,129,0.2)', icon: <CheckCircle size={14}/> },
  denied:   { color: 'text-red-400',     bg: 'rgba(239,68,68,0.1)',   border: 'rgba(239,68,68,0.2)',   icon: <XCircle size={14}/> },
  review:   { color: 'text-amber-400',   bg: 'rgba(245,158,11,0.1)',  border: 'rgba(245,158,11,0.2)',  icon: <Clock size={14}/> },
  pending:  { color: 'text-sky-400',     bg: 'rgba(14,165,233,0.1)',  border: 'rgba(14,165,233,0.2)',  icon: <Clock size={14}/> },
};

export default function DashboardPage() {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user, logoutUser } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    getMyApplications()
      .then(res => setApplications(res.data.applications || []))
      .finally(() => setLoading(false));
  }, []);

  const stats = {
    total: applications.length,
    approved: applications.filter(a => a.status === 'approved').length,
    pending: applications.filter(a => ['pending', 'review'].includes(a.status)).length,
    denied: applications.filter(a => a.status === 'denied').length,
  };

  return (
    <div className="min-h-screen" style={{ background: 'radial-gradient(ellipse at top, #0c2340 0%, #0a0f1e 60%)' }}>
      {/* Navbar */}
      <nav className="glass border-b border-white/10 px-6 py-4">
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-3">
            <span className="text-xl">💰</span>
            <span className="font-display text-xl text-white">LoanIQ</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-slate-400 text-sm">Welcome, <span className="text-white font-medium">{user?.full_name}</span></span>
            <button onClick={() => { logoutUser(); navigate('/login'); }}
              className="flex items-center gap-2 text-slate-400 hover:text-white text-sm transition-colors">
              <LogOut size={16}/> Logout
            </button>
          </div>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-6 py-10">
        {/* Header */}
        <div className="flex justify-between items-start mb-10 fade-up">
          <div>
            <h1 className="font-display text-4xl text-white mb-2">Your Applications</h1>
            <p className="text-slate-400">Track and manage your loan applications</p>
          </div>
          <button onClick={() => navigate('/apply')}
            className="flex items-center gap-2 px-5 py-3 rounded-xl font-medium text-sm text-white transition-all"
            style={{ background: 'linear-gradient(135deg, #0ea5e9, #0369a1)' }}>
            <PlusCircle size={16}/> New Application
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
          {[
            { label: 'Total', value: stats.total, color: '#0ea5e9' },
            { label: 'Approved', value: stats.approved, color: '#10b981' },
            { label: 'In Review', value: stats.pending, color: '#f59e0b' },
            { label: 'Denied', value: stats.denied, color: '#ef4444' },
          ].map((stat, i) => (
            <div key={stat.label}
              className={`glass rounded-2xl p-5 fade-up-delay-${i}`}>
              <p className="text-slate-400 text-xs uppercase tracking-wider mb-2">{stat.label}</p>
              <p className="text-3xl font-bold" style={{ color: stat.color }}>{stat.value}</p>
            </div>
          ))}
        </div>

        {/* Applications List */}
        {loading ? (
          <div className="text-center py-20 text-slate-400">Loading applications...</div>
        ) : applications.length === 0 ? (
          <div className="glass rounded-2xl p-16 text-center fade-up">
            <div className="text-5xl mb-4">📋</div>
            <h3 className="font-display text-2xl text-white mb-2">No applications yet</h3>
            <p className="text-slate-400 mb-6">Start by submitting your first loan application</p>
            <button onClick={() => navigate('/apply')}
              className="px-6 py-3 rounded-xl text-white font-medium text-sm"
              style={{ background: 'linear-gradient(135deg, #0ea5e9, #0369a1)' }}>
              Apply Now
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {applications.map((app, i) => {
              const config = statusConfig[app.status] || statusConfig.pending;
              return (
                <div key={app.id}
                  onClick={() => navigate(`/result/${app.id}`)}
                  className={`glass rounded-2xl p-6 cursor-pointer card-hover fade-up-delay-${Math.min(i, 3)}`}>
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-white font-semibold">{app.loan_purpose}</h3>
                        <span className="px-2.5 py-1 rounded-full text-xs font-medium flex items-center gap-1"
                          style={{ color: config.color, background: config.bg, border: `1px solid ${config.border}` }}>
                          {config.icon} {app.status.toUpperCase()}
                        </span>
                      </div>
                      <div className="flex items-center gap-6 text-sm text-slate-400">
                        <span>💵 ${app.loan_amount?.toLocaleString()}</span>
                        <span>📅 {app.loan_term_months} months</span>
                        <span>💼 {app.employment_type}</span>
                        <span>📊 {app.income_records_count} months data</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-slate-500 text-xs">Application #{app.id}</p>
                      <p className="text-sky-400 text-sm mt-1 font-medium">View Details →</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

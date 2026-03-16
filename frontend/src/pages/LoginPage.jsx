import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login, register, getMe } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function LoginPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [form, setForm] = useState({ full_name: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { loginUser } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (!isLogin) {
        await register(form);
      }
      const res = await login({ email: form.email, password: form.password });
      const token = res.data.access_token;

      // ✅ Store token FIRST before calling getMe
      localStorage.setItem('token', token);

      const userRes = await getMe();
      loginUser(token, userRes.data);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4"
      style={{ background: 'radial-gradient(ellipse at top, #0c2340 0%, #0a0f1e 60%)' }}>

      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-sky-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-blue-500/5 rounded-full blur-3xl" />
      </div>

      <div className="w-full max-w-md relative z-10 fade-up">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl mb-4"
            style={{ background: 'linear-gradient(135deg, #0ea5e9, #0369a1)' }}>
            <span className="text-2xl">💰</span>
          </div>
          <h1 className="font-display text-4xl text-white mb-2">LoanIQ</h1>
          <p className="text-slate-400 text-sm">Smart loans for unstable income earners</p>
        </div>

        <div className="glass rounded-2xl p-8">
          <div className="flex rounded-xl overflow-hidden mb-6 p-1"
            style={{ background: 'rgba(255,255,255,0.05)' }}>
            {['Login', 'Register'].map((tab) => (
              <button key={tab}
                onClick={() => { setIsLogin(tab === 'Login'); setError(''); }}
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isLogin === (tab === 'Login')
                    ? 'bg-sky-500 text-white shadow-lg'
                    : 'text-slate-400 hover:text-white'
                }`}>{tab}</button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <div>
                <label className="block text-xs text-slate-400 mb-1.5 font-medium uppercase tracking-wider">Full Name</label>
                <input type="text" placeholder="Jeel Patel"
                  value={form.full_name}
                  onChange={e => setForm({...form, full_name: e.target.value})}
                  className="w-full px-4 py-3 rounded-xl text-white text-sm outline-none"
                  style={{ background: 'rgba(255,255,255,0.07)', border: '1px solid rgba(255,255,255,0.1)' }}
                  required />
              </div>
            )}

            <div>
              <label className="block text-xs text-slate-400 mb-1.5 font-medium uppercase tracking-wider">Email</label>
              <input type="email" placeholder="you@example.com"
                value={form.email}
                onChange={e => setForm({...form, email: e.target.value})}
                className="w-full px-4 py-3 rounded-xl text-white text-sm outline-none"
                style={{ background: 'rgba(255,255,255,0.07)', border: '1px solid rgba(255,255,255,0.1)' }}
                required />
            </div>

            <div>
              <label className="block text-xs text-slate-400 mb-1.5 font-medium uppercase tracking-wider">Password</label>
              <input type="password" placeholder="••••••••"
                value={form.password}
                onChange={e => setForm({...form, password: e.target.value})}
                className="w-full px-4 py-3 rounded-xl text-white text-sm outline-none"
                style={{ background: 'rgba(255,255,255,0.07)', border: '1px solid rgba(255,255,255,0.1)' }}
                required />
            </div>

            {error && (
              <div className="px-4 py-3 rounded-xl text-sm text-red-300"
                style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)' }}>
                {error}
              </div>
            )}

            <button type="submit" disabled={loading}
              className="w-full py-3 rounded-xl font-semibold text-white text-sm transition-all duration-200 mt-2"
              style={{ background: loading ? 'rgba(14,165,233,0.5)' : 'linear-gradient(135deg, #0ea5e9, #0369a1)' }}>
              {loading ? 'Please wait...' : isLogin ? 'Sign In' : 'Create Account'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

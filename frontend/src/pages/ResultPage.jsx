import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getDecision, mlEvaluate } from '../services/api';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { ArrowLeft, CheckCircle, XCircle, Clock, Brain } from 'lucide-react';

export default function ResultPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [decision, setDecision] = useState(null);
  const [mlData, setMlData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDecision(id)
      .then(res => setDecision(res.data))
      .finally(() => setLoading(false));

    mlEvaluate(id)
      .then(res => setMlData(res.data))
      .catch(() => {});
  }, [id]);

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center"
      style={{ background: '#0a0f1e' }}>
      <div className="text-center">
        <div className="text-4xl mb-4">🔄</div>
        <p className="text-slate-400">Analyzing your application...</p>
      </div>
    </div>
  );

  if (!decision) return null;

  
  
  

  const decisionConfig = {
    APPROVED: { color: '#10b981', bg: 'rgba(16,185,129,0.1)', border: 'rgba(16,185,129,0.3)', icon: <CheckCircle size={24}/>, label: 'Approved' },
    DENIED:   { color: '#ef4444', bg: 'rgba(239,68,68,0.1)',   border: 'rgba(239,68,68,0.3)',   icon: <XCircle size={24}/>,   label: 'Denied' },
    REVIEW:   { color: '#f59e0b', bg: 'rgba(245,158,11,0.1)',  border: 'rgba(245,158,11,0.3)',  icon: <Clock size={24}/>,     label: 'Under Review' },
  };

  const config = decisionConfig[decision.decision] || decisionConfig.REVIEW;

  // Build income chart data
  const incomeData = (decision.income_history || []).map((amount, i) => ({
    month: `Month ${i+1}`,
    income: amount,
    avg: decision.average_monthly_income
  }));

  return (
    <div className="min-h-screen px-4 py-10"
      style={{ background: 'radial-gradient(ellipse at top, #0c2340 0%, #0a0f1e 60%)' }}>
      <div className="max-w-3xl mx-auto">
        {/* Back button */}
        <button onClick={() => navigate('/dashboard')}
          className="flex items-center gap-2 text-slate-400 hover:text-white mb-8 transition-colors fade-up">
          <ArrowLeft size={16}/> Back to Dashboard
        </button>

        {/* Decision Banner */}
        <div className="glass rounded-2xl p-8 mb-6 text-center fade-up"
          style={{ border: `1px solid ${config.border}` }}>
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full mb-4"
            style={{ background: config.bg, color: config.color }}>
            {config.icon}
          </div>
          <h1 className="font-display text-4xl text-white mb-2">{config.label}</h1>
          <p className="text-slate-400 text-sm mb-4">Application #{id} · {decision.loan_purpose}</p>
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium"
            style={{ background: config.bg, color: config.color, border: `1px solid ${config.border}` }}>
            Stability Score: {decision.stability_score}/100
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {[
            { label: 'Loan Amount', value: `$${decision.loan_amount?.toLocaleString()}` },
            { label: 'Monthly Payment', value: `$${decision.interest_details?.monthly_payment?.toFixed(2)}` },
            { label: 'Interest Rate', value: decision.interest_details?.annual_interest_rate },
            { label: 'Total Interest', value: `$${decision.interest_details?.total_interest_paid?.toLocaleString()}` },
          ].map((metric, i) => (
            <div key={metric.label} className={`glass rounded-2xl p-4 fade-up-delay-${i}`}>
              <p className="text-slate-400 text-xs uppercase tracking-wider mb-1">{metric.label}</p>
              <p className="text-white font-semibold text-lg">{metric.value}</p>
            </div>
          ))}
        </div>

        {/* Income Chart */}
        {incomeData.length > 0 && (
          <div className="glass rounded-2xl p-6 mb-6 fade-up-delay-1">
            <h3 className="font-display text-xl text-white mb-4">Income History</h3>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={incomeData}>
                <defs>
                  <linearGradient id="incomeGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#0ea5e9" stopOpacity={0.3}/>
                    <stop offset="100%" stopColor="#0ea5e9" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="month" stroke="#475569" tick={{ fill: '#94a3b8', fontSize: 11 }}/>
                <YAxis stroke="#475569" tick={{ fill: '#94a3b8', fontSize: 11 }}
                  tickFormatter={v => `$${(v/1000).toFixed(0)}k`}/>
                <Tooltip
                  contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#f1f5f9' }}
                  formatter={(v) => [`$${v.toLocaleString()}`, 'Income']}/>
                <Area type="monotone" dataKey="income" stroke="#0ea5e9" fill="url(#incomeGrad)" strokeWidth={2}/>
                <Area type="monotone" dataKey="avg" stroke="#f59e0b" fill="none" strokeWidth={1} strokeDasharray="4 4"/>
              </AreaChart>
            </ResponsiveContainer>
            <p className="text-slate-500 text-xs mt-2">Blue = monthly income · Orange dashed = average</p>
          </div>
        )}

        {/* Score Breakdown */}
        <div className="glass rounded-2xl p-6 mb-6 fade-up-delay-2">
          <h3 className="font-display text-xl text-white mb-5">Score Breakdown</h3>
          <div className="space-y-4">
            {[
              { label: 'Income Stability', value: decision.stability_score, max: 100, color: '#0ea5e9' },
              { label: 'Debt-to-Income Ratio', value: Math.max(0, 100 - decision.debt_to_income_ratio), max: 100, color: '#10b981', note: `${decision.debt_to_income_ratio}% DTI` },
            ].map(item => (
              <div key={item.label}>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-slate-300">{item.label}</span>
                  <span className="text-white font-medium">{item.note || `${item.value}/100`}</span>
                </div>
                <div className="h-2 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.1)' }}>
                  <div className="h-full rounded-full transition-all duration-1000"
                    style={{ width: `${Math.min(item.value, 100)}%`, background: item.color }}/>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ML Comparison */}
        {mlData && (
          <div className="glass rounded-2xl p-6 mb-6 fade-up-delay-3">
            <div className="flex items-center gap-2 mb-5">
              <Brain size={18} className="text-sky-400"/>
              <h3 className="font-display text-xl text-white">AI Model Comparison</h3>
            </div>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="p-4 rounded-xl" style={{ background: 'rgba(255,255,255,0.03)' }}>
                <p className="text-slate-400 text-xs mb-1">Rule-Based Decision</p>
                <p className="text-white font-semibold">{mlData.comparison?.rule_based_decision}</p>
              </div>
              <div className="p-4 rounded-xl" style={{ background: 'rgba(255,255,255,0.03)' }}>
                <p className="text-slate-400 text-xs mb-1">ML Model Decision</p>
                <p className="text-sky-400 font-semibold">{mlData.comparison?.ml_decision}</p>
              </div>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <span className={mlData.comparison?.decisions_agree ? 'text-emerald-400' : 'text-amber-400'}>
                {mlData.comparison?.decisions_agree ? '✅ Both models agree' : '⚠️ Models disagree'}
              </span>
              <span className="text-slate-500">·</span>
              <span className="text-slate-400">{mlData.ml_details?.model_type}</span>
              <span className="text-slate-500">·</span>
              <span className="text-slate-400">{mlData.ml_details?.confidence_in_decision} confidence</span>
            </div>
          </div>
        )}

        {/* Reasoning */}
        <div className="glass rounded-2xl p-6 fade-up-delay-3">
          <h3 className="font-display text-xl text-white mb-4">Decision Reasoning</h3>
          <div className="space-y-2">
            {(decision.reasoning || '').split('|').map((reason, i) => (
              <div key={i} className="flex items-start gap-2 text-sm text-slate-300 py-2 border-b border-white/5 last:border-0">
                <span className="text-sky-400 mt-0.5 shrink-0">→</span>
                <span>{reason.trim()}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

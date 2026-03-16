import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { applyForLoan, evaluateLoan } from '../services/api';
import { PlusCircle, Trash2, ArrowLeft, ChevronRight } from 'lucide-react';

const EMPLOYMENT_TYPES = ['freelancer', 'gig_worker', 'part_time', 'full_time', 'seasonal'];
const LOAN_PURPOSES = ['Home Renovation', 'Business', 'Education', 'Car', 'Emergency', 'Debt Consolidation', 'Other'];

export default function ApplyPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({
    loan_amount: '',
    loan_purpose: '',
    loan_term_months: 24,
    employment_type: 'freelancer',
  });
  const [incomeRecords, setIncomeRecords] = useState([
    { month_year: '', amount: '', source: '' },
    { month_year: '', amount: '', source: '' },
    { month_year: '', amount: '', source: '' },
  ]);

  const addIncomeRecord = () => {
    setIncomeRecords([...incomeRecords, { month_year: '', amount: '', source: '' }]);
  };

  const removeIncomeRecord = (index) => {
    if (incomeRecords.length <= 3) return;
    setIncomeRecords(incomeRecords.filter((_, i) => i !== index));
  };

  const updateRecord = (index, field, value) => {
    const updated = [...incomeRecords];
    updated[index][field] = value;
    setIncomeRecords(updated);
  };

  const handleSubmit = async () => {
    setError('');
    setLoading(true);
    try {
      const payload = {
        ...form,
        loan_amount: parseFloat(form.loan_amount),
        loan_term_months: parseInt(form.loan_term_months),
        income_records: incomeRecords
          .filter(r => r.month_year && r.amount)
          .map(r => ({ ...r, amount: parseFloat(r.amount) }))
      };
      const res = await applyForLoan(payload);
      const appId = res.data.application_id;
      await evaluateLoan(appId);
      navigate(`/result/${appId}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit application.');
    } finally {
      setLoading(false);
    }
  };

  const inputClass = "w-full px-4 py-3 rounded-xl text-white text-sm outline-none transition-all";
  const inputStyle = { background: 'rgba(255,255,255,0.07)', border: '1px solid rgba(255,255,255,0.1)' };
  const labelClass = "block text-xs text-slate-400 mb-1.5 font-medium uppercase tracking-wider";

  return (
    <div className="min-h-screen px-4 py-10"
      style={{ background: 'radial-gradient(ellipse at top, #0c2340 0%, #0a0f1e 60%)' }}>
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8 fade-up">
          <button onClick={() => navigate('/dashboard')}
            className="p-2 glass rounded-xl text-slate-400 hover:text-white transition-colors">
            <ArrowLeft size={18}/>
          </button>
          <div>
            <h1 className="font-display text-3xl text-white">Apply for a Loan</h1>
            <p className="text-slate-400 text-sm">Step {step} of 2</p>
          </div>
        </div>

        {/* Progress */}
        <div className="flex gap-2 mb-8">
          {[1,2].map(s => (
            <div key={s} className="flex-1 h-1 rounded-full overflow-hidden"
              style={{ background: 'rgba(255,255,255,0.1)' }}>
              <div className="h-full rounded-full transition-all duration-500"
                style={{ background: 'linear-gradient(90deg, #0ea5e9, #0369a1)', width: step >= s ? '100%' : '0%' }}/>
            </div>
          ))}
        </div>

        <div className="glass rounded-2xl p-8 fade-up-delay-1">
          {step === 1 ? (
            <div className="space-y-5">
              <h2 className="font-display text-xl text-white mb-6">Loan Details</h2>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className={labelClass}>Loan Amount ($)</label>
                  <input type="number" placeholder="15000"
                    value={form.loan_amount}
                    onChange={e => setForm({...form, loan_amount: e.target.value})}
                    className={inputClass} style={inputStyle}/>
                </div>
                <div>
                  <label className={labelClass}>Term (Months)</label>
                  <select value={form.loan_term_months}
                    onChange={e => setForm({...form, loan_term_months: parseInt(e.target.value)})}
                    className={inputClass} style={inputStyle}>
                    {[12, 24, 36, 48, 60].map(t => (
                      <option key={t} value={t} style={{background:'#1a2035'}}>{t} months</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className={labelClass}>Loan Purpose</label>
                <select value={form.loan_purpose}
                  onChange={e => setForm({...form, loan_purpose: e.target.value})}
                  className={inputClass} style={inputStyle}>
                  <option value="" style={{background:'#1a2035'}}>Select purpose...</option>
                  {LOAN_PURPOSES.map(p => (
                    <option key={p} value={p} style={{background:'#1a2035'}}>{p}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className={labelClass}>Employment Type</label>
                <div className="grid grid-cols-2 gap-2">
                  {EMPLOYMENT_TYPES.map(type => (
                    <button key={type} type="button"
                      onClick={() => setForm({...form, employment_type: type})}
                      className="py-2.5 px-4 rounded-xl text-sm font-medium transition-all text-left"
                      style={{
                        background: form.employment_type === type ? 'rgba(14,165,233,0.2)' : 'rgba(255,255,255,0.05)',
                        border: `1px solid ${form.employment_type === type ? 'rgba(14,165,233,0.5)' : 'rgba(255,255,255,0.1)'}`,
                        color: form.employment_type === type ? '#0ea5e9' : '#94a3b8'
                      }}>
                      {type.replace('_', ' ')}
                    </button>
                  ))}
                </div>
              </div>

              <button
                onClick={() => { if(!form.loan_amount || !form.loan_purpose) { setError('Please fill all fields'); return; } setError(''); setStep(2); }}
                className="w-full py-3 rounded-xl font-semibold text-white text-sm flex items-center justify-center gap-2 mt-2"
                style={{ background: 'linear-gradient(135deg, #0ea5e9, #0369a1)' }}>
                Next: Income History <ChevronRight size={16}/>
              </button>
              {error && <p className="text-red-400 text-sm text-center">{error}</p>}
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex justify-between items-center mb-6">
                <h2 className="font-display text-xl text-white">Income History</h2>
                <span className="text-slate-400 text-sm">Min. 3 months required</span>
              </div>

              {incomeRecords.map((record, i) => (
                <div key={i} className="p-4 rounded-xl" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)' }}>
                  <div className="flex justify-between items-center mb-3">
                    <span className="text-slate-400 text-xs font-medium">Month {i+1}</span>
                    {i >= 3 && (
                      <button onClick={() => removeIncomeRecord(i)} className="text-red-400 hover:text-red-300">
                        <Trash2 size={14}/>
                      </button>
                    )}
                  </div>
                  <div className="grid grid-cols-3 gap-3">
                    <div>
                      <label className="block text-xs text-slate-500 mb-1">Month (YYYY-MM)</label>
                      <input type="text" placeholder="2024-01"
                        value={record.month_year}
                        onChange={e => updateRecord(i, 'month_year', e.target.value)}
                        className="w-full px-3 py-2 rounded-lg text-white text-sm outline-none"
                        style={inputStyle}/>
                    </div>
                    <div>
                      <label className="block text-xs text-slate-500 mb-1">Amount ($)</label>
                      <input type="number" placeholder="3000"
                        value={record.amount}
                        onChange={e => updateRecord(i, 'amount', e.target.value)}
                        className="w-full px-3 py-2 rounded-lg text-white text-sm outline-none"
                        style={inputStyle}/>
                    </div>
                    <div>
                      <label className="block text-xs text-slate-500 mb-1">Source</label>
                      <input type="text" placeholder="Freelance"
                        value={record.source}
                        onChange={e => updateRecord(i, 'source', e.target.value)}
                        className="w-full px-3 py-2 rounded-lg text-white text-sm outline-none"
                        style={inputStyle}/>
                    </div>
                  </div>
                </div>
              ))}

              <button onClick={addIncomeRecord}
                className="w-full py-2.5 rounded-xl text-sky-400 text-sm font-medium flex items-center justify-center gap-2 transition-colors hover:text-sky-300"
                style={{ background: 'rgba(14,165,233,0.05)', border: '1px dashed rgba(14,165,233,0.3)' }}>
                <PlusCircle size={14}/> Add Another Month
              </button>

              {error && (
                <div className="px-4 py-3 rounded-xl text-sm text-red-300"
                  style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)' }}>
                  {error}
                </div>
              )}

              <div className="flex gap-3 pt-2">
                <button onClick={() => setStep(1)}
                  className="flex-1 py-3 rounded-xl text-slate-400 text-sm font-medium transition-colors hover:text-white"
                  style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)' }}>
                  Back
                </button>
                <button onClick={handleSubmit} disabled={loading}
                  className="flex-1 py-3 rounded-xl font-semibold text-white text-sm"
                  style={{ background: loading ? 'rgba(14,165,233,0.5)' : 'linear-gradient(135deg, #0ea5e9, #0369a1)' }}>
                  {loading ? 'Analyzing...' : 'Submit & Get Decision'}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

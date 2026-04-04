import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import { getFarmHistory, addFarmHistory } from '../api';
import { Sprout, TrendingUp, Wallet, MapPin, Ruler, Droplets, Plus, X, LineChart as LucideLineChart } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';

export default function Dashboard() {
  const [farmer, setFarmer] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newRecord, setNewRecord] = useState({
    crop: '', season: 'Kharif', year: new Date().getFullYear(), yield_kg: '', income: '', notes: ''
  });
  const navigate = useNavigate();

  useEffect(() => {
    const data = localStorage.getItem('farmer');
    if (!data) {
      navigate('/login');
      return;
    }
    const parsedFarmer = JSON.parse(data);
    setFarmer(parsedFarmer);
    fetchHistory(parsedFarmer.id);
  }, [navigate]);

  const fetchHistory = async (fid) => {
    try {
      const res = await getFarmHistory(fid);
      const sortedHistory = (res.data.history || []).sort((a, b) => a.year - b.year);
      setHistory(sortedHistory);
    } catch (e) {
      console.error("Failed to fetch history", e);
    } finally {
      setLoading(false);
    }
  };

  const handleAddSubmit = async (e) => {
    e.preventDefault();
    try {
      await addFarmHistory({ ...newRecord, farmer_id: farmer.id });
      setShowAddForm(false);
      setNewRecord({ crop: '', season: 'Kharif', year: new Date().getFullYear(), yield_kg: '', income: '', notes: '' });
      fetchHistory(farmer.id);
    } catch (e) {
      alert("Failed to add record");
    }
  };

  if (!farmer) return null;

  // Prepare chart data
  const chartData = history.map(h => ({
    name: `${h.year} ${h.season}`,
    income: h.income,
    yield: h.yield_kg
  }));

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-8">
        <div className="max-w-6xl mx-auto">
          <header className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Welcome back, {farmer.name}! 🌾</h1>
              <p className="text-gray-600 mt-1">Monitor your farm's performance and past history.</p>
            </div>
            <button 
              onClick={() => setShowAddForm(true)}
              className="btn-primary flex items-center gap-2"
            >
              <Plus size={20} /> Add Crop Record
            </button>
          </header>

          {/* Profile Stats */}
          <div className="grid gap-6 md:grid-cols-3 mb-10">
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center gap-4">
              <div className="bg-blue-50 p-3 rounded-xl text-blue-600"><MapPin size={24} /></div>
              <div>
                <p className="text-sm text-gray-500 font-medium">Location</p>
                <p className="text-lg font-bold text-gray-900">{farmer.location}</p>
              </div>
            </div>
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center gap-4">
              <div className="bg-green-50 p-3 rounded-xl text-green-600"><Ruler size={24} /></div>
              <div>
                <p className="text-sm text-gray-500 font-medium">Land Size</p>
                <p className="text-lg font-bold text-gray-900">{farmer.land_size} ha</p>
              </div>
            </div>
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center gap-4">
              <div className="bg-cyan-50 p-3 rounded-xl text-cyan-600"><Droplets size={24} /></div>
              <div>
                <p className="text-sm text-gray-500 font-medium">Water Source</p>
                <p className="text-lg font-bold text-gray-900">{farmer.water_source}</p>
              </div>
            </div>
          </div>

          {/* Graph Section */}
          <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 mb-10">
            <div className="flex items-center gap-2 mb-6">
              <LucideLineChart className="text-brand-600" />
              <h2 className="text-xl font-bold text-gray-900">Income & Yield Insights</h2>
            </div>
            <div className="h-80 w-full">
              {history.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData}>
                    <defs>
                      <linearGradient id="colorIncome" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#16a34a" stopOpacity={0.1}/>
                        <stop offset="95%" stopColor="#16a34a" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                    <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#9ca3af', fontSize: 12}} dy={10} />
                    <YAxis axisLine={false} tickLine={false} tick={{fill: '#9ca3af', fontSize: 12}} />
                    <Tooltip 
                      contentStyle={{borderRadius: '12px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)'}}
                    />
                    <Area type="monotone" dataKey="income" stroke="#16a34a" strokeWidth={3} fillOpacity={1} fill="url(#colorIncome)" />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex items-center justify-center text-gray-400 border-2 border-dashed border-gray-100 rounded-xl">
                  Add more records to see performance trends.
                </div>
              )}
            </div>
          </div>

          {/* Crop History Table */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden mb-10">
            <div className="p-6 border-b border-gray-100 flex justify-between items-center">
              <div className="flex items-center gap-2">
                <Sprout className="text-brand-600" />
                <h2 className="text-xl font-bold text-gray-900">Crop History</h2>
              </div>
              <span className="text-sm text-gray-500 font-medium">{history.length} Seasons Recorded</span>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead className="bg-gray-50 text-gray-500 text-xs uppercase tracking-wider">
                  <tr>
                    <th className="px-6 py-4 font-semibold">Year / Season</th>
                    <th className="px-6 py-4 font-semibold">Crop</th>
                    <th className="px-6 py-4 font-semibold text-right">Yield (kg)</th>
                    <th className="px-6 py-4 font-semibold text-right">Income (₹)</th>
                    <th className="px-6 py-4 font-semibold">Notes</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {loading ? (
                    <tr><td colSpan="5" className="px-6 py-10 text-center text-gray-400">Loading history...</td></tr>
                  ) : history.length === 0 ? (
                    <tr><td colSpan="5" className="px-6 py-10 text-center text-gray-400">No crop history found.</td></tr>
                  ) : [...history].reverse().map((row, idx) => (
                    <tr key={idx} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4">
                        <div className="font-bold text-gray-900">{row.year}</div>
                        <div className="text-sm text-gray-500">{row.season}</div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-brand-50 text-brand-700">
                          {row.crop}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right font-medium">{row.yield_kg?.toLocaleString() || '-'}</td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end text-green-600 font-bold">
                          {row.income ? `₹${row.income.toLocaleString()}` : '-'}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500 italic">
                        {row.notes || 'No notes'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* CTA to Chat */}
          <div className="bg-brand-900 rounded-3xl p-8 text-white relative overflow-hidden shadow-2xl">
            <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-6">
              <div className="max-w-lg text-center md:text-left">
                <h2 className="text-2xl font-bold mb-2">Need advice for the next season?</h2>
                <p className="text-brand-100 opacity-90">
                  Talk to Digital Sarathi to get tailored recommendations based on your soil, budget, and past history.
                </p>
              </div>
              <button 
                onClick={() => navigate('/chat')}
                className="bg-white text-brand-900 font-bold px-8 py-4 rounded-2xl hover:bg-brand-50 transition-all flex items-center gap-2 shadow-lg"
              >
                Go to Consultant Chat 💬
              </button>
            </div>
          </div>
        </div>

        {/* Add Record Modal */}
        {showAddForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-3xl w-full max-w-lg p-8 shadow-2xl">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Add Crop History</h2>
                <button onClick={() => setShowAddForm(false)} className="text-gray-400 hover:text-gray-600"><X /></button>
              </div>
              <form onSubmit={handleAddSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-500 mb-1">Crop Name</label>
                    <input required placeholder="e.g., Wheat" value={newRecord.crop} onChange={e => setNewRecord({...newRecord, crop: e.target.value})} className="input-field" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-500 mb-1">Season</label>
                    <select value={newRecord.season} onChange={e => setNewRecord({...newRecord, season: e.target.value})} className="input-field">
                      <option>Kharif</option>
                      <option>Rabi</option>
                      <option>Zaid</option>
                    </select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-500 mb-1">Year</label>
                    <input required type="number" value={newRecord.year} onChange={e => setNewRecord({...newRecord, year: e.target.value})} className="input-field" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-500 mb-1">Yield (kg)</label>
                    <input type="number" placeholder="1200" value={newRecord.yield_kg} onChange={e => setNewRecord({...newRecord, yield_kg: e.target.value})} className="input-field" />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-1">Income (₹)</label>
                  <input type="number" placeholder="45000" value={newRecord.income} onChange={e => setNewRecord({...newRecord, income: e.target.value})} className="input-field" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-1">Notes</label>
                  <textarea placeholder="Any observations..." value={newRecord.notes} onChange={e => setNewRecord({...newRecord, notes: e.target.value})} className="input-field h-20" />
                </div>
                <button type="submit" className="btn-primary w-full py-3 text-lg mt-4">Save Record</button>
              </form>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

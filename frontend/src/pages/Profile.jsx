import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import { updateProfile } from '../api';
import { Save, User, MapPin, Ruler, Droplets, Wallet, ShieldCheck, Tractor } from 'lucide-react';

export default function Profile() {
  const [farmer, setFarmer] = useState(null);
  const [formData, setFormData] = useState({});
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const data = localStorage.getItem('farmer');
    if (!data) {
      navigate('/login');
      return;
    }
    const parsedFarmer = JSON.parse(data);
    setFarmer(parsedFarmer);
    setFormData(parsedFarmer);
  }, [navigate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    try {
      const res = await updateProfile(farmer.id, formData);
      localStorage.setItem('farmer', JSON.stringify(res.data.farmer));
      setFarmer(res.data.farmer);
      setMessage('Profile updated successfully! ✅');
      setTimeout(() => setMessage(''), 3000);
    } catch (err) {
      setMessage('Failed to update profile. ❌');
    } finally {
      setLoading(false);
    }
  };

  if (!farmer) return null;

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-8">
        <div className="max-w-4xl mx-auto">
          <header className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">My Profile</h1>
            <p className="text-gray-600 mt-1">Manage your personal and agricultural configurations.</p>
          </header>

          <form onSubmit={handleSubmit} className="space-y-6">
            {message && (
              <div className={`p-4 rounded-xl text-center font-medium ${message.includes('success') ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                {message}
              </div>
            )}

            <div className="grid gap-6 md:grid-cols-2">
              {/* Basic Info */}
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 space-y-4">
                <div className="flex items-center gap-2 font-bold text-gray-900 border-b pb-2">
                  <User size={20} className="text-brand-600" />
                  Basic Information
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-1">Full Name</label>
                  <input name="name" value={formData.name || ''} onChange={handleChange} className="input-field" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-1">Email (View Only)</label>
                  <input value={formData.email || ''} disabled className="input-field bg-gray-50 opacity-70" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-1">Location</label>
                  <input name="location" value={formData.location || ''} onChange={handleChange} className="input-field" />
                </div>
              </div>

              {/* Farm Configuration */}
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 space-y-4">
                <div className="flex items-center gap-2 font-bold text-gray-900 border-b pb-2">
                  <Tractor size={20} className="text-brand-600" />
                  Farm Configuration
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-500 mb-1">Land Size (ha)</label>
                    <input name="land_size" type="number" step="0.1" value={formData.land_size || ''} onChange={handleChange} className="input-field" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-500 mb-1">Soil Type</label>
                    <select name="soil_type" value={formData.soil_type || ''} onChange={handleChange} className="input-field">
                      <option value="">Select Soil Type</option>
                      <option value="Alluvial">Alluvial Soil</option>
                      <option value="Black">Black Soil (Regur)</option>
                      <option value="Red">Red Soil</option>
                      <option value="Laterite">Laterite Soil</option>
                      <option value="Arid">Arid / Desert Soil</option>
                      <option value="Mountain">Mountain / Forest Soil</option>
                      <option value="Saline">Saline / Alkaline Soil</option>
                      <option value="Peaty">Peaty / Marshy Soil</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-1">Water Source</label>
                  <select name="water_source" value={formData.water_source || ''} onChange={handleChange} className="input-field">
                    <option value="Rain-fed">Rain-fed</option>
                    <option value="Borewell">Borewell</option>
                    <option value="Canal">Canal</option>
                    <option value="River">River</option>
                    <option value="Drip Irrigation">Drip Irrigation</option>
                  </select>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-500 mb-1">Budget (₹)</label>
                    <input name="budget" type="number" value={formData.budget || ''} onChange={handleChange} className="input-field" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-500 mb-1">Risk Level</label>
                    <select name="risk_level" value={formData.risk_level || ''} onChange={handleChange} className="input-field">
                      <option value="low">Low Risk</option>
                      <option value="medium">Medium Risk</option>
                      <option value="high">High Risk</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex justify-end pt-4">
              <button disabled={loading} type="submit" className="btn-primary flex items-center gap-2 px-10">
                <Save size={20} />
                {loading ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}

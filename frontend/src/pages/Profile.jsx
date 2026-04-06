import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import { updateProfile, getPestHistory, addPestHistory } from '../api';
import { Save, User, MapPin, Ruler, Droplets, Wallet, ShieldCheck, Tractor, FlaskConical, Plus, Trash2, Calendar, AlertTriangle, X } from 'lucide-react';

const SOIL_TYPES = [
  "Alluvial", "Black", "Red", "Laterite", "Arid", "Mountain", "Saline", "Peaty"
];

const EQUIPMENTS = [
  "Sprinkler", "Power Tiller", "Drip Irrigation", "Tractor", "Harvester", "Plow", "Seeder"
];

const INDIAN_STATES = [
  "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", "Haryana", 
  "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", 
  "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", 
  "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal", "Andaman and Nicobar Islands", 
  "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Jammu and Kashmir", "Ladakh", 
  "Lakshadweep", "Puducherry"
];

const LANGUAGES = [
  { code: "en", name: "English" },
  { code: "hi", name: "Hindi (हिन्दी)" },
  { code: "mr", name: "Marathi (मराठी)" },
  { code: "ta", name: "Tamil (தமிழ்)" },
  { code: "te", name: "Telugu (తెలుగు)" },
  { code: "bn", name: "Bengali (বাংলা)" },
  { code: "gu", name: "Gujarati (ગુજરાતી)" },
  { code: "kn", name: "Kannada (ಕನ್ನಡ)" },
  { code: "ml", name: "Malayalam (മലയാളம்)" },
  { code: "pa", name: "Punjabi (ਪੰਜਾਬੀ)" }
];

const WATER_SOURCES = [
  "Rain-fed", "Borewell", "Canal", "River", "Open Well", "Drip Irrigation", "Sprinkler System", "Tank/Pond", "Tanker Water", "Treated Waste Water"
];

export default function Profile() {
  const [farmer, setFarmer] = useState(null);
  const [formData, setFormData] = useState({
    equipment: [],
    soil_type_distribution: [{ type: '', size: 0 }]
  });
  const [pestHistory, setPestHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [showPestModal, setShowPestModal] = useState(false);
  const [newPestEntry, setNewPestEntry] = useState({
    pest_name: '',
    affected_crop: '',
    severity: 'Medium',
    observation_date: new Date().toISOString().split('T')[0],
    description: ''
  });
  
  const navigate = useNavigate();

  useEffect(() => {
    const data = localStorage.getItem('farmer');
    if (!data) {
      navigate('/login');
      return;
    }
    const parsedFarmer = JSON.parse(data);
    
    // Ensure equipment is an array
    if (parsedFarmer.equipment && typeof parsedFarmer.equipment === 'string') {
      try {
        parsedFarmer.equipment = JSON.parse(parsedFarmer.equipment);
      } catch (e) {
        parsedFarmer.equipment = [];
      }
    } else if (!parsedFarmer.equipment) {
      parsedFarmer.equipment = [];
    }

    // Ensure soil_type_distribution is an array
    if (parsedFarmer.soil_type_distribution && typeof parsedFarmer.soil_type_distribution === 'string') {
      try {
        parsedFarmer.soil_type_distribution = JSON.parse(parsedFarmer.soil_type_distribution);
      } catch (e) {
        parsedFarmer.soil_type_distribution = [{ type: '', size: 0 }];
      }
    } else if (!parsedFarmer.soil_type_distribution) {
      parsedFarmer.soil_type_distribution = [{ type: '', size: 0 }];
    }

    setFarmer(parsedFarmer);
    setFormData(parsedFarmer);
    fetchPestHistory(parsedFarmer.id);
  }, [navigate]);

  const fetchPestHistory = async (id) => {
    try {
      const res = await getPestHistory(id);
      setPestHistory(res.data.history);
    } catch (err) {
      console.error("Failed to fetch pest history", err);
    }
  };

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({ 
      ...prev, 
      [name]: type === 'number' ? parseFloat(value) : value 
    }));
  };

  const handleEquipmentToggle = (item) => {
    setFormData(prev => {
      const current = prev.equipment || [];
      if (current.includes(item)) {
        return { ...prev, equipment: current.filter(i => i !== item) };
      } else {
        return { ...prev, equipment: [...current, item] };
      }
    });
  };

  const handleSoilDistChange = (index, field, value) => {
    const newDist = [...formData.soil_type_distribution];
    newDist[index][field] = field === 'size' ? parseFloat(value) : value;
    setFormData(prev => ({ ...prev, soil_type_distribution: newDist }));
  };

  const addSoilType = () => {
    setFormData(prev => ({
      ...prev,
      soil_type_distribution: [...prev.soil_type_distribution, { type: '', size: 0 }]
    }));
  };

  const removeSoilType = (index) => {
    const newDist = formData.soil_type_distribution.filter((_, i) => i !== index);
    setFormData(prev => ({ ...prev, soil_type_distribution: newDist }));
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

  const handleAddPestIncident = async (e) => {
    e.preventDefault();
    try {
      await addPestHistory(farmer.id, newPestEntry);
      fetchPestHistory(farmer.id);
      setShowPestModal(false);
      setNewPestEntry({
        pest_name: '',
        affected_crop: '',
        severity: 'Medium',
        observation_date: new Date().toISOString().split('T')[0],
        description: ''
      });
    } catch (err) {
      alert("Failed to add pest incident");
    }
  };

  if (!farmer) return null;

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-8">
        <div className="max-w-5xl mx-auto">
          <header className="mb-8 flex justify-between items-end">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Farmer Profile</h1>
              <p className="text-gray-600 mt-1">Configure your farm details for better AI recommendations.</p>
            </div>
            <button 
              onClick={handleSubmit} 
              disabled={loading}
              className="btn-primary flex items-center gap-2 px-8 shadow-lg shadow-brand-200"
            >
              <Save size={20} />
              {loading ? 'Saving...' : 'Save All Changes'}
            </button>
          </header>

          {message && (
            <div className={`mb-6 p-4 rounded-xl text-center font-medium animate-in fade-in slide-in-from-top-4 duration-300 ${
              message.includes('success') ? 'bg-green-100 text-green-700 border border-green-200' : 'bg-red-100 text-red-700 border border-red-200'
            }`}>
              {message}
            </div>
          )}

          <div className="grid gap-6 lg:grid-cols-3">
            {/* Column 1: Identity & Location */}
            <div className="space-y-6">
              <section className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                <div className="flex items-center gap-2 font-bold text-gray-900 border-b pb-3 mb-4">
                  <User size={18} className="text-brand-600" />
                  Basic Info
                </div>
                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-semibold text-gray-400 uppercase mb-1">Full Name</label>
                    <input name="name" value={formData.name || ''} onChange={handleChange} className="input-field" />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-400 uppercase mb-1">Email (Locked)</label>
                    <input value={formData.email || ''} disabled className="input-field bg-gray-50 opacity-70 cursor-not-allowed" />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-400 uppercase mb-1">Location / State</label>
                    <select 
                      name="location" 
                      value={formData.location || ''} 
                      onChange={handleChange} 
                      className="input-field"
                    >
                      <option value="">Select State</option>
                      {INDIAN_STATES.map(state => (
                        <option key={state} value={state}>{state}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-400 uppercase mb-1">Preferred Language</label>
                    <select 
                      name="language_preference" 
                      value={formData.language_preference || 'en'} 
                      onChange={handleChange} 
                      className="input-field border-brand-200 focus:border-brand-500"
                    >
                      {LANGUAGES.map(lang => (
                        <option key={lang.code} value={lang.code}>{lang.name}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </section>

              <section className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                <div className="flex items-center gap-2 font-bold text-gray-900 border-b pb-3 mb-4">
                  <Wallet size={18} className="text-brand-600" />
                  Economics & Risk
                </div>
                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-semibold text-gray-400 uppercase mb-1">Budget (₹)</label>
                    <input name="budget" type="number" value={formData.budget || ''} onChange={handleChange} className="input-field" />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-400 uppercase mb-1">Risk Tolerance</label>
                    <div className="grid grid-cols-3 gap-2 mt-1">
                      {['low', 'medium', 'high'].map(level => (
                        <button
                          key={level}
                          type="button"
                          onClick={() => setFormData(prev => ({ ...prev, risk_level: level }))}
                          className={`py-2 text-xs font-bold rounded-lg border transition-all capitalize ${
                            formData.risk_level === level 
                              ? 'bg-brand-600 text-white border-brand-600' 
                              : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'
                          }`}
                        >
                          {level}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </section>
            </div>

            {/* Column 2: Farm Details & Equipment */}
            <div className="lg:col-span-2 space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <section className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                  <div className="flex items-center gap-2 font-bold text-gray-900 border-b pb-3 mb-4">
                    <Tractor size={18} className="text-brand-600" />
                    Farm Assets
                  </div>
                  <div className="space-y-4">
                    <div className="flex gap-4">
                      <div className="flex-1">
                        <label className="block text-xs font-semibold text-gray-400 uppercase mb-1">Total Land (Acres)</label>
                        <input name="land_size" type="number" value={formData.land_size || ''} onChange={handleChange} className="input-field" />
                      </div>
                      <div className="flex-1">
                        <label className="block text-xs font-semibold text-gray-400 uppercase mb-1">Water Source</label>
                        <select 
                          name="water_source" 
                          value={WATER_SOURCES.includes(formData.water_source) ? formData.water_source : (formData.water_source ? "Others" : "")} 
                          onChange={(e) => {
                            const val = e.target.value;
                            if (val !== "Others") {
                              setFormData(prev => ({ ...prev, water_source: val }));
                            } else {
                              setFormData(prev => ({ ...prev, water_source: "" })); // Clear to let user type
                            }
                          }} 
                          className="input-field"
                        >
                          <option value="">Select Source</option>
                          {WATER_SOURCES.map(s => <option key={s} value={s}>{s}</option>)}
                          <option value="Others">Others (Specify)</option>
                        </select>
                      </div>
                    </div>
                    {(!WATER_SOURCES.includes(formData.water_source) && formData.water_source !== undefined) && (
                      <div className="mt-2 animate-in fade-in slide-in-from-top-2 duration-200">
                        <label className="block text-xs font-semibold text-brand-600 uppercase mb-1">Specify Other Water Source</label>
                        <input 
                          type="text" 
                          placeholder="e.g. Community Well, Mountain Spring" 
                          value={formData.water_source || ''} 
                          onChange={(e) => setFormData(prev => ({ ...prev, water_source: e.target.value }))}
                          className="input-field border-brand-200 focus:border-brand-500"
                        />
                      </div>
                    )}
                    <div>
                      <label className="block text-xs font-semibold text-gray-400 uppercase mb-1 mb-2">Equipment Available</label>
                      <div className="flex flex-wrap gap-2">
                        {EQUIPMENTS.map(item => (
                          <button
                            key={item}
                            type="button"
                            onClick={() => handleEquipmentToggle(item)}
                            className={`px-3 py-1.5 rounded-full border text-xs font-medium transition-all ${
                              formData.equipment?.includes(item)
                                ? 'bg-brand-100 text-brand-700 border-brand-300'
                                : 'bg-gray-50 text-gray-500 border-gray-200 hover:border-gray-300'
                            }`}
                          >
                            {item}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                </section>

                <section className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                  <div className="flex items-center gap-2 font-bold text-gray-900 border-b pb-3 mb-4">
                    <FlaskConical size={18} className="text-brand-600" />
                    Soil Composition (NPK)
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-semibold text-gray-400 uppercase mb-1">Nitrogen (N)</label>
                      <input name="npk_n" type="number" value={formData.npk_n || ''} onChange={handleChange} className="input-field" placeholder="mg/kg" />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-gray-400 uppercase mb-1">Phosphorus (P)</label>
                      <input name="npk_p" type="number" value={formData.npk_p || ''} onChange={handleChange} className="input-field" placeholder="mg/kg" />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-gray-400 uppercase mb-1">Potassium (K)</label>
                      <input name="npk_k" type="number" value={formData.npk_k || ''} onChange={handleChange} className="input-field" placeholder="mg/kg" />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-gray-400 uppercase mb-1">Soil pH</label>
                      <input name="soil_ph" type="number" step="0.1" value={formData.soil_ph || ''} onChange={handleChange} className="input-field" placeholder="0-14" />
                    </div>
                  </div>
                </section>
              </div>

              {/* Pest History Log */}
              <section className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                <div className="flex items-center justify-between border-b pb-3 mb-4">
                  <div className="flex items-center gap-2 font-bold text-gray-900">
                    <Calendar size={18} className="text-brand-600" />
                    Pest History Log
                  </div>
                  <button 
                    type="button" 
                    onClick={() => setShowPestModal(true)}
                    className="flex items-center gap-1 text-xs font-bold text-brand-600 hover:text-brand-700 bg-brand-50 px-2 py-1 rounded"
                  >
                    <Plus size={14} /> Add Incident
                  </button>
                </div>
                
                <div className="space-y-4">
                  {pestHistory.length === 0 ? (
                    <p className="text-sm text-gray-500 italic text-center py-4">No past incidents recorded.</p>
                  ) : (
                    pestHistory.map((pest, idx) => (
                      <div key={idx} className="p-3 bg-gray-50 rounded-xl border border-gray-100 relative group">
                        <div className="flex justify-between items-start mb-1">
                          <h4 className="font-bold text-gray-900 text-sm">{pest.pest_name}</h4>
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                            pest.severity === 'High' ? 'bg-red-100 text-red-700' : 
                            pest.severity === 'Medium' ? 'bg-orange-100 text-orange-700' : 
                            'bg-blue-100 text-blue-700'
                          }`}>
                            {pest.severity}
                          </span>
                        </div>
                        <p className="text-xs text-gray-600 mb-2">Affected: <span className="font-medium">{pest.affected_crop}</span></p>
                        <div className="flex items-center gap-1 text-[10px] text-gray-400">
                          <Calendar size={10} />
                          {pest.observation_date}
                        </div>
                        {pest.description && (
                          <p className="text-[11px] text-gray-500 mt-2 italic border-l-2 border-gray-200 pl-2">
                            {pest.description}
                          </p>
                        )}
                      </div>
                    ))
                  )}
                </div>
              </section>

              {/* Soil Type Distribution */}
              <section className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                <div className="flex items-center justify-between border-b pb-3 mb-4">
                  <div className="flex items-center gap-2 font-bold text-gray-900">
                    <MapPin size={18} className="text-brand-600" />
                    Soil Variety within Land
                  </div>
                  <button 
                    type="button" 
                    onClick={addSoilType}
                    className="flex items-center gap-1 text-xs font-bold text-brand-600 hover:text-brand-700 bg-brand-50 px-2 py-1 rounded"
                  >
                    <Plus size={14} /> Add Variety
                  </button>
                </div>
                <div className="space-y-3">
                  {formData.soil_type_distribution.map((item, idx) => (
                    <div key={idx} className="flex items-center gap-3 animate-in fade-in zoom-in-95 duration-200">
                      <div className="flex-1">
                        <select 
                          value={item.type} 
                          onChange={(e) => handleSoilDistChange(idx, 'type', e.target.value)}
                          className="input-field text-sm"
                        >
                          <option value="">Select Soil Type</option>
                          {SOIL_TYPES.map(t => <option key={t} value={t}>{t} Soil</option>)}
                        </select>
                      </div>
                      <div className="w-32">
                        <div className="relative">
                          <input 
                            type="number" 
                            value={item.size} 
                            onChange={(e) => handleSoilDistChange(idx, 'size', e.target.value)}
                            className="input-field pr-10 text-sm"
                            placeholder="Area"
                          />
                          <span className="absolute right-3 top-2.5 text-xs text-gray-400">Acres</span>
                        </div>
                      </div>
                      {formData.soil_type_distribution.length > 1 && (
                        <button 
                          type="button" 
                          onClick={() => removeSoilType(idx)}
                          className="p-2 text-red-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        >
                          <Trash2 size={18} />
                        </button>
                      )}
                    </div>
                  ))}
                  <div className="mt-4 p-3 bg-gray-50 rounded-xl border border-dashed border-gray-200 text-xs text-gray-500 flex justify-between">
                    <span>Total Allocated: <strong>{formData.soil_type_distribution.reduce((acc, curr) => acc + (curr.size || 0), 0)} Acres</strong></span>
                    <span>Total Land: <strong>{formData.land_size || 0} Acres</strong></span>
                  </div>
                </div>
              </section>
            </div>
          </div>
        </div>

        {/* Pest Incident Modal */}
        {showPestModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4 animate-in fade-in duration-200">
            <div className="bg-white w-full max-w-md rounded-2xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200">
              <div className="bg-brand-600 p-4 flex justify-between items-center text-white">
                <h3 className="font-bold flex items-center gap-2">
                  <AlertTriangle size={20} />
                  Add Pest Incident
                </h3>
                <button onClick={() => setShowPestModal(false)} className="hover:bg-brand-700 p-1 rounded-lg">
                  <X size={20} />
                </button>
              </div>
              <form onSubmit={handleAddPestIncident} className="p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Pest/Disease Name</label>
                    <input 
                      required
                      className="input-field"
                      placeholder="e.g. Whiteflies"
                      value={newPestEntry.pest_name}
                      onChange={e => setNewPestEntry({...newPestEntry, pest_name: e.target.value})}
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Affected Crop</label>
                    <input 
                      required
                      className="input-field"
                      placeholder="e.g. Cotton"
                      value={newPestEntry.affected_crop}
                      onChange={e => setNewPestEntry({...newPestEntry, affected_crop: e.target.value})}
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Severity</label>
                    <select 
                      className="input-field"
                      value={newPestEntry.severity}
                      onChange={e => setNewPestEntry({...newPestEntry, severity: e.target.value})}
                    >
                      <option value="Low">Low</option>
                      <option value="Medium">Medium</option>
                      <option value="High">High</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Date Noticed</label>
                    <input 
                      type="date"
                      required
                      className="input-field"
                      value={newPestEntry.observation_date}
                      onChange={e => setNewPestEntry({...newPestEntry, observation_date: e.target.value})}
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Short Description</label>
                  <textarea 
                    className="input-field h-24 resize-none"
                    placeholder="Briefly describe the damage or symptoms..."
                    value={newPestEntry.description}
                    onChange={e => setNewPestEntry({...newPestEntry, description: e.target.value})}
                  />
                </div>
                <button type="submit" className="btn-primary w-full py-3 font-bold mt-2 shadow-lg shadow-brand-200">
                  Save Incident Log
                </button>
              </form>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

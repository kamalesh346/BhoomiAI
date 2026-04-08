import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login, register } from '../api';
import { Wheat, User, Mail, Lock, MapPin, Ruler, Droplets } from 'lucide-react';

const INDIAN_STATES = [
  "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", "Haryana", 
  "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", 
  "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", 
  "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal", "Andaman and Nicobar Islands", 
  "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Jammu and Kashmir", "Ladakh", 
  "Lakshadweep", "Puducherry"
];

const WATER_SOURCES = [
  "Rain-fed", "Borewell", "Canal", "River", "Open Well", "Drip Irrigation", "Sprinkler System", "Tank/Pond", "Tanker Water", "Treated Waste Water"
];

export default function Login() {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    location: '',
    land_size: 1.0,
    water_source: 'Rain-fed'
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      let res;
      if (isLogin) {
        res = await login(formData.email, formData.password);
      } else {
        res = await register(formData);
      }
      localStorage.setItem('farmer', JSON.stringify(res.data.farmer));
      navigate('/dashboard');
    } catch (err) {
      const detail = err.response?.data?.detail || 'Authentication failed';
      if (!isLogin && typeof detail === 'string' && detail.toLowerCase().includes('email already exists')) {
        setError('An account with this email already exists. Please sign in instead.');
      } else {
        setError(detail);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDemo = async () => {
    try {
      const res = await login('test@farmer.com', 'test123');
      localStorage.setItem('farmer', JSON.stringify(res.data.farmer));
      navigate('/dashboard');
    } catch (err) {
      setError('Demo login failed. Run init_db.py to seed data.');
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-brand-50 px-4 py-12">
      <div className="w-full max-w-md space-y-8 rounded-2xl bg-white p-10 shadow-xl border border-brand-100">
        <div className="text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-brand-100">
            <Wheat className="h-10 w-10 text-brand-600" />
          </div>
          <h2 className="mt-6 text-3xl font-bold tracking-tight text-gray-900">
            BhoomiAI
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Your AI-powered farming consultant
          </p>
        </div>

        <div className="flex justify-center mb-6">
          <div className="inline-flex rounded-md shadow-sm" role="group">
            <button
              type="button"
              onClick={() => setIsLogin(true)}
              className={`px-6 py-2 text-sm font-medium rounded-l-lg border ${
                isLogin 
                  ? 'bg-brand-600 text-white border-brand-600' 
                  : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-50'
              }`}
            >
              Login
            </button>
            <button
              type="button"
              onClick={() => setIsLogin(false)}
              className={`px-6 py-2 text-sm font-medium rounded-r-lg border ${
                !isLogin 
                  ? 'bg-brand-600 text-white border-brand-600' 
                  : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-50'
              }`}
            >
              Sign Up
            </button>
          </div>
        </div>
        
        <form className="mt-4 space-y-4" onSubmit={handleSubmit}>
          {error && <div className="p-3 bg-red-100 text-red-700 text-sm rounded-lg text-center">{error}</div>}
          
          {!isLogin && (
            <div className="relative">
              <User className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
              <input
                name="name"
                type="text"
                required
                className="input-field pl-10"
                placeholder="Full Name"
                value={formData.name}
                onChange={handleInputChange}
              />
            </div>
          )}

          <div className="relative">
            <Mail className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
            <input
              name="email"
              type="email"
              required
              className="input-field pl-10"
              placeholder="Email address"
              value={formData.email}
              onChange={handleInputChange}
            />
          </div>

          <div className="relative">
            <Lock className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
            <input
              name="password"
              type="password"
              required
              className="input-field pl-10"
              placeholder="Password"
              value={formData.password}
              onChange={handleInputChange}
            />
          </div>

          {!isLogin && (
            <>
              <div className="relative">
                <MapPin className="absolute left-3 top-3 h-5 w-5 text-gray-400 z-10" />
                <select
                  name="location"
                  required
                  className="input-field pl-10 appearance-none"
                  value={formData.location}
                  onChange={handleInputChange}
                >
                  <option value="">Select State</option>
                  {INDIAN_STATES.map(state => (
                    <option key={state} value={state}>{state}</option>
                  ))}
                </select>
              </div>
              <div className="relative">
                <Ruler className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                <input
                  name="land_size"
                  type="number"
                  step="0.1"
                  required
                  className="input-field pl-10"
                  placeholder="Land Size (acres)"
                  value={formData.land_size}
                  onChange={handleInputChange}
                />
              </div>
              <div className="relative">
                <Droplets className="absolute left-3 top-3 h-5 w-5 text-gray-400 z-10" />
                <select
                  name="water_source"
                  required
                  className="input-field pl-10 appearance-none"
                  value={WATER_SOURCES.includes(formData.water_source) ? formData.water_source : "Others"}
                  onChange={(e) => {
                    const val = e.target.value;
                    setFormData(prev => ({ ...prev, water_source: val === "Others" ? "" : val }));
                  }}
                >
                  <option value="">Select Water Source</option>
                  {WATER_SOURCES.map(s => <option key={s} value={s}>{s}</option>)}
                  <option value="Others">Others (Specify)</option>
                </select>
              </div>

              {(!WATER_SOURCES.includes(formData.water_source)) && (
                <div className="animate-in fade-in slide-in-from-top-2 duration-200">
                  <input
                    type="text"
                    required
                    className="input-field border-brand-200 focus:border-brand-500"
                    placeholder="Specify other water source"
                    value={formData.water_source}
                    onChange={(e) => setFormData(prev => ({ ...prev, water_source: e.target.value }))}
                  />
                </div>
              )}
            </>
          )}

          <div className="flex flex-col gap-3 mt-6">
            <button disabled={loading} type="submit" className="btn-primary w-full py-3 text-lg font-semibold">
              {loading ? 'Processing...' : (isLogin ? 'Sign In' : 'Create Account')}
            </button>
            {isLogin && (
              <button type="button" onClick={handleDemo} className="w-full py-2 text-brand-600 font-medium hover:underline transition-colors">
                Try Demo Login
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}

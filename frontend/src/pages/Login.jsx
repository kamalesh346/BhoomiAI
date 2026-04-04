import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../api';
import { Wheat } from 'lucide-react';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await login(email, password);
      localStorage.setItem('farmer', JSON.stringify(res.data.farmer));
      navigate('/dashboard');
    } catch (err) {
      setError('Invalid credentials');
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
    <div className="flex min-h-screen items-center justify-center bg-brand-50 px-4">
      <div className="w-full max-w-md space-y-8 rounded-2xl bg-white p-10 shadow-xl border border-brand-100">
        <div className="text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-brand-100">
            <Wheat className="h-10 w-10 text-brand-600" />
          </div>
          <h2 className="mt-6 text-3xl font-bold tracking-tight text-gray-900">
            Digital Sarathi
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Your AI-powered farming consultant
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleLogin}>
          {error && <div className="text-red-500 text-sm text-center">{error}</div>}
          <div className="space-y-4 rounded-md shadow-sm">
            <div>
              <label className="sr-only" htmlFor="email-address">Email address</label>
              <input
                id="email-address"
                type="email"
                required
                className="input-field"
                placeholder="Email address"
                value={email}
                onChange={e => setEmail(e.target.value)}
              />
            </div>
            <div>
              <label className="sr-only" htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                required
                className="input-field"
                placeholder="Password"
                value={password}
                onChange={e => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div className="flex gap-4">
            <button type="submit" className="btn-primary w-full">
              Sign in
            </button>
            <button type="button" onClick={handleDemo} className="w-full py-2 px-4 border border-brand-500 text-brand-600 rounded-lg hover:bg-brand-50 transition-colors">
              Demo Login
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

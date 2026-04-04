import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { Wheat, LayoutDashboard, MessageSquareText, LogOut } from 'lucide-react';

export default function Sidebar() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('farmer');
    localStorage.removeItem('chat_session_id');
    navigate('/login');
  };

  return (
    <aside className="flex w-64 flex-col border-r border-gray-200 bg-white px-4 py-8 shadow-sm">
      <div className="flex items-center gap-3 px-2 mb-10">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-100">
          <Wheat className="h-6 w-6 text-brand-600" />
        </div>
        <span className="text-xl font-bold text-gray-900">Digital Sarathi</span>
      </div>

      <nav className="flex-1 space-y-2">
        <NavLink
          to="/dashboard"
          className={({ isActive }) =>
            `flex items-center gap-3 rounded-lg px-3 py-2.5 transition-colors ${
              isActive ? 'bg-brand-50 text-brand-700 font-medium' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            }`
          }
        >
          <LayoutDashboard className="h-5 w-5" />
          Dashboard
        </NavLink>
        <NavLink
          to="/chat"
          className={({ isActive }) =>
            `flex items-center gap-3 rounded-lg px-3 py-2.5 transition-colors ${
              isActive ? 'bg-brand-50 text-brand-700 font-medium' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            }`
          }
        >
          <MessageSquareText className="h-5 w-5" />
          Consultant Chat
        </NavLink>
        <NavLink
          to="/profile"
          className={({ isActive }) =>
            `flex items-center gap-3 rounded-lg px-3 py-2.5 transition-colors ${
              isActive ? 'bg-brand-50 text-brand-700 font-medium' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            }`
          }
        >
          <Wheat className="h-5 w-5" />
          My Profile
        </NavLink>
      </nav>

      <div className="mt-auto border-t border-gray-200 pt-4">
        <button
          onClick={handleLogout}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-gray-600 transition-colors hover:bg-red-50 hover:text-red-600"
        >
          <LogOut className="h-5 w-5" />
          Logout
        </button>
      </div>
    </aside>
  );
}

import React, { useState } from 'react';
import api from '../api';
import { useNavigate } from 'react-router-dom';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleReset = async (e) => {
    e.preventDefault();
    try {
      const form = new FormData();
      form.append('email', email);
      form.append('new_password', newPassword);

      const res = await api.post('/reset-password', form);
      setMessage(res.data.message);
      setTimeout(() => navigate('/login'), 2000); // redirect after 2 sec
    } catch (err) {
      setMessage(err.response?.data?.error || 'Reset failed');
    }
  };

  return (
    <div className="flex min-h-screen bg-gradient-to-r from-purple-100 to-pink-100 items-center justify-center px-4">
      <div className="bg-white p-10 rounded-3xl shadow-lg w-full max-w-xl">
        <h2 className="text-3xl font-bold text-center text-gray-800 mb-6">Reset Your Password</h2>

        <form onSubmit={handleReset} className="space-y-6">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Your registered email"
            required
            className="w-full px-5 py-3 border border-gray-300 rounded-lg text-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
          />

          <input
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            placeholder="New password"
            required
            className="w-full px-5 py-3 border border-gray-300 rounded-lg text-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
          />

          <button
            type="submit"
            className="w-full bg-purple-600 hover:bg-purple-700 text-white py-3 rounded-lg text-lg font-semibold"
          >
            Reset Password
          </button>
        </form>

        {message && (
          <p className="mt-4 text-center text-sm text-red-600">{message}</p>
        )}

        <div className="text-center mt-6">
          <button onClick={() => navigate('/login')} className="text-blue-600 hover:underline text-sm">
            Back to Login
          </button>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;

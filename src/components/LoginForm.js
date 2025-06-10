import React, { useState } from 'react';
import api from '../api';
import { useNavigate } from 'react-router-dom';

const LoginForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const form = new FormData();
      form.append('email', email);
      form.append('password', password);

      await api.post('/login', form);
      alert('Login successful!');
      navigate('/dashboard');
    } catch (err) {
      alert(err.response?.data?.error || 'Login failed');
    }
  };

  return (
    <div className="flex min-h-screen bg-gradient-to-r from-blue-100 to-purple-200 items-center justify-center px-6">
      <div className="flex flex-col md:flex-row bg-white rounded-3xl shadow-xl overflow-hidden w-full max-w-6xl">

        {/* Left Image */}
        <div className="md:w-1/2 hidden md:block">
          <img
            src="/image1.png"
            alt="Login Visual"
            className="h-full w-full object-cover"
          />
        </div>

        {/* Login Form */}
        <div className="md:w-1/2 w-full p-10 md:p-16 flex flex-col justify-center">
          {/* Logo */}
          <div className="flex justify-center mb-6">
            <img src="/logo.png" alt="Logo" className="h-16 w-auto" />
          </div>

          {/* Heading */}
          <h2 className="text-4xl font-extrabold text-gray-900 mb-4 text-center">Welcome Back</h2>
          <p className="text-center text-gray-500 mb-8 text-lg">Log in to continue analyzing your code</p>

          <form onSubmit={handleLogin} className="space-y-6">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              required
              className="w-full px-6 py-4 border border-gray-300 rounded-xl text-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />

            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
              className="w-full px-6 py-4 border border-gray-300 rounded-xl text-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />

            {/* Forgot Password Link */}
            <div className="text-right text-sm">
              <button
                type="button"
                className="text-blue-600 hover:underline"
                onClick={() => navigate('/forgot-password')}
              >
                Forgot Password?
              </button>
            </div>

            <button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white py-4 rounded-xl text-xl font-semibold transition duration-300"
            >
              Log in
            </button>
          </form>

          {/* Sign up Prompt */}
          <div className="mt-8 text-center">
            <span className="text-gray-600 text-base">
              Don’t have an account?{' '}
              <button
                onClick={() => navigate('/signup')}
                className="text-blue-600 hover:underline font-medium"
              >
                Sign up here
              </button>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginForm;

import React, { useState } from 'react';
import api from '../api';
import { useNavigate } from 'react-router-dom';

const SignupForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleSignup = async (e) => {
    e.preventDefault();
    try {
      const form = new FormData();
      form.append('email', email);
      form.append('password', password);

      await api.post('/signup', form);
      alert('Signup successful!');
      navigate('/dashboard');
    } catch (err) {
      alert(err.response?.data?.error || 'Signup failed');
    }
  };

  return (
    <div className="flex min-h-screen bg-gradient-to-r from-blue-100 to-purple-200 items-center justify-center px-6">
      <div className="flex flex-col md:flex-row bg-white rounded-3xl shadow-xl overflow-hidden w-full max-w-6xl">

        {/* Left Side Image */}
        <div className="md:w-1/2 hidden md:block">
          <img
            src="/image1.png" // Replace with actual image path
            alt="Sign Up Visual"
            className="h-full w-full object-cover"
          />
        </div>

        {/* Signup Form Section */}
        <div className="md:w-1/2 w-full p-10 md:p-16 flex flex-col justify-center">
          <h2 className="text-4xl font-extrabold text-gray-900 mb-8 text-center">Create Your Account</h2>

          <form onSubmit={handleSignup} className="space-y-6">
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
              placeholder="Enter password"
              required
              className="w-full px-6 py-4 border border-gray-300 rounded-xl text-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />

            <button
              type="submit"
              className="w-full bg-purple-600 hover:bg-purple-700 text-white py-4 rounded-xl text-xl font-semibold transition duration-300"
            >
              Sign Up
            </button>
          </form>

          <div className="mt-8 text-center">
            <span className="text-gray-600 text-base">
              Already have an account?{' '}
              <button
                onClick={() => navigate('/login')}
                className="text-blue-600 hover:underline font-medium"
              >
                Log in here
              </button>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SignupForm;

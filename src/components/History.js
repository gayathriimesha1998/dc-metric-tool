import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

const History = () => {
  const [history, setHistory] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [search, setSearch] = useState('');
  const [error, setError] = useState('');
  const [modalCode, setModalCode] = useState('');
  const [showModal, setShowModal] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await api.get('/history');
        setHistory(res.data);
        setFiltered(res.data);
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to load history');
      }
    };
    fetchHistory();
  }, []);

  const handleSearch = (e) => {
    const value = e.target.value.toLowerCase();
    setSearch(value);
    const result = history.filter(entry =>
      entry.filename.toLowerCase().includes(value) ||
      entry.language.toLowerCase().includes(value)
    );
    setFiltered(result);
  };

  const openModal = (code) => {
    setModalCode(code);
    setShowModal(true);
  };

  const closeModal = () => {
    setModalCode('');
    setShowModal(false);
  };

  const handleDelete = async (entry) => {
    if (!window.confirm(`Delete ${entry.filename}?`)) return;
    try {
      await api.delete(`/history/${entry.id}`);
      const updated = history.filter(h => h !== entry);
      setHistory(updated);
      setFiltered(updated);
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to delete entry');
    }
  };

  const handleBack = () => {
    navigate('/dashboard');
  };

  const handleCancel = async () => {
    try {
      await api.post('/logout');
      navigate('/login');
    } catch {
      alert('Logout failed.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Navigation Buttons */}
        <div className="flex justify-between items-center mb-4">
          <button
            onClick={handleBack}
            className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700"
          >
            ← Back to Dashboard
          </button>
          <button
            onClick={handleCancel}
            className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
          >
            Cancel & Logout
          </button>
        </div>

        <h2 className="text-3xl font-semibold mb-6">Your Submission History</h2>
        {error && <p className="text-red-600 mb-4">{error}</p>}

        {/* Search Bar */}
        <input
          type="text"
          placeholder="Search by filename or language..."
          value={search}
          onChange={handleSearch}
          className="border border-gray-300 px-4 py-3 text-lg rounded w-full max-w-md mb-6"
        />

        {filtered.length === 0 ? (
          <p className="text-gray-600 text-lg">No matching submissions found.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white shadow border border-gray-200 rounded-lg text-lg">
              <thead className="bg-gray-100 text-gray-800">
                <tr>
                  <th className="px-6 py-4 text-left">Filename</th>
                  <th className="px-6 py-4 text-left">Language</th>
                  <th className="px-4 py-4 text-left">DC</th>
                  <th className="px-4 py-4 text-left">CC</th>
                  <th className="px-6 py-4 text-left">Timestamp</th>
                  <th className="px-6 py-4 text-left">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((entry, index) => (
                  <tr key={index} className="border-t hover:bg-gray-50">
                    <td className="px-6 py-4">{entry.filename}</td>
                    <td className="px-6 py-4 capitalize">{entry.language}</td>
                    <td className="px-4 py-4">{entry.dc}</td>
                    <td className="px-4 py-4">{entry.cc}</td>
                    <td className="px-6 py-4">{entry.timestamp}</td>
                    <td className="px-6 py-4 flex flex-wrap gap-2">
                      <button
                        onClick={() => openModal(entry.code)}
                        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 text-sm"
                      >
                        View Code
                      </button>
                      <button
                        onClick={() => handleDelete(entry)}
                        className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 text-sm"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Modal for Viewing Code */}
        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-lg p-6 max-w-3xl w-full">
              <h3 className="text-xl font-bold mb-4">Submitted Code</h3>
              <pre className="bg-gray-100 p-4 rounded overflow-x-auto whitespace-pre-wrap text-sm max-h-[60vh]">
                {modalCode}
              </pre>
              <div className="text-right mt-4">
                <button
                  onClick={closeModal}
                  className="bg-gray-700 text-white px-4 py-2 rounded hover:bg-gray-800"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default History;

import React, { useState } from 'react';
import api from '../api';
import { useNavigate } from 'react-router-dom';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const Dashboard = () => {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [filename, setFilename] = useState('untitled.py');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const [expanded, setExpanded] = useState({});

  const handleAnalyze = async () => {
    setError('');
    try {
      const res = await api.post('/analyze', { code, language, filename });
      setResult({
        dc: res.data.dc,
        cc: res.data.cc,
        line_dc_map: res.data.line_dc_map || {},
        methods: res.data.methods || {},
        classes: res.data.classes || {},
        structures: res.data.structures || {},
        code: code
      });
    } catch (err) {
      setError(err.response?.data?.error || 'Analysis failed');
    }
  };

  const handleLogout = async () => {
    try {
      await api.post('/logout');
      navigate('/login');
    } catch {
      alert('Logout failed');
    }
  };

  const chartData = result ? {
    labels: ['DC', 'CC'],
    datasets: [
      {
        label: 'Complexity Score',
        data: [result.dc, result.cc],
        backgroundColor: ['#38bdf8', '#a78bfa'],
        borderWidth: 1
      }
    ]
  } : null;

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'DC vs CC Comparison' }
    }
  };

  const heatColor = (score) => {
    if (score >= 10) return 'bg-red-200';
    if (score >= 5) return 'bg-yellow-200';
    return 'bg-green-100';
  };

  const toggleStructure = (type) => {
  setExpanded((prev) => ({
    ...prev,
    [type]: !prev[type]
  }));
};

  const renderTable = (title, data) => (
    <div className="mt-6">
      <h4 className="font-semibold text-lg mb-2 text-gray-800">{title}</h4>
      <table className="min-w-full border border-gray-300 rounded-lg overflow-hidden">
        <thead className="bg-gray-200 text-sm text-gray-700">
          <tr>
            <th className="px-4 py-2 text-left">Name</th>
            <th className="px-4 py-2 text-left">DC</th>
            <th className="px-4 py-2 text-left">CC</th>
          </tr>
        </thead>
        <tbody className="bg-white text-sm">
          {Object.entries(data).map(([name, scores], idx) => (
            <tr key={idx} className="border-t">
              <td className="px-4 py-2">{name}</td>
              <td className="px-4 py-2">{scores.dc}</td>
              <td className="px-4 py-2">{scores.cc}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

const renderStructureTable = (structures) => {
  return (
    <div className="mt-6">
      <h4 className="font-semibold text-lg mb-2 text-gray-800">Control Structure Summary</h4>
      <table className="min-w-full border border-gray-300 rounded-lg overflow-hidden text-sm">
        <thead className="bg-gray-200 text-gray-700">
          <tr>
            <th className="px-4 py-2 text-left">Structure</th>
            <th className="px-4 py-2 text-left">Total Count</th>
            <th className="px-4 py-2 text-left">Level Summary with Nested Conditions</th>
          </tr>
        </thead>
        <tbody className="bg-white">
          {Object.entries(structures).map(([type, data], idx) => (
            <tr key={idx} className="border-t">
              <td className="px-4 py-2 capitalize">{type}</td>
              <td className="px-4 py-2">{data.count}</td>
              <td className="px-4 py-2">
                {Object.entries(data.level_counts || {}).map(([level, count]) => (
                  <div key={level} className="mb-2">
                    <div className="font-semibold text-gray-800">Level {level} → {count} occurrence(s)</div>
                    <ul className="ml-4 list-disc text-gray-700">
                      {Object.entries(data.nested_conditions?.[level] || {}).length > 0 ? (
                        Object.entries(data.nested_conditions[level]).map(([cond, condCount], i) => (
                          <li key={i}>{cond}: {condCount}</li>
                        ))
                      ) : (
                        <li className="text-gray-400 italic">No nested conditions</li>
                      )}
                    </ul>
                  </div>
                ))}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};


  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 via-purple-100 to-pink-100 p-8">
      <div className="max-w-6xl mx-auto bg-white rounded-3xl shadow-xl p-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-3xl font-bold text-gray-800">Decisional Complexity Analyzer</h2>
          <button
            onClick={handleLogout}
            className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600"
          >
            Logout
          </button>
        </div>

        <div className="flex flex-col md:flex-row gap-4 mb-4">
          <div className="flex flex-col w-full md:w-1/4">
            <label className="text-gray-700 font-semibold mb-1" htmlFor="language">
              Select Language
            </label>
            <select
              id="language"
              value={language}
              onChange={(e) => {
                setLanguage(e.target.value);
                setFilename(`untitled.${e.target.value === 'python' ? 'py' : e.target.value === 'java' ? 'java' : 'cpp'}`);
              }}
              className="border border-gray-300 px-4 py-2 rounded-lg"
            >
              <option value="python">Python (.py)</option>
              <option value="java">Java (.java)</option>
              <option value="c++">C++ (.cpp)</option>
            </select>
          </div>

          <div className="flex flex-col w-full">
            <label className="text-gray-700 font-semibold mb-1" htmlFor="filename">
              Enter File Name <span className="text-sm text-gray-500">(with extension)</span>
            </label>
            <input
              id="filename"
              type="text"
              className="border border-gray-300 px-4 py-2 rounded-lg"
              value={filename}
              onChange={(e) => setFilename(e.target.value)}
              placeholder="e.g., main.py"
            />
          </div>
        </div>

        <textarea
          className="w-full border border-gray-300 p-4 rounded-lg text-base mb-4 resize-y min-h-[350px]"
          placeholder="Paste your code here..."
          value={code}
          onChange={(e) => setCode(e.target.value)}
        />

        <div className="flex gap-4 mb-6">
          <button
            onClick={handleAnalyze}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
          >
            Analyze
          </button>
          <button
            onClick={() => window.location.href = "/history"}
            className="bg-gray-700 text-white px-6 py-2 rounded-lg hover:bg-gray-800"
          >
            View Submission History
          </button>
        </div>

        {error && <p className="text-red-600 mb-4 font-semibold">{error}</p>}

        {result && (
          <div className="bg-gray-50 p-6 rounded-xl shadow-md">
            <h3 className="text-xl font-bold mb-4 text-gray-800">Results</h3>
            <p className="text-lg text-gray-700 mb-1"><strong>DC:</strong> {result.dc}</p>
            <p className="text-lg text-gray-700 mb-6"><strong>CC:</strong> {result.cc}</p>

            <div className="my-6 max-w-xl mx-auto">
              <Bar data={chartData} options={chartOptions} />
            </div>

            {renderTable("Method-wise Complexity", result.methods)}
            {renderTable("Class-wise Complexity", result.classes)}
            {result.structures && Object.keys(result.structures).length > 0 && renderStructureTable(result.structures)}

            <div className="mt-10">
              <h4 className="font-semibold text-lg mb-2">Heatmap View</h4>

              <div className="flex items-center gap-4 mb-2 text-sm">
                <div className="flex items-center gap-1">
                  <div className="w-4 h-4 bg-green-200 border border-gray-300 rounded"></div>
                  <span className="text-gray-700">Low (0–1)</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-4 h-4 bg-yellow-200 border border-gray-300 rounded"></div>
                  <span className="text-gray-700">Medium (2–4)</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-4 h-4 bg-red-200 border border-gray-300 rounded"></div>
                  <span className="text-gray-700">High (≥5)</span>
                </div>
              </div>

              <div className="w-full border border-gray-300 rounded-lg text-sm font-mono bg-white mb-4">
                {result.code.split('\n').map((line, i) => {
                  const score = result.line_dc_map?.[i + 1] || 0;
                  const bg = heatColor(score);
                  return (
                    <div key={i} className={`px-3 py-1 ${bg}`}>
                      <span className="text-gray-500 pr-2">{i + 1}</span>
                      <span>{line}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="flex gap-4 justify-center mt-6">
              <button
                onClick={() => window.open('http://localhost:5000/download/pdf', '_blank')}
                className="bg-green-500 text-white px-6 py-2 rounded-lg hover:bg-green-600"
              >
                Download PDF
              </button>
              <button
                onClick={() => window.open('http://localhost:5000/download/csv', '_blank')}
                className="bg-yellow-500 text-white px-6 py-2 rounded-lg hover:bg-yellow-600"
              >
                Download CSV
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;

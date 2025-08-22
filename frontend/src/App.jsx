import React, { useState, useEffect } from "react";

const API = import.meta.env.VITE_API;

export default function App() {
  const [datasetId, setDatasetId] = useState("");
  const [target, setTarget] = useState("");
  const [nTrials, setNTrials] = useState(12);
  const [file, setFile] = useState(null);
  const [runId, setRunId] = useState("");
  const [status, setStatus] = useState(null);
  const [champion, setChampion] = useState(null);
  const [loading, setLoading] = useState(false);

  const uploadDataset = async () => {
    if (!file) return alert("Select a CSV file");
    const formData = new FormData();
    formData.append("file", file);
    setLoading(true);
    try {
      const res = await fetch(`${API}/datasets/upload`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setDatasetId(data.dataset_id);
      alert(`Uploaded: ${data.dataset_id}`);
    } catch (err) {
      console.error(err);
      alert("Upload failed");
    }
    setLoading(false);
  };

  const startRun = async () => {
    if (!datasetId || !target) return alert("Dataset and target required");
    setLoading(true);
    try {
      const res = await fetch(`${API}/runs/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          dataset_id: datasetId,
          target,
          n_trials: nTrials,
        }),
      });
      const data = await res.json();
      setRunId(data.run_id);
      alert(`Run started: ${data.run_id}`);
    } catch (err) {
      console.error(err);
      alert("Run start failed");
    }
    setLoading(false);
  };

  useEffect(() => {
    if (!runId) return;
    const interval = setInterval(async () => {
      const res = await fetch(`${API}/runs/${runId}/status`);
      const data = await res.json();
      setStatus(data);
      if (data.status === "done" || data.status === "error") {
        clearInterval(interval);
        fetchChampion();
      }
    }, 3000);
    return () => clearInterval(interval);
  }, [runId]);

  const fetchChampion = async () => {
    const res = await fetch(`${API}/models/champion`);
    const data = await res.json();
    setChampion(data);
  };

  return (
    <div className="p-6 font-sans bg-gray-100 min-h-screen">
      <h1 className="text-3xl font-bold mb-4 text-blue-600">
        NeuroGenX NG-1 v2
      </h1>

      {/* Upload Section */}
      <div className="bg-white rounded-xl shadow p-4 mb-6">
        <h2 className="text-xl font-semibold mb-2">1. Upload Dataset (CSV)</h2>
        <input
          type="file"
          accept=".csv"
          onChange={(e) => setFile(e.target.files[0])}
          className="block mb-2"
        />
        <button
          onClick={uploadDataset}
          disabled={loading}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Upload
        </button>
        {datasetId && <p className="mt-2 text-green-600">Uploaded: {datasetId}</p>}
      </div>

      {/* Start Run */}
      <div className="bg-white rounded-xl shadow p-4 mb-6">
        <h2 className="text-xl font-semibold mb-2">2. Start AutoML Run</h2>
        <input
          placeholder="Target column"
          value={target}
          onChange={(e) => setTarget(e.target.value)}
          className="border p-2 rounded mr-2"
        />
        <input
          type="number"
          min="4"
          max="200"
          value={nTrials}
          onChange={(e) => setNTrials(Number(e.target.value))}
          className="border p-2 rounded mr-2 w-24"
        />
        <button
          onClick={startRun}
          disabled={loading}
          className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
        >
          Start Run
        </button>
      </div>

      {/* Status */}
      {runId && (
        <div className="bg-white rounded-xl shadow p-4 mb-6">
          <h2 className="text-xl font-semibold mb-2">
            Run Status: {status?.status || "starting..."}
          </h2>
          <p className="text-gray-500 mb-2">Run ID: {runId}</p>
          {status?.events && (
            <ul className="text-sm text-gray-700">
              {status.events.map((e, idx) => (
                <li key={idx}>
                  <strong>{e.stage}</strong>: {JSON.stringify(e.data)}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Champion */}
      {champion && champion.metrics && (
        <div className="bg-white rounded-xl shadow p-4">
          <h2 className="text-xl font-semibold mb-2">Champion Model</h2>
          <p>Family: {champion.model.family}</p>
          <p>Metrics: AUC {champion.metrics.auc.toFixed(3)}, F1 {champion.metrics.f1.toFixed(3)}</p>
        </div>
      )}
    </div>
  );
}

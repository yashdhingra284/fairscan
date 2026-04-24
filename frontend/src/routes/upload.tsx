import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import axios from "axios";

export const Route = createFileRoute("/upload")({
  component: UploadPage,
});

function UploadPage() {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [gender, setGender] = useState(true);
  const [race, setRace] = useState(true);

  const handleFileDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const dropped = e.dataTransfer.files[0];
    if (dropped && dropped.name.endsWith(".csv")) {
      setFile(dropped);
      setError("");
    } else {
      setError("Only CSV files are supported");
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected && selected.name.endsWith(".csv")) {
      setFile(selected);
      setError("");
    } else {
      setError("Only CSV files are supported");
    }
  };

  const handleAnalyze = async () => {
    if (!file) {
      setError("Please select a CSV file first");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      const response = await axios.post("https://fairscan-backend.onrender.com", formData);
      const dataset_id = response.data.dataset_id;
      navigate({ to: "/analysis", search: { dataset_id } });
    } catch (err) {
      setError("Upload failed. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0f172a] text-white">
      {/* Navbar */}
<nav className="px-8 py-4 border-b border-slate-700 flex justify-between items-center">
  <span
    className="text-blue-400 text-xl font-bold cursor-pointer"
    onClick={() => navigate({ to: "/" })}
  >
    FairScan
  </span>
  <span className="text-slate-400 text-sm">
    Upload your dataset to scan for hidden bias
  </span>
</nav>

      {/* Main */}
      <div className="flex flex-col items-center justify-center px-4 py-20">
        <h1 className="text-3xl font-bold mb-2">Upload Your Dataset</h1>
        <p className="text-slate-400 mb-10">Upload a CSV file to scan it for hidden bias</p>

        <div className="bg-slate-800 rounded-2xl p-10 w-full max-w-xl shadow-lg">

          {/* Drop Zone */}
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleFileDrop}
            className="border-2 border-dashed border-slate-500 rounded-xl p-10 flex flex-col items-center justify-center cursor-pointer hover:border-blue-400 transition"
            onClick={() => document.getElementById("fileInput")?.click()}
          >
            <svg className="w-12 h-12 text-slate-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <p className="text-slate-400 text-center">
              {file ? (
                <span className="text-blue-400 font-semibold">{file.name}</span>
              ) : (
                "Drag & drop your CSV dataset here or click to browse"
              )}
            </p>
            <input
              id="fileInput"
              type="file"
              accept=".csv"
              className="hidden"
              onChange={handleFileSelect}
            />
          </div>

          {/* Sensitive Attributes */}
          <div className="mt-6">
            <p className="text-slate-300 font-semibold mb-3">Sensitive Attributes to Analyze:</p>
            <div className="flex gap-6">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={gender}
                  onChange={() => setGender(!gender)}
                  className="w-4 h-4 accent-blue-500"
                />
                <span className="text-slate-300">Gender</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={race}
                  onChange={() => setRace(!race)}
                  className="w-4 h-4 accent-blue-500"
                />
                <span className="text-slate-300">Race</span>
              </label>
            </div>
          </div>

          {/* Error */}
          {error && <p className="mt-4 text-red-400 text-sm">{error}</p>}

          {/* Button */}
          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="mt-8 w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-xl transition disabled:opacity-50"
          >
            {loading ? "Uploading..." : "Analyze for Bias"}
          </button>
        </div>
      </div>
    </div>
  );
}
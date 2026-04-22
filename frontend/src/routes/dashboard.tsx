import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import axios from "axios";

export const Route = createFileRoute("/dashboard")({
  component: DashboardPage,
});

function getBiasColor(level: string) {
  if (level === "Low") return "text-green-400 bg-green-400/10 border-green-400/20";
  if (level === "Medium") return "text-yellow-400 bg-yellow-400/10 border-yellow-400/20";
  return "text-red-400 bg-red-400/10 border-red-400/20";
}

function DashboardPage() {
  const navigate = useNavigate();
  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    setLoading(true);
    try {
      const response = await axios.get("http://localhost:8000/reports");
      setReports(response.data);
    } catch (err) {
      setError("Failed to load reports. Make sure the backend is running.");
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
        <button
          onClick={() => navigate({ to: "/upload" })}
          className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold px-4 py-2 rounded-lg transition"
        >
          + New Analysis
        </button>
      </nav>

      <div className="max-w-5xl mx-auto px-6 py-12">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold">Reports Dashboard</h1>
            <p className="text-slate-400 mt-1">All bias analysis reports generated so far</p>
          </div>
          <div className="bg-slate-800 rounded-xl px-5 py-3 text-center">
            <p className="text-2xl font-bold text-blue-400">{reports.length}</p>
            <p className="text-slate-400 text-sm">Total Reports</p>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-3 gap-4 mb-10">
          <div className="bg-slate-800 rounded-xl p-5">
            <p className="text-slate-400 text-sm mb-1">High Bias</p>
            <p className="text-red-400 text-2xl font-bold">
              {reports.filter(r => r.overall_bias_level === "High").length}
            </p>
          </div>
          <div className="bg-slate-800 rounded-xl p-5">
            <p className="text-slate-400 text-sm mb-1">Medium Bias</p>
            <p className="text-yellow-400 text-2xl font-bold">
              {reports.filter(r => r.overall_bias_level === "Medium").length}
            </p>
          </div>
          <div className="bg-slate-800 rounded-xl p-5">
            <p className="text-slate-400 text-sm mb-1">Low Bias</p>
            <p className="text-green-400 text-2xl font-bold">
              {reports.filter(r => r.overall_bias_level === "Low").length}
            </p>
          </div>
        </div>

        {/* Loading */}
        {loading && (
          <div className="flex justify-center py-20">
            <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        {/* Error */}
        {error && <p className="text-red-400">{error}</p>}

        {/* Reports List */}
        {!loading && reports.length === 0 && (
          <div className="text-center py-20">
            <p className="text-slate-400 text-lg mb-4">No reports yet</p>
            <button
              onClick={() => navigate({ to: "/upload" })}
              className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-xl font-semibold transition"
            >
              Upload Your First Dataset
            </button>
          </div>
        )}

        {!loading && reports.length > 0 && (
          <div className="space-y-4">
            {reports.map((report) => (
              <div
                key={report.report_id}
                className="bg-slate-800 rounded-xl p-6 hover:bg-slate-700 transition cursor-pointer"
                onClick={() => navigate({ to: "/analysis", search: { dataset_id: report.dataset_id } })}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-slate-300 font-semibold">
                        Report #{report.report_id}
                      </span>
                      <span className={`text-xs font-bold px-3 py-1 rounded-full border ${getBiasColor(report.overall_bias_level)}`}>
                        {report.overall_bias_level} Bias
                      </span>
                    </div>
                    <p className="text-slate-400 text-sm">Dataset ID: {report.dataset_id}</p>
                    <p className="text-slate-400 text-sm">Created: {new Date(report.created_at).toLocaleString()}</p>
                  </div>

                  {/* Scores */}
                  <div className="flex gap-6 text-right">
                    <div>
                      <p className="text-slate-400 text-xs mb-1">Disparate Impact</p>
                      <p className={`font-bold ${report.disparate_impact_score >= 0.8 ? "text-green-400" : "text-red-400"}`}>
                        {report.disparate_impact_score?.toFixed(3)}
                      </p>
                    </div>
                    <div>
                      <p className="text-slate-400 text-xs mb-1">Stat. Parity</p>
                      <p className={`font-bold ${report.statistical_parity_score <= 0.1 ? "text-green-400" : "text-red-400"}`}>
                        {report.statistical_parity_score?.toFixed(3)}
                      </p>
                    </div>
                    <div>
                      <p className="text-slate-400 text-xs mb-1">Equal Opp.</p>
                      <p className={`font-bold ${report.equal_opportunity_score <= 0.1 ? "text-green-400" : "text-red-400"}`}>
                        {report.equal_opportunity_score?.toFixed(3)}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Recommendation preview */}
                <p className="text-slate-500 text-sm mt-3 truncate">
                  💡 {report.recommendations}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import axios from "axios";

type SearchParams = {
  dataset_id: number;
};

export const Route = createFileRoute("/analysis")({
  validateSearch: (search: Record<string, unknown>): SearchParams => ({
    dataset_id: Number(search.dataset_id),
  }),
  component: AnalysisPage,
});

function BiasGauge({ score, label }: { score: number; label: string }) {
  const percentage = Math.round(score * 100);
  const color =
    score >= 0.8 ? "bg-green-500" : score >= 0.6 ? "bg-yellow-500" : "bg-red-500";
  const status =
    score >= 0.8 ? "Fair" : score >= 0.6 ? "Moderate" : "Biased";
  const statusColor =
    score >= 0.8 ? "text-green-400" : score >= 0.6 ? "text-yellow-400" : "text-red-400";

  return (
    <div className="bg-slate-800 rounded-xl p-6">
      <div className="flex justify-between items-center mb-2">
        <span className="text-slate-300 font-medium">{label}</span>
        <span className={`font-bold ${statusColor}`}>{status}</span>
      </div>
      <div className="w-full bg-slate-700 rounded-full h-3 mb-2">
        <div
          className={`h-3 rounded-full ${color} transition-all duration-700`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className="text-slate-400 text-sm">Score: {score.toFixed(4)}</span>
    </div>
  );
}

function AnalysisPage() {
  const { dataset_id } = Route.useSearch();
  const navigate = useNavigate();
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState<"gender" | "race">("gender");

  useEffect(() => {
    fetchAnalysis(activeTab);
  }, [activeTab]);

  const fetchAnalysis = async (sensitive_col: string) => {
    setLoading(true);
    setError("");
    try {
      const response = await axios.get(
        `https://fairscan-backend.onrender.com/analyze/${dataset_id}?sensitive_col=${sensitive_col}`
      );
      setReport(response.data);
    } catch (err) {
      setError("Analysis failed. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const getBiasColor = (level: string) => {
    if (level === "Low") return "text-green-400 bg-green-400/10";
    if (level === "Medium") return "text-yellow-400 bg-yellow-400/10";
    return "text-red-400 bg-red-400/10";
  };

  return (
    <div className="min-h-screen bg-[#0f172a] text-white">
      {/* Navbar */}
      <nav className="px-8 py-4 border-b border-slate-700 flex justify-between items-center">
        <span className="text-blue-400 text-xl font-bold">FairScan</span>
        <button
          onClick={() => navigate({ to: "/dashboard" })}
          className="text-slate-400 hover:text-white text-sm transition"
        >
          View All Reports →
        </button>
      </nav>

      <div className="max-w-4xl mx-auto px-6 py-12">
        <h1 className="text-3xl font-bold mb-2">Bias Analysis Report</h1>
        <p className="text-slate-400 mb-8">Dataset ID: {dataset_id}</p>

        {/* Tabs */}
        <div className="flex gap-2 mb-8">
          {["gender", "race"].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab as "gender" | "race")}
              className={`px-6 py-2 rounded-full text-sm font-semibold transition capitalize ${
                activeTab === tab
                  ? "bg-blue-600 text-white"
                  : "bg-slate-800 text-slate-400 hover:text-white"
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {loading && (
          <div className="flex justify-center py-20">
            <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        {error && <p className="text-red-400">{error}</p>}

        {report && !loading && (
          <>
            {/* Bias Level Badge */}
<div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full font-bold text-lg mb-8 ${getBiasColor(report.overall_bias_level)}`}>
  {report.overall_bias_level === "Low" ? "✅" : report.overall_bias_level === "Medium" ? "⚠️" : "🚨"} Overall Bias Level: {report.overall_bias_level}
</div>

            {/* Metrics */}
            <div className="grid grid-cols-1 gap-4 mb-8">
              <BiasGauge
                score={report.disparate_impact_score}
                label="Disparate Impact (≥0.8 is fair)"
              />
              <BiasGauge
                score={Math.max(0, 1 - report.statistical_parity_score)}
                label="Statistical Parity (higher is better)"
              />
              <BiasGauge
                score={Math.max(0, 1 - report.equal_opportunity_score)}
                label="Equal Opportunity (higher is better)"
              />
            </div>

            {/* Group Rates */}
            <div className="bg-slate-800 rounded-xl p-6 mb-8">
              <h2 className="text-lg font-bold mb-4">Positive Outcome Rates by Group</h2>
              <div className="space-y-3">
                {Object.entries(report.group_positive_rates).map(([group, rate]) => (
                  <div key={group} className="flex items-center gap-4">
                    <span className="text-slate-300 w-40 capitalize">{group}</span>
                    <div className="flex-1 bg-slate-700 rounded-full h-2">
                      <div
                        className="h-2 rounded-full bg-blue-500"
                        style={{ width: `${Math.round((rate as number) * 100)}%` }}
                      />
                    </div>
                    <span className="text-slate-400 text-sm w-12 text-right">
                      {((rate as number) * 100).toFixed(1)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Recommendations */}
            <div className="bg-slate-800 rounded-xl p-6 mb-8">
              <h2 className="text-lg font-bold mb-3">💡 Recommendations</h2>
              <p className="text-slate-300 leading-relaxed">{report.recommendations}</p>
            </div>

            {/* Actions */}
            <div className="flex gap-4">
              <button
                onClick={() => navigate({ to: "/dashboard" })}
                className="px-6 py-3 bg-slate-700 hover:bg-slate-600 rounded-xl transition font-semibold"
              >
                View All Reports
              </button>
                <button
              onClick={() => window.open(`https://fairscan-backend.onrender.com/reports/${report.report_id}/pdf?sensitive_col=${activeTab}`, "_blank")}
              className="px-6 py-3 bg-green-600 hover:bg-green-700 rounded-xl transition font-semibold"
                >
              ⬇ Download PDF Report
              </button>
              <button
                onClick={() => navigate({ to: "/upload" })}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-xl transition font-semibold"
              >
                Analyze Another Dataset
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
import { createFileRoute, useNavigate } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "FairScan — AI Bias Auditor" },
      {
        name: "description",
        content:
          "FairScan detects and fixes AI bias in datasets with fairness metrics and actionable recommendations.",
      },
      { property: "og:title", content: "FairScan — AI Bias Auditor" },
      {
        property: "og:description",
        content:
          "Detect and fix AI bias before it harms people. Run fairness metrics and get actionable fix suggestions.",
      },
    ],
  }),
  component: LandingPage,
});

function LandingPage() {
  const navigate = useNavigate();
  const goUpload = () => navigate({ to: "/upload" });

  const features = [
    {
      title: "Bias Detection",
      description: "Scans datasets for hidden discrimination.",
    },
    {
      title: "Fairness Metrics",
      description:
        "Measures Disparate Impact, Statistical Parity, Equal Opportunity.",
    },
    {
      title: "Fix Suggestions",
      description: "Actionable recommendations to reduce bias.",
    },
  ];

  return (
    <div className="min-h-screen bg-[#0f172a] text-white flex flex-col">
      {/* Navbar */}
      <header className="flex items-center justify-between px-6 md:px-12 py-5 border-b border-white/5">
        <div className="text-2xl font-bold text-blue-500 tracking-tight">
          FairScan
        </div>
        <button
          onClick={goUpload}
          className="bg-blue-600 hover:bg-blue-500 transition-colors text-white font-medium px-5 py-2.5 rounded-lg shadow-lg shadow-blue-600/20"
        >
          Get Started
        </button>
      </header>

      {/* Hero */}
      <section className="flex-1 flex flex-col items-center justify-center text-center px-6 py-20 md:py-28">
        <h1 className="text-4xl md:text-6xl font-extrabold text-white max-w-4xl leading-tight tracking-tight">
          Detect & Fix AI Bias Before It Harms People
        </h1>
        <p className="mt-6 text-lg md:text-xl text-gray-400 max-w-2xl">
          Audit your datasets and models for fairness. Identify hidden
          discrimination, measure impact, and get clear steps to fix it.
        </p>
        <button
          onClick={goUpload}
          className="mt-10 bg-blue-600 hover:bg-blue-500 transition-colors text-white text-lg font-semibold px-8 py-4 rounded-xl shadow-xl shadow-blue-600/30"
        >
          Upload Dataset
        </button>
      </section>

      {/* Features */}
      <section className="px-6 md:px-12 pb-24">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {features.map((f) => (
            <div
              key={f.title}
              className="bg-slate-800/60 border border-white/5 rounded-2xl p-8 hover:bg-slate-800 transition-colors"
            >
              <h3 className="text-xl font-semibold text-white mb-3">
                {f.title}
              </h3>
              <p className="text-gray-400 leading-relaxed">{f.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 py-6 text-center text-gray-500 text-sm">
        FairScan © 2026
      </footer>
    </div>
  );
}

export default LandingPage;

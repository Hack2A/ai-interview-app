import { FileText, Download, TrendingUp, Calendar } from "lucide-react";

const REPORTS = [
    {
        id: 1,
        title: "Weekly Performance Summary",
        date: "Oct 21 - Oct 27, 2023",
        type: "Weekly",
        overallScore: 87,
        highlight: "+5% improvement from last week",
        highlightPositive: true,
    },
    {
        id: 2,
        title: "Product Manager Mock — Detailed Report",
        date: "Oct 24, 2023",
        type: "Session",
        overallScore: 85,
        highlight: "Strong on structure, improve on specifics",
        highlightPositive: true,
    },
    {
        id: 3,
        title: "Technical Interview Analysis",
        date: "Oct 18, 2023",
        type: "Session",
        overallScore: 78,
        highlight: "Review system design fundamentals",
        highlightPositive: false,
    },
    {
        id: 4,
        title: "Monthly Progress Report — September",
        date: "Oct 1, 2023",
        type: "Monthly",
        overallScore: 82,
        highlight: "Consistent growth across all areas",
        highlightPositive: true,
    },
];

export default function ReportsPage() {
    return (
        <div className="w-[90%] max-w-5xl mx-auto px-6 py-10">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-indigo-100 rounded-xl flex items-center justify-center">
                        <FileText size={20} className="text-indigo-600" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-gray-800">My Reports</h1>
                        <p className="text-sm text-gray-400">Track your interview performance over time</p>
                    </div>
                </div>
            </div>

            {/* Stats Bar */}
            <div className="grid grid-cols-3 gap-4 mb-8">
                {[
                    { label: "Total Sessions", value: "24", icon: Calendar, color: "text-blue-600 bg-blue-50" },
                    { label: "Avg. Score", value: "84", icon: TrendingUp, color: "text-green-600 bg-green-50" },
                    { label: "Reports Generated", value: "18", icon: FileText, color: "text-purple-600 bg-purple-50" },
                ].map((stat) => (
                    <div key={stat.label} className="bg-white rounded-xl border border-gray-100 p-5 flex items-center gap-4">
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${stat.color}`}>
                            <stat.icon size={18} />
                        </div>
                        <div>
                            <p className="text-2xl font-bold text-gray-800">{stat.value}</p>
                            <p className="text-xs text-gray-400">{stat.label}</p>
                        </div>
                    </div>
                ))}
            </div>

            {/* Reports List */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-100">
                    <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Recent Reports</h2>
                </div>
                {REPORTS.map((report, i) => (
                    <div
                        key={report.id}
                        className={`flex items-center justify-between px-6 py-5 hover:bg-gray-50/80 transition-colors cursor-pointer
                            ${i < REPORTS.length - 1 ? "border-b border-gray-100" : ""}`}
                    >
                        <div className="flex items-center gap-4">
                            <div className="w-10 h-10 bg-gray-50 rounded-lg flex items-center justify-center text-gray-400">
                                <FileText size={18} />
                            </div>
                            <div>
                                <h3 className="text-sm font-semibold text-gray-800">{report.title}</h3>
                                <div className="flex items-center gap-3 mt-1">
                                    <span className="text-xs text-gray-400">{report.date}</span>
                                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-gray-100 text-gray-500 uppercase tracking-wider">
                                        {report.type}
                                    </span>
                                </div>
                            </div>
                        </div>
                        <div className="flex items-center gap-6">
                            <div className="text-right">
                                <p className="text-xl font-bold text-gray-800">{report.overallScore}</p>
                                <p className={`text-xs ${report.highlightPositive ? "text-green-500" : "text-amber-500"}`}>
                                    {report.highlight}
                                </p>
                            </div>
                            <button className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors cursor-pointer">
                                <Download size={16} />
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

import { HelpCircle, MessageCircle, BookOpen, Mail, ChevronRight } from "lucide-react";

const FAQ_ITEMS = [
    {
        question: "How does the AI interview work?",
        answer: "Our AI simulates realistic interview scenarios using advanced language models. Choose your role, industry, and difficulty — then practice with real-time feedback."
    },
    {
        question: "What types of interviews can I practice?",
        answer: "We support behavioral, technical, product, case study, and presentation-style interviews. You can customize the role and difficulty level."
    },
    {
        question: "How is my score calculated?",
        answer: "Scores are based on communication clarity, technical accuracy, confidence, pacing, and content relevance — each weighted by interview type."
    },
    {
        question: "Can I review my past interviews?",
        answer: "Yes! All session transcripts, scores, and AI feedback are saved in your Past Interviews tab on the dashboard."
    },
    {
        question: "Is my data secure?",
        answer: "Absolutely. All interview recordings and transcripts are encrypted and stored securely. We never share your data with third parties."
    },
];

const SUPPORT_CHANNELS = [
    {
        icon: MessageCircle,
        title: "Live Chat",
        desc: "Chat with our support team in real time",
        action: "Start Chat",
        color: "text-blue-600 bg-blue-50",
    },
    {
        icon: Mail,
        title: "Email Support",
        desc: "Get a response within 24 hours",
        action: "Send Email",
        color: "text-purple-600 bg-purple-50",
    },
    {
        icon: BookOpen,
        title: "Documentation",
        desc: "Browse guides and tutorials",
        action: "View Docs",
        color: "text-green-600 bg-green-50",
    },
];

export default function SupportPage() {
    return (
        <div className="w-[90%] max-w-5xl mx-auto px-6 py-10">
            {/* Header */}
            <div className="text-center mb-12">
                <div className="w-14 h-14 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <HelpCircle size={28} className="text-blue-600" />
                </div>
                <h1 className="text-3xl font-bold text-gray-800 mb-2">Help & Support</h1>
                <p className="text-gray-400 max-w-lg mx-auto">
                    Find answers to common questions or reach out to our support team
                </p>
            </div>

            {/* Support Channels */}
            <div className="grid grid-cols-3 gap-4 mb-12">
                {SUPPORT_CHANNELS.map((channel) => (
                    <div key={channel.title} className="bg-white rounded-xl border border-gray-100 p-6 flex flex-col items-center text-center hover:shadow-md hover:border-gray-200 transition-all duration-300 hover:-translate-y-0.5 cursor-pointer">
                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 ${channel.color}`}>
                            <channel.icon size={22} />
                        </div>
                        <h3 className="text-sm font-semibold text-gray-800 mb-1">{channel.title}</h3>
                        <p className="text-xs text-gray-400 mb-4">{channel.desc}</p>
                        <span className="text-xs font-semibold text-blue-600">{channel.action} →</span>
                    </div>
                ))}
            </div>

            {/* FAQ */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-100">
                    <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Frequently Asked Questions</h2>
                </div>
                {FAQ_ITEMS.map((faq, i) => (
                    <details
                        key={i}
                        className={`group ${i < FAQ_ITEMS.length - 1 ? "border-b border-gray-100" : ""}`}
                    >
                        <summary className="flex items-center justify-between px-6 py-4 cursor-pointer hover:bg-gray-50/80 transition-colors list-none">
                            <span className="text-sm font-medium text-gray-700">{faq.question}</span>
                            <ChevronRight size={16} className="text-gray-400 transition-transform duration-200 group-open:rotate-90" />
                        </summary>
                        <div className="px-6 pb-4">
                            <p className="text-sm text-gray-500 leading-relaxed">{faq.answer}</p>
                        </div>
                    </details>
                ))}
            </div>
        </div>
    );
}

import { Bell, CheckCircle, Info, AlertTriangle, MessageSquare } from "lucide-react";

const NOTIFICATIONS = [
    {
        id: 1,
        type: "success",
        icon: CheckCircle,
        iconColor: "text-green-500 bg-green-50",
        title: "Interview Session Completed",
        message: "Your Product Manager Mock Interview has been scored. Overall: 85/100.",
        time: "2 hours ago",
        unread: true,
    },
    {
        id: 2,
        type: "info",
        icon: Info,
        iconColor: "text-blue-500 bg-blue-50",
        title: "New Feature: Skill Gap Analysis",
        message: "Try our new Skill Gap Analysis tool to identify areas for improvement.",
        time: "5 hours ago",
        unread: true,
    },
    {
        id: 3,
        type: "warning",
        icon: AlertTriangle,
        iconColor: "text-amber-500 bg-amber-50",
        title: "Resume Update Recommended",
        message: "Your resume hasn't been updated in 30 days. Consider refreshing it.",
        time: "1 day ago",
        unread: false,
    },
    {
        id: 4,
        type: "message",
        icon: MessageSquare,
        iconColor: "text-purple-500 bg-purple-50",
        title: "Feedback from AI Coach",
        message: "Great improvement on communication clarity! Keep practicing technical questions.",
        time: "2 days ago",
        unread: false,
    },
    {
        id: 5,
        type: "success",
        icon: CheckCircle,
        iconColor: "text-green-500 bg-green-50",
        title: "Weekly Report Ready",
        message: "Your weekly performance summary is now available in Reports.",
        time: "3 days ago",
        unread: false,
    },
];

export default function NotificationsPage() {
    return (
        <div className="w-[90%] max-w-4xl mx-auto px-6 py-10">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
                        <Bell size={20} className="text-blue-600" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-gray-800">Notifications</h1>
                        <p className="text-sm text-gray-400">Stay updated on your progress</p>
                    </div>
                </div>
                <button className="text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors cursor-pointer">
                    Mark all as read
                </button>
            </div>

            {/* Notifications List */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                {NOTIFICATIONS.map((notification, i) => (
                    <div
                        key={notification.id}
                        className={`flex items-start gap-4 px-6 py-5 transition-colors hover:bg-gray-50/80 cursor-pointer
                            ${i < NOTIFICATIONS.length - 1 ? "border-b border-gray-100" : ""}
                            ${notification.unread ? "bg-blue-50/30" : ""}`}
                    >
                        <div className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 ${notification.iconColor}`}>
                            <notification.icon size={18} />
                        </div>
                        <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                                <h3 className={`text-sm font-semibold text-gray-800 ${notification.unread ? "" : "font-medium"}`}>
                                    {notification.title}
                                </h3>
                                {notification.unread && (
                                    <span className="w-2 h-2 rounded-full bg-blue-500 shrink-0" />
                                )}
                            </div>
                            <p className="text-sm text-gray-500 mt-0.5">{notification.message}</p>
                        </div>
                        <span className="text-xs text-gray-400 shrink-0 whitespace-nowrap">{notification.time}</span>
                    </div>
                ))}
            </div>
        </div>
    );
}

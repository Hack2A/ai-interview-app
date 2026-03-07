"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { User, Mail, LogOut, Calendar } from "lucide-react";
import { userService, UserProfileResponse } from "@/services/userService";

export default function Profile() {
    const router = useRouter();
    const [showSignOutConfirm, setShowSignOutConfirm] = useState(false);
    const [userData, setUserData] = useState<UserProfileResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Fetch user profile on component mount
    useEffect(() => {
        const fetchUserProfile = async () => {
            try {
                setLoading(true);
                const profileData = await userService.getUserProfile();
                setUserData(profileData);
                setError(null);
            } catch (err: any) {
                console.error("Failed to fetch user profile:", err);
                setError(err.response?.data?.message || "Failed to load profile data");
            } finally {
                setLoading(false);
            }
        };

        fetchUserProfile();
    }, []);

    const handleSignOut = () => {
        // Clear the authentication cookie
        document.cookie = "token=; path=/; max-age=0";
        // Redirect to login page
        router.push("/login");
    };

    // Format date for display
    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    };

    // Loading state
    if (loading) {
        return (
            <div className="min-h-screen w-full p-6 flex items-center justify-center">
                <div className="text-center space-y-4">
                    <div className="w-16 h-16 border-4 border-[#7C3AED] border-t-transparent rounded-full animate-spin mx-auto"></div>
                    <p className="text-[#94A3B8] text-lg">Loading profile...</p>
                </div>
            </div>
        );
    }

    // Error state
    if (error || !userData) {
        return (
            <div className="min-h-screen w-full p-6 flex items-center justify-center">
                <div className="text-center space-y-4 max-w-md">
                    <div className="w-16 h-16 bg-red-600/20 rounded-full flex items-center justify-center mx-auto">
                        <User className="w-8 h-8 text-red-500" />
                    </div>
                    <h2 className="text-2xl font-bold text-[#F1F5F9]">Failed to Load Profile</h2>
                    <p className="text-[#94A3B8]">{error || "Unable to fetch profile data"}</p>
                    <button
                        onClick={() => window.location.reload()}
                        className="mt-4 px-6 py-3 bg-[#7C3AED] hover:bg-[#6D28D9] text-white font-semibold rounded-xl transition-all"
                    >
                        Retry
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen w-full p-6 flex items-center justify-center">
            <div className="min-w-lg lg:min-w-2xl mx-auto space-y-6">
                {/* Header */}
                <div className="text-center space-y-2 mb-8">
                    <div className="w-24 h-24 bg-linear-to-br from-[#5B21B6] to-[#7C3AED] rounded-full flex items-center justify-center mx-auto shadow-2xl shadow-[#7C3AED]/50">
                        <User className="w-12 h-12 text-white" />
                    </div>
                    <h1 className="text-3xl font-bold text-[#F1F5F9]">Profile</h1>
                    <p className="text-[#94A3B8]">Manage your account information</p>
                </div>

                {/* Profile Information Card */}
                <div className="bg-[#1E293B] border border-[#7C3AED]/30 rounded-2xl shadow-xl shadow-[#7C3AED]/10 overflow-hidden">
                    {/* User Details */}
                    <div className="p-6 space-y-6">
                        {/* Username */}
                        <div className="flex items-center gap-4 p-4 bg-[#0F172A] rounded-xl border border-[#7C3AED]/20">
                            <div className="w-12 h-12 bg-[#7C3AED]/20 rounded-lg flex items-center justify-center shrink-0">
                                <User className="w-6 h-6 text-[#7C3AED]" />
                            </div>
                            <div className="flex-1">
                                <p className="text-sm text-[#94A3B8] mb-1">Username</p>
                                <p className="text-lg font-semibold text-[#F1F5F9]">{userData.username}</p>
                            </div>
                        </div>

                        {/* Email */}
                        <div className="flex items-center gap-4 p-4 bg-[#0F172A] rounded-xl border border-[#7C3AED]/20">
                            <div className="w-12 h-12 bg-[#7C3AED]/20 rounded-lg flex items-center justify-center shrink-0">
                                <Mail className="w-6 h-6 text-[#7C3AED]" />
                            </div>
                            <div className="flex-1">
                                <p className="text-sm text-[#94A3B8] mb-1">Email</p>
                                <p className="text-lg font-semibold text-[#F1F5F9]">{userData.email}</p>
                            </div>
                        </div>

                        {/* Date Joined */}
                        <div className="flex items-center gap-4 p-4 bg-[#0F172A] rounded-xl border border-[#7C3AED]/20">
                            <div className="w-12 h-12 bg-[#7C3AED]/20 rounded-lg flex items-center justify-center shrink-0">
                                <Calendar className="w-6 h-6 text-[#7C3AED]" />
                            </div>
                            <div className="flex-1">
                                <p className="text-sm text-[#94A3B8] mb-1">Member Since</p>
                                <p className="text-lg font-semibold text-[#F1F5F9]">{formatDate(userData.date_joined)}</p>
                            </div>
                        </div>
                    </div>

                    {/* Divider */}
                    <div className="border-t border-[#7C3AED]/20"></div>

                    {/* Sign Out Button */}
                    <div className="p-6">
                        <button
                            onClick={() => setShowSignOutConfirm(true)}
                            className="w-full py-3 px-4 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-xl shadow-lg shadow-red-600/30 hover:shadow-red-600/50 hover:scale-[1.02] transition-all focus:outline-none focus:ring-2 focus:ring-red-600/50 flex items-center justify-center gap-2 cursor-pointer"
                        >
                            <LogOut className="w-5 h-5" />
                            Sign Out
                        </button>
                    </div>
                </div>
            </div>

            {/* Sign Out Confirmation Modal */}
            {showSignOutConfirm && (
                <>
                    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-40" />
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                        <div className="bg-[#1E293B] border border-red-500/30 rounded-2xl shadow-2xl shadow-red-500/20 w-full max-w-md p-6">
                            <div className="text-center mb-6">
                                <div className="w-16 h-16 bg-red-600/20 rounded-full flex items-center justify-center mx-auto mb-4">
                                    <LogOut className="w-8 h-8 text-red-500" />
                                </div>
                                <h3 className="text-2xl font-bold text-[#F1F5F9] mb-2">Sign Out?</h3>
                                <p className="text-[#94A3B8]">
                                    Are you sure you want to sign out of your account?
                                </p>
                            </div>
                            <div className="flex gap-3">
                                <button
                                    onClick={() => setShowSignOutConfirm(false)}
                                    className="flex-1 py-3 px-4 bg-[#475569] text-white font-semibold rounded-xl hover:bg-[#64748B] transition-all cursor-pointer"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleSignOut}
                                    className="flex-1 py-3 px-4 bg-red-600 text-white font-semibold rounded-xl hover:bg-red-700 transition-all cursor-pointer"
                                >
                                    Sign Out
                                </button>
                            </div>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}
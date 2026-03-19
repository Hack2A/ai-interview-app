"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { User, Mail, LogOut, Calendar } from "lucide-react";
import { userService, UserProfileResponse } from "@/services/userService";
import { useNavbar } from "../NavbarContext";

export default function Profile() {
    const router = useRouter();
    const { setShowNavbar } = useNavbar();
    const [showSignOutConfirm, setShowSignOutConfirm] = useState(false);
    const [userData, setUserData] = useState<UserProfileResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Hide navbar on this page
    useEffect(() => {
        setShowNavbar(false);
        return () => setShowNavbar(true);
    }, [setShowNavbar]);

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
    // if (error || !userData) {
    //     return (
    //         <div className="min-h-screen w-full p-6 flex items-center justify-center">
    //             <div className="text-center space-y-4 max-w-md">
    //                 <div className="w-16 h-16 bg-red-600/20 rounded-full flex items-center justify-center mx-auto">
    //                     <User className="w-8 h-8 text-red-500" />
    //                 </div>
    //                 <h2 className="text-2xl font-bold text-[#F1F5F9]">Failed to Load Profile</h2>
    //                 <p className="text-[#94A3B8]">{error || "Unable to fetch profile data"}</p>
    //                 <button
    //                     onClick={() => window.location.reload()}
    //                     className="mt-4 px-6 py-3 bg-[#7C3AED] hover:bg-[#6D28D9] text-white font-semibold rounded-xl transition-all"
    //                 >
    //                     Retry
    //                 </button>
    //             </div>
    //         </div>
    //     );
    // }

    return (
        <div className="min-h-screen w-full pb-12">
            {/* Back Button */}
            <div className="w-[90%] mx-auto px-6 pt-6">
                <button
                    onClick={() => router.back()}
                    className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors cursor-pointer"
                >
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                    Back
                </button>
            </div>

            {/* Profile Card */}
            <div className="w-[90%] mx-auto px-6 mt-6">
                <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
                    {/* Banner */}
                    <div className="h-40 bg-linear-to-r from-blue-400 via-blue-500 to-cyan-400 relative">
                        {/* Profile Picture */}
                        <div className="absolute -bottom-12 left-1/2 transform -translate-x-1/2">
                            <div className="w-24 h-24 rounded-full bg-gray-300 border-4 border-white shadow-lg flex items-center justify-center">
                                <User className="w-12 h-12 text-gray-500" />
                            </div>
                        </div>
                    </div>

                    {/* Profile Info */}
                    <div className="pt-16 pb-6 text-center">
                        <h1 className="text-2xl font-bold text-gray-900">Alexandre Naud</h1>
                        <p className="text-gray-500 mt-1">Member since Aug 23, 2023 • New York, USA</p>
                    </div>

                    {/* Stats Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 px-6 pb-8">
                        <div className="bg-gray-50 rounded-xl p-6 text-center">
                            <div className="text-3xl font-bold text-gray-900">120</div>
                            <div className="text-sm text-gray-500 mt-1">Courses enrolled</div>
                        </div>
                        <div className="bg-gray-50 rounded-xl p-6 text-center">
                            <div className="text-3xl font-bold text-gray-900">2.8k</div>
                            <div className="text-sm text-gray-500 mt-1">Hours spent learning</div>
                        </div>
                        <div className="bg-gray-50 rounded-xl p-6 text-center">
                            <div className="text-3xl font-bold text-gray-900">26</div>
                            <div className="text-sm text-gray-500 mt-1">Tasks completed</div>
                        </div>
                    </div>

                    {/* Courses Enrolled Section */}
                    <div className="px-6 pb-8">
                        <h2 className="text-xl font-bold text-gray-900 mb-4">Courses enrolled</h2>
                        <div className="space-y-3">
                            {/* Course Item */}
                            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                                <div className="flex items-center gap-3">
                                    <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                    </svg>
                                    <span className="font-medium text-gray-700">Welcome Orientation</span>
                                </div>
                                <div className="flex items-center gap-4">
                                    <span className="text-sm text-gray-500">2 lessons • 8min</span>
                                    <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                                        <div className="h-full bg-blue-500 w-3/4"></div>
                                    </div>
                                </div>
                            </div>

                            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                                <div className="flex items-center gap-3">
                                    <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                    </svg>
                                    <span className="font-medium text-gray-700">Basic Financials - Overview and Startup Plan</span>
                                </div>
                                <div className="flex items-center gap-4">
                                    <span className="text-sm text-gray-500">8 lessons • 33min</span>
                                    <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                                        <div className="h-full bg-blue-500 w-1/2"></div>
                                    </div>
                                </div>
                            </div>

                            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                                <div className="flex items-center gap-3">
                                    <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                    </svg>
                                    <span className="font-medium text-gray-700">Basic Financials - Forecast Sales & Expenses</span>
                                </div>
                                <div className="flex items-center gap-4">
                                    <span className="text-sm text-gray-500">3 lessons • 8min</span>
                                    <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                                        <div className="h-full bg-blue-500 w-1/4"></div>
                                    </div>
                                </div>
                            </div>

                            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                                <div className="flex items-center gap-3">
                                    <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                    </svg>
                                    <span className="font-medium text-gray-700">Cash and Taxes</span>
                                </div>
                                <div className="flex items-center gap-4">
                                    <span className="text-sm text-gray-500">2 lessons • 8min</span>
                                    <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                                        <div className="h-full bg-blue-500 w-1/3"></div>
                                    </div>
                                </div>
                            </div>

                            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                                <div className="flex items-center gap-3">
                                    <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                    </svg>
                                    <span className="font-medium text-gray-700">Next Steps</span>
                                </div>
                                <div className="flex items-center gap-4">
                                    <span className="text-sm text-gray-500">2 lessons • 8min</span>
                                    <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                                        <div className="h-full bg-blue-500 w-1/5"></div>
                                    </div>
                                </div>
                            </div>

                            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                                <div className="flex items-center gap-3">
                                    <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                    </svg>
                                    <span className="font-medium text-gray-700">Optional Downloads</span>
                                </div>
                                <div className="flex items-center gap-4">
                                    <span className="text-sm text-gray-500">2 lessons • 8min</span>
                                    <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                                        <div className="h-full bg-blue-500 w-0"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Tasks Assigned Section */}
                    <div className="px-6 pb-8">
                        <h2 className="text-xl font-bold text-gray-900 mb-4">Tasks assigned</h2>
                        <div className="space-y-3">
                            {/* Task Item */}
                            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                                <div className="flex items-center gap-3">
                                    <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                    </svg>
                                    <span className="font-medium text-gray-700">Welcome Orientation</span>
                                </div>
                                <div className="flex items-center gap-4">
                                    <span className="text-sm text-gray-500">Due Aug 28, 2023</span>
                                    <span className="text-sm text-gray-500">2 lessons • 08min</span>
                                    <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                                        <div className="h-full bg-blue-500 w-0"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
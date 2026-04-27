"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
	User,
	Mail,
	ShieldAlert,
	ShieldCheck,
	CheckCircle,
	Clock,
} from "lucide-react";
import { useNavbar } from "../NavbarContext";
import { authService, UserProfile } from "@/services/authService";
import {
	reportService,
	InterviewSessionSummary,
} from "@/services/reportService";

export default function Profile() {
	const router = useRouter();
	const { setShowNavbar } = useNavbar();
	const [userData, setUserData] = useState<UserProfile | null>(null);
	const [interviews, setInterviews] = useState<InterviewSessionSummary[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);

	// Hide navbar on this page
	useEffect(() => {
		setShowNavbar(false);
		return () => setShowNavbar(true);
	}, [setShowNavbar]);

	// Fetch user profile and interviews
	useEffect(() => {
		const fetchData = async () => {
			try {
				setLoading(true);
				const [profileData, interviewsData] = await Promise.all([
					authService.getUserProfile(),
					reportService.getPastInterviews(),
				]);
				setUserData(profileData);
				setInterviews(interviewsData);
				setError(null);
			} catch (err: any) {
				console.error("Failed to fetch profile data:", err);
				setError("Failed to load profile data");
			} finally {
				setLoading(false);
			}
		};

		fetchData();
	}, []);

	// Calculate stats
	const completedInterviews = interviews.filter(
		(i) => i.status === "completed",
	);
	const avgScore =
		completedInterviews.length > 0
			? Math.round(
					completedInterviews.reduce(
						(acc, curr) =>
							acc +
							(curr.evaluation_report?.score ||
								curr.ats_combined_score ||
								0),
						0,
					) / completedInterviews.length,
				)
			: 0;

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

	if (error || !userData) {
		return (
			<div className="min-h-screen w-full p-6 flex items-center justify-center">
				<div className="text-center space-y-4 max-w-md">
					<div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto">
						<User className="w-8 h-8 text-red-500" />
					</div>
					<h2 className="text-2xl font-bold text-gray-900">
						Failed to Load Profile
					</h2>
					<p className="text-gray-500">
						{error || "Unable to fetch profile data"}
					</p>
					<button
						onClick={() => window.location.reload()}
						className="mt-4 px-6 py-3 bg-[#7C3AED] hover:bg-[#6D28D9] text-white font-semibold rounded-xl transition-all cursor-pointer"
					>
						Retry
					</button>
				</div>
			</div>
		);
	}

	return (
		<div className="min-h-screen w-full pb-12">
			{/* Back Button */}
			<div className="w-[90%] mx-auto px-6 pt-6">
				<button
					onClick={() => router.back()}
					className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors cursor-pointer font-medium"
				>
					<svg
						className="w-5 h-5"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
					>
						<path
							strokeLinecap="round"
							strokeLinejoin="round"
							strokeWidth={2}
							d="M15 19l-7-7 7-7"
						/>
					</svg>
					Back to Dashboard
				</button>
			</div>

			{/* Profile Card */}
			<div className="w-[90%] mx-auto px-6 mt-6">
				<div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
					{/* Banner */}
					<div className="h-40 bg-gradient-to-r from-blue-400 via-blue-500 to-indigo-500 relative">
						{/* Profile Picture */}
						<div className="absolute -bottom-12 left-1/2 transform -translate-x-1/2">
							<div className="w-24 h-24 rounded-full bg-white border-4 border-white shadow-lg flex items-center justify-center">
								<span className="text-3xl font-bold text-blue-500">
									{userData.name.charAt(0).toUpperCase()}
								</span>
							</div>
						</div>
					</div>

					{/* Profile Info */}
					<div className="pt-16 pb-6 text-center">
						<h1 className="text-2xl font-bold text-gray-900">
							{userData.name}
						</h1>
						<p className="text-gray-500 mt-1 flex items-center justify-center gap-2">
							<span>@{userData.username}</span>
						</p>
						<div className="flex items-center justify-center gap-4 mt-4">
							<div className="flex items-center gap-2 text-sm text-gray-600 bg-gray-50 px-3 py-1.5 rounded-full">
								<Mail size={16} className="text-gray-400" />
								{userData.email}
							</div>
							<div
								className={`flex items-center gap-2 text-sm px-3 py-1.5 rounded-full ${userData.is_onboard ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-700"}`}
							>
								{userData.is_onboard ? (
									<>
										<ShieldCheck
											size={16}
											className="text-emerald-500"
										/>
										Onboarded
									</>
								) : (
									<>
										<ShieldAlert
											size={16}
											className="text-amber-500"
										/>
										Pending Onboarding
									</>
								)}
							</div>
						</div>
					</div>

					{/* Stats Cards */}
					<div className="grid grid-cols-1 md:grid-cols-3 gap-4 px-8 pb-8">
						<div className="bg-gray-50 rounded-xl p-6 text-center border border-gray-100">
							<div className="text-3xl font-bold text-blue-600">
								{interviews.length}
							</div>
							<div className="text-sm text-gray-500 mt-1 font-medium flex items-center justify-center gap-1">
								<Clock size={14} /> Total Interviews
							</div>
						</div>
						<div className="bg-gray-50 rounded-xl p-6 text-center border border-gray-100">
							<div className="text-3xl font-bold text-emerald-600">
								{completedInterviews.length}
							</div>
							<div className="text-sm text-gray-500 mt-1 font-medium flex items-center justify-center gap-1">
								<CheckCircle size={14} /> Completed
							</div>
						</div>
						<div className="bg-gray-50 rounded-xl p-6 text-center border border-gray-100">
							<div className="text-3xl font-bold text-indigo-600">
								{avgScore}%
							</div>
							<div className="text-sm text-gray-500 mt-1 font-medium flex items-center justify-center gap-1">
								<svg
									className="w-4 h-4"
									fill="none"
									viewBox="0 0 24 24"
									stroke="currentColor"
								>
									<path
										strokeLinecap="round"
										strokeLinejoin="round"
										strokeWidth={2}
										d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
									/>
								</svg>
								Average Score
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	);
}

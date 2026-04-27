"use client";

import React, { useState } from "react";
import { GoogleLogin, GoogleOAuthProvider } from "@react-oauth/google";
import { authService } from "@/services/authService";
import { navigate } from "@/lib/navigation";

interface GoogleAuthProps {
	onSuccess?: (response: any) => void;
	onError?: (error: any) => void;
	redirectPath?: string;
	buttonText?: "signin_with" | "signup_with" | "continue_with";
	clientId?: string;
}

export default function GoogleAuth({
	onSuccess,
	onError,
	redirectPath = "/home",
	buttonText = "signin_with",
	clientId = "185103870142-n0vur7j8hn6bq8m8hpdp9kgo7ao6o07i.apps.googleusercontent.com",
}: GoogleAuthProps) {
	const [isLoading, setIsLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);

	const handleGoogleLogin = (credentialResponse: any) => {
		const idToken = credentialResponse.credential;
		setIsLoading(true);
		setError(null);

		// Execute async logic without blocking
		(async () => {
			try {
				const response = await authService.googleLogin(idToken);
				console.log("Google login response:", response);

				// Check if login was successful
				if (response && response.tokens && response.tokens.access) {
					// Token is already saved by authService.googleLogin in localStorage,
					// let's also save it in cookie for Next.js middleware
					document.cookie = `token=${response.tokens.access}; path=/; max-age=${60 * 60 * 24 * 7}`; // 7 days
					
					console.log("Login successful, token saved");

					// Call the onSuccess callback if provided
					if (onSuccess) {
						onSuccess(response);
					} else {
						// Default navigation
						navigate(redirectPath, true);
					}
				} else {
					const errorMsg = "Login failed. No token received.";
					setError(errorMsg);
					if (onError) {
						onError(new Error(errorMsg));
					}
				}
			} catch (error: any) {
				console.error("Google login error:", error);
				const errorMsg =
					error.response?.data?.error || error.message || "Google login failed. Please try again.";
				setError(errorMsg);

				if (onError) {
					onError(error);
				}
			} finally {
				setIsLoading(false);
			}
		})();
	};

	const handleGoogleLoginError = () => {
		console.error("Google login error callback triggered");
		const errorMsg = "Google login failed. Please try again.";
		setError(errorMsg);

		if (onError) {
			onError(new Error(errorMsg));
		}
	};

	return (
		<div className="w-full">
			<GoogleOAuthProvider clientId={clientId}>
				<div className="flex flex-col items-center">
					{/* Google Login Button */}
					<div className="flex justify-center w-full">
						<GoogleLogin
							onSuccess={handleGoogleLogin}
							onError={handleGoogleLoginError}
							size="large"
							width="384"
							theme="outline"
							shape="rectangular"
							text={buttonText}
						/>
					</div>

					{/* Error Message */}
					{error && (
						<p className="mt-2 text-sm text-red-500 text-center">{error}</p>
					)}

					{/* Loading State */}
					{isLoading && (
						<p className="mt-2 text-sm text-gray-600 text-center">
							Signing in...
						</p>
					)}
				</div>
			</GoogleOAuthProvider>
		</div>
	);
}

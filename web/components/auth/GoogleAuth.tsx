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
	redirectPath = "/dashboard",
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
				if (response.status === "success") {
					// Token is already saved by authService.googleLogin
					console.log("Login successful, token saved");

					// Call the onSuccess callback if provided
					if (onSuccess) {
						onSuccess(response);
					} else {
						// Default navigation
						navigate(redirectPath, true);
					}
				} else {
					const errorMsg = "Login failed. Please try again.";
					setError(errorMsg);
					if (onError) {
						onError(new Error(errorMsg));
					}
				}
			} catch (error: any) {
				console.error("Google login error:", error);
				const errorMsg =
					error.message || "Google login failed. Please try again.";
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
				<div className="flex flex-col items-center space-y-4 mt-4">
					{/* Divider */}
					<div className="relative w-full">
						<div className="absolute inset-0 flex items-center">
							<div className="w-full border-t border-gray-300"></div>
						</div>
						<div className="relative flex justify-center text-sm">
							<span className="px-2 bg-white text-gray-500">
								Or continue with
							</span>
						</div>
					</div>

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
						<p className="text-sm text-red-500 text-center">{error}</p>
					)}

					{/* Loading State */}
					{isLoading && (
						<p className="text-sm text-gray-600 text-center">
							Signing in...
						</p>
					)}
				</div>
			</GoogleOAuthProvider>
		</div>
	);
}

import apiClient from "./apiClient";
import axios from "axios";

export interface GoogleCredentialResponse {
	credential: string;
	select_by?: string;
}

export interface GoogleLoginResponse {
	message: string;
	status: string;
	token: string;
	id: string;
}

export const authService = {
	// Authentication service methods will be implemented here
	login: async (credentials: { email: string; password: string }) => {
		return apiClient.post("/auth/login/", credentials);
	},

	register: async (userData: { email: string; password: string }) => {
		return apiClient.post("/auth/register/", userData);
	},

	logout: async () => {
		localStorage.removeItem("token");
		return apiClient.post("/auth/logout/");
	},

	// Check if user is authenticated
	isAuthenticated: (): boolean => {
		const token = localStorage.getItem("token");
		return !!token;
	},

	// Check if user is authenticated with server validation (async)
	validateAuth: async (): Promise<boolean> => {
		const token = localStorage.getItem("token");
		if (token) {
			try {
				const res = await apiClient.get("/auth/check-auth");
				return res.data.status === "success";
			} catch (error) {
				// Token is invalid, remove it
				localStorage.removeItem("token");
				return false;
			}
		}
		return false;
	},

	// Get stored token
	getToken: (): string | null => {
		return localStorage.getItem("token");
	},

	// Clear stored token
	clearToken: (): void => {
		localStorage.removeItem("token");
	},

	// Google login
	googleLogin: async (idToken: string): Promise<GoogleLoginResponse> => {
		const endpoint = "/api/auth/login";
		try {
			const response = await axios.post(endpoint, { token: idToken });
			const responseData = response.data as GoogleLoginResponse;

			// Save the token to localStorage
			localStorage.setItem("token", responseData.token);

			// Set authorization header for future requests
			if (responseData && responseData.token) {
				axios.defaults.headers.common["Authorization"] =
					`Bearer ${responseData.token}`;
			}
			return responseData;
		} catch (error: any) {
			// If it's an AxiosError and has a response (e.g., 401, 400, etc.)
			if (axios.isAxiosError(error) && error.response) {
				// Re-throw the original AxiosError directly.
				// This is crucial. The SignInForm component needs the original error.response.status.
				throw error;
			}
			// For non-Axios errors or Axios errors without a response (e.g., network issues)
			throw new Error(
				"Google login failed. Please check your internet connection or try again.",
			);
		}
	},
};

import axios from "axios";
import type {
	AxiosInstance,
	AxiosResponse,
	InternalAxiosRequestConfig,
} from "axios";

// Create axios instance with base configuration
const apiClient: AxiosInstance = axios.create({
	baseURL: process.env.NEXT_PUBLIC_API_URL || "/api",
	timeout: 120000, // 2 minutes timeout for file uploads and ML processing
	withCredentials: true, // Send cookies with requests
	headers: {
		"Content-Type": "application/json",
	},
});

// Request interceptor to add authorization token from cookies
apiClient.interceptors.request.use(
	(config: InternalAxiosRequestConfig) => {
		// Ensure headers object exists
		config.headers = config.headers ?? {};

		// Get token from cookies
		const token =
			typeof window !== "undefined"
				? document.cookie
						.split("; ")
						.find((row) => row.startsWith("token="))
						?.split("=")[1]
				: null;

		// Add authorization header if token exists
		if (token) {
			// @ts-ignore
			config.headers.Authorization = `Bearer ${token}`;
		}

		return config;
	},
	(error) => {
		return Promise.reject(error);
	},
);

// Response interceptor to handle common errors
apiClient.interceptors.response.use(
	(response: AxiosResponse) => {
		return response;
	},
	(error) => {
		// Handle common error scenarios
		if (error.response?.status === 401) {
			// Unauthorized - clear token cookie and redirect to login
			document.cookie = "token=; path=/; max-age=0";
			// Redirect to login page
			window.location.href = "/login";
		} else if (error.response?.status === 403) {
			// Forbidden - handle as needed
			console.error("Access forbidden");
		} else if (error.response?.status >= 500) {
			// Server errors
			console.error(
				"Server error:",
				error.response?.data?.message || "Internal server error",
			);
		}

		return Promise.reject(error);
	},
);

export default apiClient;

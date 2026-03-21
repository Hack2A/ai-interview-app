import apiClient from "./apiClient";

export interface UserProfileResponse {
	id: number;
	username: string;
	email: string;
	date_joined: string;
}

export const userService = {
	// Get current user profile
	getUserProfile: async (): Promise<UserProfileResponse> => {
		const response = await apiClient.get<UserProfileResponse>("/auth/profile/");
		return response.data;
	},
};

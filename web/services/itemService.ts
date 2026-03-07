import apiClient from "./apiClient";

// Interface for store item request
export interface StoreItemRequest {
	name: string;
	body: string;
	is_adv: boolean;
	seed_phrase?: string; // Optional, required only when advanced is true
}

// Interface for get item request
export interface GetItemRequest {
	id: string;
	is_adv: boolean;
	seed_phrase?: string; // Optional, required only when advanced is true
}

// Interface for get item response
export interface GetItemResponse {
	item_name: string;
	plaintext: string;
	is_advanced: boolean;
}

// Interface for vault item
export interface VaultItem {
	id: number;
	name: string;
	ciphertext: string;
	is_advanced: boolean;
	created_at: string;
	block_hash?: string; // Only present for advanced items
}

// Interface for get all items response
export interface GetAllItemsResponse {
	normal: VaultItem[];
	advanced: VaultItem[];
	total_count: number;
}

export const itemService = {
	// Get all items
	getAllItems: async (): Promise<GetAllItemsResponse> => {
		const response = await apiClient.get<GetAllItemsResponse>("/vault/items/");
		return response.data;
	},

	// Store a new item
	storeItem: async (data: StoreItemRequest) => {
		// Validate that seed is provided when advanced is true
		if (data.is_adv && !data.seed_phrase) {
			throw new Error("Seed is required when advanced mode is enabled");
		}

		return apiClient.post("/vault/store/", data);
	},

	// Get a specific item
	getItem: async (params: GetItemRequest): Promise<GetItemResponse> => {
		// Validate that seed is provided when advanced is true
		if (params.is_adv && !params.seed_phrase) {
			throw new Error("Seed is required when advanced mode is enabled");
		}

		// Send data in request body for POST request
		const response = await apiClient.post<GetItemResponse>("/vault/decrypt/", params);
		return response.data;
	},
};

export default itemService;

"use client";

import { useState, useEffect } from "react";
import VaultItem from "./VaultItem";
import ViewVaultModal from "./ViewVaultModal";
import { Vault, ShieldCheck } from "lucide-react";
import itemService, { VaultItem as VaultItemType } from "@/services/itemService";

type VaultItemData = {
    id: string;
    name: string;
    content: string;
    isAdvanced: boolean;
};

interface VaultListProps {
    refreshTrigger?: number; // Used to trigger refresh from parent
}

export default function VaultList({ refreshTrigger }: VaultListProps) {
    const [isViewModalOpen, setIsViewModalOpen] = useState(false);
    const [selectedItem, setSelectedItem] = useState<VaultItemData | null>(null);
    const [normalItems, setNormalItems] = useState<VaultItemType[]>([]);
    const [advancedItems, setAdvancedItems] = useState<VaultItemType[]>([]);
    const [totalCount, setTotalCount] = useState(0);
    const [isLoading, setIsLoading] = useState(true);
    const [isLoadingItem, setIsLoadingItem] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Fetch all items on component mount and when refreshTrigger changes
    useEffect(() => {
        fetchAllItems();
    }, [refreshTrigger]);

    const fetchAllItems = async () => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await itemService.getAllItems();

            setNormalItems(response.normal);
            setAdvancedItems(response.advanced);
            setTotalCount(response.total_count);
        } catch (err: any) {
            console.error("Error fetching items:", err);
            setError(err.response?.data?.message || "Failed to load vault items");
        } finally {
            setIsLoading(false);
        }
    };

    const handleViewItem = async (item: VaultItemType, seed?: string) => {
        // If it's an advanced item and no seed is provided, just open the modal to ask for seed
        if (item.is_advanced && !seed) {
            const placeholderItem: VaultItemData = {
                id: item.id.toString(),
                name: item.name,
                content: "", // Empty content, will be filled after unlock
                isAdvanced: true,
            };
            setSelectedItem(placeholderItem);
            setIsViewModalOpen(true);
            return;
        }

        // Fetch the actual item content
        try {
            setIsLoadingItem(true);
            const params = {
                id: item.id.toString(),
                is_adv: item.is_advanced,
                ...(item.is_advanced && seed ? { seed_phrase: seed } : {}),
            };

            const response = await itemService.getItem(params);

            // Map the response to VaultItemData format
            const fullItem: VaultItemData = {
                id: item.id.toString(),
                name: response.item_name,
                content: response.plaintext,
                isAdvanced: response.is_advanced,
            };

            setSelectedItem(fullItem);
            setIsViewModalOpen(true);
        } catch (err: any) {
            console.error("Error fetching item:", err);
            alert(err.response?.data?.message || "Failed to fetch item details");
        } finally {
            setIsLoadingItem(false);
        }
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center py-12">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-[#7C3AED] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="text-[#94A3B8]">Loading your vault...</p>
                </div>
            </div>
        );
    }

    return (
        <>
            <div className="space-y-6">
                <h2 className="text-2xl font-bold text-[#F1F5F9] flex items-center gap-2">
                    <Vault className="w-7 h-7 text-[#7C3AED]" />
                    Access Vault
                    <span className="text-sm text-[#94A3B8] font-normal ml-2">
                        ({totalCount} total items)
                    </span>
                </h2>

                {error && (
                    <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
                        <p className="text-red-400 text-sm">{error}</p>
                        <button
                            onClick={fetchAllItems}
                            className="mt-2 text-xs text-red-300 hover:text-red-100 underline"
                        >
                            Try again
                        </button>
                    </div>
                )}

                <div className="grid md:grid-cols-2 gap-6">
                    {/* Normal Vault */}
                    <div className="space-y-4">
                        <div className="flex items-center gap-2 mb-4">
                            <div className="w-8 h-8 bg-[#7C3AED]/20 rounded-lg flex items-center justify-center">
                                <Vault className="w-5 h-5 text-[#7C3AED]" />
                            </div>
                            <h3 className="text-lg font-semibold text-[#F1F5F9]">
                                Normal Vault
                            </h3>
                            <span className="text-xs text-[#94A3B8] bg-[#1E293B] px-2 py-1 rounded-full">
                                {normalItems.length} items
                            </span>
                        </div>

                        <div className="space-y-3">
                            {normalItems.length > 0 ? (
                                normalItems.map((item) => (
                                    <VaultItem
                                        key={item.id}
                                        id={item.id.toString()}
                                        name={item.name}
                                        isAdvanced={false}
                                        onClick={() => handleViewItem(item)}
                                    />
                                ))
                            ) : (
                                <div className="text-center p-8 bg-[#1E293B] border border-[#7C3AED]/20 rounded-xl">
                                    <p className="text-[#94A3B8] text-sm">
                                        No items in normal vault
                                    </p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Advanced/Secured Vault */}
                    <div className="space-y-4">
                        <div className="flex items-center gap-2 mb-4">
                            <div className="w-8 h-8 bg-[#10B981]/20 rounded-lg flex items-center justify-center">
                                <ShieldCheck className="w-5 h-5 text-[#10B981]" />
                            </div>
                            <h3 className="text-lg font-semibold text-[#F1F5F9]">
                                Advanced Vault
                            </h3>
                            <span className="text-xs text-[#94A3B8] bg-[#1E293B] px-2 py-1 rounded-full">
                                {advancedItems.length} items
                            </span>
                        </div>

                        <div className="space-y-3">
                            {advancedItems.length > 0 ? (
                                advancedItems.map((item) => (
                                    <VaultItem
                                        key={item.id}
                                        id={item.id.toString()}
                                        name={item.name}
                                        isAdvanced={true}
                                        onClick={() => handleViewItem(item)}
                                    />
                                ))
                            ) : (
                                <div className="text-center p-8 bg-[#1E293B] border border-[#10B981]/20 rounded-xl">
                                    <p className="text-[#94A3B8] text-sm">
                                        No items in advanced vault
                                    </p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* View Modal */}
            <ViewVaultModal
                isOpen={isViewModalOpen}
                item={selectedItem}
                isLoading={isLoadingItem}
                onClose={() => {
                    setIsViewModalOpen(false);
                    setSelectedItem(null);
                }}
                onUnlock={(seed: string) => {
                    if (selectedItem) {
                        const item = advancedItems.find(v => v.id.toString() === selectedItem.id);
                        if (item) {
                            handleViewItem(item, seed);
                        }
                    }
                }}
            />
        </>
    );
}

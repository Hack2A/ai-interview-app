"use client";

import { useState } from "react";
import NewItem from "@/components/home/newItem";
import AddItemModal from "@/components/home/AddItemModal";
import VaultList from "@/components/home/VaultList";
import itemService from "@/services/itemService";

export default function Home() {
    const [isAddModalOpen, setIsAddModalOpen] = useState(false);
    const [refreshTrigger, setRefreshTrigger] = useState(0);

    const handleAddItem = async (data: any) => {
        try {
            const payload = {
                name: data.itemName,
                body: data.itemContent,
                is_adv: data.isAdvanced,
                ...(data.isAdvanced && data.securityWords ? { seed_phrase: data.securityWords } : {}),
            };

            await itemService.storeItem(payload);
            // Trigger refresh of vault list
            setRefreshTrigger(prev => prev + 1);
            return true;
        } catch (err: any) {
            console.error("Error adding item:", err);
            alert(err.response?.data?.message || "Failed to add item");
            return false;
        }
    };

    return (
        <div className="min-h-screen w-[90%] p-6 flex items-center justify-center">
            <div className="mx-auto space-y-8 min-w-[90%]">
                {/* Header */}
                <div className="text-center space-y-2">
                    <h1 className="text-4xl font-bold text-[#F1F5F9]">
                        Secure Vault
                    </h1>
                    <p className="text-[#94A3B8]">
                        Your encrypted storage for sensitive information
                    </p>
                </div>

                {/* Add New Item Section */}
                <NewItem onClick={() => setIsAddModalOpen(true)} />

                {/* Vault List Section */}
                <VaultList refreshTrigger={refreshTrigger} />
            </div>

            {/* Add Item Modal */}
            <AddItemModal
                isOpen={isAddModalOpen}
                onClose={() => setIsAddModalOpen(false)}
                onSubmit={handleAddItem}
            />
        </div>
    );
}
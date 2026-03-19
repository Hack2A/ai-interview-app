"use client";

import ProtectedNavbar from "@/components/navbar/ProtectedNavbar";
import { NavbarProvider, useNavbar } from "./NavbarContext";

function ProtectedContent({ children }: { children: React.ReactNode }) {
    const { showNavbar } = useNavbar();

    return (
        <div
            className={`h-screenflex flex-col bg-linear-to-br ${showNavbar ? "pt-17" : ""}`}
        >
            {showNavbar && (
                <ProtectedNavbar />
            )}
            {children}
        </div>
    );
}

export default function AuthLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <NavbarProvider>
            <ProtectedContent>{children}</ProtectedContent>
        </NavbarProvider>
    );
}

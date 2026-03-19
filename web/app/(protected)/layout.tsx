"use client";

import ProtectedNavbar from "@/components/navbar/ProtectedNavbar";
import { NavbarProvider, useNavbar } from "./NavbarContext";

function ProtectedContent({ children }: { children: React.ReactNode }) {
    const { showNavbar } = useNavbar();

    return (
        <div className="h-screen flex flex-col justify-center items-center bg-linear-to-br">
            {showNavbar && (
                <div className="fixed top-0 left-0 w-full z-10">
                    <ProtectedNavbar />
                </div>
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

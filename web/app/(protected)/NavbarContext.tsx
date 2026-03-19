"use client";

import { createContext, useContext, useState, ReactNode } from "react";

interface NavbarContextType {
    showNavbar: boolean;
    setShowNavbar: (show: boolean) => void;
}

const NavbarContext = createContext<NavbarContextType | undefined>(undefined);

export function NavbarProvider({ children }: { children: ReactNode }) {
    const [showNavbar, setShowNavbar] = useState(true);

    return (
        <NavbarContext.Provider value={{ showNavbar, setShowNavbar }}>
            {children}
        </NavbarContext.Provider>
    );
}

export function useNavbar() {
    const context = useContext(NavbarContext);
    if (context === undefined) {
        throw new Error("useNavbar must be used within a NavbarProvider");
    }
    return context;
}

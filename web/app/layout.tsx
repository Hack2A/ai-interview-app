import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { RouterProvider } from "@/lib/navigation";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Cryptrael Vault",
  description: "Cryptrael Vault is a secure digital vault platform that combines end-to-end AES-256 encryption, SHA-256 integrity hashing, and blockchain-based audit logging to provide tamper-proof, zero-trust storage for sensitive digital assets.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="bg-slate-900 text-white">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <RouterProvider />
        {children}
      </body>
    </html>
  );
}

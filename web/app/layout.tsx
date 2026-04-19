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
  title: "IntrvAI - Your AI Interview Coach",
  description: "IntrvAI is your AI interview coach which will help you in your interview prep.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="bg-gray-50 text-black">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <RouterProvider />
        {children}
      </body>
    </html>
  );
}

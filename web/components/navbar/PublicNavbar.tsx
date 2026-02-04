"use client";

import Link from "next/link";

export default function PublicNavbar() {
    return (
        <div className="w-full flex items-center justify-between p-4">
            <Link href="/">BeaverAI</Link>
            <ul className="flex gap-5">
                <li>
                    <Link href="/login">Home</Link>
                </li>
                <li>
                    <Link href="/register">Features</Link>
                </li>
                <li>
                    <Link href="/">Pricing</Link>
                </li>
            </ul>
            <div className="flex gap-4">
                <Link href="/login">Log in</Link>
                <Link href="/register">Get Started</Link>
            </div>
        </div>
    );
}
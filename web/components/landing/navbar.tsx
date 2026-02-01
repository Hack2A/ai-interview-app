"use client";

import Link from "next/link";

export default function Navbar() {
    return (
        <div className="w-full flex items-center justify-between p-4">
            <div>BeaverAI</div>
            <ul className="flex gap-5">
                <li>
                    <Link href="/login">Login</Link>
                </li>
                <li>
                    <Link href="/register">Register</Link>
                </li>
                <li>
                    <Link href="/">Something</Link>
                </li>
            </ul>
        </div>
    );
}
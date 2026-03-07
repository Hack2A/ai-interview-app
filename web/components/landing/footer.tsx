"use client";

import Link from "next/link";

export default function Footer() {
  return (
    <footer className="relative bg-linear-to-b from-[#0F172A] to-[#020617] border-t border-[#7C3AED]/20">
      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-linear-to-br from-[#5B21B6]/5 to-transparent pointer-events-none"></div>

      <div className="relative max-w-7xl mx-auto px-6 py-16">
        <div className="grid md:grid-cols-2 lg:grid-cols-5 gap-12 mb-12">
          {/* Brand Section */}
          <div className="lg:col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-10 h-10 bg-linear-to-br from-[#5B21B6] to-[#7C3AED] rounded-xl flex items-center justify-center shadow-lg shadow-[#7C3AED]/30">
                <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <span className="text-2xl font-bold text-[#F1F5F9]">Cryptrael Vault</span>
            </div>
            <p className="text-[#94A3B8] leading-relaxed max-w-md mb-6">
              Enterprise-grade digital vault with blockchain-integrated security.
              Protecting what matters most with unbreakable encryption.
            </p>
            {/* Social Icons */}
            <div className="flex gap-4">
              <a
                href="#"
                className="w-10 h-10 bg-[#1E293B] hover:bg-[#7C3AED] rounded-lg flex items-center justify-center transition-all duration-300 hover:scale-110"
                aria-label="Twitter"
              >
                <svg className="w-5 h-5 text-[#94A3B8] hover:text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z" />
                </svg>
              </a>
              <a
                href="#"
                className="w-10 h-10 bg-[#1E293B] hover:bg-[#7C3AED] rounded-lg flex items-center justify-center transition-all duration-300 hover:scale-110"
                aria-label="LinkedIn"
              >
                <svg className="w-5 h-5 text-[#94A3B8] hover:text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
                </svg>
              </a>
              <a
                href="#"
                className="w-10 h-10 bg-[#1E293B] hover:bg-[#7C3AED] rounded-lg flex items-center justify-center transition-all duration-300 hover:scale-110"
                aria-label="GitHub"
              >
                <svg className="w-5 h-5 text-[#94A3B8] hover:text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                </svg>
              </a>
            </div>
          </div>

          {/* Product Links */}
          <div>
            <h3 className="text-[#F1F5F9] font-semibold mb-4">Product</h3>
            <ul className="space-y-3">
              <li>
                <Link href="#" className="text-[#94A3B8] hover:text-[#10B981] transition-colors">
                  Features
                </Link>
              </li>
              <li>
                <Link href="#" className="text-[#94A3B8] hover:text-[#10B981] transition-colors">
                  Pricing
                </Link>
              </li>
              <li>
                <Link href="#" className="text-[#94A3B8] hover:text-[#10B981] transition-colors">
                  Architecture
                </Link>
              </li>
              <li>
                <Link href="#" className="text-[#94A3B8] hover:text-[#10B981] transition-colors">
                  API Docs
                </Link>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h3 className="text-[#F1F5F9] font-semibold mb-4">Resources</h3>
            <ul className="space-y-3">
              <li>
                <Link href="#" className="text-[#94A3B8] hover:text-[#10B981] transition-colors">
                  Documentation
                </Link>
              </li>
              <li>
                <Link href="#" className="text-[#94A3B8] hover:text-[#10B981] transition-colors">
                  Whitepapers
                </Link>
              </li>
              <li>
                <Link href="#" className="text-[#94A3B8] hover:text-[#10B981] transition-colors">
                  Blog
                </Link>
              </li>
              <li>
                <Link href="#" className="text-[#94A3B8] hover:text-[#10B981] transition-colors">
                  Support
                </Link>
              </li>
            </ul>
          </div>

          {/* Security & Compliance */}
          <div>
            <h3 className="text-[#F1F5F9] font-semibold mb-4">Security</h3>
            <ul className="space-y-3">
              <li>
                <Link href="#" className="text-[#94A3B8] hover:text-[#10B981] transition-colors">
                  Security Overview
                </Link>
              </li>
              <li>
                <Link href="#" className="text-[#94A3B8] hover:text-[#10B981] transition-colors">
                  Compliance
                </Link>
              </li>
              <li>
                <Link href="#" className="text-[#94A3B8] hover:text-[#10B981] transition-colors">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link href="#" className="text-[#94A3B8] hover:text-[#10B981] transition-colors">
                  Terms of Service
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-[#7C3AED]/20 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-[#94A3B8] text-sm">
            © 2026 Cryptrael Vault. All rights reserved.
          </p>
          <div className="flex items-center gap-6 text-sm text-[#94A3B8]">
            <span className="flex items-center gap-2">
              <svg className="w-4 h-4 text-[#10B981]" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
              </svg>
              Enterprise-Grade Security
            </span>
            <span className="flex items-center gap-2">
              <svg className="w-4 h-4 text-[#10B981]" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              SOC 2 Compliant
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
}
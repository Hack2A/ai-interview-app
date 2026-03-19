"use client";

import review from "@/components/assets/review-home.svg";

export default function GreetSection() {
    return (
        <section className="basis-2/5 shrink-0 flex w-[90%] mx-auto justify-center items-center px-20 py-5">
            {/* Left Written Section */}
            <div className="flex-1">
                {/* Text Section */}
                <div className="flex flex-col">
                    <h1 className="text-4xl font-bold">Hey [Username]!</h1>
                    <h2 className="text-2xl font-bold">Let's take a quick look at your progress</h2>
                    <span className="w-[85%] text-gray-500">Jump back into your latest interview and review your performance.See what worked, what didn't, and what to improve next.</span>
                </div>
                {/* CTA Section */}
                <div className="flex gap-4 items-center mt-6">
                    <button className="px-6 py-3 bg-yellow-200 text-yellow-900 rounded-lg font-semibold hover:bg-yellow-300 transition-colors duration-200 cursor-pointer">
                        Last Interview Report
                    </button>
                    <span className="text-gray-400 font-medium">or</span>
                    <button className="px-6 py-3 bg-blue-200 text-blue-900 rounded-lg font-semibold hover:bg-blue-300 transition-colors duration-200 cursor-pointer">
                        Start New Interview
                    </button>
                </div>
            </div>
            {/* Right Image Section */}
            <div className="w-[35%] h-full flex items-start justify-center">
                <img src={review.src} alt="Review Illustration" className="w-full h-full object-cover" />
            </div>
        </section>
    );
}
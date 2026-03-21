import ProtectedNavbar from "@/components/navbar/ProtectedNavbar";

export default function AuthLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="min-h-screen flex flex-col justify-center items-center bg-linear-to-br from-[#0F172A] via-[#1E293B] to-[#0F172A]">
            <div className="fixed top-0 left-0 w-full z-10">
                <ProtectedNavbar />
            </div>
            {children}
        </div>
    );
}

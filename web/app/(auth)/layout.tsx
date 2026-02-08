import AuthNavbar from "@/components/navbar/AuthNavbar";

export default function AuthLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="min-h-screen flex flex-col justify-center items-center">
            <div className="fixed top-0 left-0 w-full z-10">
                <AuthNavbar />
            </div>
            {children}
        </div>
    );
}

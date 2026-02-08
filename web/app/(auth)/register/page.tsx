import RegisterForm from "@/components/auth/regform";

export default function Register() {
    return (
        <div className="min-h-screen w-full flex">
            <div className="w-1/2 h-screen flex items-center justify-center border-r border-gray-800">
                <div className="text-center space-y-4 px-8">
                    <h1 className="text-4xl font-bold text-white">
                        Join Us Today
                    </h1>
                    <p className="text-gray-400 text-lg">
                        Create your account and start your journey
                    </p>
                </div>
            </div>
            <div className="w-1/2 h-screen flex items-center justify-center bg-white">
                <RegisterForm />
            </div>
        </div>
    );
}
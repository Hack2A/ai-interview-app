import LoginForm from "@/components/auth/loginform";

export default function Login() {
    return (
        <div className="w-full h-full flex flex-col items-center justify-center gap-10">
            <h1 className="text-5xl">Login</h1>
            <LoginForm />
        </div>
    );
}
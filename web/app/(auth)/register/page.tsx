import RegisterForm from "@/components/auth/regform";

export default function PageName() {
    return (
        <div className="w-full h-full flex flex-col items-center justify-center gap-10">
            <h1 className="text-5xl">Register</h1>
            <RegisterForm />
        </div>
    );
}
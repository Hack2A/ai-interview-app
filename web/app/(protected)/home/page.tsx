import ActionSection from "@/components/home/ActionSection";
import GreetSection from "@/components/home/GreetSection";

export default function Home() {
    return (
        <div className="w-full h-full flex flex-col min-h-0 ">
            <GreetSection />
            <ActionSection />
        </div>
    );
}
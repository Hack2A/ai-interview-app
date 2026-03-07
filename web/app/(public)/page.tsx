import PublicNavbar from "@/components/navbar/PublicNavbar";
import Hero from "@/components/landing/Hero";
import WhyChooseUs from "@/components/landing/WhyChooseUs";
import Testimonials from "@/components/landing/Testimonials";
import InsightSection from "@/components/landing/insights";
import Footer from "@/components/landing/footer";

export default function Home() {
    return (
        <>
            <PublicNavbar />
            <Hero />
            <WhyChooseUs />
            <Testimonials />
            {/* <InsightSection /> */}
            <Footer />
        </>
    );
}
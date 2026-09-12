import { CertifySection } from "@/components/landing/CertifySection";
import { ClosingCTA, SiteFooter } from "@/components/landing/SiteFooter";
import { EvidenceSection } from "@/components/landing/EvidenceSection";
import { Hero } from "@/components/landing/Hero";
import { PropagateSection } from "@/components/landing/PropagateSection";
import { RecordSection } from "@/components/landing/RecordSection";
import { SiteHeader } from "@/components/landing/SiteHeader";
import { ThesisSection } from "@/components/landing/ThesisSection";
import { TrustTicker } from "@/components/landing/TrustTicker";
import { VerifySection } from "@/components/landing/VerifySection";

export default function Landing() {
  return (
    <>
      <SiteHeader />
      <main id="main">
        <Hero />
        <TrustTicker />
        <ThesisSection />
        <RecordSection />
        <VerifySection />
        <PropagateSection />
        <CertifySection />
        <EvidenceSection />
        <ClosingCTA />
      </main>
      <SiteFooter />
    </>
  );
}

import { apiFetch } from "@/lib/api";
import { EmptyState } from "@/components/ui";
import CertificatesClient from "@/components/CertificatesClient";

type CertRow = {
  id: string; serial: string; execution_id: string; status: string;
  alg: string; key_id: string; issued_at: string; revoked_reason: string | null;
};

export default async function CertificatesPage() {
  let rows: CertRow[];
  try {
    rows = await apiFetch<CertRow[]>("/api/v1/certificates");
  } catch (e) {
    return <EmptyState title="Could not load certificates" hint={(e as { message?: string }).message} />;
  }

  return (
    <div className="space-y-5">
      <header>
        <h1 className="text-xl font-bold tracking-tight">AI Trust Certificates</h1>
        <p className="mt-1 text-sm text-ink-dim">
          Ed25519-signed in-toto statements over each execution&apos;s provenance.
          Verification = signature + revocation status + subject fingerprint match.
        </p>
      </header>
      {rows.length === 0 ? (
        <EmptyState title="No certificates issued" hint="Certificates are issued automatically for executions that pass all expected-state checks." />
      ) : (
        <CertificatesClient rows={rows} />
      )}
    </div>
  );
}

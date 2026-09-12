import type { Metadata, Viewport } from "next";
import { IBM_Plex_Sans, JetBrains_Mono, Space_Grotesk } from "next/font/google";

import { ThemeProvider, themeInitScript } from "@/components/theme";
import "./globals.css";

const spaceGrotesk = Space_Grotesk({
  weight: ["400", "500", "600", "700"],
  subsets: ["latin"],
  variable: "--font-space-grotesk",
  display: "swap",
});

const plexSans = IBM_Plex_Sans({
  weight: ["400", "500", "600", "700"],
  subsets: ["latin"],
  variable: "--font-plex-sans",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  weight: ["400", "500", "600"],
  subsets: ["latin"],
  variable: "--font-jetbrains-mono",
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL(process.env.SITE_URL ?? "http://localhost:3000"),
  title: {
    default: "AegisTrace — Continuous AI Execution Attestation",
    template: "%s · AegisTrace",
  },
  description:
    "AegisTrace builds a causal provenance graph of every component behind an AI execution, verifies the observed run against its expected contract, propagates compromise to every dependent output, and issues verifiable AI Trust Certificates.",
  keywords: [
    "AI security", "provenance", "attestation", "supply chain",
    "trust propagation", "MCP security", "agent security",
  ],
  openGraph: {
    type: "website",
    siteName: "AegisTrace",
    title: "AegisTrace — Continuous AI Execution Attestation",
    description:
      "Runtime causal trust for AI agents: provenance graphs, expected-vs-observed verification, trust propagation, verifiable per-execution certificates.",
  },
  twitter: {
    card: "summary_large_image",
    title: "AegisTrace — Continuous AI Execution Attestation",
    description:
      "Prove what caused every AI output. Runtime causal trust for agents.",
  },
  robots: { index: true, follow: true },
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: dark)", color: "#0b0e14" },
    { media: "(prefers-color-scheme: light)", color: "#f4f2ec" },
  ],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className={`${spaceGrotesk.variable} ${plexSans.variable} ${jetbrainsMono.variable}`}
      suppressHydrationWarning
    >
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeInitScript }} />
      </head>
      <body>
        <a
          href="#main"
          className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-lg focus:border focus:border-accent focus:bg-surface focus:px-4 focus:py-2 focus:text-sm"
        >
          Skip to content
        </a>
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}

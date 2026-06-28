import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";

import { AuthGate } from "@/components/auth-gate";

import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

export const metadata: Metadata = {
  title: "AI Decision OS",
  description:
    "Turn any decision into a clear, reasoned, visual recommendation in under 30 seconds.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-sans antialiased`}>
        <AuthGate />
        <header className="fixed inset-x-0 top-0 z-10 flex items-center justify-between px-6 py-4 text-sm">
          <Link href="/" className="font-medium tracking-tight">
            AI Decision OS
          </Link>
          <Link href="/history" className="text-muted-foreground transition hover:text-foreground">
            History
          </Link>
        </header>
        {children}
      </body>
    </html>
  );
}

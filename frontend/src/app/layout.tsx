import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import "./globals.css";

const inter = Inter({ 
  subsets: ["latin"],
  variable: "--font-inter",
  display: 'swap',
});

const outfit = Outfit({ 
  subsets: ["latin"],
  variable: "--font-outfit",
  display: 'swap',
});

export const metadata: Metadata = {
  title: "ACME Corporation | AI-Powered Customer Support",
  description: "Experience the future of customer support with ACME Corporation's AI-powered platform. Get instant answers, track orders, and request refunds 24/7.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${outfit.variable}`}>
      <body className="font-sans min-h-screen flex flex-col selection:bg-violet-500 selection:text-white">
        {children}
      </body>
    </html>
  );
}

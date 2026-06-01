import type { Metadata } from "next";
import { Elms_Sans, Source_Sans_3 } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

/** App uses client-side auth + React Query; avoid static prerender without providers. */
export const dynamic = "force-dynamic";

const elmsSans = Elms_Sans({
  variable: "--font-heading",
  subsets: ["latin"],
  weight: ["500", "600", "700"],
});

const sourceSans = Source_Sans_3({
  variable: "--font-body",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

export const metadata: Metadata = {
  title: "Subjective Alignment",
  description: "Workplace assessment for executives, HR, and individuals",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${elmsSans.variable} ${sourceSans.variable} h-full`}
    >
      <body className="min-h-full flex flex-col font-sans">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}

import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import { 
  Brain, 
  Home, 
  Sparkles, 
  BarChart3, 
  Save, 
  BookOpen, 
  FileText,
  Github
} from "lucide-react";
import "./globals.css";
import { ThemeProvider } from "@/components/ui/theme-provider";
import { ModeToggle } from "@/components/ui/mode-toggle";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Hint Generation and Evaluation",
  description: "Interactive UI for generating, evaluating and visualizing hints.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-background text-foreground min-h-screen flex flex-col selection:bg-primary/30`}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {/* --- GLOBAL HEADER --- */}
          <header className="sticky top-0 z-50 w-full border-b border-border bg-background/80 backdrop-blur-md">
            <nav className="mx-auto flex h-16 max-w-[1900px] items-center justify-between px-6">
              
              {/* Logo Area */}
              <Link 
                href="/" 
                className="flex items-center gap-3 group transition-opacity hover:opacity-90"
              >
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary shadow-lg shadow-primary/20 border border-white/10 text-primary-foreground">
                  <Brain className="h-5 w-5" />
                </div>
                <span className="font-bold tracking-tight text-foreground text-lg">
                  Hint Generation and Evaluation
                </span>
              </Link>

              {/* Navigation Links */}
              <div className="hidden md:flex items-center gap-1">
                <NavLink href="/" icon={<Home className="w-4 h-4" />} label="Home" />
                <NavLink href="/generation_and_evaluation" icon={<Sparkles className="w-4 h-4" />} label="Generate Hints" />
                <NavLink href="/metrics" icon={<BarChart3 className="w-4 h-4" />} label="Metrics" />
                <NavLink href="/save_and_load" icon={<Save className="w-4 h-4" />} label="Save / Load" />
              </div>

              <div className="flex items-center gap-4">
                 <ModeToggle />
                 
                 <div className="md:hidden">
                   <span className="text-xs text-muted-foreground font-medium">Menu</span>
                 </div>
              </div>
            </nav>
          </header>

          {/* --- MAIN CONTENT --- */}
          <main className="flex-1 relative">
            {children}
          </main>

          {/* --- FOOTER --- */}
          <footer className="border-t border-border bg-background py-6 mt-auto">
            <div className="mx-auto max-w-[1900px] px-6 flex flex-col sm:flex-row justify-between items-center gap-4 text-xs text-muted-foreground">
              
              <div className="flex items-center gap-2">
                <span className="font-semibold text-foreground">Hint Generation and Evaluation</span>
                <span className="hidden sm:inline text-border">|</span>
                <span>v1.0</span>
              </div>

              <div className="flex items-center gap-6">
                <a
                  href="https://github.com/DataScienceUIBK/HintEval" 
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-2 hover:text-primary transition-colors"
                >
                  <Github className="w-3.5 h-3.5" /> GitHub
                </a>
                <a
                  href="https://hinteval.readthedocs.io/en/latest/index.html"
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-2 hover:text-primary transition-colors"
                >
                  <BookOpen className="w-3.5 h-3.5" /> Documentation
                </a>
                <a
                  href="https://arxiv.org/pdf/2502.00857"
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-2 hover:text-primary transition-colors"
                >
                  <FileText className="w-3.5 h-3.5" /> Research Paper
                </a>
              </div>
            </div>
          </footer>
        </ThemeProvider>
      </body>
    </html>
  );
}

function NavLink({ href, icon, label }: { href: string; icon: React.ReactNode; label: string }) {
  return (
    <Link
      href={href}
      className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-accent transition-all duration-200 border border-transparent hover:border-border"
    >
      {icon}
      <span>{label}</span>
    </Link>
  );
}
import { ArrowRight } from "lucide-react";
import { motion } from "motion/react";
import { Header } from "./Header";

export function WelcomeScreen() {
  return (
    <main className="relative min-h-screen overflow-hidden bg-black text-white">
      <Header />

      {/* Ambient geometric background */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-[8%] top-[20%] h-px w-[84%] bg-[#D4AF37]/10" />
        <div className="absolute left-[8%] top-[72%] h-px w-[84%] bg-[#D4AF37]/10" />

        <div className="absolute left-[58%] top-[12%] h-[80vh] w-[80vh] rounded-full border border-[#D4AF37]/10" />
        <div className="absolute left-[63%] top-[19%] h-[66vh] w-[66vh] rounded-full border border-[#D4AF37]/5" />

        <div className="absolute left-[70%] top-[34%] h-2 w-2 rounded-full bg-[#D4AF37]/50" />
        <div className="absolute left-[78%] top-[57%] h-1.5 w-1.5 rounded-full bg-[#D4AF37]/40" />
        <div className="absolute left-[65%] top-[67%] h-1 w-1 rounded-full bg-[#D4AF37]/50" />
      </div>

      <section className="relative z-10 flex min-h-screen items-center px-8 pb-12 pt-28 md:px-12 lg:px-20">
        <div className="grid w-full grid-cols-1 items-center gap-12 lg:grid-cols-[1fr_0.9fr]">
          
          {/* Left: content */}
          <motion.div
            initial={{ opacity: 0, x: -24 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.7, ease: "easeOut" }}
            className="max-w-2xl"
          >
            <p className="mb-5 text-xs font-semibold uppercase tracking-[0.35em] text-[#D4AF37]">
              Welcome · Assistant Ready
            </p>

            <h1 className="text-6xl font-black uppercase leading-[0.85] tracking-[-0.04em] md:text-7xl lg:text-8xl">
              Drishti
              <br />
              <span className="text-[#D4AF37]">AI</span>
            </h1>

            <div className="mt-8 h-px w-24 bg-[#D4AF37]" />

            <p className="mt-7 max-w-md text-base leading-relaxed text-white/60 md:text-lg">
              Your intelligent guide to Drishti 2026.
              <br />
              Ask about events, venues, timings and more.
            </p>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="group mt-10 flex min-h-16 items-center gap-6 border border-[#D4AF37] bg-[#D4AF37] px-8 text-sm font-bold uppercase tracking-[0.2em] text-black transition-colors hover:bg-transparent hover:text-[#D4AF37]"
            >
              Ask a Question

              <ArrowRight
                size={20}
                strokeWidth={2.5}
                className="transition-transform duration-200 group-hover:translate-x-1"
              />
            </motion.button>

            <div className="mt-10 flex flex-wrap gap-x-6 gap-y-2 text-[10px] font-medium uppercase tracking-[0.2em] text-white/30">
              <span>Events</span>
              <span>Venues</span>
              <span>Timings</span>
              <span>History</span>
            </div>
          </motion.div>

          {/* Right: mascot placeholder */}
          <motion.div
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.15, ease: "easeOut" }}
            className="relative flex min-h-[420px] items-center justify-center lg:min-h-[600px]"
          >
            <div className="relative flex aspect-square w-[min(75vw,520px)] items-center justify-center border border-[#D4AF37]/30">
              
              {/* Corner accents */}
              <div className="absolute -left-px -top-px h-8 w-8 border-l-2 border-t-2 border-[#D4AF37]" />
              <div className="absolute -right-px -top-px h-8 w-8 border-r-2 border-t-2 border-[#D4AF37]" />
              <div className="absolute -bottom-px -left-px h-8 w-8 border-b-2 border-l-2 border-[#D4AF37]" />
              <div className="absolute -bottom-px -right-px h-8 w-8 border-b-2 border-r-2 border-[#D4AF37]" />

              <div className="text-center">
                <div className="text-[10px] font-semibold uppercase tracking-[0.35em] text-[#D4AF37]/60">
                  Mascot
                </div>
                <div className="mt-2 text-xs uppercase tracking-[0.2em] text-white/20">
                  Coming Soon
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>
    </main>
  );
}
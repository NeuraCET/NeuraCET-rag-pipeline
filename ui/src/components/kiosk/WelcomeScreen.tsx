import { motion } from "motion/react";
import { GoldButton } from "./GoldButton";
import { KioskScreen } from "./KioskScreen";
import { MascotPlaceholder } from "./MascotPlaceholder";

interface WelcomeScreenProps {
  onStart: () => void;
}

export function WelcomeScreen({ onStart }: WelcomeScreenProps) {
  return (
    <KioskScreen className="items-center">
      <div className="grid w-full grid-cols-1 items-center gap-12 lg:grid-cols-[1fr_0.9fr]">

        {/* Left: content */}
        <motion.div
          initial={{ opacity: 0, x: -24 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.7, ease: "easeOut" }}
          className="max-w-2xl"
        >
          <p className="mb-5 text-xs font-semibold uppercase tracking-[0.35em] text-gold">
            Welcome · Assistant Ready
          </p>

          <h1 className="text-6xl font-black uppercase leading-[0.85] tracking-[-0.04em] md:text-7xl lg:text-8xl">
            Drishti
            <br />
            <span className="gold-text">AI</span>
          </h1>

          <motion.div
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ duration: 0.7, delay: 0.35, ease: "easeOut" }}
            className="gold-surface mt-8 h-px w-24 origin-left"
          />

          <p className="mt-7 max-w-md text-base leading-relaxed text-white/60 md:text-lg">
            Your intelligent guide to Drishti 2026.
            <br />
            Ask about events, venues, timings and more.
          </p>

          <GoldButton label="Ask a Question" onClick={onStart} className="mt-10" />

          <div className="mt-10 flex flex-wrap gap-x-6 gap-y-2 text-[10px] font-medium uppercase tracking-[0.2em] text-white/30">
            {["Events", "Venues", "Timings", "History"].map((tag, index) => (
              <motion.span
                key={tag}
                animate={{ opacity: [0.3, 0.85, 0.3] }}
                transition={{
                  duration: 5,
                  repeat: Infinity,
                  ease: "easeInOut",
                  delay: index * 0.8,
                }}
              >
                {tag}
              </motion.span>
            ))}
          </div>
        </motion.div>

        {/* Right: mascot placeholder */}
        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.15, ease: "easeOut" }}
          className="relative flex min-h-[420px] items-center justify-center lg:min-h-[600px]"
        >
          <motion.div
            animate={{ y: [-8, 8, -8] }}
            transition={{ duration: 9, repeat: Infinity, ease: "easeInOut" }}
          >
            <MascotPlaceholder />
          </motion.div>
        </motion.div>
      </div>
    </KioskScreen>
  );
}

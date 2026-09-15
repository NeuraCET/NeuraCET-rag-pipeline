import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { KioskScreen } from "./KioskScreen";
import { MascotPlaceholder } from "./MascotPlaceholder";

const STATUSES = ["Searching Drishti Knowledge", "Formulating Answer"];

interface ThinkingScreenProps {
  question: string;
}

export function ThinkingScreen({ question }: ThinkingScreenProps) {
  const [statusIndex, setStatusIndex] = useState(0);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setStatusIndex((index) => (index + 1) % STATUSES.length);
    }, 2200);

    return () => window.clearInterval(timer);
  }, []);

  return (
    <KioskScreen className="flex-col items-center justify-center">
      <motion.p
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="max-w-3xl text-center text-lg leading-relaxed text-white/45 md:text-xl"
      >
        “{question}”
      </motion.p>

      <div className="relative mt-12 flex items-center justify-center">
        {/* Rotating geometry */}
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 28, repeat: Infinity, ease: "linear" }}
          className="pointer-events-none absolute aspect-square w-[min(80vw,500px)] border border-gold/25"
        />

        <motion.div
          animate={{ rotate: -360 }}
          transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
          className="pointer-events-none absolute aspect-square w-[min(88vw,560px)] rounded-full border border-dashed border-gold/15"
        />

        <motion.div
          animate={{ opacity: [0.15, 0.45, 0.15], scale: [0.98, 1.03, 0.98] }}
          transition={{ duration: 3.4, repeat: Infinity, ease: "easeInOut" }}
          className="pointer-events-none absolute aspect-square w-[min(94vw,620px)] rounded-full border border-gold/20"
        />

        <div className="relative overflow-hidden">
          <MascotPlaceholder size="w-[min(60vw,360px)]" />

          {/* Scanning line across the mascot frame */}
          <motion.div
            animate={{ y: ["0%", "100%", "0%"] }}
            transition={{ duration: 3.2, repeat: Infinity, ease: "easeInOut" }}
            className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-gold-light to-transparent"
          />
        </div>
      </div>

      <div className="mt-14 flex flex-col items-center">
        <div className="flex gap-2">
          {[0, 1, 2].map((dot) => (
            <motion.div
              key={dot}
              animate={{ opacity: [0.2, 1, 0.2] }}
              transition={{
                duration: 1.4,
                repeat: Infinity,
                delay: dot * 0.22,
                ease: "easeInOut",
              }}
              className="gold-surface h-1.5 w-6"
            />
          ))}
        </div>

        <div className="mt-6 h-6">
          <AnimatePresence mode="wait">
            <motion.p
              key={statusIndex}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.35 }}
              className="gold-text text-xs font-semibold uppercase tracking-[0.35em]"
            >
              {STATUSES[statusIndex]}
            </motion.p>
          </AnimatePresence>
        </div>
      </div>
    </KioskScreen>
  );
}

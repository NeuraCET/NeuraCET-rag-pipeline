import { Home } from "lucide-react";
import { motion } from "motion/react";
import { GoldButton } from "./GoldButton";
import { KioskScreen } from "./KioskScreen";

interface ErrorScreenProps {
  message: string;
  onRetry: () => void;
  onHome: () => void;
}

export function ErrorScreen({ message, onRetry, onHome }: ErrorScreenProps) {
  return (
    <KioskScreen className="flex-col items-center justify-center text-center">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.45, ease: "easeOut" }}
        className="flex max-w-2xl flex-col items-center"
      >
        <p className="gold-text text-[10px] font-semibold uppercase tracking-[0.35em]">
          Unable to Answer
        </p>

        <h2 className="mt-6 text-4xl font-black uppercase leading-[0.9] tracking-[-0.03em] md:text-5xl">
          Something
          <br />
          Went Wrong
        </h2>

        <div className="gold-surface mt-8 h-px w-24" />

        <p className="mt-7 text-base leading-relaxed text-white/50 md:text-lg">
          {message}
        </p>

        <div className="mt-10 flex flex-wrap items-center justify-center gap-6">
          <GoldButton label="Try Again" onClick={onRetry} />

          <button
            type="button"
            onClick={onHome}
            className="flex min-h-14 items-center gap-3 px-4 text-[10px] font-semibold uppercase tracking-[0.3em] text-white/40 transition-colors hover:text-gold"
          >
            <Home size={16} strokeWidth={2.5} />
            Home
          </button>
        </div>
      </motion.div>
    </KioskScreen>
  );
}

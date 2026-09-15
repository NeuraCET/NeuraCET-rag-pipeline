import { Home } from "lucide-react";
import { motion } from "motion/react";
import type { KioskAnswer } from "../../types/kiosk";
import { GoldButton } from "./GoldButton";
import { KioskScreen } from "./KioskScreen";
import { MascotPlaceholder } from "./MascotPlaceholder";

interface AnswerScreenProps {
  result: KioskAnswer;
  onAskAnother: () => void;
  onHome: () => void;
}

export function AnswerScreen({
  result,
  onAskAnother,
  onHome,
}: AnswerScreenProps) {
  return (
    <KioskScreen className="items-center">
      <div className="grid w-full grid-cols-1 items-center gap-12 lg:grid-cols-[1.3fr_0.55fr]">

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          className="flex max-w-4xl flex-col"
        >
          <p className="gold-text text-[10px] font-semibold uppercase tracking-[0.35em]">
            You Asked
          </p>

          <p className="mt-3 text-base leading-relaxed text-white/45 md:text-lg">
            {result.question}
          </p>

          <motion.div
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ duration: 0.7, delay: 0.15, ease: "easeOut" }}
            className="gold-surface mt-7 h-px w-full origin-left opacity-60"
          />

          <motion.div
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55, delay: 0.25, ease: "easeOut" }}
            className="mt-8 max-h-[42vh] overflow-y-auto pr-2"
          >
            <p className="text-2xl font-medium leading-[1.5] tracking-[-0.01em] text-white md:text-3xl lg:text-[2.1rem]">
              {result.answer}
            </p>
          </motion.div>

          <div className="mt-8 flex w-fit items-center gap-4 border-l border-gold/40 pl-4 text-[10px] font-medium uppercase tracking-[0.25em] text-white/30">
            <span>Source</span>
            <span className="text-white/55">{result.source}</span>
          </div>

          <div className="mt-10 flex flex-wrap items-center gap-6">
            <GoldButton label="Ask Another Question" onClick={onAskAnother} />

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

        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.1, ease: "easeOut" }}
          className="relative hidden items-center justify-center lg:flex"
        >
          <MascotPlaceholder size="w-[min(24vw,300px)]" />
        </motion.div>
      </div>
    </KioskScreen>
  );
}

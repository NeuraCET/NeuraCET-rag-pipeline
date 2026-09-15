import { useState } from "react";
import { ChevronLeft } from "lucide-react";
import { motion } from "motion/react";
import { GoldButton } from "./GoldButton";
import { KioskScreen } from "./KioskScreen";
import { MascotPlaceholder } from "./MascotPlaceholder";

interface AskScreenProps {
  onSubmit: (question: string) => void;
  onHome: () => void;
}

export function AskScreen({ onSubmit, onHome }: AskScreenProps) {
  const [question, setQuestion] = useState("");
  const [focused, setFocused] = useState(false);

  const trimmed = question.trim();

  const submit = () => {
    if (trimmed) onSubmit(trimmed);
  };

  return (
    <KioskScreen className="items-center">
      <div className="grid w-full grid-cols-1 items-center gap-12 lg:grid-cols-[1.15fr_0.7fr]">

        <motion.div
          initial={{ opacity: 0, x: -24 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          className="max-w-3xl"
        >
          <motion.button
            type="button"
            onClick={onHome}
            whileHover={{ x: -4 }}
            className="mb-8 flex min-h-12 items-center gap-2 pr-4 text-[10px] font-semibold uppercase tracking-[0.3em] text-white/40 transition-colors hover:text-gold"
          >
            <ChevronLeft size={16} strokeWidth={2.5} />
            Back to Home
          </motion.button>

          <h1 className="text-5xl font-black uppercase leading-[0.9] tracking-[-0.04em] md:text-6xl lg:text-7xl">
            Ask About
            <br />
            <span className="gold-text">Drishti</span>
          </h1>

          <motion.div
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ duration: 0.6, delay: 0.25, ease: "easeOut" }}
            className="gold-surface mt-8 h-px w-24 origin-left"
          />

          <motion.div
            animate={{
              borderColor: focused
                ? "rgba(213,180,92,0.95)"
                : "rgba(213,180,92,0.3)",
              boxShadow: focused
                ? "0 0 38px -18px rgba(247,231,176,0.9)"
                : "0 0 0px 0px rgba(247,231,176,0)",
            }}
            transition={{ duration: 0.35 }}
            className="relative mt-10 border"
          >
            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              onFocus={() => setFocused(true)}
              onBlur={() => setFocused(false)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  submit();
                }
              }}
              rows={3}
              autoFocus
              placeholder="What would you like to know?"
              className="w-full resize-none bg-transparent p-7 text-2xl leading-relaxed text-white outline-none placeholder:text-white/25 md:text-3xl"
            />

            <motion.div
              animate={{ scaleX: trimmed ? 1 : 0 }}
              transition={{ duration: 0.4, ease: "easeOut" }}
              className="gold-surface absolute inset-x-0 bottom-0 h-px origin-left"
            />
          </motion.div>

          <GoldButton
            label="Ask"
            onClick={submit}
            disabled={!trimmed}
            className="mt-10"
          />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.1, ease: "easeOut" }}
          className="relative hidden items-center justify-center lg:flex"
        >
          <MascotPlaceholder size="w-[min(30vw,400px)]" />
        </motion.div>
      </div>
    </KioskScreen>
  );
}

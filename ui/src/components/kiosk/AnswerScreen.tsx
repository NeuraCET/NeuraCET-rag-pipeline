import { Home } from "lucide-react";
import { motion } from "motion/react";
import type { KioskAnswer } from "../../types/kiosk";
import { GoldButton } from "./GoldButton";
import { KioskScreen } from "./KioskScreen";
import Strands from "./Strands";
import ReactMarkdown from "react-markdown";
import { useState, useEffect, useRef, useCallback } from "react";

function useTypewriter(text: string = "", speed: number = 4) {
  const [displayedText, setDisplayedText] = useState("");
  const [prevText, setPrevText] = useState(text);

  if (text !== prevText) {
    setPrevText(text);
    setDisplayedText("");
  }

  useEffect(() => {
    if (!text) return;

    let index = 0;
    // Step 2 chars per tick for smooth, responsive reading speed without 15s artificial lag
    const step = 2;
    const intervalId = setInterval(() => {
      index = Math.min(text.length, index + step);
      setDisplayedText(text.slice(0, index));
      if (index >= text.length) {
        clearInterval(intervalId);
      }
    }, speed);

    return () => clearInterval(intervalId);
  }, [text, speed]);

  const finish = useCallback(() => {
    setDisplayedText(text);
  }, [text]);

  return {
    displayedText,
    isTyping: displayedText.length < text.length,
    finish,
  };
}

interface AnswerScreenProps {
  result: KioskAnswer;
  onAskAnother: () => void;
  onHome: () => void;
  isStreaming?: boolean;
}

export function AnswerScreen({
  result,
  onAskAnother,
  onHome,
  isStreaming = false,
}: AnswerScreenProps) {
  const typewriter = useTypewriter(isStreaming ? "" : result.answer, 4);
  const displayedText = isStreaming ? result.answer : typewriter.displayedText;
  const isTyping = isStreaming || typewriter.isTyping;
  const finish = useCallback(() => {
    if (!isStreaming) {
      typewriter.finish();
    }
  }, [isStreaming, typewriter]);

  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll while typing or streaming
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }, [displayedText]);

  return (
    <KioskScreen className="items-start justify-center pt-24 pb-16">
      <div
        className={`grid w-full items-start gap-10 ${
          result.poster
            ? "grid-cols-1 lg:grid-cols-[1.28fr_0.72fr]"
            : "grid-cols-1 max-w-5xl mx-auto"
        }`}
      >
        <motion.div
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          className="flex w-full flex-col"
        >
          {/* Top header row: Question info + smaller animated Strands overlay */}
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="gold-text text-xs font-bold uppercase tracking-[0.3em]">
                You Asked
              </p>
              <p className="mt-1 text-base font-medium leading-relaxed text-white/70 md:text-lg">
                "{result.question}"
              </p>
            </div>

            {/* Smaller, non-obstructive overlay badge with glowing Strands animation */}
            <div className="flex items-center gap-3 rounded-xl border border-gold/30 bg-black/60 px-3.5 py-2 backdrop-blur-md shadow-[0_0_25px_rgba(212,175,55,0.12)]">
              <div className="relative h-12 w-12 overflow-hidden rounded-lg border border-gold/40">
                <Strands
                  colors={["#f0c763", "#d59828", "#ffd700"]}
                  count={3}
                  speed={0.4}
                  amplitude={0.85}
                  waviness={1.05}
                  thickness={0.5}
                  glow={2.6}
                  taper={2.8}
                  spread={1.0}
                  intensity={0.65}
                  saturation={1.6}
                  opacity={1.0}
                  scale={1.35}
                  glass={false}
                  hueShift={0}
                />
              </div>

              <div className="flex flex-col">
                <div className="flex items-center gap-2">
                  {isStreaming ? (
                    <>
                      <span className="h-2 w-2 rounded-full bg-amber-400 animate-ping" />
                      <span className="gold-text text-[11px] font-bold uppercase tracking-[0.25em]">
                        Live AI Generating
                      </span>
                    </>
                  ) : (
                    <>
                      <span className="h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_6px_#34d399]" />
                      <span className="text-[11px] font-bold uppercase tracking-[0.25em] text-emerald-400">
                        Official Drishti AI
                      </span>
                    </>
                  )}
                </div>
                <span className="mt-0.5 text-[10px] uppercase tracking-[0.14em] text-white/50">
                  {isStreaming
                    ? "Formulating live response..."
                    : result.source || "Official Knowledge Base"}
                </span>
              </div>
            </div>
          </div>

          <motion.div
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ duration: 0.6, delay: 0.1, ease: "easeOut" }}
            className="gold-surface mt-5 h-px w-full origin-left opacity-70"
          />

          {/* Main Answer Window: enlarged, luxurious glass container */}
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2, ease: "easeOut" }}
            onClick={finish}
            title={isTyping ? "Click to show full answer immediately" : undefined}
            className="mt-6 max-h-[66vh] w-full cursor-pointer overflow-y-auto rounded-2xl border border-gold/25 bg-black/50 p-6 md:p-8 backdrop-blur-md shadow-[0_0_40px_rgba(212,175,55,0.06)] [scrollbar-width:thin] [scrollbar-color:rgba(213,180,92,0.4)_transparent]"
          >
            {/* If streaming hasn't produced tokens yet, show shimmer state */}
            {!displayedText && isStreaming ? (
              <div className="flex flex-col gap-4 py-8">
                <div className="flex items-center gap-3">
                  <span className="h-3 w-3 rounded-full bg-gold animate-ping" />
                  <span className="text-base font-semibold tracking-wide text-gold md:text-lg">
                    Searching official Drishti festival records & formulating answer...
                  </span>
                </div>
                <div className="space-y-3 pt-3">
                  <div className="h-4 w-3/4 animate-pulse rounded bg-white/10" />
                  <div className="h-4 w-5/6 animate-pulse rounded bg-white/10" />
                  <div className="h-4 w-2/3 animate-pulse rounded bg-white/10" />
                </div>
              </div>
            ) : (
              <div className="w-full font-sans leading-relaxed text-white">
                <ReactMarkdown
                  components={{
                    h1: ({ children }) => (
                      <h1 className="mb-3 mt-4 text-2xl font-bold text-amber-400 md:text-3xl">
                        {children}
                      </h1>
                    ),
                    h2: ({ children }) => (
                      <h2 className="mb-2 mt-4 text-xl font-bold text-amber-300 md:text-2xl">
                        {children}
                      </h2>
                    ),
                    h3: ({ children }) => (
                      <h3 className="mb-2 mt-3 text-lg font-semibold text-amber-200 md:text-xl">
                        {children}
                      </h3>
                    ),
                    p: ({ children }) => (
                      <p className="mb-3.5 text-base leading-relaxed text-gray-100 md:text-lg">
                        {children}
                      </p>
                    ),
                    ul: ({ children }) => (
                      <ul className="mb-4 list-inside list-disc space-y-2 text-base leading-relaxed text-gray-100 md:text-lg">
                        {children}
                      </ul>
                    ),
                    ol: ({ children }) => (
                      <ol className="mb-4 list-inside list-decimal space-y-2 text-base leading-relaxed text-gray-100 md:text-lg">
                        {children}
                      </ol>
                    ),
                    li: ({ children }) => (
                      <li className="text-gray-100 leading-relaxed">{children}</li>
                    ),
                    strong: ({ children }) => (
                      <strong className="font-bold text-white">{children}</strong>
                    ),
                  }}
                >
                  {displayedText}
                </ReactMarkdown>

                {/* Blinking cursor while typing/streaming */}
                {isTyping && (
                  <span className="ml-1 inline-block h-5 w-2 animate-pulse align-middle bg-amber-400 shadow-[0_0_8px_#fbbf24]" />
                )}

                {/* Invisible anchor for auto-scrolling */}
                <div ref={bottomRef} />
              </div>
            )}
          </motion.div>

          {/* Action buttons */}
          <div className="mt-8 flex flex-wrap items-center gap-6">
            <GoldButton label="Ask Another Question" onClick={onAskAnother} />

            <button
              type="button"
              onClick={onHome}
              className="flex min-h-14 items-center gap-3 px-5 text-xs font-bold uppercase tracking-[0.3em] text-white/50 transition-colors hover:text-gold"
            >
              <Home size={18} strokeWidth={2.5} />
              Home
            </button>
          </div>
        </motion.div>

        {/* Right column: ONLY shown if official 2026 event poster exists! (No mascot box) */}
        {result.poster && (
          <motion.div
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.15, ease: "easeOut" }}
            className="relative hidden items-center justify-center lg:flex"
          >
            <div className="group relative overflow-hidden rounded-xl border border-gold/40 bg-black/50 p-2.5 shadow-[0_0_35px_-10px_rgba(213,180,92,0.35)] backdrop-blur-md">
              <img
                src={result.poster}
                alt="Official Event Poster"
                className="max-h-[64vh] w-auto rounded-lg object-contain transition-transform duration-500 group-hover:scale-[1.02]"
              />
              <div className="mt-2.5 text-center">
                <span className="gold-text text-[10px] font-bold uppercase tracking-[0.25em]">
                  Official Event Poster · Drishti 2026
                </span>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </KioskScreen>
  );
}

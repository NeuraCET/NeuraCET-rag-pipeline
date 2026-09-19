import { Home } from "lucide-react";
import { motion } from "motion/react";
import type { KioskAnswer } from "../../types/kiosk";
import { GoldButton } from "./GoldButton";
import { KioskScreen } from "./KioskScreen";
import { MascotPlaceholder } from "./MascotPlaceholder";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
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
  // Track if this answer was delivered via live token streaming
  const hasStreamedRef = useRef(isStreaming);
  if (isStreaming) {
    hasStreamedRef.current = true;
  }

  const typewriter = useTypewriter(!hasStreamedRef.current ? result.answer : "", 4);
  const displayedText = hasStreamedRef.current ? result.answer : typewriter.displayedText;
  const isTyping = isStreaming || (!hasStreamedRef.current && typewriter.isTyping);
  const finish = useCallback(() => {
    if (!hasStreamedRef.current) {
      typewriter.finish();
    }
  }, [typewriter]);

  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll while typing or streaming
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }, [displayedText]);

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
            onClick={finish}
            title={isTyping ? "Click to show full answer immediately" : undefined}
            className="mt-6 max-h-[56vh] cursor-pointer overflow-y-auto pr-3 [scrollbar-width:thin] [scrollbar-color:rgba(213,180,92,0.3)_transparent]"
          >
            <div className="w-full max-w-3xl font-sans leading-relaxed text-white">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  h1: ({ children }) => (
                    <h1 className="mb-2 mt-4 text-2xl font-bold text-amber-400">{children}</h1>
                  ),
                  h2: ({ children }) => (
                    <h2 className="mb-2 mt-4 text-xl font-semibold text-amber-300">{children}</h2>
                  ),
                  h3: ({ children }) => (
                    <h3 className="mb-1 mt-3 text-lg font-medium text-amber-200">{children}</h3>
                  ),
                  p: ({ children }) => (
                    <p className="mb-3 text-base leading-normal text-gray-200">{children}</p>
                  ),
                  ul: ({ children }) => (
                    <ul className="mb-3 list-inside list-disc space-y-1 text-gray-200">{children}</ul>
                  ),
                  ol: ({ children }) => (
                    <ol className="mb-3 list-inside list-decimal space-y-1 text-gray-200">{children}</ol>
                  ),
                  li: ({ children }) => <li className="text-gray-200">{children}</li>,
                  strong: ({ children }) => (
                    <strong className="font-semibold text-white">{children}</strong>
                  ),
                  table: ({ children }) => (
                    <div className="my-4 w-full overflow-x-auto rounded-lg border border-[#d5b45c]/30 bg-black/40 p-1 shadow-[0_0_20px_-5px_rgba(213,180,92,0.15)] [scrollbar-width:thin] [scrollbar-color:rgba(213,180,92,0.3)_transparent]">
                      <table className="w-full min-w-full table-auto border-collapse text-left text-sm text-gray-200">
                        {children}
                      </table>
                    </div>
                  ),
                  thead: ({ children }) => (
                    <thead className="border-b border-[#d5b45c]/40 bg-[#d5b45c]/10 text-xs font-semibold uppercase tracking-wider text-amber-300">
                      {children}
                    </thead>
                  ),
                  tbody: ({ children }) => (
                    <tbody className="divide-y divide-[#d5b45c]/15">{children}</tbody>
                  ),
                  tr: ({ children }) => (
                    <tr className="transition-colors hover:bg-white/[0.04]">{children}</tr>
                  ),
                  th: ({ children }) => (
                    <th className="px-3.5 py-2.5 font-semibold text-amber-300">{children}</th>
                  ),
                  td: ({ children }) => (
                    <td className="px-3.5 py-2.5 align-top text-gray-200">{children}</td>
                  ),
                }}
              >
                {displayedText}
              </ReactMarkdown>

              {/* Blinking cursor while typing */}
              {isTyping && (
                <span className="ml-1 inline-block h-4 w-2 animate-pulse align-middle bg-amber-400" />
              )}

              {/* Invisible anchor for auto-scrolling */}
              <div ref={bottomRef} />
            </div>
          </motion.div>

          <div className="mt-8 flex flex-wrap items-center gap-6">
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

        {/* Right column: official event poster or fallback mascot */}
        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.1, ease: "easeOut" }}
          className="relative hidden items-center justify-center lg:flex"
        >
          {result.poster ? (
            <div className="group relative overflow-hidden border border-gold/40 bg-black/40 p-2 shadow-[0_0_30px_-10px_rgba(213,180,92,0.3)]">
              <img
                src={result.poster}
                alt="Official Event Poster"
                className="max-h-[54vh] w-auto rounded object-contain transition-transform duration-500 group-hover:scale-[1.02]"
              />
              <div className="mt-2 text-center">
                <span className="gold-text text-[9px] font-semibold uppercase tracking-[0.25em]">
                  Official Event Poster
                </span>
              </div>
            </div>
          ) : (
            <MascotPlaceholder size="w-[min(24vw,300px)]" />
          )}
        </motion.div>
      </div>
    </KioskScreen>
  );
}

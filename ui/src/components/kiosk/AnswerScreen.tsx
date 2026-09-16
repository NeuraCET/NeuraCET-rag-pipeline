import { Home } from "lucide-react";
import { motion } from "motion/react";
import type { KioskAnswer } from "../../types/kiosk";
import { GoldButton } from "./GoldButton";
import { KioskScreen } from "./KioskScreen";
import { MascotPlaceholder } from "./MascotPlaceholder";
import ReactMarkdown from 'react-markdown';
import { useState, useEffect, useRef } from 'react';

function useTypewriter(text: string = '', speed: number = 15) {
  const [displayedText, setDisplayedText] = useState('');
  const [prevText, setPrevText] = useState(text);

  if (text !== prevText) {
    setPrevText(text);
    setDisplayedText('');
  }

  useEffect(() => {
    if (!text) return;

    let index = 0;
    const intervalId = setInterval(() => {
      index++;
      setDisplayedText(text.slice(0, index));
      if (index >= text.length) {
        clearInterval(intervalId);
      }
    }, speed);

    return () => clearInterval(intervalId);
  }, [text, speed]);

  return displayedText;
}

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
  
  const displayedText = useTypewriter(result.answer, 12);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll whenever displayedText changes
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'auto' });
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
            className="mt-8 max-h-[42vh] overflow-y-auto pr-2"
          >
            <div className="text-white font-sans leading-relaxed max-w-2xl">
              <ReactMarkdown
                components={{
                  h1: ({ children }) => <h1 className="text-2xl font-bold text-amber-400 mt-4 mb-2">{children}</h1>,
                  h2: ({ children }) => <h2 className="text-xl font-semibold text-amber-300 mt-4 mb-2">{children}</h2>,
                  h3: ({ children }) => <h3 className="text-lg font-medium text-amber-200 mt-3 mb-1">{children}</h3>,
                  p: ({ children }) => <p className="mb-3 text-base text-gray-200 leading-normal">{children}</p>,
                  ul: ({ children }) => <ul className="list-disc list-inside mb-3 space-y-1 text-gray-200">{children}</ul>,
                  ol: ({ children }) => <ol className="list-decimal list-inside mb-3 space-y-1 text-gray-200">{children}</ol>,
                  li: ({ children }) => <li className="text-gray-200">{children}</li>,
                  strong: ({ children }) => <strong className="font-semibold text-white">{children}</strong>,
                }}
              >
                {displayedText}
              </ReactMarkdown>
              
              {/* Blinking cursor while typing */}
              {displayedText.length < result.answer.length && (
                <span className="inline-block w-2 h-4 bg-amber-400 animate-pulse ml-1 align-middle" />
              )}
              
              {/* Invisible anchor for auto-scrolling */}
              <div ref={bottomRef} />
            </div>
          </motion.div>

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

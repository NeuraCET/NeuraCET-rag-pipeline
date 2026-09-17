import { useCallback, useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { AnswerScreen } from "../components/kiosk/AnswerScreen";
import { AskScreen } from "../components/kiosk/AskScreen";
import { ErrorScreen } from "../components/kiosk/ErrorScreen";
import { Header } from "../components/kiosk/Header";
import { KioskBackground } from "../components/kiosk/KioskBackground";
import { ThinkingScreen } from "../components/kiosk/ThinkingScreen";
import { WelcomeScreen } from "../components/kiosk/WelcomeScreen";
import { streamQuestion } from "../lib/assistant";
import type { KioskAnswer, KioskState } from "../types/kiosk";

export function Kiosk() {
  const [state, setState] = useState<KioskState>("welcome");
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<KioskAnswer | null>(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [isKioskLocked, setIsKioskLocked] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [noticeMessage, setNoticeMessage] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const requestKioskFullscreen = useCallback(async () => {
    try {
      if (!document.fullscreenElement) {
        await document.documentElement.requestFullscreen();
      }
      const nav = navigator as unknown as {
        keyboard?: {
          lock?: (keys?: string[]) => Promise<void>;
          unlock?: () => void;
        };
      };
      if (nav.keyboard?.lock) {
        await nav.keyboard.lock(["Escape"]);
      }
    } catch (err) {
      console.warn("Fullscreen or keyboard lock request failed:", err);
    }
  }, []);

  const unlockKiosk = useCallback(async () => {
    setIsKioskLocked(false);
    const nav = navigator as unknown as {
      keyboard?: {
        lock?: (keys?: string[]) => Promise<void>;
        unlock?: () => void;
      };
    };
    if (nav.keyboard?.unlock) {
      nav.keyboard.unlock();
    }
    if (document.fullscreenElement) {
      try {
        await document.exitFullscreen();
      } catch (err) {
        console.warn("Exit fullscreen failed:", err);
      }
    }
    setNoticeMessage("Kiosk mode unlocked");
    setTimeout(() => setNoticeMessage(null), 3500);
  }, []);

  const handleStart = useCallback(async () => {
    setIsKioskLocked(true);
    await requestKioskFullscreen();
    setState("asking");
    setNoticeMessage("Kiosk Fullscreen Active · Press Ctrl+Shift+F to exit");
    setTimeout(() => setNoticeMessage(null), 4000);
  }, [requestKioskFullscreen]);

  // Keyboard shortcut listener for Ctrl+Shift+F and Escape prevention
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const isCtrlShiftF =
        (e.ctrlKey || e.metaKey) &&
        e.shiftKey &&
        (e.key === "F" || e.key === "f" || e.code === "KeyF");

      if (isCtrlShiftF) {
        e.preventDefault();
        e.stopPropagation();
        unlockKiosk();
        return;
      }

      if (isKioskLocked && e.key === "Escape") {
        e.preventDefault();
        e.stopPropagation();
      }
    };

    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    window.addEventListener("keydown", handleKeyDown, { capture: true });
    document.addEventListener("fullscreenchange", handleFullscreenChange);

    return () => {
      window.removeEventListener("keydown", handleKeyDown, { capture: true });
      document.removeEventListener("fullscreenchange", handleFullscreenChange);
    };
  }, [isKioskLocked, unlockKiosk]);

  const run = useCallback(async (asked: string) => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const ac = new AbortController();
    abortControllerRef.current = ac;

    setQuestion(asked);
    setResult({
      question: asked,
      answer: "",
      source: "Official Drishti Knowledge Base",
      poster: null,
    });
    // Immediately open the answer window instead of waiting on the mascot screen!
    setState("answering");
    setIsStreaming(true);

    let currentMeta = {
      poster: null as string | null,
      source: "Official Drishti Knowledge Base",
    };
    let fullAnswer = "";

    try {
      await streamQuestion(
        asked,
        {
          onMeta: (meta) => {
            currentMeta = meta;
            setResult((prev) =>
              prev
                ? {
                    ...prev,
                    poster: meta.poster,
                    source: meta.source,
                  }
                : null,
            );
          },
          onToken: (token) => {
            fullAnswer += token;
            setResult({
              question: asked,
              answer: fullAnswer,
              source: currentMeta.source,
              poster: currentMeta.poster,
            });
          },
          onDone: () => {
            setIsStreaming(false);
          },
        },
        ac.signal,
      );
    } catch {
      if (ac.signal.aborted) return;
      setErrorMessage(
        "The assistant could not reach the Drishti knowledge base. Please try again.",
      );
      setState("error");
      setIsStreaming(false);
    }
  }, []);

  const goHome = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsStreaming(false);
    setQuestion("");
    setResult(null);
    setState("welcome");
  }, []);

  const askAnother = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsStreaming(false);
    setState("asking");
  }, []);

  return (
    <main className="relative min-h-screen overflow-hidden bg-black text-white">
      <Header />
      <KioskBackground />

      <AnimatePresence mode="wait">
        <motion.div
          key={state}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3, ease: "easeInOut" }}
        >
          {state === "welcome" && (
            <WelcomeScreen onStart={handleStart} />
          )}

          {state === "asking" && (
            <AskScreen onSubmit={run} onHome={goHome} />
          )}

          {state === "thinking" && <ThinkingScreen question={question} />}

          {state === "answering" && result && (
            <AnswerScreen
              result={result}
              isStreaming={isStreaming}
              onAskAnother={askAnother}
              onHome={goHome}
            />
          )}

          {state === "error" && (
            <ErrorScreen
              message={errorMessage}
              onRetry={() => setState("asking")}
              onHome={goHome}
            />
          )}
        </motion.div>
      </AnimatePresence>

      {/* Kiosk status toast notification */}
      <AnimatePresence>
        {noticeMessage && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="pointer-events-none fixed top-24 left-1/2 z-50 -translate-x-1/2 rounded-full border border-gold/40 bg-black/90 px-6 py-2.5 text-xs font-semibold tracking-wider text-white shadow-[0_0_30px_rgba(212,175,55,0.25)] backdrop-blur-md md:text-sm"
          >
            <span className="gold-text mr-2">✦</span>
            {noticeMessage}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Kiosk locked recovery overlay: if user exits fullscreen while locked */}
      {isKioskLocked && !isFullscreen && (
        <div
          onClick={requestKioskFullscreen}
          className="fixed inset-0 z-50 flex cursor-pointer flex-col items-center justify-center bg-black/90 p-8 text-center backdrop-blur-md"
        >
          <div className="max-w-md rounded-2xl border border-gold/40 bg-zinc-950/95 p-8 shadow-[0_0_50px_rgba(212,175,55,0.2)]">
            <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full border border-gold/40 bg-gold/10 text-2xl text-gold">
              🔒
            </div>
            <h3 className="text-xl font-bold uppercase tracking-wider text-white">
              Kiosk Fullscreen Locked
            </h3>
            <p className="mt-3 text-sm text-white/70">
              Fullscreen is enforced for kiosk mode. Click anywhere to return to full screen.
            </p>
          </div>
        </div>
      )}

      {/* Bottom info bar */}
      <footer className="pointer-events-none fixed inset-x-0 bottom-0 z-30 flex items-center justify-between border-t border-white/10 bg-black/40 px-8 py-3 backdrop-blur-md md:px-12 lg:px-16">
        <div className="hidden sm:flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-white/60">
          <span className="text-gold font-bold">CET</span>
          <span>·</span>
          <span>College of Engineering Trivandrum</span>
        </div>

        <div className="flex items-center gap-3">
          {isKioskLocked && (
            <span className="hidden md:inline-flex items-center gap-1.5 rounded-full border border-gold/30 bg-black/60 px-3 py-1 text-[11px] font-mono tracking-wider text-gold/90">
              <span>🔒 KIOSK LOCKED</span>
              <span className="text-white/40">·</span>
              <span className="text-white/60">Ctrl+Shift+F to exit</span>
            </span>
          )}

          <div className="flex items-center gap-3 rounded-full border border-gold/30 bg-black/70 px-4 py-1.5 shadow-[0_0_20px_rgba(212,175,55,0.15)]">
            <span className="h-2.5 w-2.5 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_#34d399]" />
            <span className="text-xs font-bold uppercase tracking-[0.2em] text-white/95 md:text-sm">
              Drishti 2026 <span className="text-gold">·</span> AI Assistant Kiosk
            </span>
          </div>
        </div>
      </footer>
    </main>
  );
}

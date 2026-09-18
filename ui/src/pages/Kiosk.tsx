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
  const [isFullscreen, setIsFullscreen] = useState(
    typeof document !== "undefined" ? !!document.fullscreenElement : false
  );
  const abortControllerRef = useRef<AbortController | null>(null);

  const enterFullscreen = useCallback(async () => {
    try {
      if (!document.fullscreenElement && document.documentElement.requestFullscreen) {
        await document.documentElement.requestFullscreen();
      }
    } catch {
      // Ignored if user dismissed or cancelled
    }
  }, []);

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    setIsFullscreen(!!document.fullscreenElement);
    document.addEventListener("fullscreenchange", handleFullscreenChange);
    return () => {
      document.removeEventListener("fullscreenchange", handleFullscreenChange);
    };
  }, []);

  const run = useCallback(async (asked: string) => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const ac = new AbortController();
    abortControllerRef.current = ac;

    setQuestion(asked);
    setResult(null);
    setState("thinking");
    setIsStreaming(true);

    let currentMeta = {
      poster: null as string | null,
      source: "Official Drishti Knowledge Base",
    };
    let fullAnswer = "";
    let hasSwitched = false;

    try {
      await streamQuestion(
        asked,
        {
          onMeta: (meta) => {
            currentMeta = meta;
          },
          onToken: (token) => {
            fullAnswer += token;
            if (!hasSwitched) {
              hasSwitched = true;
              setResult({
                question: asked,
                answer: fullAnswer,
                source: currentMeta.source,
                poster: currentMeta.poster,
              });
              // Prompt analysis complete & first token arrived: switch immediately to AnswerScreen!
              setState("answering");
            } else {
              setResult({
                question: asked,
                answer: fullAnswer,
                source: currentMeta.source,
                poster: currentMeta.poster,
              });
            }
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
            <WelcomeScreen
              onStart={() => {
                enterFullscreen();
                setState("asking");
              }}
            />
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

      {/* Mandatory full screen overlay: kiosk requires full screen to operate */}
      {!isFullscreen && (
        <div
          onClick={enterFullscreen}
          className="fixed inset-0 z-50 flex cursor-pointer flex-col items-center justify-center bg-black/90 p-6 text-center backdrop-blur-md select-none"
        >
          <div className="max-w-md rounded-2xl border border-gold/40 bg-zinc-950/95 p-8 shadow-[0_0_50px_rgba(212,175,55,0.2)] transition-transform active:scale-95">
            <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full border border-gold/40 bg-gold/10 text-2xl text-gold">
              ⛶
            </div>
            <h2 className="text-xl font-bold uppercase tracking-wider text-white">
              Full Screen Required
            </h2>
            <p className="mt-3 text-sm text-white/70">
              Drishti 2026 AI Kiosk operates exclusively in full screen mode. Click anywhere to enter full screen.
            </p>
            <button
              onClick={enterFullscreen}
              className="gold-surface mt-6 inline-flex items-center gap-2 rounded-xl px-6 py-2.5 text-xs font-bold uppercase tracking-widest text-black shadow-lg"
            >
              <span>Enter Full Screen</span>
              <span>→</span>
            </button>
          </div>
        </div>
      )}
    </main>
  );
}

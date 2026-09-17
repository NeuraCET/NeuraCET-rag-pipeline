import { useCallback, useRef, useState } from "react";
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
  const abortControllerRef = useRef<AbortController | null>(null);

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
            <WelcomeScreen onStart={() => setState("asking")} />
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
    </main>
  );
}

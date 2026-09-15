import { useCallback, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { AnswerScreen } from "../components/kiosk/AnswerScreen";
import { AskScreen } from "../components/kiosk/AskScreen";
import { ErrorScreen } from "../components/kiosk/ErrorScreen";
import { Header } from "../components/kiosk/Header";
import { KioskBackground } from "../components/kiosk/KioskBackground";
import { ThinkingScreen } from "../components/kiosk/ThinkingScreen";
import { WelcomeScreen } from "../components/kiosk/WelcomeScreen";
import { placeholderAssistant } from "../lib/assistant";
import type { AskQuestion, KioskAnswer, KioskState } from "../types/kiosk";

interface KioskProps {
  /** Swap in the real retrieval backend without touching the screens. */
  askQuestion?: AskQuestion;
}

export function Kiosk({ askQuestion = placeholderAssistant }: KioskProps) {
  const [state, setState] = useState<KioskState>("welcome");
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<KioskAnswer | null>(null);
  const [errorMessage, setErrorMessage] = useState("");

  const run = useCallback(
    async (asked: string) => {
      setQuestion(asked);
      setState("thinking");

      try {
        const answer = await askQuestion(asked);
        setResult(answer);
        setState("answering");
      } catch {
        setErrorMessage(
          "The assistant could not reach the Drishti knowledge base. Please try again.",
        );
        setState("error");
      }
    },
    [askQuestion],
  );

  const goHome = useCallback(() => {
    setQuestion("");
    setResult(null);
    setState("welcome");
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
              onAskAnother={() => setState("asking")}
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

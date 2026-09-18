import type { AskQuestion, KioskAnswer } from "../types/kiosk";

export const placeholderAssistant: AskQuestion = async (
  question: string
): Promise<KioskAnswer> => {
  
  // 1. Send the user's question to your Python FastAPI server
  const endpoint = import.meta.env.VITE_API_URL 
    ? `${import.meta.env.VITE_API_URL}/api/ask` 
    : "/api/ask";

  let response: Response;
  try {
    response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question }),
    });
    // If proxy returned 502/503/504 Bad Gateway, try directly contacting backend
    if (!response.ok && (response.status === 502 || response.status === 503 || response.status === 504) && !endpoint.includes(":8000")) {
      response = await fetch("http://127.0.0.1:8000/api/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
      });
    }
  } catch {
    // Fallback directly to 127.0.0.1:8000 if network failed
    response = await fetch("http://127.0.0.1:8000/api/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question }),
    });
  }

  // 2. If the Python server is off or crashes, throw an error to trigger the ErrorScreen
  if (!response.ok) {
    throw new Error("Failed to connect to backend");
  }

  // 3. Get the JSON response from Qwen/Python
  const data = await response.json();

  // 4. Return it in the format the UI expects
  return {
    question: question,
    answer: data.answer,
    source: data.source || "Official Drishti Event Data",
    poster: data.poster || null,
  };
};

export interface StreamQuestionCallbacks {
  onMeta?: (meta: { poster: string | null; source: string }) => void;
  onToken?: (token: string) => void;
  onDone?: () => void;
}

export async function streamQuestion(
  question: string,
  callbacks: StreamQuestionCallbacks,
  signal?: AbortSignal
): Promise<void> {
  const endpoint = import.meta.env.VITE_API_URL
    ? `${import.meta.env.VITE_API_URL}/api/ask-stream`
    : "/api/ask-stream";

  let response: Response;
  try {
    response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question }),
      signal,
    });
    // If proxy returned 502/503/504 Bad Gateway, try directly contacting backend
    if (!response.ok && (response.status === 502 || response.status === 503 || response.status === 504) && !endpoint.includes(":8000")) {
      response = await fetch("http://127.0.0.1:8000/api/ask-stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
        signal,
      });
    }
  } catch (err: unknown) {
    if (signal?.aborted) return;
    // Fallback directly to 127.0.0.1:8000 if fetch rejected
    response = await fetch("http://127.0.0.1:8000/api/ask-stream", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question }),
      signal,
    });
  }

  if (!response.ok || !response.body) {
    throw new Error(`Failed to connect to backend (status ${response.status})`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) continue;
        try {
          const event = JSON.parse(trimmed);
          if (event.type === "meta") {
            callbacks.onMeta?.({
              poster: event.poster || null,
              source: event.source || "Official Drishti Knowledge Base",
            });
          } else if (event.type === "token") {
            callbacks.onToken?.(event.content);
          } else if (event.type === "done") {
            callbacks.onDone?.();
          }
        } catch {
          // Ignore partial or unparseable lines
        }
      }
    }
  } finally {
    reader.releaseLock();
    callbacks.onDone?.();
  }
}

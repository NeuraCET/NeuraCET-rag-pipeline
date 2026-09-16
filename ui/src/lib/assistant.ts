import type { AskQuestion, KioskAnswer } from "../types/kiosk";

export const placeholderAssistant: AskQuestion = async (
  question: string
): Promise<KioskAnswer> => {
  
  // 1. Send the user's question to your Python FastAPI server
  const response = await fetch("http://localhost:8000/api/ask", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question }),
  });

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
    source: data.source || "Official Drishti Event Data"
    // Add any other fields Ashik's UI expects here (like 'sources' or 'timeTakes')
  };
};

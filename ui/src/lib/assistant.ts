import type { AskQuestion } from "../types/kiosk";

/**
 * Placeholder until the retrieval backend is wired in: it holds the flow
 * together without inventing answers. Pass a real AskQuestion into <Kiosk />
 * to replace it; no screen has to change.
 */
export const placeholderAssistant: AskQuestion = async (question) => {
  await new Promise((resolve) => setTimeout(resolve, 2600));

  return {
    question,
    answer:
      "The Drishti knowledge base is not connected to this kiosk yet. Once it is, the answer to this question appears here.",
    source: "Backend not connected",
  };
};

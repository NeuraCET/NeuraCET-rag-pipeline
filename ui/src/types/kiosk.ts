export type KioskState =
  | "welcome"
  | "asking"
  | "thinking"
  | "answering"
  | "error";

export interface KioskAnswer {
  question: string;
  answer: string;
  source: string;
  poster?: string | null;
}

export type AskQuestion = (question: string) => Promise<KioskAnswer>;

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
}

export type AskQuestion = (question: string) => Promise<KioskAnswer>;

import type { ReactNode } from "react";

interface KioskScreenProps {
  children: ReactNode;
  className?: string;
}

/** Shared fullscreen frame: content sits under the fixed header. */
export function KioskScreen({ children, className = "" }: KioskScreenProps) {
  return (
    <section
      className={`relative z-10 flex min-h-screen px-8 pb-12 pt-28 md:px-12 lg:px-20 ${className}`}
    >
      {children}
    </section>
  );
}

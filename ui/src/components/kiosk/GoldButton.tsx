import { ArrowRight } from "lucide-react";
import { motion } from "motion/react";

interface GoldButtonProps {
  label: string;
  onClick: () => void;
  disabled?: boolean;
  className?: string;
}

export function GoldButton({
  label,
  onClick,
  disabled = false,
  className = "",
}: GoldButtonProps) {
  return (
    <motion.button
      type="button"
      onClick={onClick}
      disabled={disabled}
      whileHover={disabled ? undefined : { scale: 1.02 }}
      whileTap={disabled ? undefined : { scale: 0.97 }}
      transition={{ type: "spring", stiffness: 340, damping: 22 }}
      className={`group relative flex min-h-16 items-center gap-6 overflow-hidden border px-8 text-sm font-bold uppercase tracking-[0.2em] ${
        disabled
          ? "cursor-not-allowed border-gold/20 bg-transparent text-gold/25"
          : "gold-surface border-gold/70 text-black shadow-[0_0_28px_-14px_rgba(213,180,92,0.9)]"
      } ${className}`}
    >
      {!disabled && <span className="gold-glint" />}

      <span className="relative">{label}</span>

      <motion.span
        aria-hidden
        animate={disabled ? undefined : { x: [0, 5, 0] }}
        transition={{ duration: 2.2, repeat: Infinity, ease: "easeInOut" }}
        className="relative"
      >
        <ArrowRight size={20} strokeWidth={2.5} />
      </motion.span>
    </motion.button>
  );
}

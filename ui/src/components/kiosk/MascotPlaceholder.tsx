import { motion } from "motion/react";

interface MascotPlaceholderProps {
  size?: string;
  className?: string;
}

export function MascotPlaceholder({
  size = "w-[min(75vw,520px)]",
  className = "",
}: MascotPlaceholderProps) {
  return (
    <div
      className={`relative flex aspect-square ${size} items-center justify-center border border-gold/30 ${className}`}
    >
      {/* Corner accents, breathing in sequence */}
      {[
        "-left-px -top-px border-l-2 border-t-2",
        "-right-px -top-px border-r-2 border-t-2",
        "-bottom-px -left-px border-b-2 border-l-2",
        "-bottom-px -right-px border-b-2 border-r-2",
      ].map((corner, index) => (
        <motion.div
          key={corner}
          animate={{ opacity: [0.55, 1, 0.55] }}
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: "easeInOut",
            delay: index * 0.5,
          }}
          className={`absolute h-8 w-8 border-gold ${corner}`}
        />
      ))}

      <motion.div
        animate={{ y: [-4, 4, -4] }}
        transition={{ duration: 7, repeat: Infinity, ease: "easeInOut" }}
        className="text-center"
      >
        <div className="gold-text text-[10px] font-semibold uppercase tracking-[0.35em]">
          Mascot
        </div>
        <div className="mt-2 text-xs uppercase tracking-[0.2em] text-white/20">
          Coming Soon
        </div>
      </motion.div>
    </div>
  );
}

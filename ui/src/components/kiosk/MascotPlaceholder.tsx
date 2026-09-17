import { motion } from "motion/react";
import GhostCursor from "./GhostCursor";
import Strands from "./Strands";

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
      className={`relative flex aspect-square ${size} items-center justify-center overflow-hidden rounded-2xl border border-gold/30 bg-black/40 shadow-[0_0_50px_rgba(212,175,55,0.08)] ${className}`}
    >
      {/* Corner accents */}
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
          className={`pointer-events-none absolute h-7 w-7 border-gold/70 ${corner}`}
        />
      ))}

      {/* Strands contained seamlessly within the mascot box without overflow */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden rounded-2xl">
        <Strands
          colors={["#f0c763", "#d59828", "#ffd700"]}
          count={3}
          speed={0.4}
          amplitude={0.85}
          waviness={1.05}
          thickness={0.5}
          glow={2.6}
          taper={2.8}
          spread={1.0}
          intensity={0.65}
          saturation={1.6}
          opacity={1.0}
          scale={1.35}
          glass={false}
          hueShift={0}
        />
      </div>

      <GhostCursor
        color="#d4af37"
        brightness={1.1}
        edgeIntensity={0}
        trailLength={25}
        inertia={0.3}
        grainIntensity={0.03}
        bloomStrength={0.12}
        bloomRadius={0.8}
        bloomThreshold={0.06}
        fadeDelayMs={300}
        fadeDurationMs={600}
        autoIdle={false}
      />
    </div>
  );
}

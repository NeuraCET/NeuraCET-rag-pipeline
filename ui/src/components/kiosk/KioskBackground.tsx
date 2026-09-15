import { motion } from "motion/react";

const PARTICLES = [
  { left: "70%", top: "34%", size: "h-2 w-2", delay: 0, drift: 14 },
  { left: "78%", top: "57%", size: "h-1.5 w-1.5", delay: 1.4, drift: -18 },
  { left: "65%", top: "67%", size: "h-1 w-1", delay: 2.6, drift: 10 },
  { left: "14%", top: "44%", size: "h-1 w-1", delay: 0.8, drift: -12 },
  { left: "40%", top: "83%", size: "h-1.5 w-1.5", delay: 2, drift: 16 },
];

export function KioskBackground() {
  return (
    <div className="pointer-events-none absolute inset-0">
      {/* Horizon lines with a slow travelling highlight */}
      {["20%", "72%"].map((top, index) => (
        <div
          key={top}
          className="absolute left-[8%] h-px w-[84%] overflow-hidden bg-gold/10"
          style={{ top }}
        >
          <motion.div
            animate={{ x: ["-30%", "130%"] }}
            transition={{
              duration: 14,
              repeat: Infinity,
              ease: "easeInOut",
              delay: index * 5,
            }}
            className="h-px w-1/4 bg-gradient-to-r from-transparent via-gold-light/70 to-transparent"
          />
        </div>
      ))}

      {/* Asymmetric orbital rings */}
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 160, repeat: Infinity, ease: "linear" }}
        className="absolute left-[58%] top-[12%] h-[80vh] w-[80vh] rounded-full border border-gold/10"
      >
        <div className="absolute -top-1 left-1/2 h-1.5 w-1.5 -translate-x-1/2 rounded-full bg-gold/60" />
      </motion.div>

      <motion.div
        animate={{ rotate: -360 }}
        transition={{ duration: 220, repeat: Infinity, ease: "linear" }}
        className="absolute left-[63%] top-[19%] h-[66vh] w-[66vh] rounded-full border border-dashed border-gold/5"
      />

      <motion.div
        animate={{ opacity: [0.06, 0.16, 0.06], scale: [1, 1.04, 1] }}
        transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
        className="absolute left-[52%] top-[26%] h-[46vh] w-[46vh] rounded-full border border-gold"
      />

      {/* Drifting motes */}
      {PARTICLES.map((particle) => (
        <motion.div
          key={`${particle.left}-${particle.top}`}
          animate={{ y: [0, particle.drift, 0], opacity: [0.25, 0.7, 0.25] }}
          transition={{
            duration: 9,
            repeat: Infinity,
            ease: "easeInOut",
            delay: particle.delay,
          }}
          style={{ left: particle.left, top: particle.top }}
          className={`absolute rounded-full bg-gold ${particle.size}`}
        />
      ))}
    </div>
  );
}

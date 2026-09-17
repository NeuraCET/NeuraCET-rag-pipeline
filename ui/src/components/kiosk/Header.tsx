export function Header() {
  return (
    <header className="absolute inset-x-0 top-0 z-30 flex items-center justify-between border-b border-white/10 bg-black/40 px-8 py-4 backdrop-blur-md md:px-12 lg:px-16">

      {/* Drishti / College Info */}
      <div className="flex items-center gap-4">
        <img
          src="../assets/drishti-logo.svg"
          alt="Drishti 2026"
          className="h-14 w-auto drop-shadow-[0_0_12px_rgba(213,180,92,0.3)] md:h-16"
        />

        <div className="flex flex-col justify-center">
          <span className="text-xs font-semibold uppercase tracking-[0.18em] text-white/85 md:text-sm">
            College of Engineering Trivandrum
          </span>

          <span className="mt-0.5 text-base font-black tracking-[0.25em] text-gold md:text-lg">
            DRISHTI 2026
          </span>
        </div>
      </div>

      {/* NeuraCET */}
      <div className="flex items-center gap-4">
        <div className="flex flex-col items-end justify-center">
          <span className="text-base font-black tracking-[0.25em] text-white md:text-lg">
            NEURACET
          </span>

          <span className="mt-0.5 text-xs font-semibold uppercase tracking-[0.16em] text-white/70 md:text-sm">
            CET's Applied AI Club
          </span>
        </div>

        <img
          src="../assets/neuracet-logo.svg"
          alt="NeuraCET"
          className="h-14 w-auto drop-shadow-[0_0_12px_rgba(255,255,255,0.2)] md:h-16"
        />
      </div>

    </header>
  );
}
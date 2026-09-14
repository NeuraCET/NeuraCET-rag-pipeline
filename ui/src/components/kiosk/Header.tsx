export function Header() {
  return (
    <header className="absolute inset-x-0 top-0 z-20 flex items-center justify-between border-b border-white/10 px-8 py-4 md:px-12 lg:px-16">

      {/* Drishti */}
      <div className="flex items-center gap-4">
        <img
          src="../assets/drishti-logo.svg"
          alt="Drishti 2026"
          className="h-12 w-auto"
        />

        <div className="flex flex-col justify-center">
          <span className="text-[9px] uppercase tracking-[0.12em] text-white/50">
            College of Engineering Trivandrum
          </span>

          <span className="mt-1 text-[10px] font-semibold tracking-[0.2em] text-white/80">
            DRISHTI 2026
          </span>
        </div>
      </div>

      {/* NeuraCET */}
      <div className="flex items-center gap-4">
        <div className="flex flex-col items-end justify-center">
          <span className="text-[10px] font-semibold tracking-[0.25em] text-white/80">
            NEURACET
          </span>

          <span className="mt-1 text-[8px] uppercase tracking-[0.12em] text-white/40">
            CET's Applied AI Club
          </span>
        </div>

        <img
          src="../assets/neuracet-logo.svg"
          alt="NeuraCET"
          className="h-12 w-auto"
        />
      </div>

    </header>
  );
}
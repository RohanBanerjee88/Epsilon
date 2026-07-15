const STEPS = ["Frame", "Search", "Compare", "Write"];

export function ResearchLoading({ phase, phaseIndex }: { phase: string; phaseIndex: number }) {
  const progress = Math.max(0.14, (phaseIndex + 1) / STEPS.length);

  return (
    <section className="animate-in" aria-live="polite" aria-busy="true">
      <div className="flex items-center justify-between gap-4 border-b border-border pb-4">
        <p className="text-sm font-medium text-foreground">Research run in progress</p>
        <span className="font-mono text-[10px] text-muted-foreground">
          {String(phaseIndex + 1).padStart(2, "0")} / 04
        </span>
      </div>

      <div className="grid min-h-[29rem] items-center gap-10 py-10 lg:grid-cols-[11rem_minmax(0,1fr)] lg:gap-16">
        <div className="mx-auto" aria-hidden="true">
          <div className="epsilon-loader-mark">
            <span className="epsilon-loader-symbol epsilon-loader-symbol-base">ε</span>
            <span className="epsilon-loader-symbol epsilon-loader-symbol-fill">ε</span>
            <span className="epsilon-loader-pulse" />
          </div>
          <p className="mt-4 text-center font-mono text-[9px] text-muted-foreground">EPSILON / RESEARCH</p>
        </div>

        <div className="max-w-xl">
          <p className="text-xs font-semibold text-primary">Building your brief</p>
          <h2 className="mt-4 text-balance text-4xl font-semibold leading-[1.04] text-foreground sm:text-5xl">
            Finding the angle worth pursuing.
          </h2>
          <p className="mt-6 min-h-6 text-sm leading-6 text-muted-foreground">{phase}</p>

          <div className="mt-10 h-0.5 overflow-hidden bg-border" aria-hidden="true">
            <span
              className="block h-full origin-left bg-primary transition-transform duration-500 [transition-timing-function:cubic-bezier(0.23,1,0.32,1)]"
              style={{ transform: `scaleX(${progress})` }}
            />
          </div>
          <div className="mt-4 flex items-center justify-between gap-4 text-xs">
            <span className="font-medium text-foreground">{STEPS[phaseIndex]}</span>
            <span className="text-muted-foreground">Keep this tab open</span>
          </div>
        </div>
      </div>
    </section>
  );
}

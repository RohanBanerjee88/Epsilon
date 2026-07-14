const STEPS = ["Question", "Evidence", "Compare", "Direction"];

export function ResearchLoading({ phase, phaseIndex }: { phase: string; phaseIndex: number }) {
  const progress = Math.max(0.14, (phaseIndex + 1) / STEPS.length);

  return (
    <section className="animate-in" aria-live="polite" aria-busy="true">
      <div className="flex items-center justify-between gap-4 border-b border-border pb-4">
        <div className="flex items-center gap-3">
          <span className="epsilon-status-dot size-2 rounded-full bg-primary" aria-hidden="true" />
          <p className="text-sm font-medium text-foreground">Research engine active</p>
        </div>
        <span className="font-mono text-[10px] text-muted-foreground">EPS / LIVE</span>
      </div>

      <div className="grid min-h-[32rem] items-center gap-10 py-10 lg:grid-cols-[17rem_minmax(0,1fr)] lg:gap-14">
        <div className="epsilon-loader-stage mx-auto" aria-hidden="true">
          <span className="epsilon-axis epsilon-axis-horizontal" />
          <span className="epsilon-axis epsilon-axis-vertical" />
          <span className="epsilon-orbit epsilon-orbit-outer" />
          <span className="epsilon-orbit epsilon-orbit-inner" />
          <span className="epsilon-sweep" />
          <span className="epsilon-signal epsilon-signal-one"><i /></span>
          <span className="epsilon-signal epsilon-signal-two"><i /></span>
          <span className="epsilon-signal epsilon-signal-three"><i /></span>
          <span className="epsilon-loader-core">ε</span>
          <span className="epsilon-coordinate epsilon-coordinate-top">RESEARCH / 01</span>
          <span className="epsilon-coordinate epsilon-coordinate-bottom">EVIDENCE / LIVE</span>
        </div>

        <div className="max-w-xl">
          <p className="text-xs font-semibold text-primary">Building your research brief</p>
          <h2 className="mt-4 text-balance text-4xl font-semibold leading-[1.04] text-foreground sm:text-5xl">
            Finding the angle worth pursuing.
          </h2>
          <p className="mt-6 min-h-6 text-sm leading-6 text-muted-foreground">{phase}</p>

          <div className="mt-10 h-px overflow-hidden bg-border" aria-hidden="true">
            <span
              className="block h-full origin-left bg-primary transition-transform duration-500 [transition-timing-function:cubic-bezier(0.23,1,0.32,1)]"
              style={{ transform: `scaleX(${progress})` }}
            />
          </div>

          <ol className="mt-4 grid grid-cols-4 gap-2">
            {STEPS.map((step, index) => {
              const isActive = index === phaseIndex;
              const isReached = index <= phaseIndex;
              return (
                <li key={step} className={isReached ? "text-foreground" : "text-muted-foreground/55"}>
                  <span className={isActive ? "font-mono text-[10px] font-semibold text-primary" : "font-mono text-[10px]"}>
                    {String(index + 1).padStart(2, "0")}
                  </span>
                  <span className="mt-1 block text-[10px] sm:text-xs">{step}</span>
                </li>
              );
            })}
          </ol>

          <p className="mt-10 font-mono text-[10px] leading-5 text-muted-foreground">
            OPENALEX&nbsp;&nbsp;/&nbsp;&nbsp;ARXIV&nbsp;&nbsp;/&nbsp;&nbsp;SEMANTIC SCHOLAR
          </p>
        </div>
      </div>
    </section>
  );
}

import { ArrowUpRight, BookOpenText, CircleCheck, CircleMinus, Lightbulb } from "lucide-react";

import type { ResearchBrief as ResearchBriefType } from "@/lib/types";

function SectionLabel({ children }: { children: React.ReactNode }) {
  return <p className="mb-4 text-xs font-semibold text-primary">{children}</p>;
}

function BulletList({ items, tone = "default" }: { items: string[]; tone?: "default" | "open" | "closed" }) {
  const Icon = tone === "open" ? CircleCheck : tone === "closed" ? CircleMinus : Lightbulb;
  return (
    <ul className="space-y-4">
      {items.map((item) => (
        <li key={item} className="grid grid-cols-[18px_1fr] gap-3 text-sm leading-6 text-foreground/75">
          <Icon className="mt-1 size-4 text-primary" strokeWidth={1.75} />
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}

export function ResearchBrief({ brief }: { brief: ResearchBriefType }) {
  return (
    <article className="animate-in">
      <header className="border-b border-border pb-10">
        <div className="mb-7 flex flex-wrap items-center gap-x-3 gap-y-2 text-xs text-muted-foreground">
          <span className="font-mono tabular-nums">{String(brief.sources_considered).padStart(2, "0")} sources reviewed</span>
          <span aria-hidden="true">/</span>
          <span>{brief.model}</span>
          {brief.prior_interests.length > 0 && (
            <>
              <span aria-hidden="true">/</span>
              <span>{brief.prior_interests.length} prior topic{brief.prior_interests.length === 1 ? "" : "s"} considered</span>
            </>
          )}
        </div>
        <SectionLabel>Refined research question</SectionLabel>
        <h1 className="max-w-4xl text-pretty text-4xl font-semibold leading-[1.02] text-foreground sm:text-5xl xl:text-6xl">
          {brief.refined_question}
        </h1>
      </header>

      <section className="border-b border-border py-10">
        <SectionLabel>Recommended direction</SectionLabel>
        <div className="research-stamp mb-7 inline-flex items-center gap-2 bg-primary px-3 py-2 text-xs font-semibold text-primary-foreground">
          <BookOpenText className="size-4" />
          Direction 01
        </div>
        <h2 className="max-w-3xl text-balance text-3xl font-semibold leading-tight md:text-4xl">
          {brief.recommended_direction.title}
        </h2>
        <p className="mt-5 max-w-3xl text-pretty text-base leading-7 text-foreground/70 md:text-lg">
          {brief.recommended_direction.rationale}
        </p>
        <div className="mt-9 grid gap-px overflow-hidden rounded-[6px] border border-border bg-border md:grid-cols-2">
          <div className="bg-background p-5 md:p-6">
            <p className="mb-2 text-xs font-semibold text-primary">Why it is novel</p>
            <p className="text-sm leading-6 text-foreground/70">{brief.recommended_direction.novelty_reason}</p>
          </div>
          <div className="bg-background p-5 md:p-6">
            <p className="mb-2 text-xs font-semibold text-primary">Why it is feasible</p>
            <p className="text-sm leading-6 text-foreground/70">{brief.recommended_direction.feasibility_reason}</p>
          </div>
        </div>
      </section>

      <section className="grid gap-10 border-b border-border py-10 lg:grid-cols-[0.8fr_1.2fr]">
        <div>
          <SectionLabel>Search directions</SectionLabel>
          <div className="flex flex-wrap gap-2">
            {brief.search_directions.map((direction, index) => (
              <span key={direction} className="rounded-[4px] border border-border bg-muted/45 px-3 py-2 text-xs text-foreground/75">
                <span className="mr-2 font-mono text-primary">{String(index + 1).padStart(2, "0")}</span>
                {direction}
              </span>
            ))}
          </div>
          <div className="mt-10">
            <SectionLabel>Key themes</SectionLabel>
            <BulletList items={brief.key_themes} />
          </div>
        </div>

        <div>
          <SectionLabel>Relevant sources</SectionLabel>
          <div className="border-t border-border">
            {brief.relevant_sources.map((source, index) => (
              <a
                key={`${source.url}-${source.title}`}
                href={source.url}
                target="_blank"
                rel="noreferrer"
                className="group grid grid-cols-[2.2rem_1fr_auto] gap-3 border-b border-border py-5 outline-none transition-colors hover:bg-muted/40 focus-visible:bg-muted/50"
              >
                <span className="pt-0.5 font-mono text-xs text-muted-foreground">{String(index + 1).padStart(2, "0")}</span>
                <span>
                  <span className="block text-[15px] font-semibold leading-6 group-hover:text-primary">{source.title}</span>
                  <span className="mt-1 block text-xs text-muted-foreground">
                    {[source.source_type, source.year, source.citation_count != null ? `${source.citation_count} citations` : null]
                      .filter(Boolean)
                      .join(" / ")}
                  </span>
                  <span className="mt-2 block text-sm leading-6 text-foreground/65">{source.why_it_matters}</span>
                </span>
                <ArrowUpRight className="mt-1 size-4 text-muted-foreground transition-transform group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-primary" aria-hidden="true" />
              </a>
            ))}
          </div>
        </div>
      </section>

      <section className="grid gap-px overflow-hidden border-b border-border bg-border md:grid-cols-2">
        <div className="bg-background py-10 pr-0 md:pr-8">
          <SectionLabel>What looks saturated</SectionLabel>
          <BulletList items={brief.saturated_areas} tone="closed" />
        </div>
        <div className="bg-background py-10 md:pl-8">
          <SectionLabel>What looks open</SectionLabel>
          <BulletList items={brief.underexplored_areas} tone="open" />
        </div>
      </section>

      <section className="py-10">
        <SectionLabel>Next three moves</SectionLabel>
        <ol className="grid gap-px overflow-hidden rounded-[6px] border border-border bg-border lg:grid-cols-3">
          {brief.next_steps.map((step, index) => (
            <li key={step} className="min-h-44 bg-background p-6">
              <span className="font-mono text-sm font-semibold text-primary">{String(index + 1).padStart(2, "0")}</span>
              <p className="mt-8 text-[15px] font-medium leading-6 text-foreground/80">{step}</p>
            </li>
          ))}
        </ol>
      </section>
    </article>
  );
}

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, CircleCheck, Lightbulb } from "lucide-react";

import { EpsilonMark } from "@/components/epsilon-mark";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { API_BASE_URL } from "@/lib/runtime";
import type { BriefCard } from "@/lib/types";

export function BriefCardSkeleton() {
  return (
    <div className="w-full max-w-[30rem] overflow-hidden rounded-[8px] bg-white shadow-[0_24px_80px_rgba(70,32,35,0.16)]">
      <Skeleton className="h-32 w-full rounded-none" />
      <div className="space-y-5 p-6">
        <Skeleton className="h-3 w-28" />
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-8 w-4/5" />
        <Skeleton className="h-24 w-full" />
      </div>
    </div>
  );
}

export function BriefCardView({ cardId }: { cardId: string | null }) {
  const [card, setCard] = useState<BriefCard | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!cardId) return;

    fetch(`${API_BASE_URL}/brief-cards/${encodeURIComponent(cardId)}`)
      .then(async (response) => {
        const payload = (await response.json().catch(() => null)) as BriefCard | { detail?: string } | null;
        if (!response.ok) {
          throw new Error(payload && "detail" in payload ? payload.detail : "This brief card is unavailable.");
        }
        setCard(payload as BriefCard);
      })
      .catch((caught) => setError(caught instanceof Error ? caught.message : "This brief card is unavailable."));
  }, [cardId]);

  const displayError = !cardId ? "This card link is incomplete." : error;

  if (displayError) {
    return (
      <main className="grid min-h-dvh place-items-center bg-[#ece8e6] p-4">
        <section className="w-full max-w-md rounded-[8px] bg-white p-7 shadow-[0_24px_80px_rgba(70,32,35,0.16)]">
          <EpsilonMark />
          <p className="mt-8 text-xs font-semibold text-primary">Quick brief unavailable</p>
          <h1 className="mt-3 text-3xl font-semibold leading-tight">This note could not be opened.</h1>
          <p className="mt-4 text-sm leading-6 text-muted-foreground">{displayError}</p>
          <Button asChild variant="outline" className="mt-8">
            <Link href="/"><ArrowLeft /> Open Epsilon</Link>
          </Button>
        </section>
      </main>
    );
  }

  if (!card) {
    return <main className="grid min-h-dvh place-items-center bg-[#ece8e6] p-4"><BriefCardSkeleton /></main>;
  }

  const created = new Intl.DateTimeFormat("en", { month: "short", day: "numeric", year: "numeric" }).format(new Date(card.created_at));

  return (
    <main className="phone-card-stage grid min-h-dvh place-items-center bg-[#ece8e6] p-3 sm:p-6">
      <article className="w-full max-w-[30rem] overflow-hidden rounded-[8px] bg-white shadow-[0_24px_80px_rgba(70,32,35,0.16)]">
        <header className="bg-primary px-6 pb-7 pt-6 text-primary-foreground">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <EpsilonMark className="bg-white text-primary" />
              <span>
                <span className="block text-sm font-semibold">Epsilon</span>
                <span className="block text-[10px] text-white/70">Quick brief</span>
              </span>
            </div>
            <span className="font-mono text-[10px] text-white/70">{created}</span>
          </div>
          <p className="mt-8 text-[10px] font-semibold text-white/70">Research question</p>
          <h1 className="mt-2 break-words text-2xl font-semibold leading-[1.15] sm:text-3xl">{card.refined_question}</h1>
        </header>

        <section className="border-b border-border px-6 py-7">
          <p className="text-xs font-semibold text-primary">Recommended direction</p>
          <h2 className="mt-3 break-words text-2xl font-semibold leading-tight">{card.recommended_direction.title}</h2>
          <p className="mt-4 text-sm leading-6 text-foreground/70">{card.recommended_direction.rationale}</p>
        </section>

        <section className="border-b border-border px-6 py-7">
          <p className="mb-5 text-xs font-semibold text-primary">Keep these three moves</p>
          <ol className="space-y-5">
            {card.next_steps.slice(0, 3).map((step, index) => (
              <li key={step} className="grid grid-cols-[1.75rem_1fr] gap-3 text-sm leading-6 text-foreground/75">
                <span className="grid size-7 place-items-center rounded-[4px] bg-accent font-mono text-[10px] font-semibold text-primary">
                  {String(index + 1).padStart(2, "0")}
                </span>
                <span>{step}</span>
              </li>
            ))}
          </ol>
        </section>

        {card.underexplored_areas.length > 0 && (
          <section className="px-6 py-7">
            <p className="mb-4 flex items-center gap-2 text-xs font-semibold text-primary">
              <Lightbulb className="size-4" /> Open signals
            </p>
            <ul className="space-y-3">
              {card.underexplored_areas.slice(0, 2).map((area) => (
                <li key={area} className="grid grid-cols-[1rem_1fr] gap-2.5 text-xs leading-5 text-foreground/65">
                  <CircleCheck className="mt-0.5 size-4 text-primary" />
                  <span>{area}</span>
                </li>
              ))}
            </ul>
          </section>
        )}

        <footer className="flex items-center justify-between border-t border-border bg-muted/30 px-6 py-4 text-[10px] text-muted-foreground">
          <span>{card.sources_considered} sources considered</span>
          <span className="font-mono">EPS / NOTE</span>
        </footer>
      </article>
    </main>
  );
}

"use client";

import { useEffect, useRef, useState } from "react";
import { AlertCircle, ArrowRight, RotateCcw, Search, SlidersHorizontal } from "lucide-react";

import { EpsilonMark } from "@/components/epsilon-mark";
import { ResearchBrief } from "@/components/research-brief";
import { ResearchLoading } from "@/components/research-loading";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { API_BASE_URL, APP_BASE_PATH } from "@/lib/runtime";
import type { BriefCard, ResearchBrief as ResearchBriefType, ResearchJob } from "@/lib/types";

const EXAMPLES = [
  "Small language models for clinical text",
  "Robust tool-using agents without a saturated angle",
  "On-device retrieval for scientific search",
];
const PHASES = [
  "Sharpening the research question",
  "Searching OpenAlex, arXiv, and Semantic Scholar",
  "Comparing themes and open directions",
  "Writing the research brief",
];

function getUserId() {
  const key = "epsilon-user-id";
  const existing = window.localStorage.getItem(key) ?? window.localStorage.getItem("research-navigator-user-id");
  if (existing) return existing;
  const created = `eps_${crypto.randomUUID()}`;
  window.localStorage.setItem(key, created);
  return created;
}

function readError(payload: unknown, fallback: string) {
  if (payload && typeof payload === "object" && "detail" in payload) {
    const detail = (payload as { detail?: unknown }).detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) return detail.map((item) => (typeof item === "object" && item && "msg" in item ? String(item.msg) : String(item))).join(" ");
  }
  return fallback;
}

function wait(milliseconds: number) {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds));
}

export function ResearchWorkspace() {
  const [topic, setTopic] = useState("");
  const [context, setContext] = useState("");
  const [brief, setBrief] = useState<ResearchBriefType | null>(null);
  const [loading, setLoading] = useState(false);
  const [phase, setPhase] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [shareUrl, setShareUrl] = useState<string | null>(null);
  const [shareLoading, setShareLoading] = useState(false);
  const [shareError, setShareError] = useState<string | null>(null);
  const outputRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (!loading) return;
    const timer = window.setInterval(() => setPhase((current) => Math.min(current + 1, PHASES.length - 1)), 2200);
    return () => window.clearInterval(timer);
  }, [loading]);

  useEffect(() => {
    if (!loading && !brief && !error) return;
    window.requestAnimationFrame(() => {
      outputRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }, [brief, error, loading]);

  async function preparePhoneCard(completedBrief: ResearchBriefType) {
    setShareLoading(true);
    setShareError(null);
    setShareUrl(null);

    try {
      const response = await fetch(`${API_BASE_URL}/brief-cards`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          refined_question: completedBrief.refined_question,
          recommended_direction: completedBrief.recommended_direction,
          next_steps: completedBrief.next_steps,
          underexplored_areas: completedBrief.underexplored_areas,
          sources_considered: completedBrief.sources_considered,
        }),
      });
      const payload: unknown = await response.json().catch(() => null);
      if (!response.ok) throw new Error(readError(payload, "The phone card could not be created."));

      const card = payload as BriefCard;
      const configuredOrigin = process.env.NEXT_PUBLIC_SHARE_BASE_URL?.replace(/\/$/, "");
      const origin = configuredOrigin || `${window.location.origin}${APP_BASE_PATH}`;
      setShareUrl(`${origin}/card/?id=${encodeURIComponent(card.id)}`);
    } catch (caught) {
      setShareError(caught instanceof Error ? caught.message : "The phone card could not be created.");
    } finally {
      setShareLoading(false);
    }
  }

  async function analyze() {
    const cleanTopic = topic.trim();
    if (cleanTopic.length < 3) {
      setError("Add a research topic with at least three characters.");
      return;
    }

    setLoading(true);
    setPhase(0);
    setError(null);
    setBrief(null);
    setShareUrl(null);
    setShareError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/research/jobs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic: cleanTopic, context: context.trim(), userId: getUserId() }),
      });
      const payload: unknown = await response.json().catch(() => null);
      if (!response.ok) throw new Error(readError(payload, `Request failed with status ${response.status}.`));

      const createdJob = payload as ResearchJob;
      let completedBrief: ResearchBriefType | null = null;

      for (let attempt = 0; attempt < 240; attempt += 1) {
        await wait(1500);
        const statusResponse = await fetch(`${API_BASE_URL}/research/jobs/${encodeURIComponent(createdJob.id)}`, {
          cache: "no-store",
        });
        const statusPayload: unknown = await statusResponse.json().catch(() => null);
        if (!statusResponse.ok) {
          throw new Error(readError(statusPayload, `Status check failed with ${statusResponse.status}.`));
        }

        const job = statusPayload as ResearchJob;
        if (job.status === "failed") throw new Error(job.error || "The analysis could not be completed.");
        if (job.status === "completed" && job.brief) {
          completedBrief = job.brief;
          break;
        }
      }

      if (!completedBrief) throw new Error("The research run took too long. Please try again.");
      setBrief(completedBrief);
      void preparePhoneCard(completedBrief);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "The analysis could not be completed.");
    } finally {
      setLoading(false);
    }
  }

  function reset() {
    setBrief(null);
    setError(null);
    setShareUrl(null);
    setShareError(null);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  return (
    <div className="min-h-dvh bg-background text-foreground">
      <a href="#workspace" className="skip-link">Skip to research workspace</a>
      <header className="border-b border-border bg-background/95 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-[1480px] items-center px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <EpsilonMark />
            <div>
              <p className="text-sm font-semibold leading-none">Epsilon</p>
              <p className="mt-1 text-[11px] text-muted-foreground">Evidence before direction</p>
            </div>
          </div>
        </div>
      </header>

      <main id="workspace" className="mx-auto grid max-w-[1480px] lg:min-h-[calc(100dvh-4rem)] lg:grid-cols-[minmax(20rem,27rem)_1fr]">
        <aside className="border-b border-border bg-muted/20 p-5 sm:p-7 lg:border-b-0 lg:border-r lg:p-8">
          <div className="lg:sticky lg:top-8">
            <div className="mb-9">
              <p className="mb-3 flex items-center gap-2 text-xs font-semibold text-primary">
                <SlidersHorizontal className="size-3.5" />
                Research brief
              </p>
              <h1 className="max-w-sm text-balance text-3xl font-semibold leading-[1.08] sm:text-4xl">
                Find the angle worth pursuing.
              </h1>
              <p className="mt-4 max-w-sm text-sm leading-6 text-muted-foreground">
                Start broad. The agent narrows the question, reviews real papers, and returns one practical direction.
              </p>
            </div>

            <form onSubmit={(event) => { event.preventDefault(); void analyze(); }} className="space-y-5">
              <div>
                <label htmlFor="topic" className="mb-2 block text-xs font-semibold">Research interest</label>
                <Textarea
                  id="topic"
                  value={topic}
                  onChange={(event) => setTopic(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" && (event.metaKey || event.ctrlKey)) {
                      event.preventDefault();
                      void analyze();
                    }
                  }}
                  rows={5}
                  maxLength={2000}
                  placeholder="e.g. I want to explore lightweight retrieval methods for on-device scientific search"
                  disabled={loading}
                />
                <p className="mt-2 text-right font-mono text-[10px] tabular-nums text-muted-foreground">{topic.length}/2000</p>
              </div>
              <div>
                <label htmlFor="context" className="mb-2 block text-xs font-semibold">
                  Context <span className="font-normal text-muted-foreground">(optional)</span>
                </label>
                <Textarea
                  id="context"
                  value={context}
                  onChange={(event) => setContext(event.target.value)}
                  rows={3}
                  maxLength={4000}
                  placeholder="Your background, constraints, or intended outcome"
                  disabled={loading}
                />
              </div>
              <Button type="submit" size="lg" className="w-full" disabled={loading || topic.trim().length < 3}>
                {loading ? "Analyzing research" : "Build research brief"}
                <ArrowRight />
              </Button>
            </form>

            <div className="mt-8 border-t border-border pt-5">
              <p className="mb-3 text-[11px] font-medium text-muted-foreground">Try a starting point</p>
              <div className="space-y-1">
                {EXAMPLES.map((example) => (
                  <button
                    key={example}
                    type="button"
                    onClick={() => { setTopic(example); setError(null); }}
                    disabled={loading}
                    className="group flex w-full items-start gap-2 rounded-[4px] px-2 py-2 text-left text-xs leading-5 text-muted-foreground transition-colors hover:bg-background hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  >
                    <Search className="mt-0.5 size-3.5 shrink-0 text-primary/70 transition-colors group-hover:text-primary" />
                    {example}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </aside>

        <section ref={outputRef} className="min-w-0 scroll-mt-4 p-5 sm:p-8 lg:p-12 xl:p-16">
          <div className="mx-auto max-w-5xl">
            {error && (
              <Alert className="mb-8">
                <AlertCircle className="mt-0.5 size-4 text-destructive" />
                <AlertTitle>Analysis stopped</AlertTitle>
                <AlertDescription>
                  <p>{error}</p>
                  <Button type="button" variant="outline" size="sm" className="mt-4" onClick={() => void analyze()}>
                    <RotateCcw /> Retry
                  </Button>
                </AlertDescription>
              </Alert>
            )}

            {loading ? (
              <ResearchLoading phase={PHASES[phase]} phaseIndex={phase} />
            ) : brief ? (
              <>
                <div className="mb-6 flex justify-end">
                  <Button variant="ghost" size="sm" onClick={reset}><RotateCcw /> New brief</Button>
                </div>
                <ResearchBrief
                  brief={brief}
                  shareUrl={shareUrl}
                  shareLoading={shareLoading}
                  shareError={shareError}
                />
              </>
            ) : (
              <div className="empty-sheet flex min-h-[62vh] flex-col justify-between border-y border-border py-8 sm:py-12">
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span className="font-mono">EPS / 001</span>
                  <span>Research direction memo</span>
                </div>
                <div className="max-w-3xl py-16">
                  <p className="mb-5 text-xs font-semibold text-primary">A clearer next move</p>
                  <h2 className="text-balance text-5xl font-semibold leading-[0.94] text-foreground sm:text-6xl xl:text-7xl">
                    Your research brief will take shape here.
                  </h2>
                </div>
                <div className="grid gap-4 border-t border-border pt-6 text-xs leading-5 text-muted-foreground sm:grid-cols-3">
                  <p><span className="mr-2 font-mono text-primary">01</span>Sharper question</p>
                  <p><span className="mr-2 font-mono text-primary">02</span>Evidence scan</p>
                  <p><span className="mr-2 font-mono text-primary">03</span>Concrete next steps</p>
                </div>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}

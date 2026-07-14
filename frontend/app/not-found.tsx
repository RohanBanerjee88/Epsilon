import Link from "next/link";
import { ArrowLeft, BookOpen } from "lucide-react";

import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <main className="grid min-h-dvh place-items-center bg-background px-5">
      <section className="w-full max-w-3xl border-y border-border py-12 sm:py-16">
        <div className="mb-16 flex items-center gap-3">
          <span className="grid size-8 place-items-center rounded-[4px] bg-primary text-primary-foreground">
            <BookOpen className="size-4" />
          </span>
          <span className="text-sm font-semibold">Research Navigator</span>
        </div>
        <p className="font-mono text-xs text-primary">404 / Missing reference</p>
        <h1 className="mt-5 max-w-2xl text-balance text-5xl font-semibold leading-none sm:text-6xl">
          This research path does not exist.
        </h1>
        <p className="mt-6 max-w-xl text-base leading-7 text-muted-foreground">
          Return to the workspace and start a new brief from a research question that matters to you.
        </p>
        <Button asChild className="mt-10">
          <Link href="/"><ArrowLeft /> Back to the workspace</Link>
        </Button>
      </section>
    </main>
  );
}

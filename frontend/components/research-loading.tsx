import { Skeleton } from "@/components/ui/skeleton";

export function ResearchLoading({ phase }: { phase: string }) {
  return (
    <section className="animate-in" aria-live="polite" aria-busy="true">
      <div className="mb-10 flex items-center gap-3 border-b border-border pb-4">
        <span className="size-2 animate-pulse rounded-full bg-primary" />
        <p className="text-sm font-medium text-foreground">{phase}</p>
      </div>
      <div className="space-y-4 border-b border-border pb-10">
        <Skeleton className="h-3 w-28" />
        <Skeleton className="h-9 w-full max-w-2xl" />
        <Skeleton className="h-9 w-4/5 max-w-xl" />
      </div>
      <div className="grid gap-8 py-10 md:grid-cols-2">
        <div className="space-y-4">
          <Skeleton className="h-3 w-24" />
          <Skeleton className="h-28 w-full" />
        </div>
        <div className="space-y-4">
          <Skeleton className="h-3 w-32" />
          <Skeleton className="h-28 w-full" />
        </div>
      </div>
      <div className="space-y-3 border-t border-border pt-10">
        <Skeleton className="h-3 w-20" />
        <Skeleton className="h-20 w-full" />
        <Skeleton className="h-20 w-full" />
      </div>
    </section>
  );
}

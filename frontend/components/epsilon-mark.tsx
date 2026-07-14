import { cn } from "@/lib/utils";

export function EpsilonMark({ className }: { className?: string }) {
  return (
    <span
      aria-hidden="true"
      className={cn(
        "grid size-8 shrink-0 place-items-center rounded-[4px] bg-primary pb-0.5 text-[23px] font-semibold leading-none text-primary-foreground",
        className,
      )}
    >
      ε
    </span>
  );
}

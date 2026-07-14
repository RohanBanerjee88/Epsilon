import * as React from "react";

import { cn } from "@/lib/utils";

function Textarea({ className, ...props }: React.ComponentProps<"textarea">) {
  return (
    <textarea
      className={cn(
        "flex min-h-24 w-full resize-none rounded-[5px] border border-input bg-background px-3 py-3 text-[15px] leading-6 text-foreground outline-none transition-[border-color,box-shadow] duration-200 placeholder:text-muted-foreground/70 focus-visible:border-primary/70 focus-visible:ring-2 focus-visible:ring-ring/20 disabled:cursor-not-allowed disabled:opacity-50",
        className,
      )}
      {...props}
    />
  );
}

export { Textarea };

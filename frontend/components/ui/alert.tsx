import * as React from "react";

import { cn } from "@/lib/utils";

function Alert({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      role="alert"
      className={cn("grid grid-cols-[auto_1fr] gap-x-3 rounded-[6px] border border-destructive/25 bg-destructive/5 p-4 text-sm", className)}
      {...props}
    />
  );
}

function AlertTitle({ className, ...props }: React.ComponentProps<"h3">) {
  return <h3 className={cn("col-start-2 font-semibold text-destructive", className)} {...props} />;
}

function AlertDescription({ className, ...props }: React.ComponentProps<"div">) {
  return <div className={cn("col-start-2 mt-1 leading-6 text-foreground/75", className)} {...props} />;
}

export { Alert, AlertTitle, AlertDescription };

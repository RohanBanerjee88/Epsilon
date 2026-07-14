import { ScanLine } from "lucide-react";
import { QRCodeSVG } from "qrcode.react";

import { EpsilonMark } from "@/components/epsilon-mark";
import { Skeleton } from "@/components/ui/skeleton";

type BriefQrProps = {
  shareUrl: string | null;
  isPreparing: boolean;
  error: string | null;
};

export function BriefQr({ shareUrl, isPreparing, error }: BriefQrProps) {
  return (
    <aside className="w-full max-w-40 justify-self-start lg:justify-self-end" aria-label="Phone quick-note card">
      <a
        href={shareUrl ?? undefined}
        target={shareUrl ? "_blank" : undefined}
        rel={shareUrl ? "noreferrer" : undefined}
        aria-disabled={!shareUrl}
        className="group block rounded-[7px] border border-border bg-white p-2.5 outline-none transition-[border-color,transform,box-shadow] duration-200 hover:border-primary/35 hover:shadow-[0_10px_30px_rgba(77,28,32,0.1)] focus-visible:ring-2 focus-visible:ring-ring aria-disabled:pointer-events-none"
      >
        <div className="relative grid aspect-square place-items-center overflow-hidden rounded-[4px] bg-white">
          {shareUrl ? (
            <>
              <QRCodeSVG
                value={shareUrl}
                size={124}
                level="H"
                marginSize={1}
                bgColor="#ffffff"
                fgColor="#211d1d"
                className="size-full"
              />
              <EpsilonMark className="absolute size-7 border-2 border-white text-[18px] shadow-sm" />
            </>
          ) : isPreparing ? (
            <Skeleton className="size-full" />
          ) : (
            <ScanLine className="size-8 text-muted-foreground" strokeWidth={1.5} />
          )}
        </div>
        <div className="flex items-center justify-between gap-2 px-1 pb-0.5 pt-2.5">
          <span>
            <span className="block text-xs font-semibold text-foreground">Phone card</span>
            <span className="mt-0.5 block text-[10px] text-muted-foreground">
              {shareUrl ? "Open quick note" : error ? "Card unavailable" : "Preparing"}
            </span>
          </span>
          <ScanLine className="size-4 text-primary" />
        </div>
      </a>
    </aside>
  );
}

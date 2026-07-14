"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";

import { BriefCardSkeleton, BriefCardView } from "@/components/brief-card-view";

function CardFromQuery() {
  const searchParams = useSearchParams();
  return <BriefCardView cardId={searchParams.get("id")} />;
}

export default function CardPage() {
  return (
    <Suspense fallback={<main className="grid min-h-dvh place-items-center bg-[#ece8e6] p-4"><BriefCardSkeleton /></main>}>
      <CardFromQuery />
    </Suspense>
  );
}

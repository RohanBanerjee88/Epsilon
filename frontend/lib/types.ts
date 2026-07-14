export type ResearchSource = {
  title: string;
  url: string;
  why_it_matters: string;
  source_type: "paper" | "web" | "other";
  year?: number | null;
  citation_count?: number | null;
};

export type ResearchBrief = {
  refined_question: string;
  search_directions: string[];
  relevant_sources: ResearchSource[];
  key_themes: string[];
  saturated_areas: string[];
  underexplored_areas: string[];
  recommended_direction: {
    title: string;
    rationale: string;
    novelty_reason: string;
    feasibility_reason: string;
  };
  next_steps: string[];
  sources_considered: number;
  prior_interests: string[];
  model: string;
};

export type ResearchJob = {
  id: string;
  status: "queued" | "running" | "completed" | "failed";
  brief?: ResearchBrief | null;
  error?: string | null;
};

export type BriefCard = {
  id: string;
  created_at: string;
  refined_question: string;
  recommended_direction: ResearchBrief["recommended_direction"];
  next_steps: string[];
  underexplored_areas: string[];
  sources_considered: number;
};

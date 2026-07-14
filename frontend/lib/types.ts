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

export type HealthResponse = {
  status: string;
  ready_for_analysis: boolean;
  has_api_key: boolean;
  model: string;
  sdk_version?: string | null;
  sdk_compatible?: boolean;
  issue?: string | null;
};

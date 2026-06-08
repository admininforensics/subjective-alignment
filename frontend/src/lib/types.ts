export type UserRole = "RESPONDENT" | "MANAGER" | "ORG_ADMIN" | "SUPER_ADMIN";

export type AuthUser = {
  id: number;
  email: string;
  role: UserRole;
  organisation_id: number | null;
};

export type LoginResponse = {
  access: string;
  refresh: string;
  user: AuthUser;
};

export type DashboardResponse = {
  assigned_licence: { id: number; status: string } | null;
  session: { id: number; status: string; progress: number | null } | null;
  latest_result: { session_id: number } | null;
};

export type SessionDetailResponse = {
  session: {
    id: number;
    status: string;
    started_at: string | null;
    completed_at: string | null;
    last_activity_at: string | null;
    progress: number;
  };
  questions: Array<{
    id: number;
    order: number;
    text: string;
    area: string;
    subarea: string;
  }>;
  responses: Array<{
    question_id: number;
    raw_likert_score: number;
    effective_likert_score: number;
  }>;
};

export type ReportWheel = {
  scores: Record<string, number>;
  levels: Record<string, string>;
  top_pressure_zones: Array<{
    domain: string;
    slug: string;
    score: number;
    level: string;
  }>;
};

export type AssessmentReport = {
  welcome: string;
  overall_snapshot: {
    alignment_level: string;
    system_state: string;
    main_pattern: string;
    variables: Record<string, unknown>;
  };
  top_strain_areas: Array<{
    rank: number;
    domain: string;
    level: string;
    normalized_score: number;
    what_this_means: string;
  }>;
  full_results_summary: Array<{
    domain: string;
    level: string;
    normalized_score: number;
    what_it_reflects: string;
  }>;
  what_results_suggest: string;
  recommended_focus_areas: Array<{
    rank: number;
    domain: string;
    title: string;
    why_this_matters: string;
  }>;
  suggested_next_steps: string[];
  closing_reflection: string;
  wheel: ReportWheel;
  llm_used: boolean;
  llm_provider: "openai" | "ollama" | "template";
};

export type ResultsResponse = {
  session: { id: number; status: string; completed_at: string | null; respondent_id: number };
  domain_results: Array<{
    domain: string;
    score: number;
    threshold: number;
    triggered: boolean;
  }>;
  flags: Array<{ flag: string; insight: string }>;
  report: AssessmentReport | null;
};


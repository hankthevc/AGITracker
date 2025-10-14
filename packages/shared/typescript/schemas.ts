import { z } from 'zod';

// Enums
export const CategoryEnum = z.enum(['capabilities', 'agents', 'inputs', 'security']);
export const DirectionEnum = z.enum(['>=', '<=']);
export const BenchmarkFamilyEnum = z.enum(['SWE_BENCH_VERIFIED', 'OSWORLD', 'WEBARENA', 'GPQA_DIAMOND', 'OTHER']);
export const SourceTypeEnum = z.enum(['paper', 'leaderboard', 'model_card', 'press', 'blog', 'social']);
export const CredibilityEnum = z.enum(['A', 'B', 'C', 'D']);
export const ChangelogTypeEnum = z.enum(['add', 'update', 'retract']);
export const PresetEnum = z.enum(['equal', 'aschenbrenner', 'ai2027', 'custom']);
export const RoleEnum = z.enum(['admin', 'readonly']);

// Roadmap
export const RoadmapSchema = z.object({
  id: z.number(),
  slug: z.string(),
  name: z.string(),
  description: z.string().nullable(),
  preset_weights: z.record(z.number()).nullable(),
  created_at: z.string(),
});

export type Roadmap = z.infer<typeof RoadmapSchema>;

// Signpost
export const SignpostSchema = z.object({
  id: z.number(),
  code: z.string(),
  roadmap_id: z.number().nullable(),
  name: z.string(),
  description: z.string().nullable(),
  category: CategoryEnum,
  metric_name: z.string().nullable(),
  unit: z.string().nullable(),
  direction: DirectionEnum,
  baseline_value: z.number().nullable(),
  target_value: z.number().nullable(),
  methodology_url: z.string().nullable(),
  first_class: z.boolean(),
  created_at: z.string(),
});

export type Signpost = z.infer<typeof SignpostSchema>;

// Benchmark
export const BenchmarkSchema = z.object({
  id: z.number(),
  code: z.string(),
  name: z.string(),
  url: z.string().nullable(),
  family: BenchmarkFamilyEnum,
  created_at: z.string(),
});

export type Benchmark = z.infer<typeof BenchmarkSchema>;

// Source
export const SourceSchema = z.object({
  id: z.number(),
  url: z.string(),
  domain: z.string().nullable(),
  source_type: SourceTypeEnum,
  credibility: CredibilityEnum,
  first_seen_at: z.string(),
});

export type Source = z.infer<typeof SourceSchema>;

// Claim
export const ClaimSchema = z.object({
  id: z.number(),
  title: z.string().nullable(),
  summary: z.string().nullable(),
  metric_name: z.string().nullable(),
  metric_value: z.number().nullable(),
  unit: z.string().nullable(),
  observed_at: z.string(),
  source_id: z.number().nullable(),
  url_hash: z.string().nullable(),
  extraction_confidence: z.number().nullable(),
  raw_json: z.record(z.any()).nullable(),
  retracted: z.boolean(),
  created_at: z.string(),
});

export type Claim = z.infer<typeof ClaimSchema>;

// Index Snapshot
export const IndexSnapshotSchema = z.object({
  id: z.number(),
  as_of_date: z.string(),
  capabilities: z.number().nullable(),
  agents: z.number().nullable(),
  inputs: z.number().nullable(),
  security: z.number().nullable(),
  overall: z.number().nullable(),
  safety_margin: z.number().nullable(),
  preset: PresetEnum,
  details: z.record(z.any()).nullable(),
  created_at: z.string(),
});

export type IndexSnapshot = z.infer<typeof IndexSnapshotSchema>;

// Changelog
export const ChangelogSchema = z.object({
  id: z.number(),
  occurred_at: z.string(),
  type: ChangelogTypeEnum,
  title: z.string().nullable(),
  body: z.string().nullable(),
  claim_id: z.number().nullable(),
  reason: z.string().nullable(),
  created_at: z.string(),
});

export type Changelog = z.infer<typeof ChangelogSchema>;

// API Response Types
export const SignpostWithProgressSchema = SignpostSchema.extend({
  progress: z.number(),
  evidence_count: z.object({
    A: z.number(),
    B: z.number(),
    C: z.number(),
    D: z.number(),
  }),
});

export type SignpostWithProgress = z.infer<typeof SignpostWithProgressSchema>;

export const IndexResponseSchema = z.object({
  as_of_date: z.string(),
  overall: z.number(),
  capabilities: z.number(),
  agents: z.number(),
  inputs: z.number(),
  security: z.number(),
  safety_margin: z.number(),
  preset: PresetEnum,
  confidence_bands: z.object({
    overall: z.object({ lower: z.number(), upper: z.number() }),
    capabilities: z.object({ lower: z.number(), upper: z.number() }),
    agents: z.object({ lower: z.number(), upper: z.number() }),
    inputs: z.object({ lower: z.number(), upper: z.number() }),
    security: z.object({ lower: z.number(), upper: z.number() }),
  }),
});

export type IndexResponse = z.infer<typeof IndexResponseSchema>;


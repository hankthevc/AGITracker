/**
 * Core scoring algorithms for AGI signpost progress calculation.
 * Mirror implementation of Python scoring/core.py
 */

export function clamp(value: number, minVal: number = 0.0, maxVal: number = 1.0): number {
  return Math.max(minVal, Math.min(maxVal, value));
}

export function computeSignpostProgress(
  observed: number,
  baseline: number,
  target: number,
  direction: '>=' | '<='
): number {
  /**
   * Compute progress for a single signpost.
   * 
   * @param observed - Current observed value
   * @param baseline - Starting baseline value
   * @param target - Target value for completion
   * @param direction - '>=' for increasing metrics, '<=' for decreasing
   * @returns Progress value between 0 and 1
   */
  if (direction === '>=') {
    if (target === baseline) {
      return observed >= target ? 1.0 : 0.0;
    }
    return clamp((observed - baseline) / (target - baseline));
  } else if (direction === '<=') {
    if (baseline === target) {
      return observed <= target ? 1.0 : 0.0;
    }
    return clamp((baseline - observed) / (baseline - target));
  } else {
    throw new Error(`Invalid direction: ${direction}. Must be '>=' or '<='`);
  }
}

export function aggregateCategory(
  signpostProgresses: number[],
  signpostWeights?: number[]
): number {
  /**
   * Aggregate multiple signpost progresses into a category score.
   * 
   * @param signpostProgresses - Array of individual signpost progress values (0-1)
   * @param signpostWeights - Optional weights for each signpost. Defaults to equal weighting.
   * @returns Weighted mean category progress (0-1)
   */
  if (signpostProgresses.length === 0) {
    return 0.0;
  }

  const weights = signpostWeights || Array(signpostProgresses.length).fill(1.0);

  if (signpostProgresses.length !== weights.length) {
    throw new Error('signpostProgresses and signpostWeights must have same length');
  }

  const totalWeight = weights.reduce((sum, w) => sum + w, 0);
  if (totalWeight === 0) {
    return 0.0;
  }

  const weightedSum = signpostProgresses.reduce(
    (sum, progress, i) => sum + progress * weights[i],
    0
  );
  return weightedSum / totalWeight;
}

export function computeOverall(capabilities: number, inputs: number): number {
  /**
   * Compute overall AGI proximity using harmonic mean.
   * 
   * The harmonic mean ensures that both capabilities AND inputs must advance
   * together - bottleneck on either dimension significantly reduces overall score.
   * 
   * @param capabilities - Capabilities category score (0-1)
   * @param inputs - Inputs category score (0-1)
   * @returns Overall proximity score (0-1)
   */
  if (capabilities === 0 || inputs === 0) {
    return 0.0;
  }

  return 2.0 / (1.0 / capabilities + 1.0 / inputs);
}

export function computeSafetyMargin(security: number, capabilities: number): number {
  /**
   * Compute safety margin (security minus capabilities).
   * 
   * Negative values indicate capabilities are outpacing security readiness.
   * 
   * @param security - Security category score (0-1)
   * @param capabilities - Capabilities category score (0-1)
   * @returns Safety margin (-1 to 1)
   */
  return security - capabilities;
}

export interface CategoryScores {
  capabilities: number;
  agents: number;
  inputs: number;
  security: number;
}

export interface PresetWeights {
  capabilities: number;
  agents: number;
  inputs: number;
  security: number;
}

export interface IndexMetrics extends CategoryScores {
  overall: number;
  safety_margin: number;
}

export function computeIndexFromCategories(
  categoryScores: CategoryScores,
  presetWeights: PresetWeights
): IndexMetrics {
  /**
   * Compute full index metrics from category scores using preset weights.
   * 
   * @param categoryScores - Object with 'capabilities', 'agents', 'inputs', 'security'
   * @param presetWeights - Object with category weights (should sum to ~1.0)
   * @returns Object with overall, safety_margin, and all category scores
   */
  const capabilities = categoryScores.capabilities || 0.0;
  const agents = categoryScores.agents || 0.0;
  const inputs = categoryScores.inputs || 0.0;
  const security = categoryScores.security || 0.0;

  // Combine capabilities and agents into effective "capabilities API"
  const capWeight = presetWeights.capabilities || 0.25;
  const agentWeight = presetWeights.agents || 0.25;
  const combinedCap =
    capWeight + agentWeight > 0
      ? (capabilities * capWeight + agents * agentWeight) / (capWeight + agentWeight)
      : 0.0;

  const overall = computeOverall(combinedCap, inputs);
  const safety_margin = computeSafetyMargin(security, combinedCap);

  return {
    capabilities,
    agents,
    inputs,
    security,
    overall,
    safety_margin,
  };
}

export interface EvidenceCounts {
  A: number;
  B: number;
  C: number;
  D: number;
}

export interface ConfidenceBand {
  lower: number;
  upper: number;
}

export function computeConfidenceBands(
  categoryScores: Record<string, number>,
  evidenceCounts: Record<string, EvidenceCounts>,
  confidenceWidth: number = 0.1
): Record<string, ConfidenceBand> {
  /**
   * Compute confidence bands around index values based on evidence quality.
   * 
   * @param categoryScores - Category score values
   * @param evidenceCounts - Counts of A/B/C/D tier evidence per category
   * @param confidenceWidth - Base width of confidence interval (default 0.1 = ±5%)
   * @returns Object of {category: {lower, upper}} confidence bounds
   */
  const bands: Record<string, ConfidenceBand> = {};

  for (const [category, score] of Object.entries(categoryScores)) {
    if (category === 'overall' || category === 'safety_margin') {
      // Derived metrics use combined uncertainty
      bands[category] = {
        lower: Math.max(0, score - confidenceWidth),
        upper: Math.min(1, score + confidenceWidth),
      };
      continue;
    }

    const counts = evidenceCounts[category] || { A: 0, B: 0, C: 0, D: 0 };
    const total = counts.A + counts.B + counts.C + counts.D;

    if (total === 0) {
      // No evidence = maximum uncertainty
      bands[category] = { lower: 0.0, upper: 1.0 };
      continue;
    }

    // Weight evidence quality: A=1.0, B=0.8, C=0.3, D=0.1
    const qualityScore =
      (counts.A * 1.0 + counts.B * 0.8 + counts.C * 0.3 + counts.D * 0.1) / total;

    // Lower quality = wider bands
    let adjustedWidth = qualityScore > 0 ? confidenceWidth / qualityScore : 1.0;
    adjustedWidth = Math.min(adjustedWidth, 0.5); // Cap at ±25%

    bands[category] = {
      lower: Math.max(0.0, score - adjustedWidth),
      upper: Math.min(1.0, score + adjustedWidth),
    };
  }

  return bands;
}


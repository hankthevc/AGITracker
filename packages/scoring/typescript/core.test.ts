/**
 * Tests for scoring library (TypeScript)
 * Mirror of Python tests to ensure parity
 */

import {
  computeSignpostProgress,
  aggregateCategory,
  computeOverall,
  computeSafetyMargin,
} from './core'

describe('computeSignpostProgress', () => {
  test('increasing metrics (>=)', () => {
    // Perfect progress
    expect(computeSignpostProgress(85, 50, 85, '>=')).toBe(1.0)
    
    // Halfway progress
    expect(computeSignpostProgress(67.5, 50, 85, '>=')).toBeCloseTo(0.5, 2)
    
    // No progress
    expect(computeSignpostProgress(50, 50, 85, '>=')).toBe(0.0)
    
    // Over target (clamped)
    expect(computeSignpostProgress(90, 50, 85, '>=')).toBe(1.0)
  })
  
  test('decreasing metrics (<=)', () => {
    // Perfect progress
    expect(computeSignpostProgress(10, 60, 10, '<=')).toBe(1.0)
    
    // Halfway progress
    expect(computeSignpostProgress(35, 60, 10, '<=')).toBeCloseTo(0.5, 2)
    
    // No progress
    expect(computeSignpostProgress(60, 60, 10, '<=')).toBe(0.0)
  })
})

describe('aggregateCategory', () => {
  test('equal weights', () => {
    const progresses = [0.5, 0.6, 0.7]
    const result = aggregateCategory(progresses)
    const expected = (0.5 + 0.6 + 0.7) / 3
    expect(result).toBeCloseTo(expected, 2)
  })
  
  test('custom weights', () => {
    const progresses = [0.5, 1.0]
    const weights = [1.0, 2.0]
    const result = aggregateCategory(progresses, weights)
    const expected = (0.5 * 1.0 + 1.0 * 2.0) / 3.0
    expect(result).toBeCloseTo(expected, 2)
  })
})

describe('computeOverall', () => {
  test('equal inputs', () => {
    expect(computeOverall(0.5, 0.5)).toBeCloseTo(0.5, 2)
  })
  
  test('different inputs', () => {
    // Harmonic mean of 0.4 and 0.6 = 2 / (1/0.4 + 1/0.6) ≈ 0.48
    expect(computeOverall(0.4, 0.6)).toBeCloseTo(0.48, 2)
  })
  
  test('zero input', () => {
    expect(computeOverall(0.0, 0.5)).toBe(0.0)
  })
})

describe('computeSafetyMargin', () => {
  test('positive margin (security ahead)', () => {
    expect(computeSafetyMargin(0.6, 0.4)).toBe(0.2)
  })
  
  test('negative margin (capability sprint)', () => {
    expect(computeSafetyMargin(0.3, 0.7)).toBe(-0.4)
  })
  
  test('parity', () => {
    expect(computeSafetyMargin(0.5, 0.5)).toBe(0.0)
  })
})


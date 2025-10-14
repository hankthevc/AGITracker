import { test, expect } from '@playwright/test'

test.describe('Home Page', () => {
  test('loads and shows composite gauge', async ({ page }) => {
    await page.goto('/')
    
    // Check for main heading
    await expect(page.locator('h1')).toContainText('AGI Signpost Tracker')
    
    // Check for composite gauge
    await expect(page.locator('[data-testid="composite-gauge"]')).toBeVisible()
    
    // Check for safety dial
    await expect(page.locator('[data-testid="safety-dial"]')).toBeVisible()
    
    // Check for preset switcher
    await expect(page.getByText('Equal')).toBeVisible()
    await expect(page.getByText('Aschenbrenner')).toBeVisible()
    await expect(page.getByText('AI-2027')).toBeVisible()
  })
  
  test('preset switcher updates URL and data', async ({ page }) => {
    await page.goto('/')
    
    // Click Aschenbrenner preset
    await page.getByRole('button', { name: 'Aschenbrenner' }).click()
    
    // Check URL updated
    await expect(page).toHaveURL(/\?preset=aschenbrenner/)
    
    // Check that preset is shown
    await expect(page.locator('text=/Preset.*aschenbrenner/i')).toBeVisible()
  })
  
  test('shows category progress lanes', async ({ page }) => {
    await page.goto('/')
    
    // Check for all 4 category lanes
    await expect(page.getByText('Capabilities')).toBeVisible()
    await expect(page.getByText('Agents')).toBeVisible()
    await expect(page.getByText('Inputs')).toBeVisible()
    await expect(page.getByText('Security')).toBeVisible()
  })
})

test.describe('Benchmarks Page', () => {
  test('shows benchmark cards', async ({ page }) => {
    await page.goto('/benchmarks')
    
    // Check page title
    await expect(page.locator('h1')).toContainText('Benchmark Progress')
    
    // Check for benchmark cards
    await expect(page.locator('[data-testid="benchmark-card"]')).toHaveCount(4)
    
    // Check for specific benchmarks
    await expect(page.getByText('SWE-bench Verified')).toBeVisible()
    await expect(page.getByText('OSWorld')).toBeVisible()
    await expect(page.getByText('WebArena')).toBeVisible()
    await expect(page.getByText('GPQA Diamond')).toBeVisible()
  })
})

test.describe('Methodology Page', () => {
  test('shows evidence tiers with badges', async ({ page }) => {
    await page.goto('/methodology')
    
    // Check for evidence tier badges
    await expect(page.getByText('A', { exact: true })).toBeVisible()
    await expect(page.getByText('B', { exact: true })).toBeVisible()
    await expect(page.getByText('C', { exact: true })).toBeVisible()
    await expect(page.getByText('D', { exact: true })).toBeVisible()
    
    // Check for tier descriptions
    await expect(page.getByText('Primary Evidence')).toBeVisible()
    await expect(page.getByText('Official Lab Communications')).toBeVisible()
  })
  
  test('explains scoring algorithm', async ({ page }) => {
    await page.goto('/methodology')
    
    await expect(page.getByText('Scoring Algorithm')).toBeVisible()
    await expect(page.getByText(/harmonic mean/i)).toBeVisible()
  })
})


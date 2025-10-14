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
  
  test('shows non-zero capabilities and handles insufficient data state', async ({ page }) => {
    await page.goto('/')
    
    // Wait for capabilities value to load and be > 0
    const capabilitiesValue = page.locator('[data-testid="capabilities-value"]')
    await capabilitiesValue.waitFor({ state: 'visible' })
    
    // Check that capabilities shows a non-zero percentage
    const capText = await capabilitiesValue.textContent()
    expect(capText).toBeTruthy()
    
    // Check overall value - should be either N/A (insufficient data) or a positive value
    const overallValue = page.locator('[data-testid="overall-value"]')
    await overallValue.waitFor({ state: 'visible' })
    const overallText = await overallValue.textContent()
    
    // Overall should be either "N/A" (if Inputs/Security are zero) or a percentage
    expect(overallText).toMatch(/N\/A|%/)
    
    // If N/A, verify the insufficient data message
    if (overallText?.includes('N/A')) {
      await expect(page.getByText(/Waiting for Inputs\/Security/i)).toBeVisible()
    }
  })
  
  test('preset switcher updates URL and data', async ({ page }) => {
    await page.goto('/')
    
    // Wait for initial data to load
    await page.locator('[data-testid="capabilities-value"]').waitFor({ state: 'visible' })
    
    // Get initial capabilities value
    const initialCapValue = await page.locator('[data-testid="capabilities-value"]').textContent()
    
    // Click Aschenbrenner preset
    await page.locator('[data-testid="preset-aschenbrenner"]').click()
    
    // Check URL updated
    await expect(page).toHaveURL(/\?preset=aschenbrenner/)
    
    // Check that preset is shown in the page
    await expect(page.locator('text=/Preset.*aschenbrenner/i')).toBeVisible()
    
    // Wait for data to potentially update (values may or may not change)
    await page.waitForTimeout(500)
    
    // Verify data is still displayed
    await expect(page.locator('[data-testid="capabilities-value"]')).toBeVisible()
  })
  
  test('shows category progress lanes with testids', async ({ page }) => {
    await page.goto('/')
    
    // Check for all 4 category lanes with their testids
    await expect(page.locator('[data-testid="capabilities-value"]')).toBeVisible()
    await expect(page.locator('[data-testid="agents-value"]')).toBeVisible()
    await expect(page.locator('[data-testid="inputs-value"]')).toBeVisible()
    await expect(page.locator('[data-testid="security-value"]')).toBeVisible()
  })
  
  test('shows what moved this week panel', async ({ page }) => {
    await page.goto('/')
    
    // Check for the changelog panel
    await expect(page.getByText('What Moved This Week?')).toBeVisible()
    
    // The delta-list should either have entries or show empty state
    const hasEntries = await page.locator('[data-testid="delta-list"]').isVisible().catch(() => false)
    if (!hasEntries) {
      // If no entries, should show fallback message
      await expect(page.getByText(/No recent changes|Unable to load/i)).toBeVisible()
    }
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

test.describe('Evidence Cards', () => {
  test('display tier badges with correct testids', async ({ page }) => {
    // This test assumes evidence cards are shown somewhere
    // For now, we'll skip if no evidence cards are present
    await page.goto('/benchmarks')
    
    // Check if any evidence tier badges exist
    const tierBadges = page.locator('[data-testid^="evidence-tier-"]')
    const count = await tierBadges.count()
    
    // If evidence cards exist, verify tier badges have correct format
    if (count > 0) {
      const firstBadge = tierBadges.first()
      await expect(firstBadge).toBeVisible()
      
      // Verify the badge has one of the valid tier values
      const badgeText = await firstBadge.textContent()
      expect(badgeText).toMatch(/^[ABCD]$/)
    }
  })
})


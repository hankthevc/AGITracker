import { test, expect } from '@playwright/test'

const BASE_URL = process.env.PLAYWRIGHT_TEST_BASE_URL || 'http://localhost:3000'

test.describe('Roadmaps Compare Overlay', () => {
  test('toggle appears and can switch ON/OFF', async ({ page }) => {
    await page.goto(`${BASE_URL}/roadmaps/compare`)
    const toggle = page.locator('[data-testid="events-overlay-toggle"]').first()
    await expect(toggle).toBeVisible()
    await expect(toggle).toContainText('Overlay')

    // Turn ON
    await toggle.click()
    await page.waitForURL(/overlay=events/)
    await expect(page.locator('[data-testid="events-overlay-toggle"]').first()).toContainText('ON')

    // Turn OFF
    await page.locator('[data-testid="events-overlay-toggle"]').first().click()
    await expect(page).not.toHaveURL(/overlay=events/)
  })
})

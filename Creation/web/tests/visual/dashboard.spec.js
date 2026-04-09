import { expect, test } from '@playwright/test'

test('dashboard visual baseline', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('.workspace')).toBeVisible()
  await expect(page).toHaveScreenshot('dashboard-home.png', {
    fullPage: true,
    maxDiffPixelRatio: 0.02,
  })
})

const { chromium } = require("playwright");
const path = require("path");

const mockupDir = __dirname;
const htmlPath = path.join(mockupDir, "ad-campaign-dashboard-mockup.html");

const views = [
  ["tab-overview", "overview.png"],
  ["tab-platform", "platform-comparison.png"],
  ["tab-details", "campaign-details.png"],
  ["tab-time", "time-series.png"],
];

(async () => {
  const browser = await chromium.launch({
    channel: "chrome",
    headless: true,
  });
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1100 },
    deviceScaleFactor: 1.5,
    colorScheme: "light",
  });

  await page.goto(`file://${htmlPath}`, { waitUntil: "load" });
  const appFrame = page.frames().find((frame) => frame !== page.mainFrame());
  if (!appFrame) throw new Error("Mockup iframe was not found");

  const dashboard = appFrame.locator("#campaign-ui");
  await dashboard.waitFor({ state: "visible" });

  for (const [tabId, fileName] of views) {
    await appFrame.locator(`#${tabId}`).click();
    await dashboard.screenshot({
      path: path.join(mockupDir, fileName),
      animations: "disabled",
    });
  }

  await browser.close();
})();

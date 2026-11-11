#!/usr/bin/env node
/**
 * Render an already-served print HTML page to an A4 PDF with headless Chrome.
 *
 * Env:
 *   PDF_URL   required  e.g. http://127.0.0.1:8765/print-pdf.html
 *   PDF_OUT   required  output path
 *   CHROME    required  path to Chrome / Chromium
 *   NODE_PATH should include puppeteer-core (installed by build-pdf.sh)
 */
const puppeteer = require("puppeteer-core");

(async () => {
  const url = process.env.PDF_URL;
  const out = process.env.PDF_OUT;
  const chrome = process.env.CHROME;
  if (!url || !out || !chrome) {
    console.error("PDF_URL, PDF_OUT, and CHROME are required");
    process.exit(1);
  }

  const browser = await puppeteer.launch({
    executablePath: chrome,
    headless: true,
    args: [
      "--no-sandbox",
      "--disable-setuid-sandbox",
      "--disable-dev-shm-usage",
      "--disable-gpu",
      "--font-render-hinting=medium",
      "--disable-lcd-text",
      "--hide-scrollbars",
    ],
  });

  try {
    const page = await browser.newPage();
    page.setDefaultTimeout(300000);
    const resp = await page.goto(url, {
      waitUntil: "networkidle0",
      timeout: 300000,
    });
    const status = resp && resp.status();
    if (!status || status >= 400) {
      throw new Error(`Failed to load ${url} (HTTP ${status})`);
    }

    const stats = await page.evaluate(async () => {
      await document.fonts.ready;
      const imgs = [...document.images];
      await Promise.all(
        imgs.map((img) => {
          if (img.complete && img.naturalWidth > 0) return null;
          return new Promise((resolve) => {
            const done = () => resolve(null);
            img.addEventListener("load", done, { once: true });
            img.addEventListener("error", done, { once: true });
          });
        })
      );
      const failed = imgs
        .filter((i) => !i.complete || i.naturalWidth === 0)
        .map((i) => i.src);
      return {
        title: document.title,
        imgs: imgs.length,
        failed: failed.length,
        failedSrc: failed.slice(0, 8),
        font: getComputedStyle(document.body).fontFamily,
      };
    });

    console.log("print-to-pdf:", JSON.stringify(stats));
    if (stats.failed) {
      console.warn(
        `warning: ${stats.failed} image(s) failed to load`,
        stats.failedSrc
      );
    }

    await page.pdf({
      path: out,
      format: "A4",
      printBackground: true,
      displayHeaderFooter: false,
      margin: { top: "14mm", bottom: "16mm", left: "14mm", right: "14mm" },
      preferCSSPageSize: true,
      timeout: 300000,
    });
    console.log("wrote", out);
  } finally {
    await browser.close();
  }
})().catch((err) => {
  console.error(err);
  process.exit(1);
});

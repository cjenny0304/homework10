'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL, fileURLToPath} = require('node:url');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');

async function exercise(browser, viewport, mobile = false) {
  const page = await browser.newPage({viewport, isMobile: mobile, hasTouch: mobile, reducedMotion: 'reduce', offline: !process.env.LESSON_URL});
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.message));
  const entry = pathToFileURL(path.resolve(__dirname, '../slides.html'));
  if (process.env.LESSON_URL) {
    const localOrigin = new URL(process.env.LESSON_URL).origin;
    await page.route('**/*', (route) => new URL(route.request().url()).origin === localOrigin ? route.continue() : route.abort());
  }
  await page.goto(process.env.LESSON_URL || entry.href);
  const slides = page.locator('.slide');
  const position = page.locator('#position');
  const progress = page.locator('#progress');
  const previous = page.locator('#previous');
  const next = page.locator('#next');
  assert.equal(await slides.count(), 11);
  assert.equal(await previous.isDisabled(), true);
  if (!mobile) {
    await page.keyboard.press('ArrowRight');
    assert.equal(await position.innerText(), '02 / 11');
    await page.keyboard.press('ArrowLeft');
    assert.equal(await position.innerText(), '01 / 11');
  }
  for (let i = 0; i < 11; i++) {
    const slide = slides.nth(i);
    assert.equal(await page.locator('.slide:visible').count(), 1);
    assert.equal(await slide.isVisible(), true);
    assert.equal(await position.innerText(), String(i + 1).padStart(2, '0') + ' / 11');
    assert.equal(await progress.evaluate((el) => el.value), i + 1);
    const sources = slide.locator('.sources');
    assert.match(await sources.locator('summary').innerText(), /S0[1-7]/);
    await sources.locator('summary').click();
    for (const link of await sources.locator('a').evaluateAll((items) => items.map((a) => a.href))) {
      if (link.startsWith('file:')) assert.equal(fs.existsSync(fileURLToPath(link)), true, link);
      if (process.env.LESSON_URL && new URL(link).origin === new URL(process.env.LESSON_URL).origin) {
        assert.equal((await page.request.get(link)).ok(), true, link);
      }
    }
    for (const img of await slide.locator('img').all()) {
      assert.equal(await img.evaluate((el) => el.complete && el.naturalWidth > 0), true);
      assert.equal(await img.evaluate((el) => {
        const box = el.getBoundingClientRect();
        return Math.abs(box.width / box.height - el.naturalWidth / el.naturalHeight) < 0.02;
      }), true, `page ${i + 1}: distorted illustration`);
    }
    const overflow = await slide.evaluate((el) => {
      const left = 0;
      const right = document.documentElement.clientWidth;
      return document.documentElement.scrollWidth > right || [...el.querySelectorAll('*')].some((node) => {
        const box = node.getBoundingClientRect();
        const visible = node.getClientRects().length > 0;
        return visible && (box.left < left - 1 || box.right > right + 1);
      });
    });
    assert.equal(overflow, false, `page ${i + 1} horizontal overflow`);
    await sources.locator('summary').click();
    if (i === 6) {
      const guess = slide.locator('.guess button');
      await guess.nth(1).click();
      assert.match(await slide.locator('.feedback').innerText(), /擔憂/);
      await guess.nth(0).click();
      assert.match(await slide.locator('.feedback').innerText(), /答對/);
    }
    if (i === 8) {
      for (const card of await slide.locator('.flip').all()) {
        await card.click();
        assert.equal(await card.locator('.back').isVisible(), true);
        await card.click();
        assert.equal(await card.locator('.back').isVisible(), false);
      }
    }
    if (i === 10) {
      const questions = slide.locator('.question');
      await questions.nth(0).locator('.answer').nth(0).click();
      assert.match(await questions.nth(0).locator('.feedback').innerText(), /再想/);
      for (const [q, choice] of [1, 2, 0].entries()) {
        await questions.nth(q).locator('.answer').nth(choice).click();
        assert.match(await questions.nth(q).locator('.feedback').innerText(), /答對/);
      }
      assert.equal(await slide.locator('#score').innerText(), '答對 3 / 3 題');
      await slide.locator('#reset').click();
      assert.equal(await slide.locator('#score').innerText(), '已作答 0 / 3 題');
    }
    if (process.env.LESSON_SCREENSHOTS && [0, 6, 10].includes(i)) {
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.screenshot({path: path.join(process.env.LESSON_SCREENSHOTS, `${viewport.width}-${i+1}.png`), fullPage: true});
    }
    if (i < 10) await next.click();
  }
  assert.equal(await next.isDisabled(), true);
  await previous.click();
  assert.equal(await position.innerText(), '10 / 11');
  assert.deepEqual(errors, []);
  console.log(`PASS ${viewport.width}×${viewport.height}: all 11 pages and source panels, local files/images and aspect ratio, navigation, guess, 3 flip cards, 3 questions, scoring, reset, no horizontal overflow or JS errors`);
  await page.close();
}

(async () => {
  const browser = await chromium.launch({executablePath: process.env.CHROMIUM_PATH || undefined, args: ['--no-sandbox']});
  try {
    console.log(`Chromium ${browser.version()}, ${process.env.LESSON_URL ? 'loopback HTTP, external requests blocked' : 'offline file://'}`);
    await exercise(browser, {width: 1440, height: 900});
    await exercise(browser, {width: 390, height: 844}, true);
    await exercise(browser, {width: 320, height: 640}, true);
  } finally {
    await browser.close();
  }
})().catch((error) => { console.error(error); process.exitCode = 1; });

import puppeteer from 'puppeteer';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const url = process.argv[2] || 'http://localhost:3000';
const scrollY = parseInt(process.argv[3] || '0', 10);
const width = parseInt(process.argv[4] || '1440', 10);
const label = process.argv[5] ? `-${process.argv[5]}` : '';

const dir = path.join(__dirname, 'temporary screenshots');
const existing = fs.readdirSync(dir).filter(f => f.startsWith('screenshot-') && f.endsWith('.png'));
const nums = existing.map(f => parseInt(f.match(/screenshot-(\d+)/)?.[1] || '0')).filter(n => !isNaN(n));
const next = nums.length ? Math.max(...nums) + 1 : 1;
const filename = `screenshot-${next}${label}.png`;
const outPath = path.join(dir, filename);

const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox'] });
const page = await browser.newPage();
await page.setViewport({ width, height: 900 });
await page.goto(url, { waitUntil: 'networkidle2', timeout: 45000 });
await page.evaluate(y => window.scrollTo(0, y), scrollY);
await new Promise(r => setTimeout(r, 700));
await page.screenshot({ path: outPath });
await browser.close();
console.log(`Screenshot saved: temporary screenshots/${filename}`);

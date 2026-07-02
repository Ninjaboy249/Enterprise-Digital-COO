#!/usr/bin/env node
/**
 * health-check.js
 * Pings the Enterprise Digital COO FastAPI server and prints a status report.
 * Usage: node health-check.js [--host http://localhost:8000]
 *
 * Does NOT modify any backend code or UI.
 */

import fetch from "node-fetch";
import chalk from "chalk";

// ── Config ───────────────────────────────────────────────────────────────────
const args = process.argv.slice(2);
const hostFlag = args.indexOf("--host");
const BASE_URL =
  hostFlag !== -1 ? args[hostFlag + 1] : "http://localhost:8000";

const ENDPOINTS = [
  { label: "Root", path: "/" },
  { label: "Health", path: "/health" },
  { label: "API v1 Metrics", path: "/api/v1/metrics/health" },
  { label: "API v1 Reports", path: "/api/v1/reports/health" },
];

const TIMEOUT_MS = 5000;

// ── Helpers ───────────────────────────────────────────────────────────────────
function statusBadge(ok, code) {
  if (ok) return chalk.bgGreen.black(` ${code} OK `);
  if (code >= 500) return chalk.bgRed.white(` ${code} ERROR `);
  if (code >= 400) return chalk.bgYellow.black(` ${code} CLIENT ERR `);
  return chalk.bgGray.white(` ${code} `);
}

async function checkEndpoint({ label, path }) {
  const url = `${BASE_URL}${path}`;
  const start = Date.now();
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
    const res = await fetch(url, { signal: controller.signal });
    clearTimeout(timer);
    const ms = Date.now() - start;
    return {
      label,
      url,
      ok: res.ok,
      status: res.status,
      ms,
      error: null,
    };
  } catch (err) {
    return {
      label,
      url,
      ok: false,
      status: err.name === "AbortError" ? "TIMEOUT" : "UNREACHABLE",
      ms: Date.now() - start,
      error: err.name === "AbortError" ? `Timed out after ${TIMEOUT_MS}ms` : err.message,
    };
  }
}

// ── Main ─────────────────────────────────────────────────────────────────────
console.log(chalk.bold("\n🔍  Enterprise Digital COO — Health Check"));
console.log(chalk.dim(`    Target: ${BASE_URL}\n`));

const results = await Promise.all(ENDPOINTS.map(checkEndpoint));

let allOk = true;
for (const r of results) {
  const badge =
    typeof r.status === "number"
      ? statusBadge(r.ok, r.status)
      : chalk.bgRed.white(` ${r.status} `);
  const latency = chalk.dim(`${r.ms}ms`);
  const label = r.ok
    ? chalk.green(r.label.padEnd(22))
    : chalk.red(r.label.padEnd(22));
  const detail = r.error ? chalk.dim(`  ← ${r.error}`) : "";
  console.log(`  ${badge}  ${label}  ${latency}${detail}`);
  if (!r.ok) allOk = false;
}

console.log();
if (allOk) {
  console.log(chalk.green.bold("  ✅  All endpoints healthy\n"));
} else {
  console.log(chalk.red.bold("  ❌  Some endpoints are unhealthy\n"));
  process.exit(1);
}

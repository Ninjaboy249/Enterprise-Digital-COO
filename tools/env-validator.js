#!/usr/bin/env node
/**
 * env-validator.js
 * Reads backend/.env.example and checks that every required key exists
 * in backend/.env (or the process environment).
 *
 * Usage: node env-validator.js
 *
 * Does NOT modify any backend code or UI.
 */

import { readFileSync, existsSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
import chalk from "chalk";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, "..");
const EXAMPLE_PATH = resolve(ROOT, "backend", ".env.example");
const ENV_PATH = resolve(ROOT, "backend", ".env");

// ── Parse a .env-style file into a Map of key → value ────────────────────────
function parseEnvFile(filePath) {
  const map = new Map();
  if (!existsSync(filePath)) return map;
  const lines = readFileSync(filePath, "utf8").split("\n");
  for (const raw of lines) {
    const line = raw.trim();
    if (!line || line.startsWith("#")) continue;
    const eqIdx = line.indexOf("=");
    if (eqIdx === -1) continue;
    const key = line.slice(0, eqIdx).trim();
    const val = line.slice(eqIdx + 1).trim();
    if (key) map.set(key, val);
  }
  return map;
}

// ── Keys that are intentionally optional (blank in .env.example is fine) ──────
const OPTIONAL_KEYS = new Set([
  "REDIS_PASSWORD",
  "LANGCHAIN_API_KEY",
  "LANGCHAIN_TRACING_V2",
]);

// ── Main ──────────────────────────────────────────────────────────────────────
console.log(chalk.bold("\n🔐  Enterprise Digital COO — Env Validator\n"));

if (!existsSync(EXAMPLE_PATH)) {
  console.error(chalk.red(`  ✖  Cannot find ${EXAMPLE_PATH}`));
  process.exit(1);
}

const example = parseEnvFile(EXAMPLE_PATH);
const env = parseEnvFile(ENV_PATH);

// Merge with process.env so CI injected vars count too
const effectiveEnv = new Map([...env]);
for (const [k, v] of Object.entries(process.env)) {
  effectiveEnv.set(k, v);
}

let missing = 0;
let placeholder = 0;
let ok = 0;

for (const [key] of example) {
  const value = effectiveEnv.get(key);
  const isOptional = OPTIONAL_KEYS.has(key);

  if (value === undefined || value === "") {
    if (isOptional) {
      console.log(`  ${chalk.dim("–")}  ${chalk.dim(key.padEnd(35))} ${chalk.dim("(optional, skipped)")}`);
    } else {
      console.log(`  ${chalk.red("✖")}  ${chalk.red(key.padEnd(35))} ${chalk.red("MISSING")}`);
      missing++;
    }
  } else if (value.startsWith("your-") || value === "change-in-production") {
    console.log(`  ${chalk.yellow("⚠")}  ${chalk.yellow(key.padEnd(35))} ${chalk.yellow("still a placeholder value")}`);
    placeholder++;
  } else {
    console.log(`  ${chalk.green("✔")}  ${chalk.green(key.padEnd(35))} ${chalk.dim("set")}`);
    ok++;
  }
}

console.log();
console.log(chalk.dim(`  Checked ${example.size} keys — `) +
  chalk.green(`${ok} ok`) + chalk.dim(", ") +
  chalk.yellow(`${placeholder} placeholder`) + chalk.dim(", ") +
  (missing > 0 ? chalk.red(`${missing} missing`) : chalk.green("0 missing")) +
  "\n");

if (missing > 0) {
  console.log(chalk.red.bold(`  ❌  Fix the ${missing} missing key(s) before starting the server.\n`));
  process.exit(1);
} else {
  console.log(chalk.green.bold("  ✅  All required env vars are present.\n"));
}

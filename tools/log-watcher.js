#!/usr/bin/env node
/**
 * log-watcher.js
 * Tails a log file (or stdin) and pretty-prints new JSON log lines produced
 * by the FastAPI backend (python-json-logger format).  Falls back to raw
 * line output for non-JSON lines.
 *
 * Usage:
 *   node log-watcher.js                          # watches ./app.log by default
 *   node log-watcher.js --file /path/to/app.log
 *   cat app.log | node log-watcher.js --stdin
 *
 * Does NOT modify any backend code or UI.
 */

import { createReadStream, statSync, existsSync, watchFile } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
import { createInterface } from "readline";
import chalk from "chalk";

const __dirname = dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);

// ── Config ────────────────────────────────────────────────────────────────────
const useStdin = args.includes("--stdin");
const fileFlag = args.indexOf("--file");
const LOG_FILE =
  fileFlag !== -1
    ? resolve(args[fileFlag + 1])
    : resolve(__dirname, "..", "backend", "app.log");

// ── Level colours ─────────────────────────────────────────────────────────────
const LEVEL_FMT = {
  DEBUG:    (s) => chalk.gray(s),
  INFO:     (s) => chalk.cyan(s),
  WARNING:  (s) => chalk.yellow(s),
  ERROR:    (s) => chalk.red(s),
  CRITICAL: (s) => chalk.bgRed.white(s),
};

function fmtLevel(level = "INFO") {
  const key = level.toUpperCase();
  const fmt = LEVEL_FMT[key] ?? ((s) => s);
  return fmt(key.padEnd(8));
}

function fmtTime(ts) {
  if (!ts) return chalk.dim("(no time)       ");
  try {
    const d = new Date(ts);
    return chalk.dim(d.toLocaleTimeString("en-GB", { hour12: false }) + "." +
      String(d.getMilliseconds()).padStart(3, "0"));
  } catch {
    return chalk.dim(ts.slice(0, 15));
  }
}

// ── Format a single log line ──────────────────────────────────────────────────
function formatLine(raw) {
  const trimmed = raw.trim();
  if (!trimmed) return null;

  // Try JSON (python-json-logger)
  if (trimmed.startsWith("{")) {
    try {
      const obj = JSON.parse(trimmed);
      const time = fmtTime(obj.timestamp ?? obj.asctime ?? obj.time);
      const level = fmtLevel(obj.levelname ?? obj.level ?? obj.severity);
      const name = obj.name ? chalk.magenta(`[${obj.name}]`) : "";
      const msg = obj.message ?? obj.msg ?? "";
      const extras = Object.entries(obj)
        .filter(([k]) => !["timestamp","asctime","time","levelname","level","severity","name","message","msg"].includes(k))
        .map(([k, v]) => `${chalk.dim(k + "=")}${chalk.white(JSON.stringify(v))}`)
        .join(" ");
      return `${time}  ${level}  ${name}  ${chalk.white(msg)}${extras ? "  " + extras : ""}`;
    } catch {
      // not valid JSON — fall through
    }
  }

  // Plain text — look for embedded level keywords
  const upper = trimmed.toUpperCase();
  if (upper.includes("ERROR") || upper.includes("CRITICAL")) return chalk.red(trimmed);
  if (upper.includes("WARNING") || upper.includes("WARN"))   return chalk.yellow(trimmed);
  if (upper.includes("DEBUG"))                               return chalk.gray(trimmed);
  return trimmed;
}

// ── Stream handler ────────────────────────────────────────────────────────────
function processStream(stream) {
  const rl = createInterface({ input: stream, crlfDelay: Infinity });
  rl.on("line", (line) => {
    const out = formatLine(line);
    if (out) console.log(out);
  });
}

// ── Main ──────────────────────────────────────────────────────────────────────
if (useStdin) {
  console.log(chalk.bold("\n📋  Enterprise Digital COO — Log Watcher (stdin)\n"));
  processStream(process.stdin);
} else {
  if (!existsSync(LOG_FILE)) {
    console.log(chalk.yellow(`\n⚠  Log file not found: ${LOG_FILE}`));
    console.log(chalk.dim("   Waiting for it to be created...\n"));
  } else {
    console.log(chalk.bold(`\n📋  Enterprise Digital COO — Log Watcher`));
    console.log(chalk.dim(`    File: ${LOG_FILE}\n`));
    // Print existing content first
    processStream(createReadStream(LOG_FILE, { encoding: "utf8" }));
  }

  // Watch for new content
  let lastSize = existsSync(LOG_FILE) ? statSync(LOG_FILE).size : 0;
  watchFile(LOG_FILE, { interval: 500 }, (curr) => {
    if (curr.size > lastSize) {
      const stream = createReadStream(LOG_FILE, { encoding: "utf8", start: lastSize });
      lastSize = curr.size;
      processStream(stream);
    }
  });

  process.on("SIGINT", () => {
    console.log(chalk.dim("\n\n  Stopped watching. Goodbye.\n"));
    process.exit(0);
  });
}

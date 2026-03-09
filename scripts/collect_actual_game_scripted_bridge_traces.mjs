#!/usr/bin/env node

import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const REPO_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function resolveGameRepoRoot() {
  const candidates = [
    process.env.GAME_REPO_ROOT,
    path.resolve(REPO_ROOT, "..", "tower-defence-origin-main-clean"),
    path.resolve(REPO_ROOT, "..", "tower-defence"),
  ];
  for (const candidate of candidates) {
    const normalized = typeof candidate === "string" ? candidate.trim() : "";
    if (!normalized) {
      continue;
    }
    if (fs.existsSync(normalized)) {
      return path.resolve(normalized);
    }
  }
  return path.resolve(REPO_ROOT, "..", "tower-defence");
}

const GAME_REPO_ROOT = resolveGameRepoRoot();
const DEFAULT_OUT_DIR = path.join(
  REPO_ROOT,
  "artifacts",
  "x526_actual_game_scripted_bridge_traces"
);
const DEFAULT_SEED_SPEC = "11,17,23,29,31";
const DEFAULT_ADAPTER_ID = "codex";
const DEFAULT_MAX_DECISIONS = 30;
const DEFAULT_STEP_TICKS = 30;
const DEFAULT_DECISION_TIMEOUT_MS = 1200;
const DEFAULT_OWNER_ID = "owner";
const DEFAULT_LLM_PLAYER_ID = "bot-bridge";
const BRIDGE_INPUT_VERSION = "td.multiplayer.llm-bridge.input.v1";
const GAMEPLAY_COMMAND_TYPES = [
  "place_tower",
  "sell_tower",
  "upgrade_tower",
  "trigger_next_round",
];

function normalizeNonEmptyString(value, fallback = "") {
  return typeof value === "string" && value.trim() ? value.trim() : fallback;
}

function normalizePositiveInteger(value, fallback) {
  const parsed = Number.parseInt(String(value ?? ""), 10);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : fallback;
}

function ensureDirectoryFor(filePath) {
  fs.mkdirSync(path.dirname(path.resolve(filePath)), { recursive: true });
}

function writeJsonFile(filePath, payload) {
  ensureDirectoryFor(filePath);
  fs.writeFileSync(filePath, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
}

function toRelativePath(targetPath) {
  const relative = path.relative(REPO_ROOT, path.resolve(targetPath));
  return relative || path.basename(targetPath);
}

function parseSeedSpec(rawSeedSpec = DEFAULT_SEED_SPEC) {
  if (typeof rawSeedSpec !== "string" || !rawSeedSpec.trim()) {
    throw new Error("Seed spec must be a non-empty string");
  }
  const normalized = rawSeedSpec.trim();
  if (normalized.includes(":")) {
    const [rawStart, rawEnd] = normalized.split(":");
    if (!rawStart || !rawEnd) {
      throw new Error(`Invalid seed range: ${rawSeedSpec}`);
    }
    const start = Number.parseInt(rawStart, 10);
    const end = Number.parseInt(rawEnd, 10);
    if (!Number.isInteger(start) || start < 0 || !Number.isInteger(end) || end < 0) {
      throw new Error(`Invalid seed range: ${rawSeedSpec}`);
    }
    const step = start <= end ? 1 : -1;
    const seeds = [];
    for (let seed = start; step > 0 ? seed <= end : seed >= end; seed += step) {
      seeds.push(seed);
    }
    return seeds;
  }
  return normalized
    .split(",")
    .map((entry) => Number.parseInt(entry.trim(), 10))
    .filter((entry) => Number.isInteger(entry) && entry >= 0);
}

function parseArgs(argv) {
  const options = {
    outDir: DEFAULT_OUT_DIR,
    seeds: DEFAULT_SEED_SPEC,
    adapterId: DEFAULT_ADAPTER_ID,
    maxDecisions: DEFAULT_MAX_DECISIONS,
    stepTicks: DEFAULT_STEP_TICKS,
    decisionTimeoutMs: DEFAULT_DECISION_TIMEOUT_MS,
    ownerId: DEFAULT_OWNER_ID,
    llmPlayerId: DEFAULT_LLM_PLAYER_ID,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--out-dir") {
      options.outDir = path.resolve(REPO_ROOT, normalizeNonEmptyString(argv[index + 1], options.outDir));
      index += 1;
    } else if (token === "--seeds") {
      options.seeds = normalizeNonEmptyString(argv[index + 1], options.seeds);
      index += 1;
    } else if (token === "--adapter-id") {
      options.adapterId = normalizeNonEmptyString(argv[index + 1], options.adapterId);
      index += 1;
    } else if (token === "--max-decisions") {
      options.maxDecisions = normalizePositiveInteger(argv[index + 1], options.maxDecisions);
      index += 1;
    } else if (token === "--step-ticks") {
      options.stepTicks = normalizePositiveInteger(argv[index + 1], options.stepTicks);
      index += 1;
    } else if (token === "--decision-timeout-ms") {
      options.decisionTimeoutMs = normalizePositiveInteger(argv[index + 1], options.decisionTimeoutMs);
      index += 1;
    } else if (token === "--owner-id") {
      options.ownerId = normalizeNonEmptyString(argv[index + 1], options.ownerId);
      index += 1;
    } else if (token === "--llm-player-id") {
      options.llmPlayerId = normalizeNonEmptyString(argv[index + 1], options.llmPlayerId);
      index += 1;
    } else if (token === "--help" || token === "-h") {
      process.stdout.write(
        [
          "Usage: node scripts/collect_actual_game_scripted_bridge_traces.mjs [options]",
          "",
          "Options:",
          `  --out-dir <path>             Output directory (default ${toRelativePath(DEFAULT_OUT_DIR)})`,
          `  --seeds <spec>               Seed spec, e.g. 11,17,23 or 11:31 (default ${DEFAULT_SEED_SPEC})`,
          `  --adapter-id <id>            Bridge adapter fallback policy to use (default ${DEFAULT_ADAPTER_ID})`,
          `  --max-decisions <n>          Max decisions per run (default ${DEFAULT_MAX_DECISIONS})`,
          `  --step-ticks <n>             Step ticks per decision (default ${DEFAULT_STEP_TICKS})`,
          `  --decision-timeout-ms <n>    Adapter timeout budget (default ${DEFAULT_DECISION_TIMEOUT_MS})`,
          `  --owner-id <id>              Owner player id (default ${DEFAULT_OWNER_ID})`,
          `  --llm-player-id <id>         LLM slot player id (default ${DEFAULT_LLM_PLAYER_ID})`,
        ].join("\n") + "\n"
      );
      process.exit(0);
    } else {
      throw new Error(`Unknown option: ${token}`);
    }
  }

  const parsedSeeds = parseSeedSpec(options.seeds);
  if (parsedSeeds.length === 0) {
    throw new Error(`No valid seeds parsed from: ${options.seeds}`);
  }
  return {
    ...options,
    parsedSeeds,
  };
}

function listen(server) {
  return new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", () => {
      server.removeListener("error", reject);
      const address = server.address();
      if (!address || typeof address !== "object") {
        reject(new Error("Unable to resolve ephemeral server port"));
        return;
      }
      resolve(address.port);
    });
  });
}

function closeServer(server) {
  return new Promise((resolve) => {
    if (!server || typeof server.close !== "function") {
      resolve();
      return;
    }
    server.close(() => resolve());
  });
}

function normalizeForArtifact(value) {
  if (!value || typeof value !== "object") {
    return value;
  }
  return JSON.parse(JSON.stringify(value));
}

function hasRequiredProvenance(entry, adapterId) {
  const provenance = entry?.command?.provenance;
  return (
    provenance
    && provenance.source === "llm_adapter"
    && provenance.adapterId === adapterId
    && typeof provenance.requestId === "string"
    && provenance.requestId.trim().length > 0
  );
}

async function loadGameModules() {
  const importFromGame = async (relativePath) =>
    import(pathToFileURL(path.join(GAME_REPO_ROOT, relativePath)).href);
  const [{ createMultiplayerSession }, { createMultiplayerWebSocketServer }, { createWebSocketMultiplayerTransport }, { runLlmBridgeSession }, { createBridgeAdapter }] =
    await Promise.all([
      importFromGame("src/sim/multiplayer-session.js"),
      importFromGame("src/adapters/multiplayer-websocket-server.js"),
      importFromGame("src/adapters/multiplayer-websocket.js"),
      importFromGame("src/adapters/llm-bridge/bridge-runner.js"),
      importFromGame("src/adapters/llm-bridge/adapter-registry.js"),
    ]);
  return {
    createMultiplayerSession,
    createMultiplayerWebSocketServer,
    createWebSocketMultiplayerTransport,
    runLlmBridgeSession,
    createBridgeAdapter,
  };
}

function summarizeRun({
  seed,
  adapterId,
  modelId,
  decisions,
  llmCommandLog,
  finalPoll,
  addLlmResult,
  maxDecisions,
  stepTicks,
  decisionTimeoutMs,
  outDir,
}) {
  const coverageByType = Object.fromEntries(
    GAMEPLAY_COMMAND_TYPES.map((commandType) => [
      commandType,
      Array.isArray(llmCommandLog)
        ? llmCommandLog.some((entry) => entry?.command?.type === commandType)
        : false,
    ])
  );
  const observed = GAMEPLAY_COMMAND_TYPES.filter((commandType) => coverageByType[commandType]);
  const successfulCommandCount = Array.isArray(llmCommandLog)
    ? llmCommandLog.filter((entry) => entry?.result?.success === true).length
    : 0;
  const decisionsEmitted = Array.isArray(decisions) && decisions.length > 0;
  const summary = {
    artifact_version: "td.actual_game.scripted_bridge_trace_run.v1",
    generated_at_utc: new Date().toISOString(),
    seed,
    adapter_id: adapterId,
    model_id: modelId,
    status: decisionsEmitted && successfulCommandCount > 0 ? "pass" : "fail",
    checks: {
      llm_slot_added: Boolean(addLlmResult?.success),
      bridge_decisions_emitted: decisionsEmitted,
      llm_provenance_command_log: Array.isArray(llmCommandLog)
        ? llmCommandLog.some((entry) => hasRequiredProvenance(entry, adapterId))
        : false,
      accepted_llm_command: successfulCommandCount > 0,
      bridge_input_version_ok: Array.isArray(decisions)
        ? decisions.every((entry) => entry?.input?.version === BRIDGE_INPUT_VERSION)
        : false,
    },
    coverage: {
      required: GAMEPLAY_COMMAND_TYPES,
      by_type: coverageByType,
      observed,
    },
    run: {
      max_decisions: maxDecisions,
      step_ticks: stepTicks,
      decision_timeout_ms: decisionTimeoutMs,
      decision_count: Array.isArray(decisions) ? decisions.length : 0,
      llm_command_count: Array.isArray(llmCommandLog) ? llmCommandLog.length : 0,
      successful_llm_command_count: successfulCommandCount,
      final_round: finalPoll?.state?.round ?? null,
      final_status: finalPoll?.state?.status ?? null,
      final_lives: finalPoll?.state?.lives ?? null,
      final_cash: finalPoll?.economy?.players?.["bot-bridge"]?.cash ?? null,
    },
    artifact_paths: {
      summary: toRelativePath(path.join(outDir, "summary.json")),
      decisions: toRelativePath(path.join(outDir, "bridge-decisions.json")),
      llm_command_log: toRelativePath(path.join(outDir, "llm-command-log.json")),
    },
  };
  return summary;
}

async function collectRun(modules, options, seed) {
  const {
    createMultiplayerSession,
    createMultiplayerWebSocketServer,
    createWebSocketMultiplayerTransport,
    runLlmBridgeSession,
    createBridgeAdapter,
  } = modules;

  const runDir = path.join(options.outDir, `${options.adapterId}-seed-${seed}`);
  const wsHttpServer = http.createServer((req, res) => {
    res.statusCode = 404;
    res.end();
  });

  const session = createMultiplayerSession({
    width: 960,
    height: 540,
    seed,
    commandLeadTicks: 1,
  });
  const wsServer = createMultiplayerWebSocketServer({
    server: wsHttpServer,
    path: "/multiplayer",
    session,
    autoStepMs: 0,
    lobbyId: "default",
    maxPlayers: 4,
  });

  let transport = null;
  try {
    const port = await listen(wsHttpServer);
    const wsUrl = `ws://127.0.0.1:${port}/multiplayer`;
    transport = createWebSocketMultiplayerTransport({
      url: wsUrl,
      createSocket(targetUrl) {
        return new WebSocket(targetUrl);
      },
      requestTimeoutMs: 2500,
    });

    const modelId = `${options.adapterId}-scripted-seed-${seed}`;
    const adapter = createBridgeAdapter({
      adapterId: options.adapterId,
      modelId,
      requestTimeoutMs: options.decisionTimeoutMs,
    });

    const bridgeResult = await runLlmBridgeSession({
      transport,
      ownerId: options.ownerId,
      llmPlayerId: options.llmPlayerId,
      adapterId: options.adapterId,
      modelId,
      adapter,
      maxDecisions: options.maxDecisions,
      stepTicksPerDecision: options.stepTicks,
      decisionTimeoutMs: options.decisionTimeoutMs,
    });

    const summary = summarizeRun({
      seed,
      adapterId: options.adapterId,
      modelId,
      decisions: bridgeResult?.decisions || [],
      llmCommandLog: bridgeResult?.llmCommandLog || [],
      finalPoll: bridgeResult?.finalPoll || {},
      addLlmResult: bridgeResult?.addLlmResult || {},
      maxDecisions: options.maxDecisions,
      stepTicks: options.stepTicks,
      decisionTimeoutMs: options.decisionTimeoutMs,
      outDir: runDir,
    });

    writeJsonFile(path.join(runDir, "bridge-decisions.json"), normalizeForArtifact(bridgeResult?.decisions || []));
    writeJsonFile(path.join(runDir, "llm-command-log.json"), normalizeForArtifact(bridgeResult?.llmCommandLog || []));
    writeJsonFile(path.join(runDir, "summary.json"), summary);
    return summary;
  } finally {
    if (transport && typeof transport.close === "function") {
      transport.close();
    }
    if (wsServer && typeof wsServer.close === "function") {
      await wsServer.close({ closeHttpServer: true });
    } else {
      await closeServer(wsHttpServer);
    }
  }
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  fs.mkdirSync(options.outDir, { recursive: true });
  const modules = await loadGameModules();
  const runs = [];
  for (const seed of options.parsedSeeds) {
    const runSummary = await collectRun(modules, options, seed);
    runs.push(runSummary);
  }

  const manifest = {
    artifact_version: "td.actual_game.scripted_bridge_trace_manifest.v1",
    generated_at_utc: new Date().toISOString(),
    source_repo: path.relative(REPO_ROOT, GAME_REPO_ROOT),
    adapter_id: options.adapterId,
    seed_spec: options.seeds,
    seeds: options.parsedSeeds,
    max_decisions: options.maxDecisions,
    step_ticks: options.stepTicks,
    decision_timeout_ms: options.decisionTimeoutMs,
    run_count: runs.length,
    pass_count: runs.filter((entry) => entry.status === "pass").length,
    observed_command_types_union: GAMEPLAY_COMMAND_TYPES.filter((commandType) =>
      runs.some((entry) => entry.coverage?.by_type?.[commandType] === true)
    ),
    run_summaries: runs,
  };

  const manifestPath = path.join(options.outDir, "manifest.json");
  writeJsonFile(manifestPath, manifest);
  process.stdout.write(`${JSON.stringify({
    manifest_path: toRelativePath(manifestPath),
    run_count: manifest.run_count,
    pass_count: manifest.pass_count,
    observed_command_types_union: manifest.observed_command_types_union,
  }, null, 2)}\n`);
  if (manifest.pass_count !== manifest.run_count) {
    process.exitCode = 1;
  }
}

main().catch((error) => {
  process.stderr.write(`${error?.stack || error?.message || String(error)}\n`);
  process.exitCode = 1;
});

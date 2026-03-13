#!/usr/bin/env node

import fs from "node:fs";
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
    const normalized = normalizeNonEmptyString(candidate);
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
const DEFAULT_OUTPUT_DIR = path.join(REPO_ROOT, "artifacts", "x572_actual_game_teacher_relabels");
const DEFAULT_REPORT_PATH = path.join(DEFAULT_OUTPUT_DIR, "relabel_report.json");
const DEFAULT_TEACHER_MODE = "hybrid-opening";
const SUPPORTED_TEACHER_MODES = new Set(["codex-safe", "deterministic", "hybrid-opening"]);
const COMMAND_SEQUENCE = ["place_tower", "upgrade_tower", "sell_tower", "trigger_next_round"];
const SUMMARY_SAFE_PLACEMENTS = [
  { x: 60, y: 60 },
  { x: 336, y: 64 },
  { x: 432, y: 64 },
  { x: 336, y: 152 },
  { x: 432, y: 152 },
  { x: 336, y: 230 },
  { x: 336, y: 310 },
  { x: 600, y: 150 },
  { x: 632, y: 228 },
  { x: 714, y: 312 },
  { x: 900, y: 180 },
  { x: 900, y: 300 },
  { x: 630, y: 499 },
  { x: 760, y: 500 },
  { x: 900, y: 500 },
];

function normalizeNonEmptyString(value, fallback = "") {
  return typeof value === "string" && value.trim() ? value.trim() : fallback;
}

function normalizeAllowedCommands(value) {
  const next = new Set();
  if (Array.isArray(value)) {
    for (const entry of value) {
      const normalized = normalizeNonEmptyString(entry).toLowerCase();
      if (normalized) {
        next.add(normalized);
      }
    }
  }
  if (next.size === 0) {
    return new Set(COMMAND_SEQUENCE);
  }
  return next;
}

function getPlayerCash(input = {}) {
  const playerId = normalizeNonEmptyString(input?.playerId, "");
  const cash = input?.economy?.players?.[playerId]?.cash;
  return Number.isFinite(cash) ? cash : 0;
}

function getStateStatus(input = {}) {
  return normalizeNonEmptyString(input?.state?.status, "").toLowerCase();
}

function toTowerId(value) {
  return Number.isInteger(value) && value > 0 ? value : null;
}

function getStateTowers(input = {}) {
  return Array.isArray(input?.state?.towers) ? input.state.towers : [];
}

function coordinateKey(x, y) {
  return `${Math.round(Number(x))}:${Math.round(Number(y))}`;
}

function canonicalizeValue(value) {
  if (Array.isArray(value)) {
    return value.map((entry) => canonicalizeValue(entry));
  }
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.keys(value)
        .sort()
        .map((key) => [key, canonicalizeValue(value[key])])
    );
  }
  return value;
}

function payloadEquals(left = {}, right = {}) {
  return JSON.stringify(canonicalizeValue(left)) === JSON.stringify(canonicalizeValue(right));
}

function buildKnownTowerOwners(input = {}) {
  const knownOwners = new Map();
  const currentTowerIds = new Set(
    getStateTowers(input)
      .map((tower) => toTowerId(tower?.id))
      .filter((towerId) => towerId != null)
  );
  const lastCommandResults = Array.isArray(input?.lastCommandResults) ? input.lastCommandResults : [];
  for (const entry of lastCommandResults) {
    const command = entry?.command ?? {};
    const result = entry?.result ?? {};
    const playerId = normalizeNonEmptyString(command?.playerId, "");
    if (!playerId || result?.success !== true) {
      continue;
    }
    const commandType = normalizeNonEmptyString(command?.type, "").toLowerCase();
    if (commandType === "place_tower") {
      const towerId = toTowerId(result?.towerId);
      if (towerId != null && currentTowerIds.has(towerId)) {
        knownOwners.set(towerId, playerId);
      }
      continue;
    }
    if (commandType === "sell_tower") {
      const towerId = toTowerId(command?.payload?.towerId);
      if (towerId != null) {
        knownOwners.delete(towerId);
      }
      continue;
    }
    if (commandType === "upgrade_tower") {
      const towerId = toTowerId(command?.payload?.towerId);
      if (towerId != null && currentTowerIds.has(towerId) && !knownOwners.has(towerId)) {
        knownOwners.set(towerId, playerId);
      }
    }
  }
  return knownOwners;
}

function getPlayerOwnedTowerCount(input = {}) {
  const playerId = normalizeNonEmptyString(input?.playerId, "");
  if (!playerId) {
    return 0;
  }
  const knownOwners = buildKnownTowerOwners(input);
  let ownedTowerCount = 0;
  for (const tower of getStateTowers(input)) {
    const towerId = toTowerId(tower?.id);
    if (towerId != null && knownOwners.get(towerId) === playerId) {
      ownedTowerCount += 1;
    }
  }
  return ownedTowerCount;
}

function playerHasSuccessfulCommandHistory(input = {}) {
  const playerId = normalizeNonEmptyString(input?.playerId, "");
  if (!playerId) {
    return false;
  }
  const lastCommandResults = Array.isArray(input?.lastCommandResults) ? input.lastCommandResults : [];
  return lastCommandResults.some((entry) => {
    const command = entry?.command ?? {};
    const result = entry?.result ?? {};
    return normalizeNonEmptyString(command?.playerId, "") === playerId && result?.success === true;
  });
}

function resolvePath(rawPath) {
  const expanded = normalizeNonEmptyString(rawPath);
  if (!expanded) {
    throw new Error("Path must be a non-empty string");
  }
  return path.isAbsolute(expanded) ? expanded : path.resolve(REPO_ROOT, expanded);
}

function ensureDirectoryFor(filePath) {
  fs.mkdirSync(path.dirname(path.resolve(filePath)), { recursive: true });
}

function writeJson(pathname, payload) {
  ensureDirectoryFor(pathname);
  fs.writeFileSync(pathname, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
}

function displayPath(targetPath) {
  const relative = path.relative(REPO_ROOT, path.resolve(targetPath));
  return relative.startsWith("..") ? path.resolve(targetPath) : relative;
}

function sanitizeSourceStem(sourcePath) {
  const displayed = displayPath(sourcePath).replace(/\\/g, "/");
  const stem = displayed.endsWith(".json") ? displayed.slice(0, -5) : displayed;
  return stem
    .replace(/^\.\//, "")
    .replace(/^\/+/, "")
    .replace(/\//g, "__")
    .replace(/[^A-Za-z0-9._-]+/g, "_");
}

function parseArgs(argv) {
  const options = {
    sources: [],
    outDir: DEFAULT_OUTPUT_DIR,
    reportPath: DEFAULT_REPORT_PATH,
    teacherMode: DEFAULT_TEACHER_MODE,
    includeNoop: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--source" || token === "--input") {
      options.sources.push(resolvePath(argv[index + 1]));
      index += 1;
    } else if (token === "--out-dir") {
      options.outDir = resolvePath(argv[index + 1]);
      index += 1;
    } else if (token === "--report") {
      options.reportPath = resolvePath(argv[index + 1]);
      index += 1;
    } else if (token === "--teacher-mode") {
      options.teacherMode = normalizeNonEmptyString(argv[index + 1], options.teacherMode).toLowerCase();
      index += 1;
    } else if (token === "--include-noop") {
      options.includeNoop = true;
    } else if (token === "--help" || token === "-h") {
      process.stdout.write(
        [
          "Usage: node scripts/relabel_actual_game_teacher_decisions.mjs [options]",
          "",
          "Options:",
          "  --source <path>            Source bridge-decisions.json. Repeat to relabel multiple files.",
          `  --out-dir <path>           Output directory (default ${displayPath(DEFAULT_OUTPUT_DIR)})`,
          `  --report <path>            Report path (default ${displayPath(DEFAULT_REPORT_PATH)})`,
          `  --teacher-mode <mode>      Teacher mode: codex-safe | deterministic | hybrid-opening (default ${DEFAULT_TEACHER_MODE})`,
          "  --include-noop             Keep relabeled noop rows instead of exporting commands only.",
        ].join("\n") + "\n"
      );
      process.exit(0);
    } else {
      throw new Error(`Unknown option: ${token}`);
    }
  }

  if (options.sources.length === 0) {
    throw new Error("At least one --source path is required");
  }
  if (!SUPPORTED_TEACHER_MODES.has(options.teacherMode)) {
    throw new Error(`Unsupported --teacher-mode: ${options.teacherMode}`);
  }
  return options;
}

async function loadModules() {
  const importFromGame = async (relativePath) =>
    import(pathToFileURL(path.join(GAME_REPO_ROOT, relativePath)).href);
  const [{ createCodexAdapter }, { createDeterministicFallbackPolicy }] = await Promise.all([
    importFromGame("src/adapters/llm-bridge/providers/codex.js"),
    importFromGame("src/adapters/llm-bridge/providers/provider-http.js"),
  ]);
  return {
    createCodexAdapter,
    createDeterministicFallbackPolicy,
  };
}

function loadSourceRows(sourcePath) {
  const payload = JSON.parse(fs.readFileSync(sourcePath, "utf8"));
  if (!Array.isArray(payload)) {
    throw new Error(`${sourcePath} must contain a top-level array`);
  }
  return payload;
}

function buildTeacherDecision(decision, { teacherMode, sourcePath, sourceIndex }) {
  const normalizedDecision = decision && typeof decision === "object" ? JSON.parse(JSON.stringify(decision)) : {};
  const provenance = normalizedDecision.provenance && typeof normalizedDecision.provenance === "object"
    ? { ...normalizedDecision.provenance }
    : {};
  normalizedDecision.provenance = {
    ...provenance,
    providerId: "teacher-relabel",
    modelId: `teacher-${teacherMode}`,
    requestId: `${sanitizeSourceStem(sourcePath)}-teacher-${String(sourceIndex).padStart(4, "0")}`,
    mode: "deterministic_teacher",
    remoteError: null,
  };
  return normalizedDecision;
}

function normalizeTeacherDecisionForRow(decision, input) {
  const normalizedDecision = decision && typeof decision === "object" ? JSON.parse(JSON.stringify(decision)) : {};
  if (normalizedDecision.kind !== "command") {
    return normalizedDecision;
  }
  const allowed = normalizeAllowedCommands(input?.allowedCommands);
  const commandType = normalizeNonEmptyString(normalizedDecision.commandType, "").toLowerCase();
  if (!commandType || !allowed.has(commandType)) {
    return {
      kind: "noop",
      reason: commandType ? `Command is not allowed: ${commandType}` : "Missing commandType",
      provenance:
        normalizedDecision.provenance && typeof normalizedDecision.provenance === "object"
          ? { ...normalizedDecision.provenance }
          : {},
    };
  }
  normalizedDecision.commandType = commandType;
  normalizedDecision.payload =
    normalizedDecision.payload && typeof normalizedDecision.payload === "object" && !Array.isArray(normalizedDecision.payload)
      ? normalizedDecision.payload
      : {};
  return normalizedDecision;
}

function chooseHybridOpeningDecision({
  input,
  codexDecision,
  deterministicDecision,
}) {
  const allowed = normalizeAllowedCommands(input?.allowedCommands);
  const codexWantsNoop = codexDecision?.kind !== "command";
  const deterministicPlaces =
    deterministicDecision?.kind === "command"
    && deterministicDecision?.commandType === "place_tower";
  const isOpeningState =
    getStateStatus(input) === "spawning"
    && getPlayerOwnedTowerCount(input) === 0
    && !playerHasSuccessfulCommandHistory(input)
    && getPlayerCash(input) >= 100
    && allowed.has("place_tower");
  return codexWantsNoop && deterministicPlaces && isOpeningState
    ? deterministicDecision
    : codexDecision;
}

function decisionIdentity(row = {}) {
  const decision = row?.decision ?? {};
  const provenance = decision?.provenance ?? {};
  const input = row?.input ?? {};
  return {
    requestId: normalizeNonEmptyString(provenance?.requestId, ""),
    playerId: normalizeNonEmptyString(input?.playerId, ""),
    commandType: normalizeNonEmptyString(decision?.commandType, "").toLowerCase(),
    payload:
      decision?.payload && typeof decision.payload === "object" && !Array.isArray(decision.payload)
        ? decision.payload
        : {},
    stateVersion: Number.isInteger(input?.stateVersion) ? input.stateVersion : null,
  };
}

function matchHistoricalCommandResult(row = {}) {
  const decision = row?.decision ?? {};
  if (decision?.kind !== "command") {
    return null;
  }

  const { requestId, playerId, commandType, payload, stateVersion } = decisionIdentity(row);
  const commandResults = Array.isArray(row?.poll?.commandResults) ? row.poll.commandResults : [];

  if (requestId) {
    for (let index = commandResults.length - 1; index >= 0; index -= 1) {
      const candidate = commandResults[index];
      const provenance = candidate?.command?.provenance ?? {};
      if (normalizeNonEmptyString(provenance?.requestId, "") === requestId) {
        return candidate;
      }
    }
  }

  for (let index = commandResults.length - 1; index >= 0; index -= 1) {
    const candidate = commandResults[index];
    const command = candidate?.command ?? {};
    const provenance = command?.provenance ?? {};
    const candidatePayload =
      command?.payload && typeof command.payload === "object" && !Array.isArray(command.payload)
        ? command.payload
        : {};
    if (normalizeNonEmptyString(command?.playerId, "") !== playerId) {
      continue;
    }
    if (normalizeNonEmptyString(command?.type, "").toLowerCase() !== commandType) {
      continue;
    }
    if (!payloadEquals(candidatePayload, payload)) {
      continue;
    }
    const candidateStateVersion = Number.isInteger(provenance?.stateVersion) ? provenance.stateVersion : null;
    if (stateVersion != null && candidateStateVersion != null && candidateStateVersion !== stateVersion) {
      continue;
    }
    return candidate;
  }

  return null;
}

function getHistoricalFailureReason(row = {}) {
  const matched = matchHistoricalCommandResult(row);
  const result = matched?.result ?? {};
  if (result?.success !== false) {
    return "";
  }
  return normalizeNonEmptyString(result?.reasonCode ?? result?.reason, "");
}

function repairIdentityMatchesHistorical(row = {}, decision = {}) {
  if (decision?.kind !== "command") {
    return false;
  }
  const historical = decisionIdentity(row);
  const historicalPayload = historical.payload ?? {};
  const currentPayload =
    decision?.payload && typeof decision.payload === "object" && !Array.isArray(decision.payload)
      ? decision.payload
      : {};
  const historicalCommandType = normalizeNonEmptyString(historical.commandType, "").toLowerCase();
  const currentCommandType = normalizeNonEmptyString(decision?.commandType, "").toLowerCase();
  if (!historicalCommandType || historicalCommandType !== currentCommandType) {
    return false;
  }
  if (currentCommandType === "place_tower") {
    return normalizeNonEmptyString(historicalPayload?.type, "").toLowerCase()
      === normalizeNonEmptyString(currentPayload?.type, "").toLowerCase();
  }
  if (currentCommandType === "upgrade_tower") {
    return String(historicalPayload?.towerId ?? "") === String(currentPayload?.towerId ?? "")
      && normalizeNonEmptyString(historicalPayload?.path, "").toLowerCase()
        === normalizeNonEmptyString(currentPayload?.path, "").toLowerCase();
  }
  return payloadEquals(historicalPayload, currentPayload);
}

function selectSummaryPlacements(input = {}) {
  const mapWidth = Number.isFinite(input?.state?.width) ? input.state.width : 960;
  const mapHeight = Number.isFinite(input?.state?.height) ? input.state.height : 540;
  return SUMMARY_SAFE_PLACEMENTS.map((anchor) => ({
    x: Math.max(40, Math.min(Math.floor(mapWidth - 40), Math.round(anchor.x))),
    y: Math.max(40, Math.min(Math.floor(mapHeight - 40), Math.round(anchor.y))),
  }));
}

function getVisibleOccupiedPlacementKeys(input = {}) {
  const occupied = new Set();
  for (const tower of getStateTowers(input)) {
    const position = tower?.position;
    if (!position || !Number.isFinite(position?.x) || !Number.isFinite(position?.y)) {
      continue;
    }
    occupied.add(coordinateKey(position.x, position.y));
  }
  return occupied;
}

function repairInvalidPlacementDecision(row = {}, decision = {}) {
  if (decision?.kind !== "command" || decision?.commandType !== "place_tower") {
    return decision;
  }
  if (getHistoricalFailureReason(row) !== "Invalid placement") {
    return decision;
  }
  if (normalizeNonEmptyString(decisionIdentity(row).commandType, "").toLowerCase() !== "place_tower") {
    return decision;
  }

  const originalPayload =
    row?.decision?.payload && typeof row.decision.payload === "object" && !Array.isArray(row.decision.payload)
      ? row.decision.payload
      : decision?.payload && typeof decision.payload === "object" && !Array.isArray(decision.payload)
        ? decision.payload
        : {};
  const originalX = Number.isFinite(originalPayload?.x) ? Number(originalPayload.x) : null;
  const originalY = Number.isFinite(originalPayload?.y) ? Number(originalPayload.y) : null;
  const occupied = getVisibleOccupiedPlacementKeys(row?.input ?? {});
  const candidates = selectSummaryPlacements(row?.input ?? {}).filter((anchor) => {
    const key = coordinateKey(anchor.x, anchor.y);
    if (occupied.has(key)) {
      return false;
    }
    if (originalX != null && originalY != null && key === coordinateKey(originalX, originalY)) {
      return false;
    }
    return true;
  });
  if (candidates.length === 0) {
    return decision;
  }
  candidates.sort((left, right) => {
    const leftDistance =
      (left.x - (originalX ?? left.x)) ** 2 + (left.y - (originalY ?? left.y)) ** 2;
    const rightDistance =
      (right.x - (originalX ?? right.x)) ** 2 + (right.y - (originalY ?? right.y)) ** 2;
    if (leftDistance !== rightDistance) {
      return leftDistance - rightDistance;
    }
    if (left.y !== right.y) {
      return left.y - right.y;
    }
    return left.x - right.x;
  });
  const repaired = candidates[0];
  return {
    ...decision,
    payload: {
      type: normalizeNonEmptyString(originalPayload?.type, decision?.payload?.type ?? "dart").toLowerCase(),
      x: repaired.x,
      y: repaired.y,
    },
    provenance:
      decision?.provenance && typeof decision.provenance === "object"
        ? {
            ...decision.provenance,
            repair: "invalid_placement_safe_anchor",
          }
        : {
            repair: "invalid_placement_safe_anchor",
          },
  };
}

function repairInsufficientCashDecision(row = {}, decision = {}) {
  if (decision?.kind !== "command") {
    return decision;
  }
  const failureReason = getHistoricalFailureReason(row);
  if (failureReason !== "INSUFFICIENT_PLAYER_CASH") {
    return decision;
  }
  if (!repairIdentityMatchesHistorical(row, decision)) {
    return decision;
  }
  const commandType = normalizeNonEmptyString(decision?.commandType, "").toLowerCase();
  if (commandType !== "place_tower" && commandType !== "upgrade_tower") {
    return decision;
  }
  if (getStateStatus(row?.input ?? {}) !== "active") {
    return decision;
  }
  return {
    kind: "noop",
    reason: "waiting_for_resources",
    provenance:
      decision?.provenance && typeof decision.provenance === "object"
        ? {
            ...decision.provenance,
            repair: "insufficient_cash_wait",
          }
        : {
            repair: "insufficient_cash_wait",
          },
  };
}

async function relabelSourceRows({
  sourcePath,
  teacherMode,
  includeNoop,
  createCodexAdapter,
  createDeterministicFallbackPolicy,
}) {
  const rows = loadSourceRows(sourcePath);
  const codexAdapter = createCodexAdapter({
    providerUrl: "",
    providerToken: "",
    modelId: `teacher-${teacherMode}`,
  });
  const deterministicPolicy = createDeterministicFallbackPolicy();
  await codexAdapter.init({ allowedCommands: COMMAND_SEQUENCE });

  const relabeledRows = [];
  const commandTypeCounts = {};
  let noopCount = 0;
  let hybridOpeningOverrides = 0;

  for (let sourceIndex = 0; sourceIndex < rows.length; sourceIndex += 1) {
    const row = rows[sourceIndex];
    if (!row || typeof row !== "object" || !row.input || typeof row.input !== "object") {
      throw new Error(`${sourcePath} entry ${sourceIndex} must contain an object input`);
    }
    const input = JSON.parse(JSON.stringify(row.input));
    const codexDecision = await codexAdapter.decide(input);
    const deterministicDecision = deterministicPolicy({
      input,
      decisionIndex: sourceIndex,
      allowedCommands: input.allowedCommands,
    });

    let selectedDecision = codexDecision;
    if (teacherMode === "deterministic") {
      selectedDecision = deterministicDecision;
    } else if (teacherMode === "hybrid-opening") {
      selectedDecision = chooseHybridOpeningDecision({
        input,
        codexDecision,
        deterministicDecision,
      });
      if (selectedDecision === deterministicDecision && codexDecision !== deterministicDecision) {
        hybridOpeningOverrides += 1;
      }
    }
    selectedDecision = repairInvalidPlacementDecision(row, selectedDecision);
    selectedDecision = repairInsufficientCashDecision(row, selectedDecision);

    const teacherDecision = buildTeacherDecision(normalizeTeacherDecisionForRow(selectedDecision, input), {
      teacherMode,
      sourcePath,
      sourceIndex,
    });

    if (teacherDecision.kind !== "command" && !includeNoop) {
      noopCount += 1;
      continue;
    }
    if (teacherDecision.kind === "command") {
      const commandType = normalizeNonEmptyString(teacherDecision.commandType, "unknown");
      commandTypeCounts[commandType] = (commandTypeCounts[commandType] || 0) + 1;
    } else {
      noopCount += 1;
    }

    relabeledRows.push({
      index: sourceIndex,
      input,
      decision: teacherDecision,
      metadata: {
        source_path: displayPath(sourcePath),
        source_index: sourceIndex,
        teacher_mode: teacherMode,
        historical_decision_kind: normalizeNonEmptyString(row?.decision?.kind, "unknown"),
        historical_command_type: normalizeNonEmptyString(row?.decision?.commandType, ""),
        historical_failure_reason: getHistoricalFailureReason(row),
      },
    });
  }

  await codexAdapter.close("teacher relabel complete");
  return {
    rows: relabeledRows,
    report: {
      source_path: displayPath(sourcePath),
      input_row_count: rows.length,
      output_row_count: relabeledRows.length,
      command_type_counts: commandTypeCounts,
      noop_count: noopCount,
      hybrid_opening_overrides: hybridOpeningOverrides,
      teacher_mode: teacherMode,
      include_noop: includeNoop,
    },
  };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const { createCodexAdapter, createDeterministicFallbackPolicy } = await loadModules();

  fs.mkdirSync(args.outDir, { recursive: true });
  const sourceReports = [];
  const outputPaths = [];

  for (const sourcePath of args.sources) {
    const { rows, report } = await relabelSourceRows({
      sourcePath,
      teacherMode: args.teacherMode,
      includeNoop: args.includeNoop,
      createCodexAdapter,
      createDeterministicFallbackPolicy,
    });
    const outputPath = path.join(
      args.outDir,
      `${sanitizeSourceStem(sourcePath)}.teacher-${args.teacherMode}.json`
    );
    writeJson(outputPath, rows);
    sourceReports.push({
      ...report,
      output_path: displayPath(outputPath),
    });
    outputPaths.push(displayPath(outputPath));
  }

  const totalInputRows = sourceReports.reduce((sum, report) => sum + report.input_row_count, 0);
  const totalOutputRows = sourceReports.reduce((sum, report) => sum + report.output_row_count, 0);
  const totalNoops = sourceReports.reduce((sum, report) => sum + report.noop_count, 0);
  const totalOverrides = sourceReports.reduce((sum, report) => sum + report.hybrid_opening_overrides, 0);
  const aggregateCommandCounts = {};
  for (const report of sourceReports) {
    for (const [commandType, count] of Object.entries(report.command_type_counts)) {
      aggregateCommandCounts[commandType] = (aggregateCommandCounts[commandType] || 0) + count;
    }
  }

  const aggregateReport = {
    schema_version: "td.actual_game.teacher_relabels_report.v1",
    generated_at: new Date().toISOString(),
    teacher_mode: args.teacherMode,
    include_noop: args.includeNoop,
    source_count: sourceReports.length,
    input_row_count: totalInputRows,
    output_row_count: totalOutputRows,
    noop_count: totalNoops,
    hybrid_opening_override_count: totalOverrides,
    command_type_counts: aggregateCommandCounts,
    outputs: outputPaths,
    sources: sourceReports,
  };
  writeJson(args.reportPath, aggregateReport);
  process.stdout.write(`${JSON.stringify(aggregateReport, null, 2)}\n`);
}

main().catch((error) => {
  process.stderr.write(`${error?.stack || error}\n`);
  process.exit(1);
});

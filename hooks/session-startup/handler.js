import fs from "node:fs/promises";
import path from "node:path";

const CRITICAL_FILES = [
  "SOUL.md",
  "USER.md",
  "MEMORY.md",
  "SESSION-STATE.md",
  "AGENTS.md",
];

const DAILY_MEMORY_DIR = "memory";

const handler = async (event) => {
  // Only handle session:start and command:new
  if (event.type !== "session" && event.type !== "command") return;
  if (event.type === "session" && event.action !== "start") return;
  if (event.type === "command" && event.action !== "new") return;

  const workspaceDir = (event.context?.workspaceDir)
    || process.env.OPENCLAW_WORKSPACE_DIR
    || path.join(process.env.HOME || "/home/oz", ".openclaw/workspace");

  if (!workspaceDir) {
    event.messages.push("[session-startup] No workspaceDir found, skipping.");
    return;
  }

  const markerPath = path.join(workspaceDir, ".startup_marker");
  const now = Math.floor(Date.now() / 1000);

  // Read critical files and record their mtimes
  const fileStats = [];

  for (const file of CRITICAL_FILES) {
    const filePath = path.join(workspaceDir, file);
    try {
      const stat = await fs.stat(filePath);
      fileStats.push(`${file}=${Math.floor(stat.mtimeMs / 1000)}`);
    } catch {
      fileStats.push(`${file}=MISSING`);
    }
  }

  // Today's and yesterday's daily memory
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  const formatDate = (d) =>
    `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;

  const memoryFiles = [`${formatDate(today)}.md`, `${formatDate(yesterday)}.md`];
  const memoryDir = path.join(workspaceDir, DAILY_MEMORY_DIR);

  for (const mf of memoryFiles) {
    const mfPath = path.join(memoryDir, mf);
    try {
      const stat = await fs.stat(mfPath);
      fileStats.push(`${DAILY_MEMORY_DIR}/${mf}=${Math.floor(stat.mtimeMs / 1000)}`);
    } catch {
      fileStats.push(`${DAILY_MEMORY_DIR}/${mf}=MISSING`);
    }
  }

  // Write comprehensive marker
  const lines = [
    `LAST_STARTUP=${now}`,
    `LAST_SESSION=${event.sessionKey}`,
    `AGENT_BOOTSTRAP=1`,
    ...fileStats,
  ];

  try {
    await fs.writeFile(markerPath, lines.join("\n") + "\n", "utf-8");
    const missing = fileStats.filter((f) => f.includes("=MISSING"));
    if (missing.length > 0) {
      event.messages.push(
        `🚀 Startup complete — ${fileStats.length - missing.length}/${fileStats.length} files verified, missing: ${missing.map((m) => m.split("=")[0]).join(", ")}`
      );
    } else {
      event.messages.push(`🚀 Startup complete — all ${fileStats.length} files verified`);
    }
  } catch (err) {
    event.messages.push(`[session-startup] Failed to write marker: ${err}`);
  }
};

export default handler;

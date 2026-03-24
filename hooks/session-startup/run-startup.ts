import fs from "node:fs/promises";
import path from "node:path";

const workspaceDir = "/home/oz/.openclaw/workspace";
const CRITICAL_FILES = ["SOUL.md", "USER.md", "MEMORY.md", "SESSION-STATE.md", "AGENTS.md"];
const DAILY_MEMORY_DIR = "memory";

const today = new Date();
const yesterday = new Date(today);
yesterday.setDate(yesterday.getDate() - 1);
const formatDate = (d: Date) =>
  `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;

const fileStats: string[] = [];
for (const file of CRITICAL_FILES) {
  try {
    const stat = await fs.stat(path.join(workspaceDir, file));
    fileStats.push(`${file}=${Math.floor(stat.mtimeMs / 1000)}`);
  } catch {
    fileStats.push(`${file}=MISSING`);
  }
}

const memoryFiles = [`${formatDate(today)}.md`, `${formatDate(yesterday)}.md`];
for (const mf of memoryFiles) {
  try {
    const stat = await fs.stat(path.join(workspaceDir, DAILY_MEMORY_DIR, mf));
    fileStats.push(`${DAILY_MEMORY_DIR}/${mf}=${Math.floor(stat.mtimeMs / 1000)}`);
  } catch {
    fileStats.push(`${DAILY_MEMORY_DIR}/${mf}=MISSING`);
  }
}

const now = Math.floor(Date.now() / 1000);
const markerPath = path.join(workspaceDir, ".startup_marker");
const lines = [`LAST_STARTUP=${now}`, `LAST_SESSION=heartbeat-recovery`, `AGENT_BOOTSTRAP=1`, ...fileStats];
await fs.writeFile(markerPath, lines.join("\n") + "\n", "utf-8");
console.log("Startup marker written:", lines.join("\n"));

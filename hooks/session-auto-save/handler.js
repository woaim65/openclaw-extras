/**
 * Session Auto-Save Hook
 * 
 * Saves session context to memory at 15-minute intervals.
 * Reads session JSONL files directly from agents directory.
 * 
 * Events: gateway (action=startup)
 */

import fs from "node:fs/promises";
import path from "node:path";

const AUTO_SAVE_DIR = "memory/autosave";
const INTERVAL_MS = 15 * 60 * 1000; // 15 minutes
const AGENTS_SESSIONS_DIR = "/home/oz/.openclaw/agents/main/sessions";

let saveTimer = null;
let lastSaveTime = 0;

async function findCurrentSessionFile() {
  try {
    const files = await fs.readdir(AGENTS_SESSIONS_DIR);
    const jsonlFiles = files.filter(n => n.endsWith(".jsonl") && !n.includes(".reset.") && !n.includes(".deleted"));
    if (jsonlFiles.length === 0) return null;
    let newest = null, newestMtime = 0;
    for (const f of jsonlFiles) {
      const stat = await fs.stat(path.join(AGENTS_SESSIONS_DIR, f));
      if (stat.mtimeMs > newestMtime) { newestMtime = stat.mtimeMs; newest = f; }
    }
    return newest ? path.join(AGENTS_SESSIONS_DIR, newest) : null;
  } catch { return null; }
}

async function saveSessionToMemory() {
  const workspaceDir = process.env.OPENCLAW_WORKSPACE_DIR || "/home/oz/.openclaw/workspace";
  const sessionFile = await findCurrentSessionFile();
  if (!sessionFile) return;

  const autoSaveDir = path.join(workspaceDir, AUTO_SAVE_DIR);
  await fs.mkdir(autoSaveDir, { recursive: true });

  const now = new Date();
  const dateStr = now.toISOString().slice(0, 16).replace("T", "-");
  const filePath = path.join(autoSaveDir, `${dateStr}.md`);

  try {
    const raw = await fs.readFile(sessionFile, "utf-8");
    const lines = raw.trim().split("\n");
    let content = `# Session Auto-Save: ${dateStr}\n\n**Session**: ${path.basename(sessionFile)}\n**Saved**: ${now.toISOString()}\n\n`;
    for (const line of lines) {
      try {
        const entry = JSON.parse(line);
        if (entry.type === "message" && entry.message?.role && entry.message?.content) {
          const text = typeof entry.message.content === "string" 
            ? entry.message.content 
            : entry.message.content?.find(c => c.type === "text")?.text;
          if (text && !text.startsWith("/") && !text.startsWith("HEARTBEAT")) {
            const role = entry.message.role === "user" ? "user" : "assistant";
            content += `**${role}**: ${text.slice(0, 300)}\n\n`;
          }
        }
      } catch {}
    }
    await fs.writeFile(filePath, content, "utf-8");
    lastSaveTime = Date.now();
    console.log(`[session-auto-save] SAVED to ${path.basename(filePath)}`);
  } catch (err) {
    console.error(`[session-auto-save] FAILED: ${err.message}`);
  }
}

const handler = async (event) => {
  if (event.type === "gateway" && event.action === "startup") {
    if (saveTimer) clearInterval(saveTimer);
    saveTimer = setInterval(saveSessionToMemory, INTERVAL_MS);
    // Save immediately on startup too
    await saveSessionToMemory();
    return;
  }
};

export default handler;

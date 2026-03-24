import fs from "node:fs/promises";
import path from "node:path";
import { execSync } from "child_process";

const handler = async (event) => {
  // Only handle agent:bootstrap
  if (event.type !== "agent" || event.action !== "bootstrap") return;

  const context = event.context;
  if (!context || !Array.isArray(context.bootstrapFiles)) return;

  const workspaceDir = context.workspaceDir;
  if (!workspaceDir) return;

  // Compute date range — last 7 days to ensure evolution/project content is injected
  const today = new Date();
  const dates = [];
  for (let i = 0; i < 7; i++) {
    const d = new Date(today);
    d.setDate(d.getDate() - i);
    dates.push(
      `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`
    );
  }

  const memoryDir = path.join(workspaceDir, "memory");
  const filesToAdd = [];

  // 1. Inject daily memory files (last 7 days)
  for (const dateStr of dates) {
    const fileName = `${dateStr}.md`;
    const filePath = path.join(memoryDir, fileName);
    try {
      await fs.stat(filePath);
      filesToAdd.push({ name: fileName, path: filePath, missing: false });
    } catch {
      filesToAdd.push({ name: fileName, path: filePath, missing: true });
    }
  }

  // 2. Query LanceDB for recent memories and inject as a bootstrap file
  const lanceFileName = "memory/lance-retrieved.md";
  const lanceFilePath = path.join(workspaceDir, lanceFileName);
  try {
    const result = execSync("python3 /home/oz/.openclaw/scripts/lance-bootstrap.py", {
      timeout: 15000,
      encoding: "utf-8",
    });
    await fs.writeFile(lanceFilePath, result, "utf-8");
    filesToAdd.push({ name: lanceFileName, path: lanceFilePath, missing: false });
  } catch (err) {
    // LanceDB unavailable — skip silently
  }

  if (filesToAdd.length === 0) return;
  context.bootstrapFiles.push(...filesToAdd);
};

export default handler;

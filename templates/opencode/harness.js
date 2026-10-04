import { tool } from "@opencode-ai/plugin"
import { spawn } from "node:child_process"
import path from "node:path"

function runRouter(executable, root, task, profile) {
  return new Promise((resolve, reject) => {
    const child = spawn(executable, [path.join(root, "scripts", "skill_router.py"), "--profile", profile], {
      cwd: root, shell: false, windowsHide: true, stdio: ["pipe", "pipe", "pipe"],
      env: { ...process.env, PYTHONUTF8: "1" },
    })
    let output = "", errors = ""
    const timer = setTimeout(() => { child.kill(); reject(new Error("Harness skill routing timed out")) }, 30_000)
    child.stdout.setEncoding("utf8").on("data", (text) => { output += text })
    child.stderr.setEncoding("utf8").on("data", (text) => { errors += text })
    child.on("error", (error) => { clearTimeout(timer); reject(error) })
    child.stdin.on("error", () => {}) // Spawn/exit errors are reported by the process handlers.
    child.on("close", (code) => {
      clearTimeout(timer)
      if (code !== 0) reject(new Error(`Harness skill router failed (${code}): ${errors.trim()}`))
      else {
        try { resolve(JSON.stringify(JSON.parse(output), null, 2)) }
        catch { reject(new Error("Harness skill router returned invalid JSON")) }
      }
    })
    child.stdin.end(task)
  })
}

export const route = tool({
  description: "Route every non-trivial project task before implementation or delegation. Returns the harness skill router's bounded activation plan; read the selected skill paths. No shell execution or model calls.",
  args: {
    task: tool.schema.string().describe("Compact task, excluding secrets."),
    profile: tool.schema.enum(["balanced", "local-small", "reasoning-high"]).optional().describe("Default balanced; local-small for small/local models."),
  },
  async execute(args, context) {
    const task = String(args.task || "").trim()
    if (!task) throw new Error("task is required")
    const root = context.worktree || context.directory || process.cwd()
    const interpreters = process.platform === "win32" ? ["python", "python3"] : ["python3", "python"]
    for (const executable of interpreters) {
      try { return await runRouter(executable, root, task, args.profile || "balanced") }
      catch (error) { if (error.code !== "ENOENT") throw error }
    }
    throw new Error("Harness skill routing requires Python 3 on PATH (python3 or python).")
  },
})

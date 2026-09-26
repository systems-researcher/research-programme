// Copyright (c) 2026 Jason D. Gower
// SPDX-License-Identifier: MIT
//
// Sets BASE_PATH to the production project-pages prefix and runs one command.
// CI's site job carries BASE_PATH on the job, and a shell cannot prefix env
// vars portably, so local gates and dry-runs reproduce that environment here:
//   node tests/with-base.mjs npm run build
import { spawnSync } from "node:child_process"

const [cmd, ...args] = process.argv.slice(2)
if (!cmd) {
  console.error("usage: node tests/with-base.mjs <command> [args...]")
  process.exit(2)
}

const result = spawnSync(cmd, args, {
  stdio: "inherit",
  env: { ...process.env, BASE_PATH: "/research-programme/" },
  // npm is a .cmd shim on Windows; shell resolution matches how CI invokes it.
  shell: process.platform === "win32",
})
process.exit(result.status ?? 1)

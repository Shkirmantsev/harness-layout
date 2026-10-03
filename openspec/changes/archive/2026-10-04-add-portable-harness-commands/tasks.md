# Tasks

- [x] Compare donor command surface, server transport and current setup behavior.
- [x] Implement portable Make/Python aliases and non-destructive Wiki initialization.
- [x] Implement connectable localhost MCP lifecycle and opt-in HTTP client configs.
- [x] Verify real lifecycle, ownership, configuration and existing stdio regressions.
- [x] Update operator documentation and Wiki; prepare capability adoption after verification.
- [x] Run full local and Linux/Windows CI gates, integrate into dev and archive.

Evidence: feature `37307fa` passed all seven native CI jobs; local full gate
passed 100 tests. Linux and Windows full gates exercise actual HTTP/stdio
requests, lifecycle ownership and cleanup. Windows Make help and Wiki init
passed under cmd.exe. Feature merged locally and published into dev; main
PR creation and merge remain with the user.

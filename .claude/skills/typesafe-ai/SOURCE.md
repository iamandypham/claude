# Source

Vendored unchanged from https://github.com/typesafe-ai/skills (MIT), commit
65a39f393687675ce170e6094757de20370365b9, file skills/typesafe-ai/SKILL.md, on 14 Oct 2026.
Pinned on purpose: the upstream plugin updates itself, and a vendored copy only changes through a PR here.

## BG notes
- The skill is design guidance only. It installs no hooks, MCP servers or scripts.
- Calling Jev needs a TypeSafe API key, which costs money ($0.042 per million input tokens,
  output free, per docs.typesafe.ai/models 14 Oct 2026). Getting a key is Andy's call.
- Keys go in an n8n credential or the Mac keychain, never in a file.
- To update: re-copy SKILL.md from a newer upstream commit and change the hash above.
- To remove: delete this folder.

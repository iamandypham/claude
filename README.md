# claude

Claude Code project config for BusinessGrowR.

## MCP servers (`.mcp.json`)

- **apify** — Apify's hosted MCP (`mcp.apify.com`), scoped to the `apify/instagram-scraper` actor.
  It reads the token from the `APIFY_TOKEN` environment variable. Set it as an API credential /
  environment variable in the Claude Code cloud environment settings (never commit the token).
  A new session picks up both the variable and the server.

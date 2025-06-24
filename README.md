# AgenticAI-PPL

This project is an MCP (Model Context Protocol) server for a web-based Agentic AI platform focused on personalized Python learning. It supports multi-LLM chatbot interactions, resource curation, documentation generation, and integration with Google Drive, Gmail, Notion, and Canva.

## Features
- Multi-LLM chatbot (Claude, GPT, Gemini, Qwen)
- Personalized learning plans
- Resource finder and documentation generator
- Integrations: Google Drive, Gmail, Notion, Canva
- Modern FastAPI backend

## Setup
1. Ensure you have Python 3.12+ and [uv](https://github.com/astral-sh/uv) installed.
2. Install dependencies:
   ```bash
   uv sync --dev --all-extras
   ```
3. Run the server:
   ```bash
   uvicorn agenticai_ppl.main:app --reload
   ```

## More Info
- MCP SDK: https://github.com/modelcontextprotocol/create-python-server

## Components

### Resources

The server implements a simple note storage system with:
- Custom note:// URI scheme for accessing individual notes
- Each note resource has a name, description and text/plain mimetype

### Prompts

The server provides a single prompt:
- summarize-notes: Creates summaries of all stored notes
  - Optional "style" argument to control detail level (brief/detailed)
  - Generates prompt combining all current notes with style preference

### Tools

The server implements one tool:
- add-note: Adds a new note to the server
  - Takes "name" and "content" as required string arguments
  - Updates server state and notifies clients of resource changes

## Configuration

[TODO: Add configuration details specific to your implementation]

## Quickstart

### Install

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  ```
  "mcpServers": {
    "AgenticAI-PPL": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/navneetsharma/Documents/Project113/AgenticAI-PPL",
        "run",
        "AgenticAI-PPL"
      ]
    }
  }
  ```
</details>

<details>
  <summary>Published Servers Configuration</summary>
  ```
  "mcpServers": {
    "AgenticAI-PPL": {
      "command": "uvx",
      "args": [
        "AgenticAI-PPL"
      ]
    }
  }
  ```
</details>

## Development

### Building and Publishing

To prepare the package for distribution:

1. Sync dependencies and update lockfile:
```bash
uv sync
```

2. Build package distributions:
```bash
uv build
```

This will create source and wheel distributions in the `dist/` directory.

3. Publish to PyPI:
```bash
uv publish
```

Note: You'll need to set PyPI credentials via environment variables or command flags:
- Token: `--token` or `UV_PUBLISH_TOKEN`
- Or username/password: `--username`/`UV_PUBLISH_USERNAME` and `--password`/`UV_PUBLISH_PASSWORD`

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).


You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory /Users/navneetsharma/Documents/Project113/AgenticAI-PPL run agenticai-ppl
```


Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.
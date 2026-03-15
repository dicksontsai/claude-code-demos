# Worktrees — Claude Code Tutorial Demo

This tutorial walks through Claude Code's **worktrees** feature using a fork of [Excalidraw](https://excalidraw.com) as the demo project.

Worktrees let you work on multiple features in parallel — each in its own isolated branch and directory — without losing your session context or stashing work. Claude Code handles the rough edges automatically.

## Prerequisites

- **Node.js** v18 or later
- **Yarn** (Excalidraw uses Yarn workspaces)
- **Claude Code**

## Setup

From inside this `worktrees-demo/` directory, clone the demo fork of Excalidraw and copy over the Claude Code settings:

```bash
git clone https://github.com/dicksontsai/excalidraw
mkdir excalidraw/.claude
cp settings_for_demo.json excalidraw/.claude/settings.json
```

Install dependencies and verify the dev server starts:

```bash
cd excalidraw
yarn install
yarn start
```

Then open Claude Code from inside the `excalidraw/` directory:

```bash
claude
```

## What are worktrees?

A git worktree is a separate working directory linked to the same repository. You get a new directory and a new branch, but share the same git history and object store.

Claude Code makes worktrees practical by handling the things that make raw `git worktree` commands annoying:

- **Automatic directory management** — Claude Code creates, names, and cleans up worktree directories for you.
- **Settings propagation** — Your Claude Code settings (MCP servers, hooks, permissions) carry over to the worktree automatically.

## Starting a worktree

### By name

```bash
claude --worktree <name>
```

This creates a new worktree with that name and starts a Claude Code session inside it. Use this when starting a new feature branch.

### For a pull request

```bash
claude --worktree #<PR number>
```

This checks out the PR's branch in a new worktree. Useful for reviewing or continuing work on an open PR without disturbing your main working directory.

## Worktree settings

You can configure worktree behavior in your Claude Code settings:

### `settings.worktree.symlinkDirectories`

Directories to symlink from the main repo into each worktree. Use this for directories that are expensive to recreate and safe to share across branches — like `node_modules`:

```json
{
  "worktree": {
    "symlinkDirectories": ["node_modules"]
  }
}
```

Without this, each worktree would need its own `yarn install`. With it, the worktree reuses the main repo's `node_modules` via a symlink.

> **Note:** Only symlink directories where branch-to-branch differences don't matter. `node_modules` is safe if all your branches share the same dependencies. Don't symlink build outputs or directories that branches actively modify differently.

### `settings.worktree.sparsePaths`

Limit which files are checked out in the worktree. Useful for very large repos where you only need a subset of files for a given task:

```json
{
  "worktree": {
    "sparsePaths": ["packages/excalidraw/", "excalidraw-app/"]
  }
}
```

## The EnterWorktree and ExitWorktree tools

When Claude Code is running as an **agent** (subagent in a multi-agent pipeline), it has access to two tools for programmatic worktree management:

- **`EnterWorktree`** — Creates a worktree and switches the agent's context into it.
- **`ExitWorktree`** — Exits the worktree, with a choice of what to do with it:
  - `action: "keep"` — Leave the worktree and its branch in place.
  - `action: "remove"` — Delete the worktree directory.
  - `discard_changes: true` — Throw away any uncommitted changes before exiting.

These tools are what make it possible to build agents that safely explore or implement changes in isolation without touching the main working directory.

### Running dev servers from agent worktrees

Agent worktrees don't have their own `node_modules` — they rely on the main repo's. This means you can't run `yarn start` from inside the worktree (the install step will fail). Instead, start dev servers from the **orchestrating session** after the agents finish their changes:

```bash
# Run from the main repo root, once per worktree
cd .claude/worktrees/<worktree-name>/excalidraw-app && \
  VITE_APP_PORT=4001 /path/to/main-repo/node_modules/.bin/vite
```

If `node_modules/.bin/vite` doesn't exist yet, run `yarn install` from the main repo root first.

## When are worktrees useful?

Worktrees shine when your sessions are long-lived and you're juggling more than one thing. Without worktrees, working on a second feature means stashing changes, switching branches, and losing the conversational context you built up. With worktrees, each feature gets its own branch and directory, and you can switch between active Claude Code sessions without any of that overhead.

Concrete scenarios:

- You're mid-way through implementing a feature and a bug report comes in. Open a second worktree for the bugfix, fix it and ship it, then return to your feature worktree exactly where you left off.
- You want Claude to prototype two different approaches to the same problem in parallel, then compare them before committing to one.
- You're reviewing a PR and want to run the code locally without touching your in-progress work.

## Tutorial walkthrough

In the Excalidraw fork, you'll implement two features in parallel using worktrees — one in each worktree — and then merge them both. The tutorial demonstrates:

1. Starting your first worktree with `claude --worktree feature-a`
2. Configuring `symlinkDirectories` to skip reinstalling `node_modules`
3. Opening a second worktree with `claude --worktree feature-b` while feature-a is still in progress
4. Switching between the two live Claude Code sessions
5. Exiting a worktree cleanly once the feature is done

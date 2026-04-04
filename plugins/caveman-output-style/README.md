# Caveman Output Style Plugin

Me plugin. Me make Claude talk caveman.

> Why waste time say lot word when few word do trick?

When active, Claude drops articles, filler, and preamble. Short sentence. Result first. Code, comments, and commit messages stay normal — only chat text goes caveman.

**Note:** Despite the promise of fewer output tokens, this doesn't actually save tokens in practice — agent turns (tool calls, thinking) dominate the output, and chat text is a tiny fraction. This is just for fun.

Inspired by [r/ClaudeAI](https://www.reddit.com/r/ClaudeAI/comments/1sble09/taught_claude_to_talk_like_a_caveman_to_use_75/).

## Usage

1. Install plugin.
2. Run `/output-style` in Claude Code. Pick **caveman**.
3. Grunt.

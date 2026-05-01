# vision-model-skill

A Claude Code plugin port of [anthropic-experimental/vision-model-skill](https://github.com/anthropic-experimental/vision-model-skill/tree/main/skills/vision-model).

The skill guides a (possibly non-technical) user from "I want a model that does X with images" to a working model. It ships ready-made scripts for classification, detection, and zero-shot classification, with a strong preference for instant pretrained results before any training.

## Install

```
claude plugin install vision-model-skill@dickson-cc-demo-plugins
```

The skill activates automatically when the user describes a vision task — see the SKILL.md frontmatter for trigger phrases.

## What's inside

- `skills/vision-model/SKILL.md` — the skill instructions
- `skills/vision-model/scripts/` — ready-to-copy training and inference scripts
- `skills/vision-model/references/` — deeper reading the skill loads on demand

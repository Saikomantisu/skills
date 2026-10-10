# skills

Personal collection of agent skills.

Each skill lives in its own directory with a `SKILL.md` file describing what it does and when to use it.

## Skills

- [astro-to-pagescms](astro-to-pagescms/) adds Pages CMS to an Astro site.
- [yeet](yeet/) deploys a static site to a subdomain like `hungover-hyena`.

## Third-party skills

Installed globally with [`npx skills`](https://github.com/vercel-labs/skills), e.g.
`npx skills add mattpocock/skills -g -a claude-code codex hermes-agent --skill tdd`.
Its lock file is linked to [skill-lock.json](skill-lock.json), so commit that after
adding, updating (`npx skills update -g`) or removing (`npx skills remove -g <name>`).

Currently: `grill-me`, `grilling`, `teach`, `tdd`, `codebase-design` from
[mattpocock/skills](https://github.com/mattpocock/skills), and `mini-browser` from
[runablehq/mini-browser](https://github.com/runablehq/mini-browser).

## Setup

`scripts/setup.sh` runs both scripts below. Use it on a new machine.

- `scripts/link-skills.sh` links the skills here into every agent's skills directory.
  Re-run after adding, removing or renaming a skill.
- `scripts/install-third-party.sh` links the `npx skills` lock to this repo and
  installs any third-party skill in it that is missing.

## Layout

```
scripts/         (repo tooling, not a skill)
skill-name/
  SKILL.md
  references/    (optional, loaded on demand)
  scripts/       (optional, run by the agent)
```

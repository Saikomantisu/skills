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

From [mattpocock/skills](https://github.com/mattpocock/skills):

- grill-me interviews you relentlessly to sharpen a plan or design.
- grilling stress-tests a plan, decision or idea.
- teach teaches a new skill or concept inside the workspace.
- tdd builds features and fixes bugs test-first.
- codebase-design gives a shared vocabulary for designing deep modules.

From [runablehq/mini-browser](https://github.com/runablehq/mini-browser):

- mini-browser automates a browser with the `mb` CLI (screenshots, scraping, forms).

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

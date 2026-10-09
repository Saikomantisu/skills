# skills

Personal collection of agent skills.

Each skill lives in its own directory with a `SKILL.md` file describing what it does and when to use it.

## Skills

- [astro-to-pagescms](astro-to-pagescms/) wires Pages CMS into an Astro site:
  what Pages CMS can do, how to set it up, the full zod-to-field mapping, and
  which structural choices to put to the user rather than decide alone.
- [yeet](yeet/) puts a static site live at its own public subdomain with
  an unhinged adjective-animal name (`hungover-hyena`) unless one is given.
  Refuses to publish secrets, handles single-page apps, and can list and
  delete what you've yeeted.

## Layout

```
skill-name/
  SKILL.md
  references/    (optional, loaded on demand)
  scripts/       (optional, run by the agent)
```

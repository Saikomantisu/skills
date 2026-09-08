---
name: astro-to-pagescms
description: Convert an Astro content collection config into a Pages CMS `.pages.yml`. Use when wiring Pages CMS into an Astro site, when adding a collection that editors need access to, or when the zod schema changed and `.pages.yml` has fallen behind. Triggers on astro content collections, defineCollection, content.config.ts, pages cms, pagescms, .pages.yml.
---

# Astro collections to Pages CMS

Astro describes content with zod. Pages CMS describes it with YAML field
definitions. The two overlap on maybe 80% of a normal schema. This skill covers
the mapping, and is explicit about the parts that do not survive the trip.

## Read these first

1. The Astro config. `src/content.config.ts` on Astro 5, `src/content/config.ts`
   on Astro 4.
2. One real content file per collection. Open the actual markdown and look at
   the frontmatter.
3. Where images are stored, and whether the schema uses the `image()` helper.

Step 2 is the one people skip. Zod types are lossy: `z.string()` covers titles,
slugs, URLs, image paths, and three-paragraph blurbs, and those become four
different Pages CMS fields. The type alone cannot tell you which. The file can.

## Step 1: map the collection

Each `defineCollection` becomes one entry under `content:`.

```ts
const events = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/events" }),
  schema: z.object({ /* ... */ }),
});
```

```yaml
content:
  - name: events
    label: Events
    type: collection
    path: src/content/events
    filename: "{primary}.md"
    format: yaml-frontmatter
    view:
      fields: [title, date, location]
      primary: title
      sort: [date, title]
      default:
        sort: date
        order: desc
    fields: [] # step 2
```

| Astro | Pages CMS |
| --- | --- |
| key in `export const collections` | `name` (keep it identical) |
| humanized key | `label` |
| `glob()` loader over a folder | `type: collection` |
| `file()` loader over one data file | `type: file` plus `list: true` |
| `base: "./src/content/events"` | `path: src/content/events`, drop the `./` |
| `pattern: "**/*.md"` | `subfolders: true` |
| `pattern: "*.md"` | `subfolders: false` |
| `.md` / `.mdx` files | `format: yaml-frontmatter` plus a `body` field |
| `.json` files | `format: json` |
| `.yaml` / `.yml` files | `format: yaml` |
| Astro 4 `type: 'content'` | `format: yaml-frontmatter` plus a `body` field |
| Astro 4 `type: 'data'` | `format: json` or `yaml`, no body |

Keep the Pages CMS `name` byte-identical to the Astro collection key. Nothing
enforces it, but `reference()` fields point at collections by name and the
debugging gets tedious once the two drift.

`filename` decides entry ids, and entry ids are usually the URL slug under a
`[...slug]` route. `"{primary}.md"` slugifies the primary field, so an editor
who types a title picks the slug. Prefix with `{year}-{month}-{day}-` if the
existing files are dated.

### The body is not in the schema

Astro never puts the markdown body in the zod schema. It arrives separately
through `render()`. Pages CMS has no such convention, so an undeclared body is
a body editors cannot reach. Add it by hand to every frontmatter collection:

```yaml
- name: body
  label: Body
  type: rich-text
```

The key must be exactly `body`. Pages CMS treats that name specially in
frontmatter formats and maps it to the content below the delimiters.

## Step 2: map the fields

Pages CMS has two separate mechanisms for repeated values, and picking the
wrong one produces a config that loads but does not work.

- `list: true` repeats the whole widget. Use it for string, text, number,
  date, code, and object.
- `options.multiple` is built into the picker widgets. Use it for select,
  reference, image, and file.

### Strings

| Zod | Pages CMS |
| --- | --- |
| `z.string()`, short value | `type: string` |
| `z.string()`, a paragraph | `type: text` |
| `z.string()`, markdown | `type: rich-text` |
| `z.string()`, path to an image | `type: image` |
| `z.string()`, path to a document | `type: file` |
| `z.string().min(n)` | `options.minlength: n` |
| `z.string().max(n)` | `options.maxlength: n` |
| `z.string().regex(re)` | `pattern: { regex: ..., message: ... }` |
| `z.string().url()` | `type: string` plus a URL `pattern` |
| `z.string().email()` | `type: string` plus an email `pattern` |
| `z.string().uuid()` | `type: uuid`, `options.editable: false` |

`minlength` and `maxlength` belong to both `string` and `text`. Nothing else in
zod's string API has a Pages CMS counterpart, so `.trim()`, `.toLowerCase()`,
and friends silently do nothing on the CMS side.

### Numbers and booleans

| Zod | Pages CMS |
| --- | --- |
| `z.number()` | `type: number` |
| `z.number().min(a)` / `.max(b)` | `options.min` / `options.max` |
| `z.number().int()` | no equivalent, see below |
| `z.boolean()` | `type: boolean` |

The number field takes `min` and `max` and nothing else. There is no integer
constraint, so `z.number().int()` will happily receive `1.5` from the CMS and
fail at build time. Say so in `description`, or use a `pattern` on a string
field if the value has to be whole.

### Dates

| Zod | Pages CMS |
| --- | --- |
| `z.date()`, `z.coerce.date()` | `type: date`, `options.format: yyyy-MM-dd` |
| a date with a time component | add `options.time: true` |

```yaml
- name: date
  label: Date
  type: date
  options:
    format: yyyy-MM-dd
```

Two things bite here. Date fields prefill with today unless you set
`default: ""`, which quietly stamps every new entry with the creation date even
when the field means something else, like an event date. And `format` uses
date-fns tokens, not zod or Astro ones. `z.coerce.date()` parses almost
anything, so a wrong `format` will not fail the build. It just writes a
different shape than the files already on disk.

### Enums and fixed choices

| Zod | Pages CMS |
| --- | --- |
| `z.enum([...])` | `type: select`, `options.values` |
| `z.array(z.enum([...]))` | add `options.multiple: true` |
| `z.array(z.enum([...])).min(a).max(b)` | `options.min` / `options.max` |
| `z.nativeEnum(E)` | `type: select`, values written out by hand |
| `z.literal("x")` | `type: string`, `hidden: true`, `default: "x"` |

```yaml
- name: status
  type: select
  options:
    values: [publish, coming-soon]
```

For friendlier labels, use the object form. The stored value is `name`, not
`value`, which is an easy one to get backwards:

```yaml
options:
  values:
    - name: coming-soon
      label: Coming soon
```

Whatever you write in `values` has to match the zod enum exactly. A label
mismatch is invisible in the CMS and fails at build.

### Arrays and objects

| Zod | Pages CMS |
| --- | --- |
| `z.array(z.string())` | `type: string`, `list: true` |
| `z.array(X).min(a).max(b)` | `list: { min: a, max: b }` |
| `z.object({ ... })` | `type: object`, nested `fields` |
| `z.array(z.object({ ... }))` | `type: object`, `list: true`, nested `fields` |
| `z.tuple([...])` | approximate with `list: { min: n, max: n }` |
| `z.record(...)` | no equivalent |

```yaml
- name: faqs
  label: FAQs
  type: object
  list:
    collapsible:
      collapsed: true
      summary: "{question}"
  fields:
    - name: question
      type: string
    - name: answer
      type: text
```

Set a `summary` on any object list longer than about three entries. Without it
the editor shows a stack of identical collapsed rows.

### Images and files

| Zod | Pages CMS |
| --- | --- |
| `image()` | `type: image` |
| `z.array(image())` | `type: image`, `options.multiple: true` |
| `z.string()` holding an image path | `type: image` |
| `z.string()` holding a document path | `type: file` |

Note the asymmetry: multiple images use `options.multiple`, not `list: true`.

`image()` is the sharpest edge in this whole conversion. The helper returns
`ImageMetadata`, which means Astro has to resolve the path through its asset
pipeline at build time. That works for images under `src/`, and does not work
for anything in `public/`. Pages CMS, meanwhile, writes exactly one prefix into
the file, whatever `media.output` says. So the two have to be reconciled
deliberately:

- Point `media.input` and `media.output` at a directory under `src/` and
  confirm Astro resolves what the CMS writes.
- Or drop `image()` for `z.string()`, store public paths, and give up Astro's
  image optimization for those fields.

Do not guess which one works. Save one entry through the CMS and run
`astro build`. A broken `image()` path fails loudly, so the check is cheap.

### References

| Zod | Pages CMS |
| --- | --- |
| `reference("authors")` | `type: reference`, `options.collection: authors` |
| `z.array(reference("authors"))` | add `options.multiple: true` |

```yaml
- name: category
  label: Category
  type: reference
  options:
    collection: productCategories
    value: "{name}"
    label: "{fields.label}"
```

Astro resolves a reference by entry id, which is the path relative to the
collection base with the extension stripped. Pages CMS `value` controls what
actually lands in the file, so set it rather than trusting the default. For a
flat collection `{name}` matches the Astro id. Once `subfolders: true` is on,
Astro's id includes the folder and `{name}` does not, so check a real entry.

Use `label` to show editors something readable. A dropdown of raw filenames is
technically correct and useless.

### Modifiers

| Zod | Pages CMS |
| --- | --- |
| no modifier | `required: true` |
| `.optional()`, `.nullable()`, `.nullish()` | omit `required` |
| `.default(v)` | `default: v`, and do not mark it required |
| `.nullable().default(null)` | omit both `required` and `default` |
| `.catch(v)` | `default: v` |
| `.describe("...")`, or a JSDoc comment | `description: "..."` |
| `.transform(fn)` | no equivalent |
| `.refine(fn)` | only if it can be written as `pattern` |
| `z.union([...])` | no equivalent, see below |
| `z.discriminatedUnion(...)` | closest is `type: block` |
| `z.any()`, `z.unknown()` | no equivalent, mark `hidden: true` |

A field carrying `.default()` is optional in the file, since Astro fills it in
when the key is missing. Marking it `required: true` blocks editors on
something Astro would have handled, and `default: ""` combined with
`required: true` produces a form nobody can save.

`.transform()` and `.refine()` run after parsing, so the CMS never sees them.
The CMS writes the raw pre-transform value and the transform still applies at
build. That is usually fine. It stops being fine when a `.refine()` encodes a
rule editors can break, in which case restate it in `description` so at least
the failure is explicable.

For a plain `z.union`, pick the member that covers real content and accept the
narrowing, or split it into a `select` discriminator plus optional fields.
Neither is clean.

## Step 3: media

```yaml
media:
  input: public/images
  output: /images
```

`input` is where files land in the repo. `output` is the prefix written into
content. Named sources work too when different collections upload to different
places, and image fields then select one with `options.media`. Details in
`references/pagescms-fields.md`.

## Step 4: verify

Do not trust the config until it round-trips.

1. Put `.pages.yml` at the repo root.
2. Open an existing entry in the CMS, save it without editing, and run
   `git diff`. Empty diff means the mapping is faithful. Anything else is
   drift: reordered keys, a different date shape, quoting changes, a dropped
   field.
3. Create one new entry per collection.
4. Run `astro build`. Zod errors point straight at the field that is wrong.

Step 2 catches more than step 3. A config can accept new entries happily while
mangling every existing file it touches.

## Reference

- `references/pagescms-fields.md` for every Pages CMS field type and its exact
  `options` keys.
- `references/example.md` for a full worked conversion.

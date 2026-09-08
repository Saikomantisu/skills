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

Every YAML block below is an illustration, not a starting point. Media does not
live in `public/images` because this document says so, bodies are not `.md`,
posts do not have a `publishDate`. Those are the conventions of some repo that
is not the one you are looking at. Copy the reasoning; derive the values from
the schema, the folder, and the files in front of you. When a worked example
and the actual repo disagree, the repo is right.

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

A loader pattern like `**/*.{md,mdx}` accepts both extensions, but `filename`
is one template. Whichever extension you write there is the only one the CMS
will ever create; files already on disk with the other keep working. Look at
the folder and pick what it actually uses — `"{primary}.mdx"` for an MDX
collection, `"{primary}.md"` otherwise.

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

### MDX bodies need a decision

`rich-text` is a markdown WYSIWYG. MDX is markdown plus `import` statements and
JSX, and neither is markdown. An `.mdx` collection whose posts are plain prose
maps to `rich-text` with no trouble. One whose posts open with

```mdx
import Callout from "../../components/Callout.astro";
```

is asking the editor to round-trip syntax it does not model, and the failure
mode is a component silently flattened into a paragraph of text.

So find out before shipping the config rather than after. Set `body` to
`rich-text`, open the most component-heavy post in the collection, save it
untouched, and diff. A clean diff means `rich-text` is fine for this content.
A mangled one means the body needs `options.switcher: true` so editors can work
in source, or `type: text` to take the WYSIWYG out of the loop entirely.

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
| `z.string().refine(isOneOf)` | `type: select`, values written out by hand |
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

A fixed set of choices does not always arrive as `z.enum`. Astro projects that
need the list at runtime too — for a filter UI, a nav, a colour map — usually
keep it in a const array and validate against it:

```ts
export const CATEGORIES = ["Guides", "Notes", "Tools", "Releases"] as const;

category: z.string().refine(isValidCategory, { message: "..." }),
```

The zod type is `z.string()`, so nothing in the schema looks enum-shaped. Grep
the refine's predicate to its source array and map it to `select` anyway —
`type: string` here hands editors a free-text box for a closed set, and every
typo becomes a build failure.

Copy the values by hand and remember that the copy is now the drift risk. The
const array is the source of truth, `.pages.yml` is a snapshot, and nothing
connects them. When someone adds a category, the CMS keeps offering the old
four.

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
| `.refine(fn)` | `pattern`, or `select` when it tests list membership |
| `z.union([...])` | no equivalent, see below |
| `z.discriminatedUnion(...)` | closest is `type: block` |
| `z.any()`, `z.unknown()` | no equivalent, mark `hidden: true` |

A field carrying `.default()` is optional in the file, since Astro fills it in
when the key is missing. Marking it `required: true` blocks editors on
something Astro would have handled, and `default: ""` combined with
`required: true` produces a form nobody can save.

The table only runs one way. A CMS `default` is an editor convenience and owes
nothing to the schema, so it is fine — often better — to add one where zod has
none. On a single-author blog, `author` is `z.string()` with no default and
still deserves a `default:` in the config, because the alternative is retyping
the same name into every post and eventually misspelling it. The rule that
matters is the other direction: a zod `.default()` must not become
`required: true`.

`.transform()` and `.refine()` run after parsing, so the CMS never sees them.
The CMS writes the raw pre-transform value and the transform still applies at
build. That is usually fine. It stops being fine when a `.refine()` encodes a
rule editors can break, in which case restate it in `description` so at least
the failure is explicable. The exception is a `.refine()` that tests membership
in a list, which maps to `select` properly — see the enum section above.

For a plain `z.union`, pick the member that covers real content and accept the
narrowing, or split it into a `select` discriminator plus optional fields.
Neither is clean.

### What to leave out

A faithful conversion is not an exhaustive one. Two kinds of omission are
normal and one is a bug.

Fields the CMS has no business showing. A `readTime` computed from the body, an
`ogImage` generated at build, a `hidden` flag only the code sets — optional in
zod, absent from `.pages.yml`, and editors never see a box they should not
touch. Safe as long as the field really is optional. Omit a required one and
the CMS produces entries that fail `astro build` on a key the editor was never
offered.

Whole collections. Content that is really source — landing-page copy under
version control, a `skills` collection whose entries carry an SVG `iconPath` —
belongs to whoever edits the repo. Leaving it out of `.pages.yml` is a real
choice, not an oversight, and worth a comment in the file saying so, because
the next person will read a missing collection as an unfinished conversion.

The bug is omitting a field by accident, and it hides well. Whether Pages CMS
preserves frontmatter keys it does not know about on save is not something the
docs commit to, so do not assume either way. The empty-diff check in step 4
answers it for the version you are running, on the collection you care about.
If undeclared keys are getting stripped, every save quietly deletes data.

## Step 3: media

```yaml
media:
  input: public/images
  output: /images
  rename: safe
```

`input` is where files land in the repo. `output` is the prefix written into
content. Named sources work too when different collections upload to different
places, and image fields then select one with `options.media`. Details in
`references/pagescms-fields.md`.

### Always set `rename: safe`

Pages CMS defaults to `rename: false`, which commits the uploaded filename
byte for byte. Editors upload from a phone or a design tool, so that filename
is `IMG 2847 (1).JPG`, or `Screenshot 2026-08-26 at 14.02.31.png`, or
something with an em dash in it. That path then goes straight into frontmatter
and into markdown image syntax, where:

- spaces break bare `![](...)` links, which stop at the first space;
- parentheses break them again, closing the link early;
- an uppercase extension resolves on a case-insensitive local filesystem and
  404s on the case-sensitive host the site deploys to;
- non-ASCII characters get percent-encoded inconsistently across the CMS, git,
  and the host.

`rename: safe` slugifies on upload, so the same file lands as `img-2847-1.jpg`
and every consumer agrees on the path. Set it on every media source, including
each entry of the array form. `rename: random` is also safe but discards a
name editors can recognize in the media library, so prefer `safe` unless
filename collisions are the actual problem.

Two things to hold on to. Field-level `options.rename` on an `image`, `file`,
or `rich-text` field overrides the media source, so setting it to `false`
there reopens the hole for that one field. And renaming applies to uploads
only: media already committed under unsafe names stays unsafe, so rename those
on disk and fix their references in content at the same time. A half-migrated
folder produces broken links that read like a CMS bug.

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
- `references/example.md` for a minimal conversion and a full worked one.

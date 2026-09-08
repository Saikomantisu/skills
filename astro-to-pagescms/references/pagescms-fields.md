# Pages CMS reference

Target-side lookup. Everything here is from the Pages CMS docs at
`pagescms.org/docs/configuration/`.

## Top level

```yaml
media: ...      # upload locations and public path rewriting
content: ...    # collections and files
components: ... # reusable field definitions
settings: ...   # repo-wide behavior, merge mode, commit templates
actions: ...    # repo-level GitHub Actions buttons
```

## Content entry

| Property | Required | Meaning |
| --- | --- | --- |
| `name` | yes | internal id |
| `label` | no | UI label |
| `type` | yes | `collection`, `file`, or `group` |
| `path` | yes | folder for collections, file path for files, unused by groups |
| `fields` | no | field definitions |
| `filename` | no | filename template, collections only |
| `exclude` | no | files to ignore, e.g. `["README.md"]` |
| `format` | no | `yaml-frontmatter`, `json-frontmatter`, `toml-frontmatter`, `yaml`, `json`, `toml`, `datagrid`, `code`, `raw` |
| `delimiters` | no | custom frontmatter delimiters, e.g. `"+++"` |
| `subfolders` | no | `true` or `false` |
| `list` | no | repeat a field, or for `type: file` store the whole file as a top-level array |
| `view` | no | collection list settings |
| `operations` | no | per-entry create/rename/delete controls |
| `commit` | no | per-entry commit settings |
| `actions` | no | collection or file action buttons |
| `items` | no | child entries inside a `group` |

## view

```yaml
view:
  fields: [title, published, author.name]
  primary: title
  sort: [date, title]
  search: [title]
  layout: list        # or tree
  default:
    sort: date
    order: desc
```

`primary` defaults to `title` when a field by that name exists. `fields`
accepts dotted paths into objects. Tree layout adds `node.filename` and
`node.hideDirs` (`all`, `nodes`, or `others`).

## filename

String form, or an object when the filename input needs controlling:

```yaml
filename: "{primary}.md"
```

```yaml
filename:
  template: "{year}-{month}-{day}-{primary}.md"
  field: create   # false = hidden, create = only on new entries, true = always
```

Placeholders: `{primary}`, `{slug}` (alias for primary), `{year}`, `{month}`,
`{day}`, `{hour}`, `{minute}`, `{second}`, `{fields.<name>}`, and `{<name>}` as
shorthand for the last one. Field values are slugified.

## Field properties, all types

| Property | Meaning |
| --- | --- |
| `name` | required, the key in stored data |
| `type` | required unless `component` is set |
| `component` | reuse a definition from `components`, mutually exclusive with `type` |
| `label` | UI label, `false` hides it |
| `description` | helper text under the field |
| `required` | mandatory |
| `hidden` | not shown in the editor |
| `readonly` | shown but not editable, inherits down into nested fields |
| `pattern` | regex validation, string and text only |
| `default` | initial value on new entries |
| `list` | repeat as an array |
| `options` | type-specific |

`pattern` takes a bare string or an object:

```yaml
pattern:
  regex: "^[A-Z]{3}-\\d{4}$"
  message: "Use format ABC-1234"
```

`list` takes `true` or an object:

```yaml
list:
  min: 1
  max: 6
  collapsible:
    collapsed: true
    summary: "{title} ({index})"
```

`summary` accepts `{index}`, `{fields.<name>}`, and `{<name>}`.

In frontmatter formats the field named `body` maps to the content below the
delimiters.

## Field types

Fourteen of them: `block`, `boolean`, `code`, `date`, `file`, `image`,
`number`, `object`, `reference`, `rich-text`, `select`, `string`, `text`,
`uuid`.

### string

`options`: `minlength`, `maxlength`. Single-line input.

```yaml
- name: title
  type: string
  options:
    maxlength: 120
```

### text

`options`: `minlength`, `maxlength`. Multi-line plain text, no formatting.

### rich-text

`options`: `format` (`markdown` or `html`, markdown is the default),
`switcher`, `media`, `path`, `extensions`, `categories`, `rename`.

```yaml
- name: body
  label: Body
  type: rich-text
  options:
    media: content_images
    path: public/images/blog
    rename: safe
    switcher: true
```

`switcher: true` gives editors a WYSIWYG/source toggle.

### number

`options`: `min`, `max`. No step, no integer constraint.

### boolean

No options. Set `default: true` or `default: false`.

### date

`options`: `time`, `format` (date-fns tokens), `min`, `max`, `step`.

```yaml
- name: publish_at
  type: date
  default: ""
  options:
    time: true
    format: yyyy-MM-dd'T'HH:mm
```

Prefills with the current date, or current date and time when `time: true`.
`default: ""` turns that off.

### select

`options`: `values` (required), `multiple`, `min`, `max`, `placeholder`.
Only static local values. For anything dynamic use `reference`.

```yaml
- name: categories
  type: select
  options:
    values:
      - name: art
        label: Art
      - name: fashion
        label: Fashion
```

`name` is stored, `label` is displayed. A plain array of strings works when
the two are the same.

### reference

`options`: `collection`, `multiple`, `min`, `max`, `search`, `value`, `label`.

```yaml
- name: author
  type: reference
  options:
    collection: authors
    search: "name,email,fields.role"
    value: "{primary}"
    label: "{primary}"
```

`value` and `label` accept `{path}`, `{name}`, `{primary}`,
`{fields.<path>}`, and `{<path>}`. `search` is a comma-separated string, not
an array.

### image

`options`: `media`, `path`, `multiple`, `extensions`, `categories`, `unique`,
`rename`.

```yaml
options:
  multiple:
    max: 6
```

Multiple images go through `options.multiple`, not `list: true`. `rename`
takes `false`, `true`, `safe`, or `random`. `unique: true` blocks duplicate
paths when multiple is on.

### file

Same shape as `image`, pointed at documents rather than images.

### object

No options. Declare nested `fields`. Add `list: true` for an array of objects.

```yaml
- name: authors
  type: object
  list: true
  fields:
    - name: name
      type: string
    - name: email
      type: string
```

`required` applies to the object itself, not automatically to its children. On
an optional object, child `required` rules only kick in once the object has
content.

### uuid

`options`: `editable`, `generate`. Generates a v4 UUID when there is no
explicit `default`. Set `default: ""` to start empty.

```yaml
- name: id
  type: uuid
  options:
    editable: false
```

### code

For source snippets. Check the docs for its language options.

### block

For polymorphic content, where a list holds items of different shapes. The
closest thing Pages CMS has to a discriminated union. Check the docs for the
exact shape before using it.

## media

String form:

```yaml
media: media   # means input: media, output: /media
```

Object form:

```yaml
media:
  input: src/media
  output: /media
  rename: safe
  categories: [image]
```

Named sources, selected per field with `options.media`:

```yaml
media:
  - name: images
    input: media/images
    output: /media/images
    rename: safe
  - name: docs
    input: media/docs
    output: /media/docs
    rename: safe
    categories: [document]
```

| Key | Meaning |
| --- | --- |
| `name` | required when using the array form |
| `label` | UI label |
| `input` | where files are written in the repo |
| `output` | prefix written into content files |
| `extensions` | allowlist, e.g. `["png", "jpg", "webp"]` |
| `categories` | `image`, `document`, `video`, `audio`, `compressed`, `code`, `font`, `spreadsheet` |
| `rename` | `false` keeps the original, `true`/`safe` slugifies, `random` generates |

`input` and `output` are independent. Files stored at `media/images/` can be
referenced as `/media/images/` in content.

`rename` defaults to `false`, which commits whatever the editor's file was
called, spaces and capitals and all. Always write `rename: safe`, on every
source in the array form. See the media section of `SKILL.md` for what breaks
without it.

### rename on fields

`image`, `file`, and `rich-text` all take `options.rename`, which overrides the
media source for that field. It exists to tighten a source that is loose, not
to loosen one that is safe. Leave it unset and inherit `safe`.

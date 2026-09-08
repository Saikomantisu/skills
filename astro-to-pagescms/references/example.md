# Worked example

A real conversion, start to finish, plus a second one that hits the `image()`
problem.

## Source

```ts
// src/content.config.ts
import { defineCollection, reference } from "astro:content";
import { glob } from "astro/loaders";
import { z } from "astro/zod";

const faqs = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/faqs" }),
  schema: z.object({
    question: z.string(),
    order: z.number().default(0),
  }),
});

const events = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/events" }),
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    /** Short blurb shown on the list card and as the intro on the detail page. */
    summary: z.string(),
    location: z.string().optional(),
    image: z.string(),
    imageAlt: z.string().default(""),
    /** Extra photos shown in a grid under the body on the detail page. */
    gallery: z
      .array(z.object({ src: z.string(), alt: z.string().default("") }))
      .default([]),
  }),
});

const productCategories = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/product-categories" }),
  schema: z.object({
    label: z.string(),
    image: z.string(),
    order: z.number().default(0),
  }),
});

const products = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/products" }),
  schema: z.object({
    brand: z.string(),
    name: z.string(),
    category: reference("productCategories"),
    image: z.string().nullable().default(null),
    description: z.string(),
  }),
});

export const collections = { faqs, events, productCategories, products };
```

## Decisions made before writing YAML

Reading the markdown files answered four things zod could not:

- `image` and `gallery[].src` hold paths like `/images/events/expo.jpg`, so
  they are `image` fields, not strings. Public paths, so `media.output` is
  `/images`.
- `summary` and `description` run two or three sentences, so `text`, not
  `string`.
- The faq answer lives in the markdown body, so `faqs` needs a `body` field
  and `question` is the primary.
- `path` for `productCategories` is `src/content/product-categories`. The
  Astro key is camelCase, the folder is kebab-case, and Pages CMS needs the
  folder. The `name` stays camelCase so `reference()` lines up.

## Result

```yaml
media:
  input: public/images
  output: /images

content:
  - name: faqs
    label: FAQs
    type: collection
    path: src/content/faqs
    filename: "{primary}.md"
    format: yaml-frontmatter
    view:
      fields: [question, order]
      primary: question
      sort: [order, question]
      default:
        sort: order
        order: asc
    fields:
      - name: question
        label: Question
        type: string
        required: true
      - name: order
        label: Order
        type: number
        default: 0
      - name: body
        label: Answer
        type: rich-text

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
    fields:
      - name: title
        label: Title
        type: string
        required: true
      - name: date
        label: Date
        type: date
        default: ""
        required: true
        options:
          format: yyyy-MM-dd
      - name: summary
        label: Summary
        type: text
        required: true
        description: Short blurb shown on the list card and as the intro on the detail page.
      - name: location
        label: Location
        type: string
      - name: image
        label: Image
        type: image
        required: true
      - name: imageAlt
        label: Image alt text
        type: string
        default: ""
      - name: gallery
        label: Gallery
        type: object
        list:
          collapsible:
            collapsed: true
            summary: "{alt}"
        description: Extra photos shown in a grid under the body on the detail page.
        fields:
          - name: src
            label: Photo
            type: image
            required: true
          - name: alt
            label: Alt text
            type: string
            default: ""
      - name: body
        label: Body
        type: rich-text

  - name: productCategories
    label: Product categories
    type: collection
    path: src/content/product-categories
    filename: "{primary}.md"
    format: yaml-frontmatter
    view:
      fields: [label, order]
      primary: label
      sort: [order, label]
      default:
        sort: order
        order: asc
    fields:
      - name: label
        label: Label
        type: string
        required: true
      - name: image
        label: Image
        type: image
        required: true
      - name: order
        label: Order
        type: number
        default: 0
      - name: body
        label: Body
        type: rich-text

  - name: products
    label: Products
    type: collection
    path: src/content/products
    filename: "{primary}.md"
    format: yaml-frontmatter
    view:
      fields: [name, brand, category]
      primary: name
      sort: [name, brand]
      search: [name, brand]
    fields:
      - name: brand
        label: Brand
        type: string
        required: true
      - name: name
        label: Name
        type: string
        required: true
      - name: category
        label: Category
        type: reference
        required: true
        options:
          collection: productCategories
          value: "{name}"
          label: "{fields.label}"
      - name: image
        label: Image
        type: image
      - name: description
        label: Description
        type: text
        required: true
      - name: body
        label: Body
        type: rich-text
```

## Why each non-obvious call was made

`date` carries both `default: ""` and `required: true`. Without the empty
default every new event is stamped with today, which is wrong for a field that
means "when the event happens". Required still forces the editor to pick one.

`order` has `default: 0` and no `required`. Astro fills the key in when it is
missing, so demanding it in the CMS would block a save over nothing.

`image` on `products` is `.nullable().default(null)`, so it gets neither
`required` nor `default`. Writing `default: null` would put a literal `null`
into the frontmatter of every new product. Astro's default already covers the
absent case.

`gallery` uses `list` with a collapsed summary. It is an array of objects and
those stack up fast in the editor.

`category` sets `value: "{name}"` because Astro resolves references by entry
id, which for this flat collection is the filename without `.md`. `label`
shows the human-readable category instead of a filename.

## The `image()` case

A different project, same idea, one extra problem:

```ts
const blogs = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/blogs' }),
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      excerpt: z.string().max(120),
      thumbnail: image(),
      author: z.string(),
      createdAt: z.coerce.date(),
    }),
});
```

The straightforward mapping:

```yaml
- name: blogs
  label: Blog posts
  type: collection
  path: src/content/blogs
  filename: "{primary}.md"
  format: yaml-frontmatter
  view:
    fields: [title, author, createdAt]
    primary: title
    sort: [createdAt, title]
    default:
      sort: createdAt
      order: desc
  fields:
    - name: title
      label: Title
      type: string
      required: true
    - name: excerpt
      label: Excerpt
      type: text
      required: true
      options:
        maxlength: 120
    - name: thumbnail
      label: Thumbnail
      type: image
      required: true
    - name: author
      label: Author
      type: string
      required: true
    - name: createdAt
      label: Created
      type: date
      default: ""
      required: true
      options:
        format: yyyy-MM-dd
    - name: body
      label: Body
      type: rich-text
```

That YAML is correct and the build can still fail. `thumbnail: image()` makes
Astro resolve the path through its asset pipeline, which only handles images
under `src/`. If `media.output` is `/images` pointing at `public/`, Astro
cannot resolve what the CMS wrote and the build dies on that entry.

Two ways out. Keep `image()` and put media under `src/`, checking that the
prefix Pages CMS writes is one Astro resolves. Or change the schema to
`z.string()`, store public paths, and lose image optimization on that field.

Either way, save one post through the CMS and run `astro build` before
declaring it done.

## Note on `excerpt`

`z.string().max(120)` becomes `options.maxlength: 120` on a `text` field. The
CMS now enforces the same limit the schema does, so editors find out while
typing instead of at build time. Carry `min`/`max` across whenever zod has
them. It is the cheapest quality win in the whole conversion.

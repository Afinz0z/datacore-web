# Design system

All tokens live in `:root` at the top of `src/css.py`. Use variables, never raw
hex values.

## Colour

| Token | Value | Use | Contrast on white |
|---|---|---|---|
| `--ink` | `#1A1B1F` | body text, footer, dark bands | 16.4:1 |
| `--ink-2` | `#565C61` | secondary text | 7.0:1 |
| `--ink-3` | `#7C848A` | labels, metadata | 4.0:1 — large text only |
| `--accent` | `#00776F` | links, buttons, anything with text | **5.43:1** |
| `--accent-d` | `#005A54` | hover on accent | 7.6:1 |
| `--brand` | `#00ACA1` | logo, dots, fills — **never text** | 2.83:1 ✗ |
| `--paper` | `#F4F7F6` | alternating sections | — |
| `--mint` | `#EAF6F4` | hero wash, CTA band, hover | — |
| `--line` / `--line-2` | `#E2E8E6` / `#CBD5D2` | borders | — |
| `--amber` | `#8A5A0F` | lead-time / on-order status | 6.2:1 |

`--brand` and `--accent` are the same hue. The split exists because the logo
teal fails WCAG AA. Putting white text on `--brand` is the most common way to
break this design.

## Type

- **Archivo** 400/500/600/700 — Latin, all sizes
- **IBM Plex Sans Arabic** 400/500/600/700 — Arabic, swapped via `html[dir=rtl]`
- **IBM Plex Mono** 400/500 — data only: part numbers, scope counts, standards
  strings, breadcrumbs. Functional, not decorative — monospace prevents 0/O
  confusion in SKUs.

Headings: `line-height: 1.14`, `letter-spacing: -0.02em`. Body: 16px / 1.55.

Arabic overrides both: `line-height: 1.9` body, `1.45` headings,
`letter-spacing: 0`. Arabic set at Latin leading looks cramped and tracked-out
Arabic is close to unreadable.

Display sizes use `clamp()` and scale with viewport. Body measure is capped at
52–62 characters.

## Spacing

8px base: `--s1` 8, `--s2` 16, `--s3` 28, `--s4` 48, `--s5` 80, `--s6` 120.
Section padding is `--s6` desktop, `--s5` below 860px. Page gutter is
`clamp(20px, 5vw, 56px)`. Shell max-width 1280px.

## Components

- **Buttons** `.btn-p` (filled accent) / `.btn-s` (outline). 2px radius.
- **Discipline / service cards** — 1px gap over a `--line` background, so the
  grid reads as a table rather than floating cards
- **Project cards** — dark band header carrying sector and city
- **Stack** — the hero's nine-discipline list; the signature element
- **Filter chips** — the only pill-shaped element on the site
- **Facets** — sticky sidebar, counts computed per dimension
- **Drawers** — slide from `inset-inline-end`, so they mirror in Arabic
- **Map facade** — CSS grid pattern, loads the iframe on click

## Motion

One orchestrated moment: the hero stack rises in on load with a 50ms stagger.
Everything else is hover and state change only. All animation is disabled under
`prefers-reduced-motion`.

## Breakpoints

1080px (3-up grids drop to 2-up) and 860px (single column, burger menu). No
separate mobile stylesheet.

## Accessibility floor

WCAG 2.1 AA. Skip link, `:focus-visible` rings at 2px offset 3px, visible and
persistent form labels, `aria-current` on nav, `aria-pressed` on toggles,
`aria-hidden` managed on drawers, Escape closes overlays, breadcrumbs below top
level. Colour is never the only signal — the active nav item also changes weight.

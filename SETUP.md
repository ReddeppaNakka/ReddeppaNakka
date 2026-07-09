# Setup, Configuration & Maintenance Guide

Everything needed to run, customise, and keep this profile alive — plus an honest account of what GitHub Markdown will and won't do.

---

## Read this first

Every URL in the README was fetched and verified. **99 of 110 returned `200`.** The failures are not typos — they are two upstream services that were down at the time of writing, plus images that don't exist yet:

| Failing | Count | Why | Action |
|:--|:--:|:--|:--|
| `github-readme-stats.vercel.app` | 9 | `503` — the shared public instance is overloaded. This affects **every profile on GitHub that uses it**, not just yours. | [Self-host it](#fixing-the-github-readme-stats-rate-limit) — 4 minutes, permanent fix |
| `github-profile-trophy.vercel.app` | 1 | `402 Payment Required` — the maintainer's Vercel account is over its free quota. | Self-host the same way, or delete the trophy row |
| `raw.githubusercontent.com/.../output/snake.svg` | 1 | The `output` branch doesn't exist until the workflow runs once. | Actions → *Generate Contribution Snake* → **Run workflow** |

Those nine stats cards are the visual centre of the profile. **Self-host `github-readme-stats` before you show this to anyone.** Everything else — the header, typing banner, badges, skill icons, dividers, radar, heatmap, activity graph, quote widget, and all 133 images' alt text — is verified working.

---

## Contents

0. [Read this first](#read-this-first)
1. [Installation](#installation)
2. [What actually renders on GitHub](#what-actually-renders-on-github)
3. [External services](#external-services)
4. [GitHub Actions workflows](#github-actions-workflows)
5. [Dynamic README updates](#dynamic-readme-updates)
6. [Customisation](#customisation)
7. [Adding achievements](#adding-achievements)
8. [Coding platform stats](#coding-platform-stats)
9. [WakaTime & Spotify](#wakatime--spotify)
10. [AI assistant integration](#ai-assistant-integration)
11. [Technical blog automation](#technical-blog-automation)
12. [Performance](#performance)
13. [Mobile optimisation](#mobile-optimisation)
14. [Accessibility](#accessibility)
15. [SEO & discoverability](#seo--discoverability)
16. [Maintenance](#maintenance)
17. [Troubleshooting](#troubleshooting)

---

## Installation

The README only renders as a profile if the repository name **exactly matches your username**.

```bash
# 1. The repo must be named ReddeppaNakka/ReddeppaNakka and be PUBLIC.
git clone https://github.com/ReddeppaNakka/ReddeppaNakka.git
cd ReddeppaNakka

# 2. Copy these files in.
#    README.md · SETUP.md · assets/ · scripts/ · .github/

# 3. Ship.
git add .
git commit -m "feat: premium profile README"
git push origin main
```

**Repository settings → Actions → General**, then set *Workflow permissions* to **Read and write**. Both workflows push commits; without this they fail with a `403`.

### File tree

```
ReddeppaNakka/
├── README.md                       ← the profile itself
├── SETUP.md                        ← this file
├── assets/
│   ├── divider-gradient.svg        ← animated sweeping gradient rule
│   ├── divider-pulse.svg           ← travelling orb divider
│   └── stack-radar.svg             ← hand-authored technology radar
├── scripts/
│   └── update_readme.py            ← refreshes the activity block
└── .github/workflows/
    ├── snake.yml                   ← contribution snake → `output` branch
    └── update-readme.yml           ← runs the script twice daily
```

---

## What actually renders on GitHub

Read this before adding anything. GitHub runs every README through a **HTML sanitizer**, and most "premium GitHub profile" tutorials quietly ignore it.

| Technique | Works? | Notes |
|:--|:--:|:--|
| `<img>`, `<a>`, `<table>`, `<div align>` | Yes | The backbone of this profile. |
| `<details>` / `<summary>` | Yes | **The only genuine interactivity available.** Used for the terminal and project cards. |
| `<picture>` + `prefers-color-scheme` | Yes | Real light/dark theming. Used for the snake. |
| Animated SVG served as an `<img>` | Yes | SMIL animation inside the SVG survives. This is how the dividers move. |
| `<style>` blocks | **No** | Stripped entirely. |
| `style="..."` attributes | **No** | Stripped. There is no CSS glassmorphism, no `backdrop-filter`, no `box-shadow`. |
| `class=` / `id=` hooks | **No** | Stripped (`id` is rewritten to `user-content-*`). |
| `<script>` | **No** | Stripped. **No JS runs in a README, ever.** |
| `<iframe>`, `<embed>`, `<canvas>` | **No** | Stripped. |
| CSS `:hover` effects | **No** | Requires CSS. Only the browser's native link/image behaviour survives. |

**What this means in practice.** Depth, glow, and "glassmorphism" must be **baked into an image** (an SVG or a rendered PNG) before GitHub ever sees it. A card looks glassy because a gradient was drawn into the SVG, not because CSS blurred a backdrop. Anything promising hover animations or an embedded chat widget inside a README is showing you a screenshot of something hosted elsewhere.

Motion in this profile comes from exactly three legitimate sources: SMIL-animated SVGs in `assets/`, animated SVGs returned by external services (Capsule Render, Typing SVG), and the snake GIF/SVG generated by Actions.

---

## External services

Every remote image in the README, what it does, and how it can fail.

| Service | Used for | Auth | Risk |
|:--|:--|:--|:--|
| [capsule-render](https://github.com/kyechan99/capsule-render) | Header & footer waves | None | Community Vercel instance; occasional cold starts |
| [readme-typing-svg](https://github.com/DenverCoder1/readme-typing-svg) | Typing banner | None | Stable |
| [github-readme-stats](https://github.com/anuraghazra/github-readme-stats) | Stats, top langs, pin cards | None | **Shared instance is rate-limited — see below** |
| [github-readme-streak-stats](https://github.com/DenverCoder1/github-readme-streak-stats) | Streak counter | None | Stable |
| [github-readme-activity-graph](https://github.com/Ashutosh00710/github-readme-activity-graph) | Contribution line graph | None | Stable |
| [github-profile-trophy](https://github.com/ryo-ma/github-profile-trophy) | Trophy row | None | Stable |
| [ghchart](https://github.com/2016rshah/githubchart-api) | Contribution heatmap | None | Occasionally slow |
| [shields.io](https://shields.io) | All badges | None | Very stable |
| [skillicons.dev](https://skillicons.dev) | Tech icons | None | Very stable |
| [geps.dev/progress](https://geps.dev) | Goal progress bars | None | Stable |
| [komarev ghpvc](https://github.com/antonkomarev/github-profile-views-counter) | Profile view counter | None | Stable |
| [quotes-github-readme](https://github.com/PiyushSuthar/github-readme-quotes) | Quote of the day | None | Stable |
| `api.github-star-counter.workers.dev` | Total-star badge | None | **Third-party worker; if it dies the badge shows `invalid`** |

### Fixing the `github-readme-stats` rate limit

The public instance is shared by hundreds of thousands of profiles and its GitHub API quota is regularly exhausted. When that happens your stats card renders as **"Maximum retries exceeded"**. This is the single most common reason a profile looks broken.

Deploy your own — it takes about four minutes and is permanent:

```bash
git clone https://github.com/anuraghazra/github-readme-stats.git
cd github-readme-stats
npm i -g vercel && vercel        # accept defaults
# In the Vercel dashboard: Settings → Environment Variables
#   PAT_1 = <a GitHub personal access token, no scopes needed for public data>
vercel --prod
```

Then swap the host in the README (four occurrences — stats, top-langs, wakatime, and all pin cards):

```
https://github-readme-stats.vercel.app/api/...
                ↓
https://<your-project>.vercel.app/api/...
```

The same applies to `github-profile-trophy` — which at time of writing returns `402 Payment Required`, meaning its Vercel free-tier quota is exhausted. Fork [`ryo-ma/github-profile-trophy`](https://github.com/ryo-ma/github-profile-trophy), deploy to your own Vercel account, and swap the host. If you'd rather not, delete the trophy row: a row of broken image icons costs you more credibility than a row of trophies buys.

---

## GitHub Actions workflows

### `snake.yml`

Reads your contribution graph and renders a snake eating it, then force-pushes the SVGs to a branch called `output`. The README reads them from `raw.githubusercontent.com`.

- Runs at `00:00` and `12:00` UTC, on push to `main`, and on demand.
- Cron on GitHub is **best-effort** — a run scheduled for midnight may land twenty minutes late, or be skipped when the runner fleet is busy. It will catch up.
- The `output` branch is generated. Never commit to it by hand; the workflow force-pushes.
- Light and dark variants are generated separately and selected by `<picture>`.

**First run:** the snake images 404 until the workflow completes once. Go to **Actions → Generate Contribution Snake → Run workflow**.

### `update-readme.yml`

Runs `scripts/update_readme.py` twice daily and commits only if the content genuinely changed.

---

## Dynamic README updates

`scripts/update_readme.py` rewrites only the text between marker pairs. Everything outside them is never parsed and cannot be damaged.

```html
<!-- RECENT_ACTIVITY:start -->
...replaced on each run...
<!-- RECENT_ACTIVITY:end -->

<sub>Last refreshed: <!-- LAST_UPDATED:start -->…<!-- LAST_UPDATED:end --></sub>
```

Three deliberate behaviours:

1. **It does not manufacture contributions.** The timestamp is refreshed *only* when the activity list itself changed. A naive implementation rewrites the timestamp every run, producing two commits a day forever and inflating your contribution graph with work nobody did. This one stays quiet on quiet days.

2. **It never prints a number it doesn't have.** The unauthenticated events API omits `payload.size` on push events. Rather than render a confident `0 commits`, the script omits the count.

3. **It aborts rather than guesses.** A missing marker pair exits non-zero instead of appending content to an arbitrary location.

Repeated events on one repository collapse to a single row, and repositories you don't own are tagged `collaboration`.

Run it locally:

```bash
GH_USERNAME=ReddeppaNakka python scripts/update_readme.py
```

Set `GITHUB_TOKEN` to raise the API limit from 60 to 5,000 requests/hour. The workflow supplies it automatically.

---

## Customisation

### Colour palette

Defined once, repeated everywhere as hex in query strings. To re-theme, find-and-replace across `README.md` and `assets/*.svg`:

| Token | Hex | Role |
|:--|:--|:--|
| Electric blue | `2563EB` | Primary |
| Purple | `8B5CF6` | Headings, accents |
| Cyan | `06B6D4` | Highlights, typing text |
| Emerald | `10B981` | Success, availability |
| Canvas | `0D1117` | Background (matches GitHub dark) |
| Muted | `94A3B8` | Secondary text |

> `0D1117` is GitHub's own dark-mode canvas. That's why the cards look inset rather than pasted on. **In light mode they become dark rectangles on white** — an accepted trade almost every profile makes. To go theme-aware, wrap each card in `<picture>` with two `srcset`s and a `bg_color` per theme.

### The typing banner

Lines are `;`-separated and URL-encoded. Spaces are `+`, and `%2C` is a comma:

```
&lines=First+line;Second+line+with+a+%2C+comma
```

Keep every line under about 60 characters or it clips on mobile. Update the `alt` text to match — it's the only version a screen reader reads.

### The technology radar

`assets/stack-radar.svg` is hand-authored. Six axes; the data polygon is one `<polygon points="...">`. Centre is `(260, 230)`, and each axis runs 200px outward. To move a vertex to `f` (0…1) along its axis, interpolate from centre toward that axis's outer point.

Values shown are **self-assessed and deliberately uneven**. A radar pinned at 100% on every axis reads as a lack of self-awareness, which is the opposite of the signal you want.

---

## Adding achievements

Drop a row into the Achievements table:

```markdown
| <img src="https://img.shields.io/badge/AWS-Solutions_Architect-8B5CF6?style=flat-square&logo=amazonwebservices&logoColor=white&labelColor=0D1117" alt="AWS Solutions Architect Associate" /> | Issued Mar 2027 · [Verify](https://credly.com/…) |
```

Rules that keep this section credible:

- Always link the verification page. An unverifiable certification badge is worth less than no badge.
- Never add a badge for a course you started. "Enrolled" is not an achievement.
- If a section has nothing real in it, **leave the honest placeholder**. A recruiter who spots one inflated claim discounts the entire profile.

---

## Coding platform stats

Currently omitted by design — an empty stat card is worse than none. When you have profiles worth showing, paste the relevant block back in.

```markdown
<!-- LeetCode -->
<img src="https://leetcard.jacoblin.cool/USERNAME?theme=dark&font=JetBrains+Mono&ext=heatmap" alt="LeetCode statistics" />

<!-- Codeforces -->
<img src="https://codeforces-readme-stats.vercel.app/api/card?username=USERNAME&theme=dark" alt="Codeforces rating" />

<!-- GeeksforGeeks -->
<img src="https://gfgstatscard.vercel.app/USERNAME?theme=dark" alt="GeeksforGeeks statistics" />

<!-- HackerRank — no stats API exists; link the profile instead -->
<a href="https://hackerrank.com/USERNAME"><img src="https://img.shields.io/badge/HackerRank-0D1117?style=for-the-badge&logo=hackerrank&logoColor=10B981" alt="HackerRank profile" /></a>

<!-- CodeChef — no official card; use a badge -->
<a href="https://codechef.com/users/USERNAME"><img src="https://img.shields.io/badge/CodeChef-0D1117?style=for-the-badge&logo=codechef&logoColor=8B5CF6" alt="CodeChef profile" /></a>
```

Add the section **only once the numbers help you.** `12 problems solved` is worse than silence.

---

## WakaTime & Spotify

Both are currently omitted. Each renders a broken image until fully configured, so wire them up *before* pasting them in.

### WakaTime

Genuinely useful — it's real evidence of hours spent, which almost no profile has.

1. Sign up at [wakatime.com](https://wakatime.com) and install the plugin for your editor.
2. **Profile → Settings → check "Display coding activity publicly"** and *"Display languages…"*. The card 404s without this.
3. Let it collect for **at least a week**. A card reading `0 hrs` is worse than no card.
4. Paste in:

```markdown
<img src="https://github-readme-stats.vercel.app/api/wakatime?username=WAKA_USER&layout=compact&hide_border=true&bg_color=0D1117&title_color=8B5CF6&text_color=94A3B8" alt="Weekly coding activity by language" />
```

The README does **not** currently include this card. A commented-out placeholder marks where it belongs, in the GitHub Analytics section. Complete steps 1–3 first, then paste the line in — pasting it early is what produces the broken card you see on so many profiles.

### Spotify

1. Deploy [`spotify-github-profile`](https://github.com/kittinan/spotify-github-profile) to Vercel.
2. Create an app at [developer.spotify.com](https://developer.spotify.com/dashboard), add the Vercel callback as a redirect URI.
3. Visit `https://<your-app>.vercel.app/api/login`, authorise, and copy the generated Markdown.

Consider whether it earns its space. It signals personality, not skill, and it exposes your listening history to every recruiter who opens the page.

---

## AI assistant integration

**A chat widget cannot run inside a README.** `<script>` is stripped, `<iframe>` is stripped. Every profile claiming an embedded assistant is displaying a static image.

The workable pattern is to host it and link out:

```
README  ──button──▶  ask.your-portfolio.app
                         │
                         ├─ Next.js route handler (Vercel)
                         ├─ RAG: résumé + repo READMEs + project docs
                         ├─ Embeddings in Supabase pgvector
                         └─ Claude SDK for generation
```

Ingest your own repository READMEs via the GitHub API so the assistant stays current as you ship. Rate-limit the endpoint — a public LLM endpoint with your API key behind it is an invitation.

---

## Technical blog automation

Once you've published articles, this workflow keeps the section current:

```yaml
name: Sync Blog Posts
on:
  schedule: [{ cron: "0 6 * * *" }]
  workflow_dispatch:
permissions:
  contents: write
jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: gautamkrishnar/blog-post-workflow@v1
        with:
          max_post_count: 5
          feed_list: "https://dev.to/feed/USERNAME,https://medium.com/feed/@USERNAME"
          comment_tags_name: "BLOG"
```

Add the markers where the posts should land:

```html
<!-- BLOG:START -->
<!-- BLOG:END -->
```

---

## Performance

The README loads **roughly 40 remote images**. Each one is proxied through GitHub's Camo, so a slow upstream service delays that image only — the page never blocks. Still:

- **Every dynamic card costs a round trip.** Cut anything that isn't earning attention.
- **`<details>` content still loads its images** when collapsed in most browsers. It reduces visual clutter, not bytes.
- **Prefer `skillicons.dev` over many individual shields** — one request instead of eight.
- **Local SVGs in `assets/` are fastest**, served from GitHub's own CDN with no third-party dependency.
- Set explicit `width` on images so the layout doesn't shift as they arrive.
- Camo caches aggressively. After changing an SVG in `assets/`, the old version may serve for a while; a hard refresh or a filename change busts it.

---

## Mobile optimisation

Roughly half of profile views arrive on a phone, where GitHub renders the README in a narrow single column.

- **Two-column `<table>` layouts collapse to stacked cells.** This is fine and intended. Three columns get cramped — the *Currently* section is the practical limit.
- **`width="49%"` on paired pin cards** lets them sit side by side on desktop and stack on mobile. Never use fixed pixel widths for these.
- **ASCII diagrams inside fenced code blocks scroll horizontally** rather than wrapping. Keep them under ~70 characters wide. Every diagram in this README obeys that.
- **Typing-banner lines clip past ~60 characters** at phone widths.
- The trophy row uses `column=7`, which scrolls on mobile. Drop to `column=4` if that bothers you.
- Test properly: GitHub mobile web, not just a narrowed desktop window.

---

## Accessibility

Most "premium" profiles are a wall of unlabelled images. This one isn't, and it should stay that way.

- **Every meaningful image carries a real `alt`.** Not `alt="stats"` — `alt="GitHub statistics for ReddeppaNakka"`. Decorative dividers correctly use `alt=""` so screen readers skip them.
- **The typing banner's `alt` contains the full sentence.** It's animated text inside an image; without it, the sentence is invisible to assistive tech.
- **The radar has `<title>` and `<desc>`** wired via `aria-labelledby`, describing the shape in words.
- **ASCII architecture diagrams read poorly aloud.** Each is preceded by a prose sentence carrying the same information, so nothing is diagram-only.
- **Don't rely on colour alone.** The goal bars pair each colour with a numeric `alt` and a text note.
- **Respect motion sensitivity.** The dividers animate on a 7–9 second loop — slow, low-contrast, non-flashing. Nothing pulses faster than 3 Hz, the photosensitive-epilepsy threshold. `prefers-reduced-motion` is *not* honoured by GitHub's sanitizer, so restraint in the source is the only control available.
- **Contrast:** `#94A3B8` on `#0D1117` is about 7.4:1, comfortably past WCAG AA. If you darken the muted colour, re-check it.

---

## SEO & discoverability

GitHub profiles are indexed by Google and searched internally by recruiters.

- **The bio field matters more than the README.** It's the `<meta description>` for your profile and it appears in GitHub's own user search. Make it specific: *"Backend & AI engineer · FastAPI, LangChain, Next.js · Hyderabad"*.
- **Set the profile's `Location` and `Website`.** Recruiters filter on location.
- **Topics on repositories are the strongest lever available.** Add them to all six featured projects: `fastapi`, `langchain`, `agentic-ai`, `nextjs`, `machine-learning`, `deep-learning`. GitHub search ranks on topics.
- **Repository descriptions are search-indexed.** Four of yours are empty — `Orvix`, `Signal_IQ`, `Treckgroq`, and `Voice_Agent`. Fixing that is the highest-value ten minutes in this entire document.
- **Add a `LICENSE`.** Unlicensed code is legally "all rights reserved," which discourages the contributions and forks that drive discovery.
- **The first 160 characters of the README** are what Google shows. Front-load them.
- **Pin the six featured repositories** so they match this README's order.
- **Alt text is indexed.** Descriptive alt text is simultaneously an accessibility and an SEO win.

---

## Maintenance

Keeping a profile alive is mostly about deleting things that have gone stale.

**Monthly**
- Do the goal percentages still reflect reality? Move them. A dashboard frozen for six months is a dead dashboard.
- Are the *Currently reading / exploring / building* cards still true? These are the fastest things to rot and the most obvious when they do.
- Check for broken images — a service disappears roughly once a year.

**Quarterly**
- Re-order featured projects so the strongest work is first.
- Update the timeline with anything genuinely new.
- Pin `@v3`-style action versions to a SHA if you want reproducibility.

**On every significant ship**
- Add the project *before* you forget the architectural decisions that made it interesting.

**Never**
- Never inflate a number. The single dishonest claim is the one a recruiter checks.
- Never leave a metric that's stopped updating. A streak counter reading `0` is worse than no counter.
- Never let the workflows manufacture contributions on your behalf.

---

## Troubleshooting

| Symptom | Cause | Fix |
|:--|:--|:--|
| Stats card: *"Maximum retries exceeded"* | Shared instance rate-limited | [Self-host it](#fixing-the-github-readme-stats-rate-limit) |
| Snake image 404s | Workflow hasn't run yet | Actions → *Generate Contribution Snake* → Run workflow |
| Workflow fails with `403` | Actions lack write access | Settings → Actions → General → *Read and write permissions* |
| WakaTime card errors | Coding activity not public | wakatime.com → Settings → *Display coding activity publicly* |
| Total-stars badge reads `invalid` | Third-party worker down | Delete the badge, or point it at your own worker |
| Dividers don't animate | Camo served a cached copy | Hard refresh, or rename the SVG |
| README renders but profile doesn't | Repo name ≠ username, or private | Rename to `ReddeppaNakka`, make public |
| Activity block never updates | Marker pair edited or removed | Restore `<!-- RECENT_ACTIVITY:start -->` / `:end` exactly |
| Two commits/day from the bot | You modified the timestamp logic | Timestamp must only change when activity changes |
| `<details>` renders as raw HTML | Blank line missing after `<summary>` | Leave one blank line before the content |

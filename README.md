# design-data-spec (Bikeshed Prototype)

This is a **Bikeshed evaluation prototype** for
[adobe/spectrum-design-data#1006](https://github.com/adobe/spectrum-design-data/issues/1006).

The prototype renders a representative slice of the [Spectrum Design Data Specification](https://adobe.github.io/spectrum-design-data/spec/)
using [Bikeshed](https://github.com/speced/bikeshed) and publishes to GitHub Pages.
It exists solely to evaluate Bikeshed as an alternative spec-authoring toolchain.

**The canonical specification lives in
[adobe/spectrum-design-data](https://github.com/adobe/spectrum-design-data).**
Do not treat this repo as authoritative — content here may lag the canonical source
and includes modifications for the Bikeshed autolink evaluation (see `AUTHORING-TAX.md`).

## Live prototype

<https://garthdb.com/design-data-spec/>

## What's in this repo

| Path | Purpose |
| ---- | ------- |
| `spec.bs` | Top-level Bikeshed source file (metadata + includes) |
| `chapters/` | Chapter markdown copied from the canonical spec, plus a rules excerpt |
| `biblio/spectrum.biblio.json` | Local bibliography entries (SEMVER, Discussion #735) |
| `AUTHORING-TAX.md` | Notes on the authoring-cost experiment (#1011) for the evaluation doc |
| `.github/workflows/build.yml` | GitHub Actions: Bikeshed build → GitHub Pages |

## Evaluation criteria

The prototype is assessed on six criteria defined in
[#1006](https://github.com/adobe/spectrum-design-data/issues/1006):

1. Visual quality
2. Markdown fidelity
3. Authoring tax (`<dfn>` / `[=term=]` autolinks)
4. Cross-ref ergonomics
5. Build time / CI complexity
6. URL & deep-link story

The evaluation doc (`eval.md`) will be written after the prototype is live and reviewed.

## Building locally

```sh
pipx install bikeshed
bikeshed update
bikeshed spec spec.bs out/index.html
open out/index.html
```

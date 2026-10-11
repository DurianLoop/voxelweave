# Final PDF visual audit

Audit date: 2026-08-14. Every page was rendered at 90 dpi and visually inspected; center figures were separately inspected at original resolution. Rendered evidence is under `outputs/visual_audit/`.

| Artifact | Pages rendered | Result | Observations |
|---|---:|---|---|
| TMI `main.pdf` | 8 | PASS | No clipping, blank pages, displaced floats or unreadable tables. Redesigned Fig. 1 has no arrow/text collision. Page 7–8 author-action ethics language remains deliberately visible as a human blocker. |
| CVPR `main.pdf` | 8 | PASS | Eight content pages plus references placement is visually coherent; no clipping or displaced floats. Redesigned findings Fig. 1 clearly separates count, response influence and evidence boundaries. Page 8 is references continuation, not content overflow. |
| CVPR `supplement.pdf` | 7 | PASS | New locked-gate and stability tables fit; long evidence paths wrap. Page 7 is a short reproducibility continuation, not a blank page. |

## Log audit

- TMI main: 8 pages; no undefined reference/citation or Overfull match in the final log.
- CVPR main: 8 pages; no undefined reference/citation or Overfull match.
- CVPR supplement: 7 pages; no undefined reference/citation or Overfull match after resizing the stability table.

## Figure-1 separation

- TMI: `shared physical evidence → aligned errors → shared error hidden`, contrasted with disjoint evidence.
- CVPR: `count-matched contexts → finite-response cosine → supported local evidence / boundary / failed gates`.
- The figures use different visual grammar, variables and reviewer message. They are not effectively identical.

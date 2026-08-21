# Task board — newton-over-hodge-char2

Coordinator: Claude (Fable 5) session 2026-08-20. One owner per area.

- [x] T1  Create public repo, rescue all artifacts (coordinator)
- [x] T2  Scaffold from axeyum-rado-paper template: Makefile, paper.yaml,
          latex/ skeleton, CLAUDE.md (canonical) + AGENTS.md/README.md,
          scripts/, LICENSE                        (agent A — owns repo root)
- [x] T3  Replication package: standalone verifier + scripts runnable
          without axeyum; axeyum-examples overlay instructions; document
          every claim->artifact mapping             (agent B — owns replication/)
- [x] T4  Paper draft: lean LaTeX from research-log/30-writeup.md; fetch
          KMU/KM arXiv source tarballs for notation alignment (refs/,
          gitignored); target ~20pp                 (agent C — owns latex/, refs/)
- [x] T5  Coordinator review pass; reconcile A/B/C; commit and push
- [ ] T6  (later) Lean-harden Lemma A / Theorem 3 core; arXiv submission
          checklist (ARXIV-SUBMISSION.md)
- [x] T7  Axeyum-primary rework of the replication path (2026-08-21).
          run.sh now runs TWO LAYERS in order: layer 1 is axeyum at pin
          75663ef8 (branch agent/noh-p2-axeyum-examples,
          github.com/mjbommar/axeyum), obtained from AXEYUM_DIR / a sibling
          checkout / a shallow clone into replication/.axeyum-pin/
          (gitignored), running `cargo run --release -p axeyum-cas --example
          noh_u2_matrix` and `--example noh_wt_certificate`; layer 2 is the
          python/rustc suite, relabelled INDEPENDENT CROSS-CHECK. The pin
          binding is a SHA-256 check on the two example sources, not a
          sentence in a README, and it is exit-status-bearing (verified by
          drifting a byte: run exits 1). New flags --axeyum-only,
          --crosscheck-only (the old default), --offline; --cargo kept as a
          no-op alias. Degrades honestly to the vendored copies when the
          pinned workspace is unreachable, with a DEGRADED banner. Measured:
          32 s cold via a local checkout, 192 s cold via clone, 13 s warm,
          3 s degraded. Also: replication/README.md restructured into
          primary / cross-check / mutants-and-limits with the provenance and
          deletion tables preserved; README.md replication section leads with
          axeyum; latex/sections/01_introduction.tex provenance paragraph and
          06_remarks.tex replication paragraph name axeyum with the pin;
          @misc{axeyum2026} added to latex/bib/references.bib.

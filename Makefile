# ============================================================
# Paper build system -- newton-over-hodge-char2.
#
#   make pdf        the paper PDF (latexmk; engine from paper.yaml)
#   make quick      one fast pass (refs may be stale)
#   make check      reference / alt-text / leftover-marker gates
#   make lint       chktex (advisory)
#   make wordcount  per-section word counts
#   make verify     the replication smoke checks (replication/run.sh)
#   make doctor     toolchain + docs/Makefile drift audit
#   make arxiv      verified arXiv source bundle (tarball + .bbl)
#   make validate   everything a submission must pass
#
# The engine comes from paper.yaml (typography.engine). Python helpers run
# through `uv run` when uv is present -- their PEP 723 headers pull in
# pyyaml with no install step -- and fall back to python3 otherwise.
# ============================================================

ROOT   := $(CURDIR)
BUILD  := $(ROOT)/build
LATEX  := $(ROOT)/latex
MAIN   := $(LATEX)/main.tex

# uv if available, plain python3 otherwise (then pyyaml must be installed).
PY := $(shell command -v uv >/dev/null 2>&1 && echo "uv run --quiet" || echo python3)

ENGINE := $(shell sed -n 's/^  engine: *//p' paper.yaml | head -1)
ENGINE := $(if $(ENGINE),$(ENGINE),pdflatex)

# Reproducible builds: pin SOURCE_DATE_EPOCH to the last commit so two
# builds of the same tree agree (reproducible-builds.org/docs/source-date-epoch/).
export SOURCE_DATE_EPOCH ?= $(shell git log -1 --format=%ct 2>/dev/null || date +%s)

ifeq ($(ENGINE),xelatex)
  LMK_ENGINE := -pdfxe
else ifeq ($(ENGINE),lualatex)
  LMK_ENGINE := -pdflua
else
  LMK_ENGINE := -pdf
endif

LATEXMK = latexmk $(LMK_ENGINE) -interaction=nonstopmode -halt-on-error \
          -output-directory=$(BUILD)/latex -cd

GREEN := \033[0;32m
NC    := \033[0m
define say
	@printf '$(GREEN)==> %s$(NC)\n' $(1)
endef

# Fail with a useful message rather than a latexmk stack trace while the
# LaTeX lane has not landed yet.
define need_main
	@test -f $(MAIN) || { \
	  echo "make: latex/main.tex does not exist yet (the paper lane owns latex/)."; \
	  exit 1; }
endef

.PHONY: help pdf quick draft check lint wordcount verify doctor arxiv \
        validate watch clean

help: ## list targets
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-12s %s\n", $$1, $$2}'

# ---------------- the paper ----------------
pdf: ## the paper PDF -> build/latex/main.pdf
	$(need_main)
	$(LATEXMK) -jobname=main $(MAIN)
	$(call say,"build/latex/main.pdf")

quick: ## one fast pass (refs may be stale)
	$(need_main)
	@mkdir -p $(BUILD)/latex
	cd $(LATEX) && $(ENGINE) -interaction=batchmode \
	  -output-directory=$(BUILD)/latex -jobname=main-quick main.tex \
	  || (tail -30 $(BUILD)/latex/main-quick.log; exit 1)
	$(call say,"build/latex/main-quick.pdf")

draft: ## DRAFT build (line numbers/banner if the preamble defines \DraftMode)
	$(need_main)
	$(LATEXMK) -usepretex='\def\DraftMode{1}' -jobname=main-draft $(MAIN)
	$(call say,"build/latex/main-draft.pdf")

# ---------------- QA ----------------
check: ## reference / alt-text / leftover-marker gates
	@$(PY) scripts/check_refs.py

lint: ## chktex on the LaTeX sources (advisory; skips if chktex absent)
	@$(PY) scripts/lint_latex.py

wordcount: ## per-section word counts (texcount)
	@$(PY) scripts/wordcount.py

# The replication lane owns replication/run.sh; until it exists this SKIPS
# loudly and says it checked nothing. When it exists, its exit status is the
# verdict and scripts/verify.sh propagates it unchanged.
verify: ## run the replication smoke checks (skips loudly if not landed)
	@scripts/verify.sh

doctor: ## toolchain, packages, docs <-> Makefile drift audit
	@$(PY) scripts/doctor.py

# ---------------- submission ----------------
arxiv: pdf check ## verified arXiv source bundle -> build/arxiv/*.tar.gz
	@$(PY) scripts/make_arxiv.py
	$(call say,"build/arxiv/ + ARXIV-SUBMISSION.md")

validate: doctor pdf check lint verify ## everything a submission must pass
	$(call say,"validate: all gates passed")

# ---------------- lifecycle ----------------
watch: ## continuous rebuild on save
	$(need_main)
	$(LATEXMK) -pvc -view=none -jobname=main $(MAIN)

clean: ## remove build output
	rm -rf $(BUILD)
	$(call say,"clean")

# Overleaf Build Guide

This directory contains a compact two-column conference manuscript and a separate supplement.

## Main paper

Set `main.tex` as the Overleaf main document and compile with pdfLaTeX:

1. `pdflatex main.tex`
2. `bibtex main`
3. `pdflatex main.tex`
4. `pdflatex main.tex`

## Supplement

Set `supplement.tex` as the main document and run pdfLaTeX twice. The supplement has no separate bibliography.

## Required upload contents

- `main.tex`
- `supplement.tex`
- `references.bib`
- `tables/`
- `figures/`

The tables and figures are generated from analysis CSVs by `rasinet.committee_paper_assets`. Do not edit generated numeric table files by hand.

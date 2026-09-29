# pii-bench

Head-to-head benchmark of PII detection in English text. Every method runs alone on the
same gold data: rules, Presidio, the Jev decision model, and cheap current LLMs. Each one
is measured on accuracy, calibration, cost and latency.

<!-- chart: docs/pareto.svg, copied from `pii-bench report` after the full run -->

## 01 · Why

Jev is a new kind of model: instead of generating text, it answers typed questions about
a text with probabilities. This repo asks how far that gets you on PII detection, next to
what people use today (regex, Presidio) and what a cheap LLM does with the same
definition, for relatively no money.

It is a benchmark of what is possible now, not a recommendation of a production
anonymiser. Jev is tested as a preview of where decision models are going.

## 02 · Results

<!-- headline tables from runs/test/results.md land here after the full run -->

Free lanes, test sets (word-level, headline metric):

| lane | ai4privacy F2 [95% CI] | TAB F2 [95% CI] |
|---|---|---|
| human (TAB annotator 2 vs 1) | – | 0.860 [0.840, 0.879] |
| presidio | 0.587 [0.563, 0.612] | 0.744 [0.725, 0.762] |
| regex | 0.539 [0.506, 0.572] | 0.505 [0.472, 0.537] |
| mask everything (floor) | 0.510 [0.482, 0.537] | 0.405 [0.386, 0.423] |

## 03 · Methods

| family | lanes | output |
|---|---|---|
| baseline | `mask_all` (floor) · `human` (TAB's second annotator) | spans |
| rules | `regex`: emails, phones, IPs, card and ID numbers, dates, times | spans |
| NER | `presidio`: default English recognizers on spaCy `en_core_web_lg` | spans + score |
| Jev | `jev_words`: one yes/no question per word · `jev_typed`: one choice per word (none or a type) · `jev_bio`: yes/no plus "same item as the word before?" | a probability per word |
| LLM | `llm_sayback:<model>`: list the PII strings, code finds them · `llm_offsets`: character offsets · `llm_tagged`: rewrite the text with tags | spans |

- → Every lane gets the same PII definition, word for word (`taxonomy.definition`).
- → Jev gets the whole doc once as its state and one question per word, batched up to 400 questions per call, so a doc costs one to a few calls.
- → Per-word scores become spans through a decoder: threshold, hysteresis, gap closing or Viterbi. Each is tuned on dev; the headline row uses whichever won on dev, never on test.
- → LLMs run at temperature 0 through OpenRouter, held to a strict JSON schema where the format has one. An answer that is cut off or won't parse counts as finding nothing.

| model key | OpenRouter id |
|---|---|
| `qwen3-30b` | `qwen/qwen3-30b-a3b-instruct-2507` |
| `qwen3-235b` | `qwen/qwen3-235b-a22b-2507` |
| `gpt4.1-nano` | `openai/gpt-4.1-nano` |
| `llama3-8b` | `meta-llama/llama-3.1-8b-instruct` |
| Jev | `typesafe/jev-1.13` (Decisions API) |

## 04 · Data

| | ai4privacy | TAB |
|---|---|---|
| source | pii-masking-300k, English files, pinned revision | Text Anonymization Benchmark, ECHR judgments, pinned commit |
| test | 500 docs sampled (seed 0) from validation | its test split, 127 docs |
| dev (tuning only) | 500 docs sampled from train | its dev split, 127 docs |
| gold | every personal detail, broad (bare hours, sex, titles count) | what must be masked so the applicant can't be re-identified |
| licence | academic / non-commercial: downloaded at run time, never committed, its text never shown | MIT |

Both map onto six coarse types (PERSON · LOCATION · CONTACT · ID · DATETIME · OTHER) for
the per-type tables. The headline ignores types: is this word PII or not.

## 05 · Scoring

- → **Headline: word-level F2.** A word is gold if a gold span overlaps it, predicted if a predicted span does. F2 weights recall: a leak costs more than an over-mask. Word level credits masking street and city as one span, and counts a half-masked name as a leak.
- → **Exact span match** next to it, the usual NER number.
- → **Recall by gold type**: where each method leaks.
- → **Calibration** (ECE, Brier) for lanes that give a probability per word.
- → **Cost**: $ per 1k docs from each response's reported cost, calls per doc, latency p50 per doc. Cached reruns report the original numbers.
- → **95% intervals** by resampling whole documents (1,000 resamples).
- → **Two reference rows**: mask everything (the floor; F2 leans on recall so hard that doing nothing smart scores ~0.4–0.5) and TAB's second annotator against the first (the ceiling).

## 06 · Run it

```sh
uv sync --extra dev --extra ner      # ner: Presidio + spaCy en_core_web_lg (~600 MB)
cp .env.template .env                # add an OpenRouter key
uv run pii-bench fetch               # datasets into data/, never committed
make bench-free                      # floor, regex, Presidio on both test sets: $0
make bench                           # everything, ~$1.4 of API calls
```

Single lanes: `uv run pii-bench run --lanes jev_words,llm_sayback:qwen3-30b --dataset tab --tier smoke`
(tiers: smoke 2 docs · pilot 20 · full). Every paid call goes through one spend ledger with
a hard cap (`budget_cap_usd` in `config.yaml`) and a response cache, so a rerun costs nothing.

## 07 · Layout

| path | what |
|---|---|
| `pii_bench/lanes/` | one file per method; `jev_designs.py` and `llm_formats.py` hold the question designs and answer formats |
| `pii_bench/clients/` | the only code that calls an API: budget hold, retries, cache |
| `pii_bench/decode.py` | word scores → spans |
| `pii_bench/align.py` | an LLM's answer → character offsets |
| `pii_bench/metrics/` | word and exact scoring, calibration, bootstrap, cost, result rows |
| `pii_bench/run/` | runner, tiers, store, decoder tuning |

## 08 · Limits

- → English only. ai4privacy is synthetic and format-driven; TAB is one domain (court judgments).
- → Decoders are tuned on 20 dev docs per dataset to stay inside a €2 budget for the whole project.
- → One run per lane at temperature 0. OpenRouter picks the serving provider per call, which can change behaviour between runs.
- → Prices are OpenRouter list prices on the run date.

## Credits

ai4privacy pii-masking-300k by AI4Privacy. TAB by Pilán et al., *The Text Anonymization
Benchmark (TAB)*, Computational Linguistics 2022.

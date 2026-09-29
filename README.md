# jev-vs-pii

How good is Jev, a decision model, at finding personal information in text, next to the
tools used today and to current LLMs? Every method runs alone on the same gold data from
three datasets, and is measured on accuracy, calibration, cost and latency.

<!-- chart: docs/pareto.svg, copied from `jev-vs-pii report` after the full run -->

## 01 · Why

Jev doesn't generate text: it answers typed questions about a text with probabilities.
This benchmark asks how far that gets you on PII detection, against regex, Presidio, two
dedicated PII models (OpenAI Privacy Filter, NVIDIA GLiNER-PII) and LLMs from cheap to
strong, on PII that is recognisable by its form (emails, IDs, dates) and PII that only
context reveals (a relative's name, the town someone was arrested in).

It is a benchmark of what is possible now, not a recommendation of a production
anonymiser. Jev is tested as a preview of where decision models are going.

## 02 · Results

<!-- headline tables from runs/test/results.md land here after the full run -->

## 03 · Findings

<!-- written from the full run: what each method is good at, where it leaks, and why -->

## 04 · Methods

| family | lanes | output |
|---|---|---|
| reference | `mask_all` (the floor) · `human` (TAB's second annotator against the first) | spans |
| rules | `regex`: emails, phones, IPs, card and ID numbers, dates, times | spans |
| NER and small PII models, local | `presidio` (spaCy `en_core_web_lg`) · `privacy_filter` (OpenAI, 1.5B MoE, 50M active) · `gliner_pii` (NVIDIA, 570M) | spans, and a probability per word for the last two |
| Jev | `jev_words`: one yes/no per word · `jev_typed`: one choice per word (none, or a type) · `jev_bio`: yes/no plus "same item as the word before?" | a probability per word |
| LLMs, via OpenRouter | `llm_sayback:<model>`: list the PII strings, code finds them in the text · `llm_offsets`: character offsets · `llm_tagged`: rewrite the text with tags | spans |

- → **Every lane gets the same brief**: the dataset's own annotation guidelines (ai4privacy's and Nemotron-PII's label lists, TAB's published guidelines), then the six types to answer in (`taxonomy.definition`).
- → **Jev** gets the whole doc once as its state and one question per word, packed into as few calls as its context allows.
- → **Per-word scores become spans through a decoder**: threshold, hysteresis, gap closing or Viterbi. Each is tuned on dev for every lane that scores words (Jev, Privacy Filter, GLiNER-PII); the headline row uses whichever won on dev, never on test.
- → **Privacy Filter** is decoded with OpenAI's own constrained Viterbi (`opf` package) at its default operating point; its spans match OpenAI's reference runtime.
- → **LLMs** run at temperature 0 under a strict JSON schema where the format has one. An answer that is cut off or won't parse counts as finding nothing, and the reason is recorded.
- → **Reasoning** is tested on one model, DeepSeek V4 Flash, with thinking off and on, pinned to one provider so nothing else changes.

| model key | OpenRouter id |
|---|---|
| `qwen3-30b` | `qwen/qwen3-30b-a3b-instruct-2507` |
| `qwen3-235b` | `qwen/qwen3-235b-a22b-2507` |
| `gpt4.1-nano` | `openai/gpt-4.1-nano` |
| `llama3-8b` | `meta-llama/llama-3.1-8b-instruct` |
| `deepseek-v4-flash` / `-think` | `deepseek/deepseek-v4-flash`, thinking off / on, DeepInfra |
| `haiku4.5` | `anthropic/claude-haiku-4.5` |
| Jev | `typesafe/jev-1.13` (Decisions API) |

## 05 · Data

| | ai4privacy | Nemotron-PII | TAB |
|---|---|---|---|
| what | short synthetic texts, pii-masking-300k English files | synthetic business prose (letters, reports, notes), unstructured records only | European Court of Human Rights judgments |
| length | ~53 words | ~87 words | ~630 words (up to ~2,000) |
| test / dev | 500 / 500 sampled, seed 0 | 500 / 500 sampled, seed 0 | 127 / 127, its own splits |
| gold | every personal detail, broadly (bare hours, sex, titles count) | 55 PII and sensitive categories | what must be masked so the applicant can't be re-identified; what can stay is marked too |
| licence | academic, non-commercial: downloaded at run time, never committed, text never shown | CC BY 4.0 | MIT |

All three map onto six coarse types (PERSON · LOCATION · CONTACT · ID · DATETIME · OTHER),
and every dataset label is tagged **format** (found by its form: emails, codes, dates,
amounts) or **context** (found by its meaning: names, places, organisations, personal
attributes). No public dataset of real everyday text (emails, chats) with PII labels
exists; all three sets are either synthetic or legal.

## 06 · Scoring

- → **Headline: word-level F2.** A word is gold if a gold span overlaps it, predicted if a predicted span does. F2 weights recall: a leak costs more than an over-mask. Word level credits masking street and city as one span, and counts a half-masked name as a leak.
- → **Format vs context**: recall on each kind of PII, and on TAB, how much of what the annotators left in clear a method masks anyway.
- → **Exact span match** next to it, the usual NER number.
- → **Recall by type and by each dataset's own labels**, precision by the type a method claims, and on TAB the strings each method most often leaks or over-masks.
- → **Calibration** (ECE, Brier, reliability bins) for every method that gives a probability per word.
- → **Cost and time**: $ per 1k docs from each response's reported cost, calls and tokens per doc, latency mean / p50 / p95 per doc. Cached reruns report the original numbers. Local models run on an Apple M1 Pro (GPU where supported).
- → **Uncertainty**: 95% intervals by resampling whole documents, and paired intervals on the same documents for "is A really better than B".
- → **Two reference rows**: mask everything (the floor; F2 leans on recall so hard that doing nothing smart scores 0.4–0.5) and TAB's second annotator (the ceiling).

## 07 · Run it

```sh
uv sync --extra dev --extra ner      # ner: Presidio, spaCy model, torch, Privacy Filter, GLiNER-PII
cp .env.template .env                # add an OpenRouter key
uv run jev-vs-pii fetch              # datasets into data/, never committed
make bench-free                      # rules and local models on the three test sets: $0
make bench                           # everything: pilot on dev, decoder tuning, full run, tables, chart
```

Single lanes: `uv run jev-vs-pii run --lanes jev_words,llm_sayback:qwen3-30b --dataset tab --tier smoke`
(tiers: smoke 2 docs · pilot 20 · full). Every paid call goes through one spend ledger with
a hard cap (`budget_cap_usd` in `config.yaml`) and a response cache, so a rerun costs nothing.

## 08 · Layout

| path | what |
|---|---|
| `jev_vs_pii/lanes/` | one file per method; `jev_designs.py` and `llm_formats.py` hold the question designs and answer formats |
| `jev_vs_pii/clients/` | the only code that calls an API: budget hold, retries, cache |
| `jev_vs_pii/taxonomy.py` | coarse types, format/context shapes, each dataset's guidelines |
| `jev_vs_pii/decode.py` | word scores → spans |
| `jev_vs_pii/align.py` | an LLM's answer → character offsets |
| `jev_vs_pii/metrics/` | word and exact scoring, calibration, bootstrap, cost, error strings, result rows |
| `jev_vs_pii/run/` | runner, tiers, store, decoder tuning |
| `jev_vs_pii/report/` | Markdown tables and the SVG chart |

## 09 · Limits

- → English only, and no real everyday text: two synthetic sets and one legal one.
- → Public datasets may be in the models' training data. GLiNER-PII was trained on Nemotron-PII's train split (this benchmark samples its test split), and Privacy Filter reports results on pii-masking-300k.
- → Decoders are tuned on 20 dev docs per dataset.
- → One run per method at temperature 0. OpenRouter picks the serving provider per call (recorded with every answer), which can change behaviour between runs; only the reasoning pair is pinned.
- → TAB is scored against its first annotator.
- → Prices are OpenRouter list prices on the run date.

## Credits

ai4privacy pii-masking-300k by AI4Privacy. Nemotron-PII by NVIDIA (CC BY 4.0). TAB by
Pilán et al., *The Text Anonymization Benchmark (TAB)*, Computational Linguistics 2022.
OpenAI Privacy Filter (Apache 2.0) and NVIDIA GLiNER-PII.

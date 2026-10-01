# jev-vs-pii

How good is Jev, a decision model, at finding personal information in text, next to the
tools used today and to current LLMs? Every method runs alone on the same gold data from
three datasets, and is measured on accuracy, calibration, cost and latency.

<!-- chart: docs/pareto.svg, copied from `jev-vs-pii report` after the full run -->

## 01 · Why

[Jev](https://docs.typesafe.ai) is a model from TypeSafe, served through OpenRouter's
[Decisions API](https://openrouter.ai/docs/guides/community/jev). It doesn't write text.
You send it a state and typed questions (yes/no, or pick one of a few options), and it
answers each one with probabilities. Output is free; you pay for input tokens.

PII detection fits that shape: it is one question per word ("is this personal
information?"), and what you want back is a probability you can put a threshold on, not
prose to parse. So the question here is how far a decision model gets on a real
extraction task, against:

- → what people already run: regex, Presidio, and two small PII models (OpenAI Privacy Filter, NVIDIA GLiNER-PII);
- → LLMs from cheap to strong, asked the same thing;
- → on PII you can spot by its form (emails, IDs, dates) and PII only context reveals (a relative's name, the town someone was arrested in).

Jev is one of the first decision models with a public API. If larger labs ship their own,
the same harness runs them as one more lane.

This is a look at what models a personal budget can afford can do (about $6 of paid calls
for everything in this repo). It is not a recommendation of what to deploy: see §04.

## 02 · Results

<!-- headline tables from runs/test/results.md land here after the full run -->

## 03 · Findings

<!-- written from the full run: what each method is good at, where it leaks, and why -->

## 04 · No single winner

The headline ranks methods on one score. Choosing one for real use turns on things that
score doesn't capture.

- → **What counts as PII for you.** The local models find the categories they were trained on: Privacy Filter has 8 fixed ones, GLiNER-PII takes a list of label names. Neither reads a policy. TAB asks for a policy: mask what would re-identify the applicant, leave the rest in clear. Changing the scope of a local model means new labels or fine-tuning, and how well it does on labels it wasn't trained for is not measured here. LLMs and Jev read the guidelines as text, so changing the scope is editing a prompt. <!-- after run: guideline vs one-line prompt delta, dev pilot -->
- → **How reliable the output must be.** A local model returns spans every time, in about the same time, from the same weights. An LLM answer can loop, get cut off, fail to parse, or change when OpenRouter routes the call to another provider; each of those counts as finding nothing here. <!-- after run: failed counts per lane --> Jev returns a probability for every question it is asked.
- → **Where the text may go.** Local models keep the text on the machine. Every Jev and LLM call here sends it to a third-party API through OpenRouter. No setup here was chosen for GDPR or data-residency terms; real personal data needs a provider and contract that allow it, or a model you host.
- → **Cost at volume.** Local models cost nothing per doc but need hardware. Jev bills input only and answers fast, but asks one question per word, so its cost grows with document length. LLM cost follows model size.
- → **Picking your own trade-off.** Methods that score each word (Jev, Privacy Filter, GLiNER-PII) let you move a threshold: fewer leaks for more over-masking, or the reverse. An LLM gives one answer; moving its trade-off means rewording the prompt.

A fixed scope at high volume over sensitive text points one way, a scope that changes per
client or per document type points another. The top row of the table answers neither.

## 05 · Methods

| family | lanes | output |
|---|---|---|
| reference | `mask_all` (the floor) · `human` (TAB's second annotator against the first) | spans |
| rules | `regex`: emails, phones, IPs, card and ID numbers, dates, times | spans |
| NER and small PII models, local | `presidio` (spaCy `en_core_web_lg`) · `privacy_filter` (OpenAI, 1.5B MoE, 50M active) · `gliner_pii` (NVIDIA, 570M) | spans, and a probability per word for the last two |
| Jev | `jev_words`: one yes/no per word · `jev_typed`: one choice per word (none, or a type) · `jev_bio`: yes/no plus "same item as the word before?" | a probability per word |
| LLMs, via OpenRouter | `llm_sayback:<model>`: list the PII strings, code finds them in the text · `llm_offsets`: character offsets · `llm_tagged`: rewrite the text with tags | spans |

- → **Lanes that read instructions get the same brief** (Jev and the LLMs): the dataset's own annotation guidelines (ai4privacy's and Nemotron-PII's label lists, TAB's published guidelines), then the six types to answer in (`taxonomy.definition`). Regex, Presidio and Privacy Filter run as shipped; GLiNER-PII gets a fixed list of label names.
- → **Jev** gets the whole doc once as its state and one question per word, with the word bracketed in a few words of context. Questions are packed into as few calls as fit. Jev's docs give a 32k-token context; calls are packed up to an estimated 48k because larger calls were accepted, and on the dev pilot answers past 32k scored the same as earlier ones (TAB, `jev_words`: Brier 0.061 past 32k, 0.063 before).
- → **Per-word scores become spans through a threshold tuned on dev** (word-level F2, never on test), for every lane that scores words. Three structured decoders (hysteresis, gap closing, Viterbi) were tuned the same way and are reported beside it; on the dev pilot none beat the threshold by more than about 0.02 F2.
- → **Privacy Filter**'s own spans come from OpenAI's constrained Viterbi (`opf` package) at its default operating point and match OpenAI's reference runtime; they are in the decoder table. Its headline row uses the tuned threshold on its per-word probability, like the other scorers. That threshold lands at 0.001, the bottom of the grid: at F2 it pays to mask anything the model gives any weight to.
- → **GLiNER-PII** returns candidates down to a 0.05 score; its card default is 0.5. Long docs run in 250-word windows overlapping by 50.
- → **LLMs** run at temperature 0 under a strict JSON schema where the format has one, with an 8k output cap. An answer that is cut off or won't parse counts as finding nothing, and the reason is recorded.
- → **Reasoning** is tested on one model, DeepSeek V4 Flash, with thinking off and on, on the same fp8 providers so nothing else changes. Thinking gets an extra 8k tokens; an answer still cut off counts as finding nothing, and the results say how many.
- → **Answer formats** (offsets, tagged rewrite) are compared on one model over the 60-doc dev pilot only: both loop to the output cap often enough that full test sets would take hours for a gap the pilot already shows.

Models were picked to span price and size within the budget:

| model key | OpenRouter id |
|---|---|
| `qwen3-30b` | `qwen/qwen3-30b-a3b-instruct-2507` |
| `qwen3-235b` | `qwen/qwen3-235b-a22b-2507` |
| `gpt4.1-nano` | `openai/gpt-4.1-nano` |
| `llama3-8b` | `meta-llama/llama-3.1-8b-instruct` (dev pilot only: loops under the strict schema) |
| `deepseek-v4-flash` / `-think` | `deepseek/deepseek-v4-flash`, thinking off / on, DeepInfra · Parasail · Alibaba |
| `haiku4.5` | `anthropic/claude-haiku-4.5` |
| Jev | `typesafe/jev-1.13` (Decisions API) |

## 06 · Data

| | ai4privacy | Nemotron-PII | TAB |
|---|---|---|---|
| what | short synthetic texts, pii-masking-300k English files | synthetic business prose (letters, reports, notes), unstructured records only | European Court of Human Rights judgments |
| length | ~53 words | ~87 words | ~630 words (up to ~2,000) |
| test / dev | 500 / 500 sampled, seed 0 | 500 from the test file / 500 from the train file, seed 0 | 127 / 127, its own splits |
| gold | every personal detail, broadly (bare hours, sex, titles count) | 55 PII and sensitive categories | what must be masked so the applicant can't be re-identified; what can stay is marked too |
| licence | academic, non-commercial: downloaded at run time, never committed, text never shown | CC BY 4.0 | MIT |

All three map onto six coarse types (PERSON · LOCATION · CONTACT · ID · DATETIME · OTHER),
and every dataset label is tagged **format** (found by its form: emails, codes, dates,
amounts) or **context** (found by its meaning: names, places, organisations, personal
attributes). No public dataset of real everyday text (emails, chats) with PII labels
exists; all three sets are either synthetic or legal.

## 07 · Scoring

- → **Headline: word-level F2.** A word is gold if a gold span overlaps it, predicted if a predicted span does. F2 weights recall: a leak costs more than an over-mask. Word level credits masking street and city as one span, and counts a half-masked name as a leak.
- → **Format vs context**: recall on each kind of PII, and on TAB, how much of what the annotators left in clear a method masks anyway.
- → **Exact span match** next to it, the usual NER number.
- → **Recall by type and by each dataset's own labels**, precision by the type a method claims, and on TAB the strings each method most often leaks or over-masks.
- → **Calibration** (ECE, Brier, reliability bins) for every method that gives a probability per word.
- → **Cost and time**: $ per 1k docs from each response's reported cost, calls and tokens per doc, latency mean / p50 / p95 per doc. Cached reruns report the original numbers. Local models run on an Apple M1 Pro (GPU where supported).
- → **Uncertainty**: 95% intervals by resampling whole documents, and paired intervals on the same documents for "is A really better than B".
- → **Two reference rows**: mask everything (the floor) and TAB's second annotator (the ceiling). F2 leans on recall hard enough that masking everything scores 0.34 to 0.58 depending on how dense the PII is (dev pilot), so read every row against its dataset's floor. <!-- after run: test floors -->

## 08 · Run it

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

## 09 · Layout

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

## 10 · Limits

- → Not a deployment recommendation (§04). Models were chosen to fit about $6 of paid calls, so no frontier-size LLM is in it, and none was chosen for GDPR terms.
- → English only, and no real everyday text: two synthetic sets and one legal one.
- → Public datasets may be in the models' training data. GLiNER-PII was trained on Nemotron-PII's train split: its test numbers come from the test file, but its tuned threshold was picked on dev, which samples train. Privacy Filter reports results on pii-masking-300k.
- → Thresholds are tuned on 20 dev docs per dataset.
- → One run per method at temperature 0. OpenRouter picks the serving provider per call (recorded with every answer), which can change behaviour between runs; only the reasoning pair is pinned.
- → Jev 1.13 is served from an alpha endpoint; its behaviour and prices may change.
- → TAB is scored against its first annotator.
- → Prices are OpenRouter list prices on the run date.

## Credits

ai4privacy pii-masking-300k by AI4Privacy. Nemotron-PII by NVIDIA (CC BY 4.0). TAB by
Pilán et al., *The Text Anonymization Benchmark (TAB)*, Computational Linguistics 2022.
OpenAI Privacy Filter (Apache 2.0) and NVIDIA GLiNER-PII.

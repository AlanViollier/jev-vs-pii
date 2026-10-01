# jev-vs-pii

How good is [Jev](https://docs.typesafe.ai), a decision model, at finding personal
information in text, next to the tools used today and to current LLMs?

**Short answer.** On court judgments, where context decides what identifies someone, Jev
is statistically tied with Claude Haiku 4.5 for first place and catches more of the
context-only PII than any other method, at a quarter of Haiku's latency. It gets there by
masking too much: on every dataset a Jev lane has the lowest precision of any non-baseline
method. On shorter, simpler text most LLMs beat it by 0.07 to 0.14 F2, and its cost grows
with every word it reads.

Every method runs alone on the same gold data from three datasets (500 synthetic texts,
500 business documents, 127 court judgments) and is scored on accuracy, calibration, cost
and latency. Total spend for everything in this repo: $5.73.

<!-- hero visual: docs/hero.png, made from docs/data/examples.json -->

## 01 · Results

Word-level F2 on the test sets (recall counts four times as much as precision; §08). Best
in each column in bold, reference rows aside.

| method | ai4privacy | Nemotron-PII | TAB | TAB F1 |
|---|---|---|---|---|
| `jev_typed` (Jev, one choice per word) | 0.829 | 0.792 | **0.790** | 0.731 |
| `jev_words` (Jev, one yes/no per word) | 0.841 | 0.719 | 0.680 | 0.616 |
| Claude Haiku 4.5 | **0.953** | **0.934** | 0.773 | **0.793** |
| Qwen3 235B | 0.952 | 0.912 | 0.722 | 0.716 |
| DeepSeek V4 Flash | 0.946 | 0.923 | 0.722 | 0.748 |
| DeepSeek V4 Flash, thinking | 0.948 | 0.864 | 0.667 | 0.724 |
| Qwen3 30B | 0.938 | 0.902 | 0.650 | 0.653 |
| GPT-4.1 nano | 0.826 | 0.837 | 0.480 | 0.546 |
| GLiNER-PII (local) | 0.841 | 0.872 † | 0.735 | 0.663 |
| Privacy Filter (local) | 0.862 | 0.698 | 0.555 | 0.654 |
| Presidio (local) | 0.587 | 0.671 | 0.744 | 0.762 |
| regex | 0.539 | 0.433 | 0.505 | 0.614 |
| mask everything (floor) | 0.510 | 0.358 | 0.405 | 0.214 |
| second human annotator (ceiling) | – | – | 0.860 | 0.856 |

† GLiNER-PII was trained on Nemotron-PII's train split.

Cost and speed per document, on short text (Nemotron-PII, ~90 words) and long text (TAB,
~630 words):

| method | $ per 1k docs, short | $ per 1k docs, long | median s per doc, short | median s per doc, long |
|---|---|---|---|---|
| `jev_typed` | 0.70 | 5.76 | 0.37 | 0.89 |
| `jev_words` | 0.16 | 1.18 | 0.29 | 0.61 |
| Claude Haiku 4.5 | 1.42 | 4.81 | 1.5 | 3.6 |
| Qwen3 235B | 0.16 | 0.69 | 11 | 30 |
| DeepSeek V4 Flash | 0.07 | 0.33 | 2.3 | 7.7 |
| DeepSeek V4 Flash, thinking | 0.26 | 1.53 | 11 | 75 |
| GPT-4.1 nano | 0.09 | 0.28 | 1.8 | 2.7 |
| local models (Presidio, Privacy Filter, GLiNER-PII) | 0 | 0 | 0.02 – 1.8 | 0.1 – 2.3 |

Every table behind these (confidence intervals, precision and recall, recall by type,
calibration, paired tests, the strings each method leaks): [`docs/results.md`](docs/results.md).
Chart-ready numbers: [`docs/data/`](docs/data).

## 02 · Findings

**Jev**

- → **Tied for first where context decides.** On TAB, `jev_typed` minus Haiku is +0.017 F2, 95% paired interval [−0.008, +0.044]: no clear gap. It is clearly ahead of everything else, by 0.05 to 0.31. It recalls 72% of the context-only PII (Haiku 58%, the second annotator 77%) and, by TAB's own evaluation script, 99.4% of direct identifiers.
- → **It wins on recall and pays in precision.** On every dataset a Jev lane has the lowest precision of any non-baseline method (`jev_typed`: 0.47 to 0.65). It masks "applicant", pronouns and court names. On F1, Haiku, Presidio and DeepSeek V4 Flash all pass it on TAB.
- → **On simpler text, LLMs lead.** On ai4privacy and Nemotron-PII every LLM but GPT-4.1 nano is 0.07 to 0.14 F2 ahead of the better Jev lane, and nano beats it on Nemotron-PII.
- → **The fastest paid method, by a lot.** 0.3 to 0.9 s per doc, against 1.3 to 30 s for the LLMs and 75 s for DeepSeek with thinking on.
- → **Cost grows with length.** Jev bills input only, but asks one question per word. On ~90-word texts `jev_typed` costs half of Haiku; on ~630-word judgments it is the most expensive method here, 20% above Haiku.
- → **Asking a richer question helps on hard text.** One choice among six types instead of yes/no: +0.11 F2 on TAB, +0.07 on Nemotron-PII, −0.01 on ai4privacy, at 3 to 5 times the cost.
- → **Its yes/no probabilities are well calibrated** (expected calibration error 0.04 to 0.06, as good as the local models). Read as "PII or not", the typed answers are less so (0.12 to 0.17).
- → **It always answered.** Every Jev call returned a probability for every question; one call failed once and went through on retry.

**Everything else**

- → **Thinking bought nothing.** On the 118 TAB docs both DeepSeek modes answered, they score the same F2 (0.737; `docs/results.md`, last section). The TAB gap is 8 thinking answers cut off at the token cap, at 10 times the latency and 4.6 times the cost. On Nemotron-PII thinking made it more conservative: precision 0.96 and recall 0.84, against 0.95 and 0.92.
- → **Model size matters where context matters.** Qwen3 235B over 30B: +0.01 F2 on the synthetic sets, +0.07 on TAB. GPT-4.1 nano drops to 0.48 on TAB.
- → **Local models are close on simple text, free, and limited by what they were trained on.** GLiNER-PII ties `jev_words` on ai4privacy. Privacy Filter's precision is 0.88 to 0.93, but its 8 categories leave out organisations, demographics and most IDs. Presidio does well on TAB (0.744), where most PII is names, dates and places.
- → **Every method leaks what identifies someone only through context**: the employer ("Serco"), a court that names the town ("Będzin District Court"), what the case is about ("widows"). The most-leaked and most over-masked strings per method are in `docs/results.md`.
- → **Instructions move LLM scores a lot.** On the dev pilot, giving the dataset's own annotation guidelines instead of a one-line definition took Qwen3 235B from 0.53 to 0.78 F2 on TAB, and GPT-4.1 nano from 0.29 to 0.54.

## 03 · Questions you might have

**Jev ties Haiku on TAB. Is it cheaper or faster?** Faster: about 4 times, 0.89 s against
3.6 s per judgment. Not cheaper: $5.76 against $4.81 per 1,000 judgments, because Jev is
asked about every word. On short documents it's the reverse: half Haiku's price, but 0.14
F2 behind.

**Could Jev ask about fewer words?** Yes. Most of what it over-masks are words like "his"
or "the applicant's". A simulation on the stored scores, made after seeing the results
and not part of the headline: skipping the words in spaCy's standard English stop-word
list removes 47% of the questions on TAB. Precision goes from 0.65 to 0.78, recall from
0.83 to 0.81, F2 from 0.790 to 0.801, and F1 to 0.79, level with Haiku, at roughly half
the cost. The cost of skipping: 5.8% of TAB's PII words are stop words, and those would
always be missed. The code is `report/analyses.py`; every dataset's numbers are at the end
of [`docs/results.md`](docs/results.md).

**Isn't tuning a threshold an unfair edge over the LLMs?** It's tuned on 20 dev
documents per dataset, never on test. A probability you can put a threshold on is part of
what Jev offers; an LLM gives one answer, and changing its trade-off means rewording the
prompt. F1 and precision at the same threshold are in the tables, so the cost of that
choice is visible.

**Why F2 and not F1?** For anonymisation, a leaked name costs more than an over-masked
word. That choice decides Jev's TAB result, which is why F1 sits next to it.

**Why no GPT-5, Claude Sonnet or Gemini Pro?** Budget: everything here cost $5.73. Haiku
is the strong reference. Any model on OpenRouter is one entry in `config.yaml` and a
rerun away.

**Can I use one of these to anonymise real data?** Not as tested. §04.

**How sure are these numbers?** 500, 500 and 127 test documents. 95% intervals come from
resampling whole documents, and "A beats B" claims use paired intervals on the same
documents. Each method ran once at temperature 0. OpenRouter picks the serving provider
per call, which can shift LLM results between runs.

**Why do strong LLMs drop so much on TAB?** TAB asks for a policy, not a list of entity
types: mask whatever would let someone re-identify the applicant. The LLMs find names and
dates, but miss about 4 in 10 context-only identifiers: relatives, places, case details.

**Did the local models see this data in training?** GLiNER-PII was trained on
Nemotron-PII's train split; its test numbers come from the test file. OpenAI reports
Privacy Filter results on pii-masking-300k, the source of the ai4privacy set.

**Can I rerun it?** `make bench`, about $6 of OpenRouter calls and 1 to 1.5 hours. Every
response is cached by request, so a rerun of finished work is free (§09).

## 04 · No single winner

The headline ranks methods on one score. Choosing one for real use turns on things that
score doesn't capture.

- → **What counts as PII for you.** The local models find the categories they were trained on: Privacy Filter has 8 fixed ones, GLiNER-PII takes a list of label names. Neither reads a policy. TAB asks for a policy: mask what would re-identify the applicant, leave the rest in clear. Changing the scope of a local model means new labels or fine-tuning, and how well it does on labels it wasn't trained for is not measured here. LLMs and Jev read the guidelines as text, so changing the scope means editing a prompt, and that alone moved Qwen3 235B from 0.53 to 0.78 F2 on TAB in the dev pilot.
- → **How reliable the output must be.** A local model returns spans every time, in about the same time, from the same weights. An LLM answer can loop, get cut off, fail to parse, or change when OpenRouter routes the call to another provider; here that happened on up to 8 of 127 TAB documents per model, and each counts as finding nothing. Jev returned a probability for every question it was asked.
- → **Where the text may go.** Local models keep the text on the machine. Every Jev and LLM call here sends it to a third-party API through OpenRouter. No setup here was chosen for GDPR or data-residency terms; real personal data needs a provider and contract that allow it, or a model you host.
- → **Cost at volume.** Local models cost nothing per document but need hardware. Jev is fast and bills input only, but its cost grows with document length. LLM cost follows model size.
- → **Picking your own trade-off.** Methods that score each word (Jev, Privacy Filter, GLiNER-PII) let you move a threshold: fewer leaks for more over-masking, or the reverse.

A fixed scope at high volume over sensitive text points one way, a scope that changes per
client or per document type points another. The top row of the table answers neither.

## 05 · Why test Jev

Jev is a model from TypeSafe, served through OpenRouter's
[Decisions API](https://openrouter.ai/docs/guides/community/jev). It doesn't write text.
You send it a state and typed questions (yes/no, or pick one of a few options), and it
answers each one with probabilities. Output is free; you pay for input tokens.

PII detection fits that shape: it is one question per word ("is this personal
information?"), and what you want back is a probability you can put a threshold on, not
prose to parse. Jev is one of the first decision models with a public API; if larger labs
ship their own, the same harness runs them as one more lane.

This is a look at what models a personal budget can afford can do. It is not a
recommendation of what to deploy.

## 06 · Methods

| family | lanes | output |
|---|---|---|
| reference | `mask_all` (the floor) · `human` (TAB's second annotator against the first) | spans |
| rules | `regex`: emails, phones, IPs, card and ID numbers, dates, times | spans |
| NER and small PII models, local | `presidio` (spaCy `en_core_web_lg`) · `privacy_filter` (OpenAI, 1.5B MoE, 50M active) · `gliner_pii` (NVIDIA, 570M) | spans, and a probability per word for the last two |
| Jev | `jev_words`: one yes/no per word · `jev_typed`: one choice per word (none, or a type) · `jev_bio`: yes/no plus "same item as the word before?" | a probability per word |
| LLMs, via OpenRouter | `llm_sayback:<model>`: list the PII strings, code finds them in the text · `llm_offsets`: character offsets · `llm_tagged`: rewrite the text with tags | spans |

- → **Lanes that read instructions get the same brief** (Jev and the LLMs): the dataset's own annotation guidelines (ai4privacy's and Nemotron-PII's label lists, TAB's published guidelines), then the six types to answer in (`taxonomy.definition`). Regex, Presidio and Privacy Filter run as shipped; GLiNER-PII gets a fixed list of label names.
- → **Jev** gets the whole document once as its state and one question per word, with the word bracketed in a few words of context. Questions are packed into as few calls as fit. Jev's docs give a 32k-token context; calls are packed up to an estimated 48k because larger calls were accepted. Counted in billed tokens, only `jev_typed` went past 32k, and on TAB its answers there are slightly worse: Brier 0.073 against 0.068 before, on a similar share of PII (`docs/results.md`, last section).
- → **Per-word scores become spans through a threshold tuned on dev** (word-level F2, never on test), for every lane that scores words. Three structured decoders (hysteresis, gap closing, Viterbi) were tuned the same way and are reported beside it; on the dev pilot none beat the threshold by more than about 0.02 F2.
- → **Privacy Filter**'s own spans come from OpenAI's constrained Viterbi (`opf` package) at its default operating point and match OpenAI's reference runtime; they are in the decoder table. Its headline row uses the tuned threshold on its per-word probability, like the other scorers. That threshold lands at 0.001, the bottom of the grid: at F2 it pays to mask anything the model gives any weight to.
- → **GLiNER-PII** returns candidates down to a 0.05 score; its card default is 0.5. Long documents run in windows sized to its 384-token limit, overlapping by 50 words.
- → **LLMs** run at temperature 0 under a strict JSON schema where the format has one, with an 8k output cap. An answer that is cut off or won't parse counts as finding nothing, and the reason is recorded.
- → **Reasoning** is tested on one model, DeepSeek V4 Flash, with thinking off and on, on the same fp8 providers so nothing else changes. Thinking gets an extra 8k tokens.
- → **Dev pilot only** (20 documents per dataset): `jev_bio` (same score as `jev_words` at twice the cost), the offsets and tagged formats (offsets scored 0.00 on TAB; both loop to the output cap often enough that full test sets would take hours) and Llama 3.1 8B (loops under the strict schema on up to 60% of documents).

| model key | OpenRouter id |
|---|---|
| `qwen3-30b` | `qwen/qwen3-30b-a3b-instruct-2507` |
| `qwen3-235b` | `qwen/qwen3-235b-a22b-2507` |
| `gpt4.1-nano` | `openai/gpt-4.1-nano` |
| `llama3-8b` | `meta-llama/llama-3.1-8b-instruct` (dev pilot only) |
| `deepseek-v4-flash` / `-think` | `deepseek/deepseek-v4-flash`, thinking off / on, DeepInfra · Parasail · Alibaba |
| `haiku4.5` | `anthropic/claude-haiku-4.5` |
| Jev | `typesafe/jev-1.13` (Decisions API) |

## 07 · Data

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
attributes). Nemotron-PII reuses some document ids for different documents; repeats get
their own id here. No public dataset of real everyday text (emails, chats) with PII
labels exists; all three sets are either synthetic or legal.

## 08 · Scoring

- → **Headline: word-level F2.** A word is gold if a gold span overlaps it, predicted if a predicted span does. F2 weights recall: a leak costs more than an over-mask. Word level credits masking street and city as one span, and counts a half-masked name as a leak.
- → **Format vs context**: recall on each kind of PII, and on TAB, how much of what the annotators left in clear a method masks anyway.
- → **Exact span match** next to it, the usual NER number.
- → **Recall by type and by each dataset's own labels**, precision by the type a method claims, and on TAB the strings each method most often leaks or over-masks.
- → **Calibration** (ECE, Brier, reliability bins) for every method that gives a probability per word.
- → **Cost and time**: $ per 1k docs from each response's reported cost, calls and tokens per doc, latency mean / p50 / p95 per doc (for Jev, whose questions on a long doc go out as parallel calls, the slowest of them). Cached reruns report the original numbers. Local models run on an Apple M1 Pro (GPU where supported).
- → **Uncertainty**: 95% intervals by resampling whole documents, and paired intervals on the same documents for "is A really better than B".
- → **Two reference rows**: mask everything (the floor) and TAB's second annotator (the ceiling). F2 leans on recall hard enough that masking everything scores 0.36 to 0.51 depending on how dense the PII is, so read every row against its dataset's floor.

## 09 · Run it

```sh
uv sync --extra dev --extra ner      # ner: Presidio, spaCy model, torch, Privacy Filter, GLiNER-PII
cp .env.template .env                # add an OpenRouter key
uv run jev-vs-pii fetch              # datasets into data/, never committed
make bench-free                      # rules and local models on the three test sets: $0
make bench                           # everything: dev pilot, threshold tuning, full run, scores, docs/
```

Single lanes: `uv run jev-vs-pii run --lanes jev_words,llm_sayback:qwen3-30b --dataset tab --tier smoke`
(tiers: smoke 2 docs · pilot 20 · full). Every paid call goes through one spend ledger with
a hard cap (`budget_cap_usd` in `config.yaml`) and a response cache, so a rerun costs
nothing. `jev-vs-pii export runs/test` rewrites `docs/results.md` and `docs/data/`.

## 10 · Layout

| path | what |
|---|---|
| `jev_vs_pii/lanes/` | one file per method; `jev_designs.py` and `llm_formats.py` hold the question designs and answer formats |
| `jev_vs_pii/clients/` | the only code that calls an API: budget hold, retries, cache |
| `jev_vs_pii/taxonomy.py` | coarse types, format/context shapes, each dataset's guidelines |
| `jev_vs_pii/decode.py` | word scores → spans |
| `jev_vs_pii/align.py` | an LLM's answer → character offsets |
| `jev_vs_pii/metrics/` | word and exact scoring, calibration, bootstrap, cost, error strings, result rows |
| `jev_vs_pii/run/` | runner, tiers, store, threshold tuning |
| `jev_vs_pii/report/` | Markdown tables and the `docs/data/` export |
| `docs/` | every results table, and the numbers behind the charts |

## 11 · Limits

- → Not a deployment recommendation (§04). Models were chosen to fit a small budget, so no frontier-size LLM is in it, and none was chosen for GDPR terms.
- → English only, and no real everyday text: two synthetic sets and one legal one.
- → Public datasets may be in the models' training data. GLiNER-PII was trained on Nemotron-PII's train split: its test numbers come from the test file, but its tuned threshold was picked on dev, which samples train. Privacy Filter reports results on pii-masking-300k.
- → Thresholds are tuned on 20 dev docs per dataset.
- → One run per method at temperature 0. OpenRouter picks the serving provider per call (recorded with every answer), which can change behaviour between runs; only the reasoning pair is pinned.
- → Jev 1.13 is served from an alpha endpoint; its behaviour and prices may change.
- → `jev_typed` calls on TAB were packed past Jev's documented 32k context, where its answers are slightly worse (§06). Packing to 32k would be the safe setting, at more calls per document.
- → TAB is scored against its first annotator.
- → Prices are OpenRouter list prices on the run date.

## Credits

ai4privacy pii-masking-300k by AI4Privacy. Nemotron-PII by NVIDIA (CC BY 4.0). TAB by
Pilán et al., *The Text Anonymization Benchmark (TAB)*, Computational Linguistics 2022.
OpenAI Privacy Filter (Apache 2.0) and NVIDIA GLiNER-PII.

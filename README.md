# jev-vs-pii

How good is [Jev](https://docs.typesafe.ai), a decision model, at finding personal
information in text, next to the tools used today and to current LLMs?

**Short answer.** On court judgments, where context decides what identifies someone, Jev
ties Claude Haiku 4.5 for the best score, runs about five times faster, costs about three
quarters as much, and lets the least personal information through: 11% stays unmasked,
against 17% for Haiku. On short synthetic text the larger LLMs stay ahead.

**What this project found**

→ **A decision model can match a strong LLM where anonymisation is hard.** On European Court of Human Rights judgments Jev scores as well as Haiku (F2 0.83 against 0.82), finds 81% of the details that identify someone only through context (a relative, an employer, a town), and answers in 0.7 s against 3.8 s.

→ **How you ask matters as much as which model you ask.** Jev first masked "Account" in "Account number: 4417…", because the question asked what each word *is*. One extra answer option, "the name of a kind of information", took it from 0.84 to 0.91 F2 on synthetic text. A reworded prompt took Haiku from 0.77 to 0.82 on judgments. Each change was picked on a separate dev set before the test run (§06).

→ **The right method depends on what you need to catch.** A fixed list of formats (emails, phone numbers, IDs) is cheap and fast with a local model. A policy like "anything that could re-identify this person" needs a model that reads instructions, Jev or an LLM, and then the scope you write is what it finds (§04).

→ **Usable today? Not yet, but soon.** Every paid method here sends the text to a third-party API through OpenRouter, and none was chosen for GDPR or data-residency terms. OpenAI announced its own decision model in September 2026. Once a provider releases one as open weights, or runs it under a GDPR-compliant contract, a decision model becomes a real option for anonymisation, depending on the scope (§05).

Every method runs alone on the same gold data from three datasets (500 synthetic texts,
500 business documents, 127 court judgments) and is scored on accuracy, leaks,
calibration, cost and latency. Total spend for everything in this repo: $11.83.

<br>

**Score against speed, on court judgments**

<img src="docs/hero.svg" alt="TAB court judgments, word-level F2 against median seconds per document: Jev 0.83 at 0.66 s, Haiku 4.5 0.82 at 3.8 s; a second human expert 0.86." width="100%">

<br>

**Watch them work**

<img src="docs/race.gif" alt="Replay: Jev and Claude Haiku 4.5 reading the same ten test documents side by side, in real time. Jev finishes each in under a second, Haiku in 2 to 5 seconds; the tally ends Jev 10, Haiku 0 on speed and Jev 2, Haiku 8 on F2." width="100%">

A replay of Jev and Haiku reading the same documents, built from their recorded answers
and timed in real time. Jev's highlight sweeps word by word as its probabilities come
back; Haiku's answer streams in as it writes; every word lights up as caught, leaked or
over-masked. [The race page](https://alanviollier.github.io/jev-vs-pii/race/) lets you
pick a document, slow it down five times, and read each document's numbers. These ten (the
first five test documents of TAB and of Nemotron-PII) favour Haiku on F2, 8 to 2; over
every test document, Jev scores higher on 73 of 127 judgments and Haiku on 371 of 500
business documents.

<br>

**Score on all three datasets**

<img src="docs/where.svg" alt="Word-level F2 on the three test sets with 95% intervals: ai4privacy Jev 0.91, Haiku 0.95, DeepSeek V4 Flash 0.94; Nemotron-PII Jev 0.90, Haiku 0.94, DeepSeek 0.94; TAB Jev 0.83, Haiku 0.82, DeepSeek 0.75." width="100%">

<br>

**What gets through:** the share of the personal information left unmasked.

| | ai4privacy | Nemotron-PII | TAB |
|---|---|---|---|
| Jev | 6.7% | **5.0%** | **11.3%** |
| Claude Haiku 4.5 | **3.0%** | 6.3% | 16.9% |
| DeepSeek V4 Flash | 4.1% | 5.9% | 26.3% |
| GLiNER-PII (local) | 6.1% | 13.3% | 20.9% |

Jev catches a lot and masks more around it. Some of what it is marked wrong for is
arguably personal (a city, "born" next to a birth date), and some of what counts as a leak
is a labelling convention: these datasets set the ceiling as much as the models do. Every
method's numbers are in §01, the details in §02 and §04.

<br>

## 01 · Results

Word-level F2 on the test sets (recall counts four times as much as precision; §08). Best
in each column in bold, reference rows aside.

| method | ai4privacy | Nemotron-PII | TAB | TAB F1 |
|---|---|---|---|---|
| `decision_fields_skip:jev` (Jev, final design) | 0.911 | 0.898 | **0.834** | 0.765 |
| `decision_typed_skip:jev` (Jev, without the field-name option) | 0.838 | 0.834 | 0.822 | 0.788 |
| `decision_typed:jev` (Jev, first design) | 0.829 | 0.792 | 0.790 | 0.731 |
| `decision_words:jev` (Jev, one yes/no per word) | 0.841 | 0.719 | 0.680 | 0.616 |
| Claude Haiku 4.5 | **0.954** | **0.942** | 0.819 | **0.802** |
| Qwen3 235B | 0.946 | 0.920 | 0.743 | 0.733 |
| DeepSeek V4 Flash | 0.939 | 0.941 | 0.746 | 0.760 |
| DeepSeek V4 Flash, thinking | 0.940 | 0.915 | 0.650 | 0.696 |
| Qwen3 30B | 0.907 | 0.900 | 0.630 | 0.627 |
| GPT-4.1 nano | 0.816 | 0.887 | 0.483 | 0.416 |
| GLiNER-PII (local) | 0.841 | 0.872 † | 0.735 | 0.663 |
| Privacy Filter (local) | 0.862 | 0.698 | 0.555 | 0.654 |
| Presidio (local) | 0.587 | 0.671 | 0.744 | 0.762 |
| regex | 0.539 | 0.433 | 0.505 | 0.614 |
| mask everything (floor) | 0.510 | 0.358 | 0.405 | 0.214 |
| a second human expert, same judgments (ceiling; 105 of the 127) | – | – | 0.860 | 0.856 |

† GLiNER-PII was trained on Nemotron-PII's train split. Jev's question designs and the
LLM prompt went through a few rounds, each chosen on the dev pilot (§06).

What gets through: the share of the personal-information words left unmasked, then the
share of documents that came out with nothing left (a failed answer leaks everything).
Lower is better on the first, higher on the second.

| method | ai4privacy | Nemotron-PII | TAB |
|---|---|---|---|
| `decision_fields_skip:jev` (Jev, final design) | 6.7% · 67% | 5.0% · 80% | **11.3%** · 8% |
| `decision_typed:jev` (Jev, first design) | 6.9% · 72% | **4.2% · 83%** | 16.6% · 6% |
| Claude Haiku 4.5 | **3.0%** · 90% | 6.3% · 76% | 16.9% · 5% |
| Qwen3 235B | 3.4% · 88% | 7.8% · 72% | 24.9% · 3% |
| DeepSeek V4 Flash | 4.1% · **91%** | 5.9% · 75% | 26.3% · 2% |
| DeepSeek V4 Flash, thinking | 4.4% · 88% | 9.3% · 67% | 37.7% · 6% |
| Qwen3 30B | 3.9% · **91%** | 7.2% · 73% | 36.8% · 2% |
| GPT-4.1 nano | 19.3% · 67% | 11.5% · 62% | 46.0% · **15%** |
| GLiNER-PII (local) | 6.1% · 79% | 13.3% · 43% | 20.9% · 0% |
| Privacy Filter (local) | 14.3% · 50% | 34.3% · 24% | 49.5% · 0% |
| Presidio (local) | 45.1% · 15% | 36.8% · 11% | 26.7% · 0% |
| regex | 51.3% · 18% | 62.1% · 4% | 54.9% · 0% |
| a second human expert | – | – | 13.7% · 6% |

On judgments almost no document comes out clean for anyone, the second human expert
included, so read TAB's second number as noise and its first as the result.

Cost and speed per document, on short text (Nemotron-PII, ~90 words) and long text (TAB,
~630 words):

| method | $ per 1k docs, short | $ per 1k docs, long | median s per doc, short | median s per doc, long |
|---|---|---|---|---|
| `decision_fields_skip:jev` | 0.50 | 3.79 | 0.47 | 0.66 |
| `decision_typed_skip:jev` | 0.42 | 3.12 | 0.37 | 0.67 |
| `decision_typed:jev` | 0.70 | 5.76 | 0.37 | 0.89 |
| `decision_words:jev` | 0.16 | 1.18 | 0.29 | 0.61 |
| Claude Haiku 4.5 | 1.51 | 5.22 | 1.8 | 3.8 |
| Qwen3 235B | 0.18 | 0.74 | 14 | 19 |
| DeepSeek V4 Flash | 0.09 | 0.42 | 2.1 | 7.0 |
| DeepSeek V4 Flash, thinking | 0.31 | 1.67 | 9.2 | 85 |
| Qwen3 30B | 0.09 | 0.50 | 3.2 | 21 |
| GPT-4.1 nano | 0.10 | 0.35 | 1.5 | 3.5 |
| local models (Presidio, Privacy Filter, GLiNER-PII) | 0 | 0 | 0.02 – 1.8 | 0.1 – 2.3 |

<img src="docs/price.svg" alt="Word-level F2 against dollars per 1,000 documents. Short documents: DeepSeek V4 Flash 0.94 at $0.09, Jev 0.90 at $0.50, Haiku 0.94 at $1.51. Court judgments: Jev 0.83 at $3.79, Haiku 0.82 at $5.22, DeepSeek V4 Flash 0.75 at $0.42." width="100%">

Every table behind these (confidence intervals, precision and recall, recall by type,
calibration, paired tests, the strings each method leaks): [`docs/results.md`](docs/results.md).
Chart-ready numbers: [`docs/data/`](docs/data).

## 02 · Findings

**Jev**

→ **It leaks the least where it matters most.** On court judgments 11.3% of the personal information gets through Jev, against 16.9% for Haiku, 13.7% for a second human expert and 21% to 55% for every method that isn't Jev or Haiku. On Nemotron-PII Jev's two designs leak the least too (4.2% and 5.0%). On ai4privacy the LLMs leak less: 3.0% to 4.4% for all but GPT-4.1 nano, against Jev's 6.7%.

→ **Level with Haiku on F2 where context decides.** On TAB, Jev scores 0.834 against Haiku's 0.819 (paired difference +0.015, [−0.002, +0.032]) and is 0.09 to 0.35 ahead of every method that isn't Jev or Haiku. It recalls 81% of the context-only personal information (a second human expert 77%, Haiku 73%) and, by TAB's own evaluation script, 99.6% of direct identifiers (Haiku 91.6%).

→ **How it's asked decides how good it is.** The first design asked "what is the bracketed word?" with six types or none. In "Account number: 4417…", Jev answered ID for "Account" and "number": the words are about an ID, which is what the question asked. One extra option, "the name of a kind of information, not the information itself", added 0.073 F2 on ai4privacy, 0.064 on Nemotron-PII and 0.012 on TAB (paired, against the same design without it). Not asking about stop words added 0.009 to 0.041 more. Every step is in §06.

→ **On short synthetic text, the larger LLMs lead.** Haiku, Qwen3 235B and DeepSeek V4 Flash, with or without thinking, are 0.02 to 0.04 F2 ahead on ai4privacy and Nemotron-PII. Jev ties Qwen3 30B on both, ties GPT-4.1 nano on Nemotron-PII and beats it on ai4privacy, and is ahead of every local model on every dataset.

→ **It still masks more than the LLMs.** Precision 0.83 / 0.74 / 0.67 on the three datasets, against Haiku's 0.89 / 0.96 / 0.77, so Haiku keeps the best TAB F1 (0.802 against 0.765). On TAB it over-masks "applicant" and "born" most; on Nemotron-PII, field names it still takes for values ("number", "date").

→ **The fastest paid method, by a lot.** 0.3 to 0.9 s per doc, against 1.1 to 21 s for the LLMs and 85 s for DeepSeek with thinking on TAB.

→ **Cost grows with length.** Jev bills input only, but asks one question per word. On ~90-word texts it costs a third of Haiku ($0.50 against $1.51 per 1k), on ~630-word judgments about three quarters ($3.79 against $5.22). The first design, which asked about every word, cost 10% more than Haiku on judgments.

→ **Its probabilities are well calibrated**: expected calibration error 0.04 to 0.08 for the final design, as good as the local models. The first typed design was off by 0.12 to 0.17.

→ **It always answered.** Every Jev call returned a probability for every question; one call failed once and went through on retry.

**Everything else**

→ **Thinking didn't help.** On the documents both DeepSeek modes answered, thinking scored the same on ai4privacy (0.942 against 0.938) and lower on Nemotron-PII (0.915 against 0.941) and TAB (0.749 against 0.775, 113 judgments; `docs/results.md`, last section). On 13 TAB judgments it spent its whole token budget thinking and never wrote an answer. On TAB it took 12 times as long and cost 4 times as much.

→ **Model size matters where context matters.** Qwen3 235B over 30B: +0.04 F2 on ai4privacy, +0.02 on Nemotron-PII, +0.11 on TAB. GPT-4.1 nano drops to 0.48 on TAB.

→ **The prompt matters for LLMs too.** Giving the dataset's own annotation guidelines instead of a one-line definition took Qwen3 235B from 0.53 to 0.78 F2 on TAB in the dev pilot. A second change, asking for exact copies, titles with names, names in full and single-word details, added 0.018 F2 on average on dev; on test it took Haiku from 0.774 to 0.819 on TAB and two models up 0.05 on Nemotron-PII, and cost up to 0.031 on ai4privacy (Haiku unchanged).

→ **Local models are free and limited by what they were trained on.** GLiNER-PII reaches 0.87 on Nemotron-PII, whose train split it learned from. Privacy Filter's precision is 0.88 to 0.93, but its 8 categories leave out organisations, demographics and most IDs. Presidio does well on TAB (0.744), where most personal information is names, dates and places.

→ **Every method leaks what identifies someone only through context**: the employer ("Serco"), a court that names the town ("Będzin District Court"), what the case is about ("widows"). The most-leaked and most over-masked strings per method are in `docs/results.md`.

## 03 · Questions you might have

**Jev ties Haiku on TAB. Is it cheaper or faster?** Both: $3.79 against $5.22 per 1,000
judgments, and 0.66 s against 3.8 s per judgment. On Nemotron-PII's short documents it
costs a third of Haiku's price, but trails it by 0.04 F2. Jev bills every word it reads, so its cost per document grows faster with
length than Haiku's; on these datasets Jev stays cheaper up to about 1,200 words:

<img src="docs/cost.svg" alt="Cents per test document against words in the document, three datasets pooled: Jev's cost rises in a straight line with length, Haiku's flattens; Jev costs more past about 1,200 words." width="100%">

**Weren't the designs changed after seeing results?** Yes, on both sides, and that is how
the numbers got right. The first full run had three problems that only its errors showed:
Jev masked field names like "Account number", the stop-word skip also skipped "May", "US"
and number words, and LLM answers written with straight quotes didn't match the curly
quotes in the judgments. Each fix, and a reworded LLM prompt, was checked on the
20-document dev pilot before the test set was run again; §06 has every step's dev and test
scores. The dev pilot now lists every method's most leaked and most over-masked words, so
problems like these show up before a full run.

**Isn't tuning a threshold an unfair edge over the LLMs?** It's tuned on 20 dev
documents per dataset, never on test. A probability you can put a threshold on is part of
what Jev offers; an LLM gives one answer, and changing its trade-off means rewording the
prompt. F1 and precision at the same threshold are in the tables, so the cost of that
choice is visible.

**Why F2 and not F1?** For anonymisation, a leaked name costs more than an over-masked
word. That choice decides Jev's TAB result, which is why F1 sits next to it.

**Why no GPT-5, Claude Sonnet or Gemini Pro?** Budget: everything here cost $11.83. Haiku
is the strong reference. Any model on OpenRouter is one entry in `config.yaml` and a
rerun away.

**Can I use one of these to anonymise real data?** Not as tested. §04.

**How sure are these numbers?** 500, 500 and 127 test documents. 95% intervals come from
resampling whole documents, and "A beats B" claims use paired intervals on the same
documents. Each method ran once at temperature 0. OpenRouter picks the serving provider
per call, which can shift LLM results between runs.

**Why do strong LLMs drop so much on TAB?** TAB asks for a policy, not a list of entity
types: mask whatever would let someone re-identify the applicant. The LLMs find names and
dates, but miss 27% (Haiku) to 54% (GPT-4.1 nano) of the context-only identifiers:
relatives, places, case details.

**Did the local models see this data in training?** GLiNER-PII was trained on
Nemotron-PII's train split; its test numbers come from the test file. OpenAI reports
Privacy Filter results on pii-masking-300k, the source of the ai4privacy set.

**Can I rerun it?** `make bench`, about $7.40 of OpenRouter calls and 1 to 2 hours. Every
response is cached by request, so a rerun of finished work is free (§09).

## 04 · No single winner

The headline ranks methods on one score. Choosing one for real use turns on things that
score doesn't capture.

→ **What counts as PII for you.** The local models find the categories they were trained on: Privacy Filter has 8 fixed ones, GLiNER-PII takes a list of label names. Neither reads a policy. TAB asks for a policy: mask what would re-identify the applicant, leave the rest in clear. Changing the scope of a local model means new labels or fine-tuning, and how well it does on labels it wasn't trained for is not measured here. LLMs and Jev read the guidelines as text, so changing the scope means editing a prompt, and that alone moved Qwen3 235B from 0.53 to 0.78 F2 on TAB in the dev pilot.

→ **How reliable the output must be.** A local model returns spans every time, in about the same time, from the same weights. An LLM answer can loop, get cut off, fail to parse, or change when OpenRouter routes the call to another provider; here that happened on up to 13 of 127 TAB documents per model, and each counts as finding nothing. Jev returned a probability for every question it was asked.

→ **Where the text may go.** Local models keep the text on the machine. Every Jev and LLM call here sends it to a third-party API through OpenRouter. No setup here was chosen for GDPR or data-residency terms; real personal data needs a provider and contract that allow it, or a model you host.

→ **Cost at volume.** Local models cost nothing per document but need hardware. Jev is fast and bills input only, but its cost grows with document length. LLM cost follows model size.

→ **Picking your own trade-off.** Methods that score each word (Jev, Privacy Filter, GLiNER-PII) let you move a threshold: fewer leaks for more over-masking, or the reverse.

The labels are one team's reading of a policy too. Two human experts labelling the same
judgments reach only 0.86 F2 against each other, and some of what every method is marked
wrong for (a city the policy leaves visible, "and" inside a court's name, cookie flags in
Nemotron-PII) is a convention you might not share. Scored against your own definition, every
number here would move.

A fixed scope at high volume over sensitive text points one way, a scope that changes per
client or per document type points another. The top row of the table answers neither.

## 05 · Why test Jev

Jev is a model from TypeSafe, served through OpenRouter's
[Decisions API](https://openrouter.ai/docs/guides/community/jev). It doesn't write text.
You send it a state and typed questions (yes/no, or pick one of a few options), and it
answers each one with probabilities. Output is free; you pay for input tokens.

PII detection fits that shape: it is one question per word ("is this personal
information?"), and what you want back is a probability you can put a threshold on, not
prose to parse.

<img src="docs/asked.svg" alt="How Jev is asked, on one sentence: each word except stop words gets a question and a probability back; Mr S. Esmer scores 0.88 to 0.92 and is masked, applicants 0.10 and lawyer 0.36 stay, Ankara 0.98 is masked though the annotators left it visible; threshold 0.4, tuned on dev." width="100%">

Decision models became a category while this was being built: OpenAI announced a
Decisions API in limited preview on September 29, 2026, and Fastino's API-only GLiDE
followed on October 1. Both came out too late for this run. A decision model that takes a
state and typed questions is one `DecisionModel` class away (`lanes/decision.py`), and
every question design runs on it unchanged.

This is a look at what models a personal budget can afford can do. It is not a
recommendation of what to deploy.

## 06 · Methods

| family | lanes | output |
|---|---|---|
| reference | `mask_all` (the floor) · `human` (TAB's second annotator against the first) | spans |
| rules | `regex`: emails, phones, IPs, card and ID numbers, dates, times | spans |
| NER and small PII models, local | `presidio` (spaCy `en_core_web_lg`) · `privacy_filter` (OpenAI, 1.5B MoE, 50M active) · `gliner_pii` (NVIDIA, 570M) | spans, and a probability per word for the last two |
| Jev (decision model) | `decision_<design>:jev`, by question design: `words`, one yes/no per word · `typed`, one choice per word (none, or a type) · `typed_skip`, `typed` minus stop words · `fields`, `typed` plus a "name of a kind of information" option · `fields_skip`, both · `bio`, yes/no plus "same item as the word before?" | a probability per word |
| LLMs, via OpenRouter | `llm_sayback:<model>`: list the PII strings, code finds them in the text · `llm_offsets`: character offsets · `llm_tagged`: rewrite the text with tags | spans |

→ **Lanes that read instructions get the same brief** (Jev and the LLMs): the dataset's own annotation guidelines (ai4privacy's and Nemotron-PII's label lists, TAB's published guidelines), then the six types to answer in (`taxonomy.definition`). Regex, Presidio and Privacy Filter run as shipped; GLiNER-PII gets a fixed list of label names.

→ **Jev** gets the whole document once as its state and one question per word, with the word bracketed in a few words of context. Questions are packed into as few calls as fit. Jev's docs give a 32k-token context; calls are packed up to an estimated 48k because larger calls were accepted. Counted in billed tokens, the typed designs went past 32k, mostly on TAB. There, `decision_typed:jev` and `decision_fields_skip:jev` answer slightly worse past 32k (Brier 0.073 against 0.068, and 0.077 against 0.072, on a similar share of PII) and `decision_typed_skip:jev` doesn't (`docs/results.md`, last section).

→ **Per-word scores become spans through a threshold tuned on dev** (word-level F2, never on test), for every lane that scores words. Three structured decoders (hysteresis, gap closing, Viterbi) were tuned the same way and are reported beside it; on the dev pilot none beat the threshold by more than about 0.02 F2.

→ **Privacy Filter**'s own spans come from OpenAI's constrained Viterbi (`opf` package) at its default operating point and match OpenAI's reference runtime; they are in the decoder table. Its headline row uses the tuned threshold on its per-word probability, like the other scorers. That threshold lands at 0.001, the bottom of the grid: at F2 it pays to mask anything the model gives any weight to.

→ **GLiNER-PII** returns candidates down to a 0.05 score; its card default is 0.5. Long documents run in windows sized to its 384-token limit, overlapping by 50 words.

→ **LLMs** run at temperature 0 under a strict JSON schema where the format has one, with an 8k output cap. The sayback prompt asks for every string copied exactly, never reformatted or merged, with titles kept on names, names given in full, and single-word details included. An answer that is cut off or won't parse counts as finding nothing, and the reason is recorded. Strings are matched to the text ignoring case, spacing, and straight vs curly quotes.

→ **Reasoning** is tested on one model, DeepSeek V4 Flash, with thinking off and on, on the same fp8 providers so nothing else changes. Thinking gets an extra 8k tokens.

→ **Dev pilot only** (20 documents per dataset): `decision_bio:jev` (same score as `decision_words:jev` at twice the cost), `decision_fields:jev` (below `decision_fields_skip:jev` on every dataset), the offsets and tagged formats (offsets scored 0.00 on TAB; both loop to the output cap often enough that full test sets would take hours) and Llama 3.1 8B (loops under the strict schema on up to 60% of documents).

### How the designs evolved

Each change was picked on the dev pilot (20 documents per dataset), then run on test.
Word-level F2, ai4privacy · Nemotron-PII · TAB:

| Jev question design | what changed | dev | test |
|---|---|---|---|
| `words` | one yes/no per word | 0.88 · 0.75 · 0.69 | 0.84 · 0.72 · 0.68 |
| `typed` | one choice: none, or one of six types | 0.85 · 0.84 · 0.79 | 0.83 · 0.79 · 0.79 |
| `typed_skip` | stop words never asked; number words and "may", "am", "us", "ca" still asked | 0.86 · 0.87 · 0.82 | 0.84 · 0.83 · 0.82 |
| `fields` | `typed` plus "the name of a kind of information, not the information itself" | 0.95 · 0.91 · 0.80 | – |
| `fields_skip` | both changes | 0.95 · 0.92 · 0.84 | 0.91 · 0.90 · 0.83 |

The first version of the stop-word skip also skipped "May", "US" and number words; it
was fixed before the final run. The LLM prompt went from a one-line definition to each
dataset's guidelines, then to the exact-copy prompt above:

| LLM, test F2 before → after the exact-copy prompt | ai4privacy | Nemotron-PII | TAB |
|---|---|---|---|
| Claude Haiku 4.5 | 0.953 → 0.954 | 0.934 → 0.942 | 0.774 → 0.819 |
| Qwen3 235B | 0.952 → 0.946 | 0.912 → 0.920 | 0.722 → 0.743 |
| DeepSeek V4 Flash | 0.946 → 0.939 | 0.923 → 0.941 | 0.722 → 0.746 |
| DeepSeek V4 Flash, thinking | 0.948 → 0.940 | 0.864 → 0.915 | 0.667 → 0.650 |
| Qwen3 30B | 0.938 → 0.907 | 0.902 → 0.900 | 0.650 → 0.630 |
| GPT-4.1 nano | 0.826 → 0.816 | 0.837 → 0.887 | 0.480 → 0.483 |

One prompt for every model, chosen on its dev average (+0.018 F2), not per model.

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

→ **Leaks**: the share of gold words left unmasked (1 − recall), and the share of documents with any gold word that came out with none left. A failed answer counts as leaking the whole document.

→ **Headline: word-level F2.** A word is gold if a gold span overlaps it, predicted if a predicted span does. F2 weights recall: a leak costs more than an over-mask. Word level credits masking street and city as one span, and counts a half-masked name as a leak.

→ **Format vs context**: recall on each kind of PII, and on TAB, how much of what the annotators left in clear a method masks anyway.

→ **Exact span match** next to it, the usual NER number.

→ **Recall by type and by each dataset's own labels**, precision by the type a method claims, and on TAB and Nemotron-PII the strings each method most often leaks or over-masks (ai4privacy's licence keeps its text out of the published results).

→ **Calibration** (ECE, Brier, reliability bins) for every method that gives a probability per word.

→ **Cost and time**: $ per 1k docs from each response's reported cost, calls and tokens per doc, latency mean / p50 / p95 per doc (for Jev, whose questions on a long doc go out as parallel calls, the slowest of them). Cached reruns report the original numbers. Local models run on an Apple M1 Pro (GPU where supported).

→ **Uncertainty**: 95% intervals by resampling whole documents, and paired intervals on the same documents for "is A really better than B".

→ **Two reference rows**: mask everything (the floor) and a second human expert who labelled the same judgments (TAB's second annotator, scored against the first: the ceiling, on the 105 judgments both labelled). F2 leans on recall hard enough that masking everything scores 0.36 to 0.51 depending on how dense the PII is, so read every row against its dataset's floor.

## 09 · Run it

```sh
uv sync --extra dev --extra ner      # ner: Presidio, spaCy model, torch, Privacy Filter, GLiNER-PII
cp .env.template .env                # add an OpenRouter key
uv run jev-vs-pii fetch              # datasets into data/, never committed
make bench-free                      # rules and local models on the three test sets: $0
make bench                           # everything: dev pilot, threshold tuning, full run, scores, docs/
```

Single lanes: `uv run jev-vs-pii run --lanes decision_words:jev,llm_sayback:qwen3-30b --dataset tab --tier smoke`
(tiers: smoke 2 docs · pilot 20 · full). Every paid call goes through one spend ledger with
a hard cap (`budget_cap_usd` in `config.yaml`) and a response cache, so a rerun costs
nothing. `jev-vs-pii export runs/test` rewrites `docs/results.md` and `docs/data/`.

## 10 · Layout

| path | what |
|---|---|
| `jev_vs_pii/lanes/` | one file per method; `decision.py` asks a decision model a question design from `designs.py` (Jev in `jev.py`), `llm_formats.py` holds the LLM answer formats |
| `jev_vs_pii/clients/` | the only code that calls an API: budget hold, retries, cache |
| `jev_vs_pii/taxonomy.py` | coarse types, format/context shapes, each dataset's guidelines |
| `jev_vs_pii/decode.py` | word scores → spans |
| `jev_vs_pii/align.py` | an LLM's answer → character offsets |
| `jev_vs_pii/metrics/` | word and exact scoring, calibration, bootstrap, cost, error strings, result rows |
| `jev_vs_pii/run/` | runner, tiers, store, threshold tuning |
| `jev_vs_pii/report/` | Markdown tables and the `docs/data/` export |
| `docs/` | every results table, and the numbers behind the charts |

## 11 · Limits

→ Not a deployment recommendation (§04). Models were chosen to fit a small budget, so no frontier-size LLM is in it, and none was chosen for GDPR terms.

→ English only, and no real everyday text: two synthetic sets and one legal one.

→ Public datasets may be in the models' training data. GLiNER-PII was trained on Nemotron-PII's train split: its test numbers come from the test file, but its tuned threshold was picked on dev, which samples train. Privacy Filter reports results on pii-masking-300k.

→ Thresholds are tuned on 20 dev docs per dataset.

→ One run per method at temperature 0. OpenRouter picks the serving provider per call (recorded with every answer), which can change behaviour between runs; only the reasoning pair is pinned.

→ Jev 1.13 is served from an alpha endpoint; its behaviour and prices may change.

→ Jev's question designs and the LLM prompt were revised after reading the first run's test errors; every revision was chosen on dev (§03, §06).

→ The typed designs' calls on TAB were packed past Jev's documented 32k context, where two of them answer slightly worse (§06). Packing to 32k would be the safe setting, at more calls per document.

→ TAB is scored against its first annotator.

→ Prices are OpenRouter list prices on the run date.

## Credits

ai4privacy pii-masking-300k by AI4Privacy. Nemotron-PII by NVIDIA (CC BY 4.0). TAB by
Pilán et al., *The Text Anonymization Benchmark (TAB)*, Computational Linguistics 2022.
OpenAI Privacy Filter (Apache 2.0) and NVIDIA GLiNER-PII.

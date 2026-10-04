## ai4privacy · test (500 docs)

### Word level (headline; per-word lanes use a threshold tuned on dev)

| lane | F2 [95% CI] | P | R | F1 | leaked | docs, no leak | ECE | $/1k docs | p50 s | failed | frontier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| llm_sayback:haiku4.5 | 0.954 [0.939, 0.966] | 0.893 | 0.970 | 0.930 | 3.0% | 90% | – | 1.407 | 1.5 | 0 (+8 dropped) | yes |
| llm_sayback:qwen3-235b | 0.946 [0.933, 0.957] | 0.874 | 0.966 | 0.918 | 3.4% | 88% | – | 0.159 | 8.6 | 0 (+4 dropped) | yes |
| llm_sayback:deepseek-v4-flash-think | 0.940 [0.922, 0.956] | 0.880 | 0.956 | 0.917 | 4.4% | 88% | – | 0.239 | 11 | 1 (+18 dropped) |  |
| llm_sayback:deepseek-v4-flash | 0.939 [0.919, 0.955] | 0.864 | 0.959 | 0.909 | 4.1% | 91% | – | 0.069 | 2.3 | 0 | yes |
| decision_fields_skip:jev · threshold cutoff=0.65 | 0.911 [0.898, 0.923] | 0.834 | 0.933 | 0.880 | 6.7% | 67% | 0.079 | 0.309 | 0.3 | 0 |  |
| llm_sayback:qwen3-30b | 0.907 [0.886, 0.926] | 0.742 | 0.961 | 0.837 | 3.9% | 91% | – | 0.072 | 3.6 | 0 (+14 dropped) |  |
| privacy_filter · threshold cutoff=0.001 | 0.862 [0.844, 0.878] | 0.885 | 0.857 | 0.871 | 14.3% | 50% | 0.042 | 0.000 | 1.5 | 0 | yes |
| decision_words:jev · threshold cutoff=0.35 | 0.841 [0.827, 0.854] | 0.631 | 0.918 | 0.748 | 8.2% | 67% | 0.058 | 0.098 | 0.27 | 0 |  |
| gliner_pii · threshold cutoff=0.05 | 0.841 [0.824, 0.856] | 0.593 | 0.939 | 0.727 | 6.1% | 79% | 0.050 | 0.000 | 0.28 | 0 |  |
| decision_typed_skip:jev · threshold cutoff=0.7 | 0.838 [0.824, 0.851] | 0.573 | 0.947 | 0.714 | 5.3% | 77% | 0.147 | 0.261 | 0.29 | 0 |  |
| decision_typed:jev · threshold cutoff=0.75 | 0.829 [0.815, 0.843] | 0.577 | 0.931 | 0.713 | 6.9% | 72% | 0.171 | 0.339 | 0.31 | 0 |  |
| llm_sayback:gpt4.1-nano | 0.816 [0.779, 0.852] | 0.856 | 0.807 | 0.831 | 19.3% | 67% | – | 0.087 | 1.1 | 0 (+11 dropped) |  |
| presidio | 0.587 [0.563, 0.612] | 0.807 | 0.549 | 0.654 | 45.1% | 15% | – | 0.000 | 0.017 | 0 |  |
| regex | 0.539 [0.506, 0.572] | 0.945 | 0.487 | 0.643 | 51.3% | 18% | – | 0.000 | 9.8e-05 | 0 |  |
| mask_all | 0.510 [0.482, 0.537] | 0.172 | 1.000 | 0.294 | 0.0% | 100% | – | 0.000 | 2.4e-06 | 0 |  |

→ OpenAI reports Privacy Filter results on pii-masking-300k, this set's source.

→ Privacy Filter has 8 categories: no organisations, demographics or most IDs.

→ An LLM answer that is cut off or won't parse counts as finding nothing (`failed`).

### Every lane against decision_fields_skip:jev · threshold cutoff=0.65, same docs (paired bootstrap)

| lane | F2 − decision_fields_skip:jev · threshold cutoff=0.65 [95% CI] | clear gap |
|---|---|---|
| llm_sayback:haiku4.5 | +0.043 [+0.032, +0.054] | yes |
| llm_sayback:qwen3-235b | +0.035 [+0.024, +0.046] | yes |
| llm_sayback:deepseek-v4-flash-think | +0.029 [+0.012, +0.044] | yes |
| llm_sayback:deepseek-v4-flash | +0.028 [+0.010, +0.044] | yes |
| llm_sayback:qwen3-30b | -0.004 [-0.025, +0.015] |  |
| privacy_filter · threshold cutoff=0.001 | -0.049 [-0.063, -0.036] | yes |
| decision_words:jev · threshold cutoff=0.35 | -0.070 [-0.080, -0.059] | yes |
| gliner_pii · threshold cutoff=0.05 | -0.070 [-0.086, -0.053] | yes |
| decision_typed_skip:jev · threshold cutoff=0.7 | -0.073 [-0.084, -0.063] | yes |
| decision_typed:jev · threshold cutoff=0.75 | -0.082 [-0.093, -0.071] | yes |
| llm_sayback:gpt4.1-nano | -0.095 [-0.132, -0.059] | yes |
| presidio | -0.324 [-0.347, -0.300] | yes |
| regex | -0.372 [-0.406, -0.339] | yes |
| mask_all | -0.401 [-0.431, -0.372] | yes |

### Format vs context: recall on PII found by its form vs by its meaning

| lane | format recall | context recall | gap |
|---|---|---|---|
| llm_sayback:haiku4.5 | 0.97 | 0.96 | +0.01 |
| llm_sayback:qwen3-235b | 0.97 | 0.97 | +0.00 |
| llm_sayback:deepseek-v4-flash-think | 0.95 | 0.97 | -0.02 |
| llm_sayback:deepseek-v4-flash | 0.96 | 0.96 | +0.00 |
| decision_fields_skip:jev · threshold cutoff=0.65 | 0.93 | 0.94 | -0.01 |
| llm_sayback:qwen3-30b | 0.95 | 0.97 | -0.02 |
| privacy_filter · threshold cutoff=0.001 | 0.91 | 0.73 | +0.18 |
| decision_words:jev · threshold cutoff=0.35 | 0.93 | 0.89 | +0.04 |
| gliner_pii · threshold cutoff=0.05 | 0.94 | 0.95 | -0.01 |
| decision_typed_skip:jev · threshold cutoff=0.7 | 0.95 | 0.93 | +0.03 |
| decision_typed:jev · threshold cutoff=0.75 | 0.94 | 0.91 | +0.03 |
| llm_sayback:gpt4.1-nano | 0.80 | 0.82 | -0.01 |
| presidio | 0.62 | 0.39 | +0.22 |
| regex | 0.70 | 0.00 | +0.70 |
| mask_all | 1.00 | 1.00 | +0.00 |

### Cost and time per doc

| lane | $/1k docs | calls/doc | tokens in/doc | tokens out/doc | latency mean s | p50 s | p95 s | wall clock s |
|---|---|---|---|---|---|---|---|---|
| gliner_pii · threshold cutoff=0.05 | 0.000 | 0.0 | 0 | 0 | 0.29 | 0.28 | 0.35 | 143 |
| mask_all | 0.000 | 0.0 | 0 | 0 | 2.6e-06 | 2.4e-06 | 2.7e-06 | 0 |
| presidio | 0.000 | 0.0 | 0 | 0 | 0.018 | 0.017 | 0.025 | 9 |
| privacy_filter · threshold cutoff=0.001 | 0.000 | 0.0 | 0 | 0 | 1.5 | 1.5 | 1.9 | 746 |
| regex | 0.000 | 0.0 | 0 | 0 | 0.0001 | 9.8e-05 | 0.00013 | 0 |
| llm_sayback:deepseek-v4-flash | 0.069 | 1.0 | 493 | 147 | 2.7 | 2.3 | 6.2 | 0 |
| llm_sayback:qwen3-30b | 0.072 | 1.0 | 520 | 190 | 4.4 | 3.6 | 10 | 0 |
| llm_sayback:gpt4.1-nano | 0.087 | 1.0 | 549 | 80 | 1.2 | 1.1 | 2.2 | 0 |
| decision_words:jev · threshold cutoff=0.35 | 0.098 | 1.0 | 2,322 | 827 | 0.28 | 0.27 | 0.38 | 0 |
| llm_sayback:qwen3-235b | 0.159 | 1.0 | 520 | 162 | 18 | 8.6 | 63 | 0 |
| llm_sayback:deepseek-v4-flash-think | 0.239 | 1.0 | 493 | 926 | 15 | 11 | 38 | 0 |
| decision_typed_skip:jev · threshold cutoff=0.7 | 0.261 | 1.0 | 6,214 | 2,298 | 0.31 | 0.29 | 0.44 | 2 |
| decision_fields_skip:jev · threshold cutoff=0.65 | 0.309 | 1.0 | 7,346 | 2,576 | 0.31 | 0.3 | 0.4 | 1 |
| decision_typed:jev · threshold cutoff=0.75 | 0.339 | 1.0 | 8,060 | 3,099 | 0.32 | 0.31 | 0.41 | 1 |
| llm_sayback:haiku4.5 | 1.407 | 1.0 | 794 | 123 | 1.6 | 1.5 | 2.3 | 0 |

### Recall by gold type (word level)

| lane | CONTACT | DATETIME | ID | LOCATION | OTHER | PERSON |
|---|---|---|---|---|---|---|
| llm_sayback:haiku4.5 | 0.99 | 0.95 | 0.98 | 0.98 | 0.96 | 0.92 |
| llm_sayback:qwen3-235b | 0.99 | 0.93 | 0.97 | 0.98 | 0.98 | 0.94 |
| llm_sayback:deepseek-v4-flash-think | 1.00 | 0.90 | 0.95 | 0.96 | 1.00 | 0.96 |
| llm_sayback:deepseek-v4-flash | 0.99 | 0.95 | 0.94 | 0.99 | 0.99 | 0.90 |
| decision_fields_skip:jev · threshold cutoff=0.65 | 0.96 | 0.88 | 0.95 | 0.93 | 0.76 | 0.97 |
| llm_sayback:qwen3-30b | 0.98 | 0.91 | 0.96 | 0.98 | 1.00 | 0.95 |
| privacy_filter · threshold cutoff=0.001 | 0.99 | 0.69 | 0.99 | 0.78 | 0.12 | 0.97 |
| decision_words:jev · threshold cutoff=0.35 | 0.99 | 0.82 | 0.98 | 0.87 | 0.85 | 0.96 |
| gliner_pii · threshold cutoff=0.05 | 0.89 | 0.96 | 0.99 | 0.92 | 0.91 | 0.95 |
| decision_typed_skip:jev · threshold cutoff=0.7 | 0.99 | 0.90 | 0.97 | 0.94 | 0.78 | 0.96 |
| decision_typed:jev · threshold cutoff=0.75 | 0.98 | 0.87 | 0.96 | 0.91 | 0.80 | 0.95 |
| llm_sayback:gpt4.1-nano | 0.87 | 0.74 | 0.82 | 0.80 | 0.73 | 0.82 |
| presidio | 0.69 | 0.67 | 0.69 | 0.37 | 0.03 | 0.35 |
| regex | 0.81 | 0.75 | 0.79 | 0.03 | 0.00 | 0.00 |
| mask_all | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |

### Recall by ai4privacy label (labels with ≥ 30 gold words)

| lane | BOD | BUILDING | CITY | COUNTRY | DATE | DRIVERLICENSE | EMAIL | GIVENNAME1 | GIVENNAME2 | IDCARD | IP | LASTNAME1 | LASTNAME2 | PASS | PASSPORT | POSTCODE | SECADDRESS | SEX | SOCIALNUMBER | STATE | STREET | TEL | TIME | TITLE | USERNAME |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| llm_sayback:haiku4.5 | 0.99 | 0.96 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.97 | 1.00 | 0.98 | 1.00 | 1.00 | 1.00 | 0.88 | 0.99 | 0.99 | 0.89 | 0.96 | 1.00 | 0.99 | 1.00 | 1.00 | 0.90 | 0.67 | 0.96 |
| llm_sayback:qwen3-235b | 1.00 | 0.99 | 0.99 | 0.99 | 0.90 | 0.97 | 0.99 | 0.97 | 0.97 | 0.95 | 1.00 | 0.91 | 0.91 | 0.90 | 0.98 | 0.99 | 0.93 | 0.98 | 1.00 | 0.97 | 0.98 | 1.00 | 0.90 | 0.95 | 0.97 |
| llm_sayback:deepseek-v4-flash-think | 1.00 | 0.99 | 0.96 | 1.00 | 0.84 | 0.91 | 0.99 | 1.00 | 1.00 | 0.97 | 1.00 | 1.00 | 1.00 | 0.98 | 0.92 | 0.98 | 0.89 | 1.00 | 1.00 | 0.96 | 0.98 | 1.00 | 0.86 | 0.82 | 1.00 |
| llm_sayback:deepseek-v4-flash | 1.00 | 0.99 | 0.99 | 0.98 | 0.94 | 0.91 | 0.99 | 0.99 | 1.00 | 0.98 | 1.00 | 0.89 | 0.97 | 0.96 | 0.89 | 0.98 | 0.96 | 0.99 | 1.00 | 0.97 | 1.00 | 1.00 | 0.91 | 0.76 | 0.95 |
| decision_fields_skip:jev · threshold cutoff=0.65 | 1.00 | 0.97 | 0.98 | 0.98 | 0.89 | 0.92 | 0.99 | 0.96 | 1.00 | 0.96 | 0.99 | 0.99 | 1.00 | 0.96 | 0.95 | 0.98 | 0.71 | 0.76 | 0.98 | 0.97 | 0.91 | 0.92 | 0.79 | 0.91 | 0.97 |
| llm_sayback:qwen3-30b | 0.98 | 0.97 | 0.98 | 0.97 | 0.89 | 0.99 | 0.99 | 1.00 | 1.00 | 0.99 | 0.96 | 0.99 | 0.97 | 0.95 | 0.96 | 0.98 | 0.96 | 1.00 | 0.93 | 0.98 | 0.99 | 0.99 | 0.88 | 0.81 | 0.96 |
| privacy_filter · threshold cutoff=0.001 | 1.00 | 1.00 | 0.96 | 0.05 | 0.98 | 1.00 | 1.00 | 0.97 | 1.00 | 0.99 | 1.00 | 0.97 | 1.00 | 0.98 | 0.99 | 1.00 | 0.99 | 0.12 | 1.00 | 0.14 | 1.00 | 1.00 | 0.31 | 0.94 | 0.97 |
| decision_words:jev · threshold cutoff=0.35 | 0.99 | 0.98 | 0.94 | 0.83 | 0.73 | 0.96 | 0.99 | 0.96 | 1.00 | 0.97 | 1.00 | 0.99 | 1.00 | 0.98 | 1.00 | 0.98 | 0.74 | 0.85 | 1.00 | 0.96 | 0.74 | 0.98 | 0.75 | 0.87 | 0.98 |
| gliner_pii · threshold cutoff=0.05 | 1.00 | 0.91 | 0.99 | 1.00 | 1.00 | 0.97 | 1.00 | 0.99 | 1.00 | 0.99 | 0.58 | 0.97 | 0.89 | 0.96 | 0.99 | 0.97 | 0.89 | 0.91 | 0.99 | 0.75 | 0.99 | 0.91 | 0.90 | 0.90 | 0.99 |
| decision_typed_skip:jev · threshold cutoff=0.7 | 1.00 | 0.99 | 0.97 | 0.98 | 0.92 | 0.94 | 0.99 | 0.96 | 1.00 | 0.98 | 1.00 | 0.99 | 1.00 | 0.99 | 0.98 | 0.98 | 0.87 | 0.78 | 0.98 | 0.96 | 0.88 | 0.99 | 0.83 | 0.87 | 0.97 |
| decision_typed:jev · threshold cutoff=0.75 | 1.00 | 0.99 | 0.95 | 0.94 | 0.84 | 0.92 | 0.99 | 0.96 | 1.00 | 0.98 | 1.00 | 0.98 | 1.00 | 0.99 | 0.98 | 0.98 | 0.83 | 0.80 | 0.97 | 0.97 | 0.80 | 0.98 | 0.80 | 0.87 | 0.97 |
| llm_sayback:gpt4.1-nano | 0.97 | 0.83 | 0.82 | 0.90 | 0.71 | 0.82 | 0.91 | 0.94 | 1.00 | 0.90 | 0.81 | 0.76 | 0.89 | 0.71 | 0.83 | 0.77 | 0.70 | 0.73 | 0.80 | 0.78 | 0.83 | 0.87 | 0.60 | 0.69 | 0.87 |
| presidio | 0.81 | 0.01 | 0.59 | 0.76 | 0.88 | 0.65 | 1.00 | 0.40 | 0.66 | 0.51 | 1.00 | 0.42 | 0.40 | 0.21 | 0.88 | 0.30 | 0.09 | 0.03 | 0.86 | 0.30 | 0.40 | 0.60 | 0.45 | 0.07 | 0.33 |
| regex | 0.91 | 0.00 | 0.00 | 0.00 | 0.95 | 0.67 | 1.00 | 0.00 | 0.00 | 0.98 | 1.00 | 0.01 | 0.00 | 0.01 | 0.97 | 0.22 | 0.00 | 0.00 | 0.93 | 0.00 | 0.00 | 0.91 | 0.52 | 0.00 | 0.34 |
| mask_all | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |

### Precision by the type a lane claims (typed lanes)

| lane | CONTACT | DATETIME | ID | LOCATION | OTHER | PERSON |
|---|---|---|---|---|---|---|
| llm_sayback:haiku4.5 | 0.95 | 0.89 | 0.95 | 0.90 | 0.60 | 0.81 |
| llm_sayback:qwen3-235b | 0.93 | 0.88 | 0.94 | 0.91 | 0.54 | 0.79 |
| llm_sayback:deepseek-v4-flash-think | 0.91 | 0.89 | 0.94 | 0.90 | 0.56 | 0.82 |
| llm_sayback:deepseek-v4-flash | 0.93 | 0.88 | 0.91 | 0.89 | 0.46 | 0.80 |
| decision_fields_skip:jev · threshold cutoff=0.65 | 0.86 | 0.84 | 0.88 | 0.87 | 0.58 | 0.74 |
| llm_sayback:qwen3-30b | 0.91 | 0.85 | 0.90 | 0.90 | 0.15 | 0.74 |
| decision_typed_skip:jev · threshold cutoff=0.7 | 0.57 | 0.61 | 0.47 | 0.64 | 0.47 | 0.63 |
| decision_typed:jev · threshold cutoff=0.75 | 0.58 | 0.61 | 0.49 | 0.66 | 0.49 | 0.59 |
| llm_sayback:gpt4.1-nano | 0.93 | 0.89 | 0.93 | 0.88 | 0.68 | 0.79 |
| presidio | 0.96 | 0.71 | 0.87 | 0.80 | 0.53 | 0.68 |
| regex | 0.97 | 0.90 | 0.95 | – | – | – |

### Exact span match

| lane | F2 [95% CI] | P | R | F1 | leaked | docs, no leak | ECE | $/1k docs | p50 s | failed | frontier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| llm_sayback:haiku4.5 | 0.901 [0.877, 0.924] | 0.873 | 0.909 | 0.891 | 9.1% | 78% | – | 1.407 | 1.5 | 0 (+8 dropped) | yes |
| llm_sayback:deepseek-v4-flash | 0.850 [0.816, 0.884] | 0.835 | 0.854 | 0.845 | 14.6% | 76% | – | 0.069 | 2.3 | 0 | yes |
| llm_sayback:deepseek-v4-flash-think | 0.827 [0.792, 0.860] | 0.806 | 0.832 | 0.819 | 16.8% | 68% | – | 0.239 | 11 | 1 (+18 dropped) |  |
| llm_sayback:qwen3-235b | 0.821 [0.782, 0.857] | 0.813 | 0.823 | 0.818 | 17.7% | 71% | – | 0.159 | 8.6 | 0 (+4 dropped) |  |
| llm_sayback:qwen3-30b | 0.811 [0.776, 0.845] | 0.756 | 0.827 | 0.790 | 17.3% | 72% | – | 0.072 | 3.6 | 0 (+14 dropped) |  |
| llm_sayback:gpt4.1-nano | 0.734 [0.690, 0.777] | 0.824 | 0.714 | 0.765 | 28.6% | 53% | – | 0.087 | 1.1 | 0 (+11 dropped) |  |
| decision_fields_skip:jev · threshold cutoff=0.65 | 0.558 [0.517, 0.601] | 0.581 | 0.553 | 0.567 | 44.7% | 31% | 0.079 | 0.309 | 0.3 | 0 |  |
| privacy_filter · threshold cutoff=0.001 | 0.505 [0.461, 0.551] | 0.654 | 0.478 | 0.552 | 52.2% | 28% | 0.042 | 0.000 | 1.5 | 0 | yes |
| regex | 0.503 [0.474, 0.534] | 0.838 | 0.457 | 0.591 | 54.3% | 16% | – | 0.000 | 9.8e-05 | 0 |  |
| gliner_pii · threshold cutoff=0.05 | 0.478 [0.438, 0.521] | 0.466 | 0.481 | 0.474 | 51.9% | 27% | 0.050 | 0.000 | 0.28 | 0 |  |
| presidio | 0.469 [0.446, 0.493] | 0.583 | 0.447 | 0.506 | 55.3% | 12% | – | 0.000 | 0.017 | 0 |  |
| decision_typed_skip:jev · threshold cutoff=0.7 | 0.217 [0.188, 0.247] | 0.240 | 0.211 | 0.225 | 78.9% | 13% | 0.147 | 0.261 | 0.29 | 0 |  |
| decision_words:jev · threshold cutoff=0.35 | 0.215 [0.186, 0.246] | 0.309 | 0.200 | 0.243 | 80.0% | 12% | 0.058 | 0.098 | 0.27 | 0 |  |
| decision_typed:jev · threshold cutoff=0.75 | 0.213 [0.183, 0.242] | 0.238 | 0.207 | 0.222 | 79.3% | 14% | 0.171 | 0.339 | 0.31 | 0 |  |
| mask_all | 0.000 [0.000, 0.000] | 0.000 | 0.000 | 0.000 | 100.0% | 0% | – | 0.000 | 2.4e-06 | 0 |  |

### Every decoder on per-word scores (word level)

| lane | F2 [95% CI] | P | R | F1 | leaked | docs, no leak | ECE | $/1k docs | p50 s | failed | frontier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| decision_fields_skip:jev · hysteresis high=0.65 low=0.6 | 0.914 [0.901, 0.926] | 0.814 | 0.943 | 0.874 | 5.7% | 72% | 0.079 | 0.309 | 0.3 | 0 | yes |
| decision_fields_skip:jev · threshold cutoff=0.65 | 0.911 [0.898, 0.923] | 0.834 | 0.933 | 0.880 | 6.7% | 67% | 0.079 | 0.309 | 0.3 | 0 |  |
| decision_fields_skip:jev | 0.910 [0.897, 0.920] | 0.739 | 0.966 | 0.837 | 3.4% | 83% | 0.079 | 0.309 | 0.3 | 0 |  |
| decision_fields_skip:jev · viterbi cutoff=0.7 switch_cost=0.25 | 0.896 [0.882, 0.910] | 0.850 | 0.909 | 0.878 | 9.1% | 60% | 0.079 | 0.309 | 0.3 | 0 |  |
| decision_fields_skip:jev · closing cutoff=0.7 gap=1 | 0.874 [0.860, 0.887] | 0.712 | 0.927 | 0.805 | 7.3% | 66% | 0.079 | 0.309 | 0.3 | 0 |  |
| privacy_filter · threshold cutoff=0.001 | 0.862 [0.844, 0.878] | 0.885 | 0.857 | 0.871 | 14.3% | 50% | 0.042 | 0.000 | 1.5 | 0 | yes |
| privacy_filter · viterbi cutoff=0.01 switch_cost=4.0 | 0.851 [0.831, 0.868] | 0.896 | 0.841 | 0.867 | 15.9% | 46% | 0.042 | 0.000 | 1.5 | 0 |  |
| privacy_filter · hysteresis high=0.25 low=0.03 | 0.846 [0.827, 0.863] | 0.916 | 0.831 | 0.871 | 16.9% | 45% | 0.042 | 0.000 | 1.5 | 0 |  |
| privacy_filter · closing cutoff=0.01 gap=1 | 0.843 [0.825, 0.860] | 0.788 | 0.859 | 0.822 | 14.1% | 52% | 0.042 | 0.000 | 1.5 | 0 |  |
| decision_words:jev · threshold cutoff=0.35 | 0.841 [0.827, 0.854] | 0.631 | 0.918 | 0.748 | 8.2% | 67% | 0.058 | 0.098 | 0.27 | 0 |  |
| gliner_pii · threshold cutoff=0.05 | 0.841 [0.824, 0.856] | 0.593 | 0.939 | 0.727 | 6.1% | 79% | 0.050 | 0.000 | 0.28 | 0 |  |
| gliner_pii · viterbi cutoff=0.03 switch_cost=0.25 | 0.841 [0.824, 0.856] | 0.593 | 0.939 | 0.727 | 6.1% | 79% | 0.050 | 0.000 | 0.28 | 0 |  |
| decision_words:jev · hysteresis high=0.35 low=0.3 | 0.841 [0.826, 0.854] | 0.602 | 0.933 | 0.732 | 6.7% | 73% | 0.058 | 0.098 | 0.27 | 0 |  |
| gliner_pii · hysteresis high=0.25 low=0.03 | 0.840 [0.822, 0.857] | 0.653 | 0.905 | 0.759 | 9.5% | 68% | 0.050 | 0.000 | 0.28 | 0 |  |
| decision_typed_skip:jev · threshold cutoff=0.7 | 0.838 [0.824, 0.851] | 0.573 | 0.947 | 0.714 | 5.3% | 77% | 0.147 | 0.261 | 0.29 | 0 |  |
| privacy_filter | 0.837 [0.817, 0.854] | 0.921 | 0.818 | 0.866 | 18.2% | 42% | 0.042 | 0.000 | 1.5 | 0 |  |
| decision_typed_skip:jev · hysteresis high=0.75 low=0.7 | 0.836 [0.822, 0.850] | 0.576 | 0.942 | 0.715 | 5.8% | 76% | 0.147 | 0.261 | 0.29 | 0 |  |
| decision_typed_skip:jev · viterbi cutoff=0.7 switch_cost=0.25 | 0.835 [0.821, 0.849] | 0.570 | 0.945 | 0.711 | 5.5% | 79% | 0.147 | 0.261 | 0.29 | 0 |  |
| decision_typed:jev · hysteresis high=0.75 low=0.7 | 0.832 [0.819, 0.845] | 0.560 | 0.948 | 0.704 | 5.2% | 78% | 0.171 | 0.339 | 0.31 | 0 |  |
| decision_typed_skip:jev | 0.832 [0.818, 0.845] | 0.523 | 0.976 | 0.681 | 2.4% | 92% | 0.147 | 0.261 | 0.29 | 0 |  |
| decision_typed:jev · threshold cutoff=0.75 | 0.829 [0.815, 0.843] | 0.577 | 0.931 | 0.713 | 6.9% | 72% | 0.171 | 0.339 | 0.31 | 0 |  |
| decision_words:jev · viterbi cutoff=0.4 switch_cost=0.25 | 0.829 [0.812, 0.845] | 0.646 | 0.892 | 0.749 | 10.8% | 61% | 0.058 | 0.098 | 0.27 | 0 |  |
| decision_words:jev · closing cutoff=0.45 gap=1 | 0.827 [0.813, 0.841] | 0.624 | 0.900 | 0.737 | 10.0% | 64% | 0.058 | 0.098 | 0.27 | 0 |  |
| decision_typed_skip:jev · closing cutoff=0.75 gap=1 | 0.826 [0.812, 0.840] | 0.551 | 0.943 | 0.696 | 5.7% | 78% | 0.147 | 0.261 | 0.29 | 0 |  |
| decision_typed:jev · viterbi cutoff=0.6 switch_cost=0.5 | 0.823 [0.809, 0.837] | 0.515 | 0.967 | 0.672 | 3.3% | 88% | 0.171 | 0.339 | 0.31 | 0 |  |
| decision_typed:jev · closing cutoff=0.75 gap=1 | 0.822 [0.809, 0.836] | 0.542 | 0.945 | 0.689 | 5.5% | 78% | 0.171 | 0.339 | 0.31 | 0 |  |
| decision_typed:jev | 0.822 [0.808, 0.836] | 0.500 | 0.980 | 0.662 | 2.0% | 94% | 0.171 | 0.339 | 0.31 | 0 |  |
| decision_words:jev | 0.817 [0.799, 0.834] | 0.725 | 0.844 | 0.780 | 15.6% | 49% | 0.058 | 0.098 | 0.27 | 0 |  |
| gliner_pii · closing cutoff=0.05 gap=1 | 0.806 [0.789, 0.820] | 0.504 | 0.948 | 0.658 | 5.2% | 81% | 0.050 | 0.000 | 0.28 | 0 |  |
| gliner_pii | 0.803 [0.782, 0.824] | 0.742 | 0.820 | 0.779 | 18.0% | 49% | 0.050 | 0.000 | 0.28 | 0 |  |

## nemotron · test (500 docs)

### Word level (headline; per-word lanes use a threshold tuned on dev)

| lane | F2 [95% CI] | P | R | F1 | leaked | docs, no leak | ECE | $/1k docs | p50 s | failed | frontier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| llm_sayback:haiku4.5 | 0.942 [0.931, 0.952] | 0.960 | 0.937 | 0.949 | 6.3% | 76% | – | 1.515 | 1.8 | 0 (+6 dropped) | yes |
| llm_sayback:deepseek-v4-flash | 0.941 [0.932, 0.950] | 0.943 | 0.941 | 0.942 | 5.9% | 75% | – | 0.086 | 2.1 | 0 (+1 dropped) | yes |
| llm_sayback:qwen3-235b | 0.920 [0.907, 0.932] | 0.915 | 0.922 | 0.918 | 7.8% | 72% | – | 0.180 | 14 | 2 (+10 dropped) |  |
| llm_sayback:deepseek-v4-flash-think | 0.915 [0.901, 0.927] | 0.946 | 0.907 | 0.926 | 9.3% | 67% | – | 0.310 | 9.2 | 0 (+5 dropped) |  |
| llm_sayback:qwen3-30b | 0.900 [0.884, 0.914] | 0.803 | 0.928 | 0.861 | 7.2% | 73% | – | 0.093 | 3.2 | 1 (+22 dropped) |  |
| decision_fields_skip:jev · threshold cutoff=0.4 | 0.898 [0.887, 0.907] | 0.736 | 0.950 | 0.829 | 5.0% | 80% | 0.040 | 0.497 | 0.47 | 0 |  |
| llm_sayback:gpt4.1-nano | 0.887 [0.872, 0.901] | 0.898 | 0.885 | 0.891 | 11.5% | 62% | – | 0.099 | 1.5 | 0 (+3 dropped) |  |
| gliner_pii · threshold cutoff=0.2 | 0.872 [0.859, 0.885] | 0.895 | 0.867 | 0.881 | 13.3% | 43% | 0.016 | 0.000 | 0.29 | 0 | yes |
| decision_typed_skip:jev · threshold cutoff=0.4 | 0.834 [0.824, 0.843] | 0.557 | 0.952 | 0.703 | 4.8% | 79% | 0.070 | 0.416 | 0.37 | 0 |  |
| decision_typed:jev · threshold cutoff=0.4 | 0.792 [0.783, 0.803] | 0.469 | 0.958 | 0.630 | 4.2% | 83% | 0.121 | 0.696 | 0.37 | 0 |  |
| decision_words:jev · threshold cutoff=0.1 | 0.719 [0.707, 0.730] | 0.365 | 0.950 | 0.527 | 5.0% | 78% | 0.042 | 0.163 | 0.29 | 0 |  |
| privacy_filter · threshold cutoff=0.001 | 0.698 [0.674, 0.722] | 0.933 | 0.657 | 0.771 | 34.3% | 24% | 0.043 | 0.000 | 1.8 | 0 |  |
| presidio | 0.671 [0.652, 0.692] | 0.897 | 0.632 | 0.741 | 36.8% | 11% | – | 0.000 | 0.019 | 0 |  |
| regex | 0.433 [0.410, 0.454] | 0.995 | 0.379 | 0.549 | 62.1% | 4% | – | 0.000 | 0.00013 | 0 |  |
| mask_all | 0.358 [0.341, 0.374] | 0.100 | 1.000 | 0.182 | 0.0% | 100% | – | 0.000 | 2.7e-06 | 0 |  |

→ GLiNER-PII was trained on Nemotron-PII's train split. Test samples the test file; dev samples train, so GLiNER's dev score and tuned threshold come from its own training data.

→ Privacy Filter has 8 categories: no organisations, demographics or most IDs.

→ An LLM answer that is cut off or won't parse counts as finding nothing (`failed`).

### Every lane against decision_fields_skip:jev · threshold cutoff=0.4, same docs (paired bootstrap)

| lane | F2 − decision_fields_skip:jev · threshold cutoff=0.4 [95% CI] | clear gap |
|---|---|---|
| llm_sayback:haiku4.5 | +0.044 [+0.035, +0.053] | yes |
| llm_sayback:deepseek-v4-flash | +0.043 [+0.034, +0.053] | yes |
| llm_sayback:qwen3-235b | +0.022 [+0.011, +0.034] | yes |
| llm_sayback:deepseek-v4-flash-think | +0.017 [+0.003, +0.031] | yes |
| llm_sayback:qwen3-30b | +0.002 [-0.014, +0.016] |  |
| llm_sayback:gpt4.1-nano | -0.011 [-0.024, +0.002] |  |
| gliner_pii · threshold cutoff=0.2 | -0.025 [-0.037, -0.014] | yes |
| decision_typed_skip:jev · threshold cutoff=0.4 | -0.064 [-0.069, -0.058] | yes |
| decision_typed:jev · threshold cutoff=0.4 | -0.105 [-0.113, -0.098] | yes |
| decision_words:jev · threshold cutoff=0.1 | -0.179 [-0.190, -0.167] | yes |
| privacy_filter · threshold cutoff=0.001 | -0.199 [-0.222, -0.178] | yes |
| presidio | -0.227 [-0.246, -0.206] | yes |
| regex | -0.465 [-0.488, -0.443] | yes |
| mask_all | -0.540 [-0.558, -0.522] | yes |

### Format vs context: recall on PII found by its form vs by its meaning

| lane | format recall | context recall | gap |
|---|---|---|---|
| llm_sayback:haiku4.5 | 0.96 | 0.91 | +0.05 |
| llm_sayback:deepseek-v4-flash | 0.97 | 0.91 | +0.06 |
| llm_sayback:qwen3-235b | 0.97 | 0.88 | +0.09 |
| llm_sayback:deepseek-v4-flash-think | 0.90 | 0.91 | -0.01 |
| llm_sayback:qwen3-30b | 0.98 | 0.87 | +0.11 |
| decision_fields_skip:jev · threshold cutoff=0.4 | 0.95 | 0.95 | -0.00 |
| llm_sayback:gpt4.1-nano | 0.95 | 0.82 | +0.13 |
| gliner_pii · threshold cutoff=0.2 | 0.86 | 0.87 | -0.01 |
| decision_typed_skip:jev · threshold cutoff=0.4 | 0.95 | 0.95 | +0.00 |
| decision_typed:jev · threshold cutoff=0.4 | 0.95 | 0.96 | -0.01 |
| decision_words:jev · threshold cutoff=0.1 | 0.97 | 0.92 | +0.05 |
| privacy_filter · threshold cutoff=0.001 | 0.85 | 0.46 | +0.40 |
| presidio | 0.76 | 0.50 | +0.26 |
| regex | 0.75 | 0.00 | +0.75 |
| mask_all | 1.00 | 1.00 | +0.00 |

### Cost and time per doc

| lane | $/1k docs | calls/doc | tokens in/doc | tokens out/doc | latency mean s | p50 s | p95 s | wall clock s |
|---|---|---|---|---|---|---|---|---|
| gliner_pii · threshold cutoff=0.2 | 0.000 | 0.0 | 0 | 0 | 0.32 | 0.29 | 0.5 | 162 |
| mask_all | 0.000 | 0.0 | 0 | 0 | 4e-06 | 2.7e-06 | 6.5e-06 | 0 |
| presidio | 0.000 | 0.0 | 0 | 0 | 0.023 | 0.019 | 0.051 | 12 |
| privacy_filter · threshold cutoff=0.001 | 0.000 | 0.0 | 0 | 0 | 1.7 | 1.8 | 2.2 | 868 |
| regex | 0.000 | 0.0 | 0 | 0 | 0.00016 | 0.00013 | 0.00037 | 0 |
| llm_sayback:deepseek-v4-flash | 0.086 | 1.0 | 586 | 149 | 2.6 | 2.1 | 4.9 | 0 |
| llm_sayback:qwen3-30b | 0.093 | 1.0 | 610 | 224 | 4.6 | 3.2 | 11 | 0 |
| llm_sayback:gpt4.1-nano | 0.099 | 1.0 | 641 | 88 | 1.6 | 1.5 | 2.5 | 0 |
| decision_words:jev · threshold cutoff=0.1 | 0.163 | 1.0 | 3,887 | 1,854 | 0.31 | 0.29 | 0.42 | 1 |
| llm_sayback:qwen3-235b | 0.180 | 1.0 | 610 | 187 | 16 | 14 | 34 | 0 |
| llm_sayback:deepseek-v4-flash-think | 0.310 | 1.0 | 586 | 1,061 | 13 | 9.2 | 34 | 0 |
| decision_typed_skip:jev · threshold cutoff=0.4 | 0.416 | 1.0 | 9,894 | 3,959 | 0.39 | 0.37 | 0.62 | 2 |
| decision_fields_skip:jev · threshold cutoff=0.4 | 0.497 | 1.0 | 11,841 | 4,434 | 0.48 | 0.47 | 0.68 | 1 |
| decision_typed:jev · threshold cutoff=0.4 | 0.696 | 1.0 | 16,563 | 6,849 | 0.41 | 0.37 | 0.65 | 1 |
| llm_sayback:haiku4.5 | 1.515 | 1.0 | 893 | 124 | 1.8 | 1.8 | 2.4 | 0 |

### Recall by gold type (word level)

| lane | CONTACT | DATETIME | ID | LOCATION | OTHER | PERSON |
|---|---|---|---|---|---|---|
| llm_sayback:haiku4.5 | 0.94 | 0.94 | 1.00 | 0.98 | 0.88 | 0.90 |
| llm_sayback:deepseek-v4-flash | 0.98 | 0.93 | 1.00 | 0.98 | 0.87 | 0.92 |
| llm_sayback:qwen3-235b | 0.97 | 0.93 | 0.99 | 0.96 | 0.81 | 0.91 |
| llm_sayback:deepseek-v4-flash-think | 0.91 | 0.77 | 0.99 | 0.88 | 0.88 | 0.97 |
| llm_sayback:qwen3-30b | 0.97 | 0.98 | 1.00 | 0.95 | 0.82 | 0.89 |
| decision_fields_skip:jev · threshold cutoff=0.4 | 0.91 | 0.94 | 1.00 | 0.99 | 0.89 | 1.00 |
| llm_sayback:gpt4.1-nano | 0.93 | 0.91 | 0.99 | 0.97 | 0.67 | 0.92 |
| gliner_pii · threshold cutoff=0.2 | 0.77 | 0.99 | 0.92 | 0.85 | 0.80 | 0.95 |
| decision_typed_skip:jev · threshold cutoff=0.4 | 0.91 | 0.95 | 1.00 | 1.00 | 0.90 | 1.00 |
| decision_typed:jev · threshold cutoff=0.4 | 0.91 | 0.95 | 1.00 | 1.00 | 0.92 | 1.00 |
| decision_words:jev · threshold cutoff=0.1 | 0.97 | 0.94 | 1.00 | 0.99 | 0.84 | 1.00 |
| privacy_filter · threshold cutoff=0.001 | 0.82 | 0.79 | 0.94 | 0.58 | 0.06 | 0.98 |
| presidio | 0.84 | 0.94 | 0.61 | 0.67 | 0.10 | 0.92 |
| regex | 0.67 | 0.90 | 0.82 | 0.01 | 0.00 | 0.00 |
| mask_all | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |

### Recall by nemotron label (labels with ≥ 30 gold words)

| lane | account_number | age | bank_routing_number | biometric_identifier | blood_type | city | company_name | coordinate | country | county | credit_debit_card | customer_id | date | date_of_birth | date_time | education_level | email | employment_status | fax_number | first_name | gender | health_plan_beneficiary_number | http_cookie | language | last_name | license_plate | medical_record_number | occupation | phone_number | pin | political_view | postcode | race_ethnicity | religious_belief | ssn | state | street_address | time | url | user_name |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| llm_sayback:haiku4.5 | 1.00 | 0.94 | 1.00 | 1.00 | 1.00 | 1.00 | 0.97 | 0.92 | 0.95 | 1.00 | 1.00 | 1.00 | 0.97 | 1.00 | 1.00 | 0.93 | 0.99 | 0.84 | 1.00 | 0.86 | 1.00 | 1.00 | 0.60 | 0.94 | 0.96 | 1.00 | 1.00 | 0.65 | 1.00 | 1.00 | 1.00 | 1.00 | 0.97 | 1.00 | 1.00 | 0.97 | 1.00 | 0.80 | 0.98 | 1.00 |
| llm_sayback:deepseek-v4-flash | 1.00 | 0.94 | 1.00 | 1.00 | 1.00 | 1.00 | 0.95 | 1.00 | 0.88 | 1.00 | 1.00 | 0.99 | 0.96 | 1.00 | 1.00 | 0.93 | 0.99 | 0.80 | 1.00 | 0.88 | 1.00 | 1.00 | 0.91 | 0.82 | 0.98 | 1.00 | 0.98 | 0.64 | 1.00 | 0.97 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.98 | 1.00 | 0.77 | 0.95 | 1.00 |
| llm_sayback:qwen3-235b | 0.95 | 0.94 | 1.00 | 1.00 | 1.00 | 0.98 | 0.93 | 0.96 | 0.88 | 1.00 | 1.00 | 1.00 | 0.97 | 1.00 | 1.00 | 0.89 | 0.98 | 0.64 | 1.00 | 0.86 | 1.00 | 1.00 | 0.87 | 0.88 | 0.97 | 1.00 | 1.00 | 0.55 | 0.99 | 0.97 | 0.81 | 1.00 | 0.94 | 1.00 | 1.00 | 0.88 | 1.00 | 0.77 | 0.97 | 1.00 |
| llm_sayback:deepseek-v4-flash-think | 1.00 | 0.94 | 1.00 | 1.00 | 0.94 | 0.86 | 0.94 | 0.76 | 0.72 | 0.97 | 1.00 | 1.00 | 0.73 | 1.00 | 0.91 | 0.90 | 0.98 | 0.86 | 1.00 | 0.95 | 1.00 | 1.00 | 0.84 | 0.76 | 0.99 | 0.90 | 0.98 | 0.79 | 1.00 | 0.94 | 0.85 | 0.94 | 0.89 | 0.94 | 1.00 | 0.83 | 0.98 | 0.65 | 0.67 | 1.00 |
| llm_sayback:qwen3-30b | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.96 | 0.95 | 0.96 | 0.83 | 1.00 | 1.00 | 1.00 | 0.96 | 1.00 | 1.00 | 0.79 | 0.98 | 0.61 | 1.00 | 0.86 | 0.97 | 1.00 | 0.88 | 0.82 | 0.93 | 1.00 | 1.00 | 0.56 | 1.00 | 1.00 | 0.91 | 1.00 | 0.94 | 1.00 | 1.00 | 0.92 | 1.00 | 0.99 | 0.96 | 1.00 |
| decision_fields_skip:jev · threshold cutoff=0.4 | 1.00 | 0.94 | 1.00 | 1.00 | 0.94 | 1.00 | 0.98 | 0.90 | 1.00 | 1.00 | 1.00 | 1.00 | 0.97 | 1.00 | 1.00 | 0.83 | 0.99 | 0.95 | 1.00 | 1.00 | 1.00 | 1.00 | 0.38 | 1.00 | 1.00 | 1.00 | 1.00 | 0.70 | 1.00 | 0.97 | 0.92 | 1.00 | 1.00 | 1.00 | 1.00 | 0.99 | 1.00 | 0.79 | 0.97 | 1.00 |
| llm_sayback:gpt4.1-nano | 0.99 | 0.94 | 1.00 | 1.00 | 0.91 | 0.95 | 0.93 | 1.00 | 0.91 | 1.00 | 1.00 | 0.99 | 0.96 | 1.00 | 1.00 | 0.37 | 0.97 | 0.38 | 1.00 | 0.89 | 0.97 | 1.00 | 0.60 | 0.67 | 0.98 | 1.00 | 1.00 | 0.27 | 1.00 | 1.00 | 0.83 | 1.00 | 0.74 | 0.86 | 1.00 | 0.98 | 1.00 | 0.71 | 0.94 | 0.99 |
| gliner_pii · threshold cutoff=0.2 | 1.00 | 0.90 | 1.00 | 0.73 | 0.00 | 1.00 | 0.99 | 0.00 | 1.00 | 0.59 | 1.00 | 0.99 | 0.98 | 1.00 | 1.00 | 0.07 | 0.99 | 0.43 | 0.91 | 1.00 | 1.00 | 0.93 | 0.14 | 0.79 | 0.87 | 0.10 | 0.94 | 0.96 | 1.00 | 0.86 | 0.53 | 1.00 | 0.66 | 0.29 | 1.00 | 0.74 | 1.00 | 1.00 | 0.62 | 1.00 |
| decision_typed_skip:jev · threshold cutoff=0.4 | 1.00 | 0.94 | 1.00 | 1.00 | 0.94 | 1.00 | 0.98 | 0.98 | 1.00 | 1.00 | 1.00 | 1.00 | 0.97 | 1.00 | 1.00 | 0.86 | 1.00 | 0.95 | 1.00 | 1.00 | 1.00 | 1.00 | 0.47 | 1.00 | 1.00 | 1.00 | 1.00 | 0.71 | 1.00 | 0.97 | 0.91 | 1.00 | 1.00 | 1.00 | 1.00 | 0.99 | 1.00 | 0.81 | 0.89 | 1.00 |
| decision_typed:jev · threshold cutoff=0.4 | 1.00 | 0.94 | 1.00 | 1.00 | 1.00 | 1.00 | 0.99 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.98 | 1.00 | 1.00 | 0.95 | 1.00 | 0.95 | 1.00 | 1.00 | 1.00 | 1.00 | 0.47 | 1.00 | 1.00 | 1.00 | 1.00 | 0.74 | 1.00 | 0.97 | 0.94 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.83 | 0.87 | 1.00 |
| decision_words:jev · threshold cutoff=0.1 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.73 | 0.98 | 0.98 | 1.00 | 1.00 | 1.00 | 0.96 | 1.00 | 1.00 | 0.99 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.79 | 1.00 | 1.00 | 1.00 | 1.00 | 0.82 | 1.00 | 1.00 | 0.94 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.99 | 0.80 | 0.98 | 1.00 |
| privacy_filter · threshold cutoff=0.001 | 0.97 | 0.00 | 0.94 | 0.98 | 0.21 | 0.44 | 0.08 | 0.76 | 0.19 | 0.30 | 0.98 | 0.93 | 0.88 | 1.00 | 1.00 | 0.00 | 0.98 | 0.04 | 0.80 | 0.97 | 0.00 | 0.93 | 0.76 | 0.12 | 0.98 | 1.00 | 1.00 | 0.02 | 0.91 | 0.89 | 0.13 | 0.82 | 0.09 | 0.20 | 0.97 | 0.39 | 0.94 | 0.33 | 0.46 | 0.89 |
| presidio | 0.83 | 0.87 | 1.00 | 0.98 | 0.00 | 0.84 | 0.06 | 0.10 | 0.97 | 0.94 | 0.61 | 0.66 | 0.97 | 1.00 | 1.00 | 0.00 | 0.99 | 0.00 | 0.94 | 0.90 | 0.00 | 0.55 | 0.26 | 0.33 | 0.94 | 0.16 | 0.96 | 0.00 | 0.89 | 0.72 | 0.30 | 0.47 | 0.34 | 0.69 | 1.00 | 0.85 | 0.44 | 0.80 | 1.00 | 0.47 |
| regex | 0.94 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.10 | 0.00 | 0.00 | 0.87 | 1.00 | 0.94 | 1.00 | 1.00 | 0.00 | 0.98 | 0.00 | 0.89 | 0.00 | 0.00 | 0.95 | 0.33 | 0.00 | 0.00 | 0.13 | 1.00 | 0.00 | 0.87 | 0.64 | 0.00 | 0.12 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.66 | 0.20 | 0.29 |
| mask_all | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |

### Precision by the type a lane claims (typed lanes)

| lane | CONTACT | DATETIME | ID | LOCATION | OTHER | PERSON |
|---|---|---|---|---|---|---|
| llm_sayback:haiku4.5 | 1.00 | 0.97 | 0.99 | 0.98 | 0.88 | 0.99 |
| llm_sayback:deepseek-v4-flash | 1.00 | 0.98 | 0.93 | 0.98 | 0.85 | 0.99 |
| llm_sayback:qwen3-235b | 0.99 | 0.95 | 0.90 | 0.96 | 0.76 | 0.97 |
| llm_sayback:deepseek-v4-flash-think | 1.00 | 0.98 | 0.95 | 0.98 | 0.85 | 0.99 |
| llm_sayback:qwen3-30b | 0.98 | 0.90 | 0.89 | 0.96 | 0.52 | 0.98 |
| decision_fields_skip:jev · threshold cutoff=0.4 | 0.80 | 0.81 | 0.63 | 0.88 | 0.59 | 0.97 |
| llm_sayback:gpt4.1-nano | 1.00 | 0.95 | 0.93 | 0.98 | 0.76 | 0.98 |
| decision_typed_skip:jev · threshold cutoff=0.4 | 0.59 | 0.68 | 0.33 | 0.82 | 0.53 | 0.95 |
| decision_typed:jev · threshold cutoff=0.4 | 0.50 | 0.58 | 0.26 | 0.78 | 0.44 | 0.87 |
| presidio | 1.00 | 0.69 | 0.98 | 0.95 | 0.93 | 0.97 |
| regex | 1.00 | 1.00 | 0.99 | – | – | – |

### Exact span match

| lane | F2 [95% CI] | P | R | F1 | leaked | docs, no leak | ECE | $/1k docs | p50 s | failed | frontier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| llm_sayback:haiku4.5 | 0.800 [0.777, 0.823] | 0.858 | 0.787 | 0.821 | 21.3% | 49% | – | 1.515 | 1.8 | 0 (+6 dropped) | yes |
| llm_sayback:deepseek-v4-flash | 0.786 [0.764, 0.809] | 0.846 | 0.772 | 0.808 | 22.8% | 45% | – | 0.086 | 2.1 | 0 (+1 dropped) | yes |
| llm_sayback:qwen3-235b | 0.758 [0.733, 0.783] | 0.816 | 0.745 | 0.779 | 25.5% | 43% | – | 0.180 | 14 | 2 (+10 dropped) |  |
| llm_sayback:qwen3-30b | 0.754 [0.731, 0.776] | 0.749 | 0.755 | 0.752 | 24.5% | 41% | – | 0.093 | 3.2 | 1 (+22 dropped) |  |
| llm_sayback:gpt4.1-nano | 0.747 [0.724, 0.769] | 0.807 | 0.733 | 0.768 | 26.7% | 36% | – | 0.099 | 1.5 | 0 (+3 dropped) |  |
| llm_sayback:deepseek-v4-flash-think | 0.746 [0.722, 0.770] | 0.835 | 0.727 | 0.777 | 27.3% | 33% | – | 0.310 | 9.2 | 0 (+5 dropped) |  |
| gliner_pii · threshold cutoff=0.2 | 0.658 [0.634, 0.680] | 0.761 | 0.636 | 0.693 | 36.4% | 19% | 0.016 | 0.000 | 0.29 | 0 | yes |
| decision_fields_skip:jev · threshold cutoff=0.4 | 0.587 [0.566, 0.608] | 0.533 | 0.603 | 0.566 | 39.7% | 16% | 0.040 | 0.497 | 0.47 | 0 |  |
| presidio | 0.506 [0.488, 0.524] | 0.592 | 0.489 | 0.535 | 51.1% | 2% | – | 0.000 | 0.019 | 0 |  |
| privacy_filter · threshold cutoff=0.001 | 0.490 [0.465, 0.514] | 0.752 | 0.451 | 0.564 | 54.9% | 9% | 0.043 | 0.000 | 1.8 | 0 |  |
| decision_typed_skip:jev · threshold cutoff=0.4 | 0.465 [0.446, 0.483] | 0.378 | 0.493 | 0.428 | 50.7% | 6% | 0.070 | 0.416 | 0.37 | 0 |  |
| regex | 0.415 [0.395, 0.433] | 0.828 | 0.369 | 0.510 | 63.1% | 2% | – | 0.000 | 0.00013 | 0 |  |
| decision_typed:jev · threshold cutoff=0.4 | 0.340 [0.322, 0.358] | 0.289 | 0.356 | 0.319 | 64.4% | 2% | 0.121 | 0.696 | 0.37 | 0 |  |
| decision_words:jev · threshold cutoff=0.1 | 0.240 [0.224, 0.256] | 0.184 | 0.260 | 0.215 | 74.0% | 1% | 0.042 | 0.163 | 0.29 | 0 |  |
| mask_all | 0.000 [0.000, 0.000] | 0.000 | 0.000 | 0.000 | 100.0% | 0% | – | 0.000 | 2.7e-06 | 0 |  |

### Every decoder on per-word scores (word level)

| lane | F2 [95% CI] | P | R | F1 | leaked | docs, no leak | ECE | $/1k docs | p50 s | failed | frontier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| decision_fields_skip:jev | 0.914 [0.903, 0.923] | 0.828 | 0.938 | 0.880 | 6.2% | 75% | 0.040 | 0.497 | 0.47 | 0 | yes |
| decision_fields_skip:jev · viterbi cutoff=0.4 switch_cost=0.25 | 0.907 [0.896, 0.917] | 0.786 | 0.943 | 0.858 | 5.7% | 78% | 0.040 | 0.497 | 0.47 | 0 |  |
| decision_fields_skip:jev · hysteresis high=0.45 low=0.4 | 0.904 [0.894, 0.913] | 0.764 | 0.948 | 0.846 | 5.2% | 79% | 0.040 | 0.497 | 0.47 | 0 |  |
| decision_fields_skip:jev · threshold cutoff=0.4 | 0.898 [0.887, 0.907] | 0.736 | 0.950 | 0.829 | 5.0% | 80% | 0.040 | 0.497 | 0.47 | 0 |  |
| decision_fields_skip:jev · closing cutoff=0.4 gap=1 | 0.882 [0.872, 0.891] | 0.672 | 0.957 | 0.789 | 4.3% | 84% | 0.040 | 0.497 | 0.47 | 0 |  |
| gliner_pii · threshold cutoff=0.2 | 0.872 [0.859, 0.885] | 0.895 | 0.867 | 0.881 | 13.3% | 43% | 0.016 | 0.000 | 0.29 | 0 | yes |
| gliner_pii · viterbi cutoff=0.2 switch_cost=0.25 | 0.872 [0.858, 0.884] | 0.903 | 0.864 | 0.883 | 13.6% | 42% | 0.016 | 0.000 | 0.29 | 0 |  |
| gliner_pii · closing cutoff=0.2 gap=1 | 0.867 [0.854, 0.880] | 0.859 | 0.869 | 0.864 | 13.1% | 43% | 0.016 | 0.000 | 0.29 | 0 |  |
| gliner_pii · hysteresis high=0.45 low=0.2 | 0.865 [0.851, 0.877] | 0.929 | 0.850 | 0.888 | 15.0% | 38% | 0.016 | 0.000 | 0.29 | 0 |  |
| gliner_pii | 0.852 [0.838, 0.865] | 0.933 | 0.834 | 0.881 | 16.6% | 32% | 0.016 | 0.000 | 0.29 | 0 |  |
| decision_typed_skip:jev · threshold cutoff=0.4 | 0.834 [0.824, 0.843] | 0.557 | 0.952 | 0.703 | 4.8% | 79% | 0.070 | 0.416 | 0.37 | 0 |  |
| decision_typed_skip:jev · hysteresis high=0.45 low=0.4 | 0.833 [0.822, 0.842] | 0.567 | 0.943 | 0.708 | 5.7% | 74% | 0.070 | 0.416 | 0.37 | 0 |  |
| decision_typed_skip:jev · viterbi cutoff=0.3 switch_cost=0.25 | 0.832 [0.822, 0.841] | 0.544 | 0.959 | 0.694 | 4.1% | 81% | 0.070 | 0.416 | 0.37 | 0 |  |
| decision_typed_skip:jev | 0.831 [0.821, 0.840] | 0.587 | 0.928 | 0.719 | 7.2% | 68% | 0.070 | 0.416 | 0.37 | 0 |  |
| decision_typed:jev | 0.808 [0.797, 0.819] | 0.522 | 0.936 | 0.671 | 6.4% | 70% | 0.121 | 0.696 | 0.37 | 0 |  |
| decision_typed_skip:jev · closing cutoff=0.4 gap=1 | 0.804 [0.794, 0.814] | 0.489 | 0.959 | 0.647 | 4.1% | 84% | 0.070 | 0.416 | 0.37 | 0 |  |
| decision_typed:jev · hysteresis high=0.45 low=0.4 | 0.795 [0.785, 0.806] | 0.478 | 0.952 | 0.637 | 4.8% | 79% | 0.121 | 0.696 | 0.37 | 0 |  |
| decision_typed:jev · threshold cutoff=0.4 | 0.792 [0.783, 0.803] | 0.469 | 0.958 | 0.630 | 4.2% | 83% | 0.121 | 0.696 | 0.37 | 0 |  |
| decision_typed:jev · viterbi cutoff=0.4 switch_cost=0.25 | 0.786 [0.776, 0.797] | 0.469 | 0.946 | 0.627 | 5.4% | 74% | 0.121 | 0.696 | 0.37 | 0 |  |
| decision_typed:jev · closing cutoff=0.5 gap=1 | 0.785 [0.775, 0.796] | 0.472 | 0.942 | 0.629 | 5.8% | 73% | 0.121 | 0.696 | 0.37 | 0 |  |
| decision_words:jev · hysteresis high=0.25 low=0.2 | 0.740 [0.725, 0.753] | 0.516 | 0.830 | 0.637 | 17.0% | 50% | 0.042 | 0.163 | 0.29 | 0 |  |
| decision_words:jev · threshold cutoff=0.1 | 0.719 [0.707, 0.730] | 0.365 | 0.950 | 0.527 | 5.0% | 78% | 0.042 | 0.163 | 0.29 | 0 |  |
| decision_words:jev · viterbi cutoff=0.1 switch_cost=0.25 | 0.717 [0.704, 0.728] | 0.374 | 0.930 | 0.533 | 7.0% | 76% | 0.042 | 0.163 | 0.29 | 0 |  |
| privacy_filter · threshold cutoff=0.001 | 0.698 [0.674, 0.722] | 0.933 | 0.657 | 0.771 | 34.3% | 24% | 0.043 | 0.000 | 1.8 | 0 |  |
| decision_words:jev · closing cutoff=0.1 gap=1 | 0.693 [0.681, 0.705] | 0.330 | 0.957 | 0.491 | 4.3% | 83% | 0.042 | 0.163 | 0.29 | 0 |  |
| privacy_filter · closing cutoff=0.01 gap=1 | 0.669 [0.643, 0.693] | 0.934 | 0.625 | 0.749 | 37.5% | 20% | 0.043 | 0.000 | 1.8 | 0 |  |
| privacy_filter · viterbi cutoff=0.01 switch_cost=0.5 | 0.664 [0.638, 0.689] | 0.954 | 0.618 | 0.750 | 38.2% | 19% | 0.043 | 0.000 | 1.8 | 0 |  |
| decision_words:jev | 0.661 [0.638, 0.683] | 0.706 | 0.650 | 0.677 | 35.0% | 25% | 0.042 | 0.163 | 0.29 | 0 |  |
| privacy_filter · hysteresis high=0.25 low=0.03 | 0.639 [0.611, 0.665] | 0.962 | 0.590 | 0.731 | 41.0% | 17% | 0.043 | 0.000 | 1.8 | 0 |  |
| privacy_filter | 0.615 [0.586, 0.643] | 0.972 | 0.564 | 0.714 | 43.6% | 16% | 0.043 | 0.000 | 1.8 | 0 |  |

### Most leaked and most over-masked strings

→ **llm_sayback:haiku4.5** leaks: paul (7), 60 seconds (5), reva (4), heather (4), author (4), kathy (4), kevin (3), yolanda (3)  
over-masks: gender (6), liverpool (4), asthma (3), manchester united (3), vegan (3), microsoft (3), chase bank (2), acmecorp (2)

→ **llm_sayback:deepseek-v4-flash** leaks: author (5), 60 seconds (5), reva (4), heather (4), kathy (4), yolanda (3), manager (3), yadira (3)  
over-masks: liverpool (4), race ethnicity (3), manchester united (3), employee (3), political view (3), microsoft (3), her (2), api key (2)

→ **llm_sayback:qwen3-235b** leaks: paul (7), author (5), 60 seconds (5), reva (4), full-time (4), heather (4), kathy (4), kerala (4)  
over-masks: the candidate (7), gender (6), liverpool (4), investor (4), race ethnicity (3), manchester united (3), email (3), phone number (3)

→ **llm_sayback:deepseek-v4-flash-think** leaks: usa (7), 2024-07-15 (5), 07/15/2024 (5), 60 seconds (5), english (4), kathy (4), kerala (4), revvibe motors (4)  
over-masks: liverpool (4), manchester united (3), his (2), chase bank (2), catholic (2), user account and transaction services (2), 34 (1), 5'10" (1)

→ **llm_sayback:qwen3-30b** leaks: lea (7), maurer (7), author (5), reva (4), full-time (4), heather (4), paul (4), kathy (4)  
over-masks: liverpool (4), the investor (4), $50 (3), asthma (3), manchester united (3), variation (3), race ethnicity (3), training plan (3)

→ **decision_fields_skip:jev · threshold cutoff=0.4** leaks: some college (7), 60 seconds (5), tecnovista it (4), sales representatives (2), 25 (2), a positive (2), janitor building cleaner (2), jwt_token=eyjhbgcioijiuzi1niisinr5cci6i… (2)  
over-masks: number (55), date (46), id (27), pin (26), contact (17), account (17), blood type (16), company (16)

→ **llm_sayback:gpt4.1-nano** leaks: full-time (9), high school (6), some college (6), part-time (6), graduate level (5), english (5), author (5), 60 seconds (5)  
over-masks: $5,000 (4), liverpool (4), the investor (4), instagram (3), facebook (3), manchester united (3), 5% (3), $500.00 (3)

→ **gliner_pii · threshold cutoff=0.2** leaks: full-time (17), high school (13), o+ (10), some college (7), english (6), bachelor's degree (6), black (5), graduate level (5)  
over-masks: support team (12), healthcare provider (9), digital marketing (5), user (4), consultant (4), 2024 (4), service representative (4), author (4)

→ **decision_typed_skip:jev · threshold cutoff=0.4** leaks: some college (7), 60 seconds (5), tecnovista it (4), https://developer.github.com/v3/repos/#… (3), sales representatives (2), 25 (2), brokerage team (2), a positive (2)  
over-masks: email (80), date (64), account (35), user (30), medical record number (28), account number (27), customer id (25), health plan beneficiary number (24)

→ **decision_typed:jev · threshold cutoff=0.4** leaks: 60 seconds (5), https://developer.github.com/v3/repos/#… (3), sales representatives (2), 25 (2), brokerage team (2), janitor building cleaner (2), jwt_token=eyjhbgcioijiuzi1niisinr5cci6i… (2), 5-minute (2)  
over-masks: email (54), account (27), date (26), the (23), a (20), customer id (20), contact (19), account number (17)

→ **decision_words:jev · threshold cutoff=0.1** leaks: harper & lane products (7), 60 seconds (5), greensprout solutions (3), tecnovista it (3), electoral solutions ltd. (3), sales representatives (2), innolink services (2), harvest capital partners (2)  
over-masks: your (147), you (45), email (44), my (37), i (35), me (30), date (29), her (23)

→ **privacy_filter · threshold cutoff=0.001** leaks: usa (28), full-time (19), male (16), female (15), english (13), high school (13), part-time (10), white (8)  
over-masks: cvv (2), http (2), 123456 (2), bic (1), us (1), u2v1bcbbdcfcmyzynzhcm1v (1), whom (1), delves (1)

→ **presidio** leaks: full-time (19), male (16), female (15), english (14), high school (13), o+ (10), part-time (10), self-employed (7)  
over-masks: today (18), daily (12), the day (5), annual (4), 2024 (3), liverpool (3), commonwealth (2), 24 hours (2)

→ **regex** leaks: usa (40), full-time (19), male (16), female (15), english (14), high school (13), su su (13), james (11)  
over-masks: 123456 (2), 120/80 (1), 80-100 (1), 12345678 (1), 555-555-5555 (1), 095514669851365 (1), 2026r01 (1), suptick-20230219-001 (1)

## tab · test (105 docs, 127 docs)

### Word level (headline; per-word lanes use a threshold tuned on dev)

| lane | F2 [95% CI] | P | R | F1 | leaked | docs, no leak | ECE | $/1k docs | p50 s | failed | frontier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| human | 0.860 [0.840, 0.879] | 0.849 | 0.863 | 0.856 | 13.7% | 6% | – | 0.000 | 0 | 0 |  |
| decision_fields_skip:jev · threshold cutoff=0.4 | 0.834 [0.821, 0.845] | 0.672 | 0.887 | 0.765 | 11.3% | 8% | 0.045 | 3.787 | 0.66 | 0 | yes |
| decision_typed_skip:jev · threshold cutoff=0.5 | 0.822 [0.806, 0.836] | 0.738 | 0.845 | 0.788 | 15.5% | 6% | 0.049 | 3.120 | 0.67 | 0 | yes |
| llm_sayback:haiku4.5 | 0.819 [0.801, 0.837] | 0.775 | 0.831 | 0.802 | 16.9% | 5% | – | 5.219 | 3.8 | 0 (+4 dropped) |  |
| decision_typed:jev · threshold cutoff=0.55 | 0.790 [0.774, 0.805] | 0.651 | 0.834 | 0.731 | 16.6% | 6% | 0.121 | 5.762 | 0.89 | 0 |  |
| llm_sayback:deepseek-v4-flash | 0.746 [0.706, 0.782] | 0.785 | 0.737 | 0.760 | 26.3% | 2% | – | 0.418 | 7 | 2 (+11 dropped) | yes |
| presidio | 0.744 [0.725, 0.762] | 0.793 | 0.733 | 0.762 | 26.7% | 0% | – | 0.000 | 0.12 | 0 | yes |
| llm_sayback:qwen3-235b | 0.743 [0.698, 0.778] | 0.716 | 0.751 | 0.733 | 24.9% | 3% | – | 0.736 | 19 | 2 (+17 dropped) |  |
| gliner_pii · threshold cutoff=0.05 | 0.735 [0.718, 0.750] | 0.571 | 0.791 | 0.663 | 20.9% | 0% | 0.063 | 0.000 | 1.4 | 0 |  |
| decision_words:jev · threshold cutoff=0.3 | 0.680 [0.662, 0.699] | 0.533 | 0.731 | 0.616 | 26.9% | 0% | 0.055 | 1.180 | 0.61 | 0 |  |
| llm_sayback:deepseek-v4-flash-think | 0.650 [0.588, 0.711] | 0.786 | 0.623 | 0.696 | 37.7% | 6% | – | 1.669 | 85 | 13 (+4 dropped) |  |
| llm_sayback:qwen3-30b | 0.630 [0.581, 0.678] | 0.622 | 0.632 | 0.627 | 36.8% | 2% | – | 0.497 | 21 | 9 (+112 dropped) |  |
| privacy_filter · threshold cutoff=0.001 | 0.555 [0.520, 0.590] | 0.928 | 0.505 | 0.654 | 49.5% | 0% | 0.084 | 0.000 | 2.3 | 0 |  |
| regex | 0.505 [0.472, 0.537] | 0.965 | 0.451 | 0.614 | 54.9% | 0% | – | 0.000 | 0.0011 | 0 |  |
| llm_sayback:gpt4.1-nano | 0.483 [0.441, 0.524] | 0.338 | 0.540 | 0.416 | 46.0% | 15% | – | 0.351 | 3.5 | 0 (+48 dropped) |  |
| mask_all | 0.405 [0.386, 0.423] | 0.120 | 1.000 | 0.214 | 0.0% | 100% | – | 0.000 | 2.5e-06 | 0 |  |

→ Privacy Filter has 8 categories: no organisations, demographics or most IDs.

→ An LLM answer that is cut off or won't parse counts as finding nothing (`failed`).

### Every lane against decision_fields_skip:jev · threshold cutoff=0.4, same docs (paired bootstrap)

| lane | F2 − decision_fields_skip:jev · threshold cutoff=0.4 [95% CI] | clear gap |
|---|---|---|
| decision_typed_skip:jev · threshold cutoff=0.5 | -0.012 [-0.019, -0.005] | yes |
| llm_sayback:haiku4.5 | -0.015 [-0.032, +0.002] |  |
| decision_typed:jev · threshold cutoff=0.55 | -0.044 [-0.053, -0.035] | yes |
| llm_sayback:deepseek-v4-flash | -0.088 [-0.130, -0.051] | yes |
| presidio | -0.090 [-0.107, -0.073] | yes |
| llm_sayback:qwen3-235b | -0.090 [-0.138, -0.051] | yes |
| gliner_pii · threshold cutoff=0.05 | -0.099 [-0.116, -0.083] | yes |
| decision_words:jev · threshold cutoff=0.3 | -0.153 [-0.167, -0.139] | yes |
| llm_sayback:deepseek-v4-flash-think | -0.183 [-0.246, -0.124] | yes |
| llm_sayback:qwen3-30b | -0.204 [-0.256, -0.153] | yes |
| privacy_filter · threshold cutoff=0.001 | -0.278 [-0.311, -0.246] | yes |
| regex | -0.329 [-0.361, -0.298] | yes |
| llm_sayback:gpt4.1-nano | -0.351 [-0.392, -0.310] | yes |
| mask_all | -0.428 [-0.450, -0.406] | yes |

### Format vs context: recall on PII found by its form vs by its meaning

| lane | format recall | context recall | gap | left-in-clear masked (lower is better) |
|---|---|---|---|---|
| human | 0.93 | 0.77 | +0.16 | 0.21 |
| decision_fields_skip:jev · threshold cutoff=0.4 | 0.94 | 0.81 | +0.14 | 0.39 |
| decision_typed_skip:jev · threshold cutoff=0.5 | 0.93 | 0.73 | +0.20 | 0.25 |
| llm_sayback:haiku4.5 | 0.90 | 0.73 | +0.17 | 0.37 |
| decision_typed:jev · threshold cutoff=0.55 | 0.92 | 0.72 | +0.20 | 0.22 |
| llm_sayback:deepseek-v4-flash | 0.80 | 0.64 | +0.16 | 0.30 |
| presidio | 0.90 | 0.50 | +0.40 | 0.25 |
| llm_sayback:qwen3-235b | 0.84 | 0.63 | +0.21 | 0.37 |
| gliner_pii · threshold cutoff=0.05 | 0.86 | 0.69 | +0.18 | 0.73 |
| decision_words:jev · threshold cutoff=0.3 | 0.79 | 0.64 | +0.15 | 0.14 |
| llm_sayback:deepseek-v4-flash-think | 0.70 | 0.51 | +0.18 | 0.25 |
| llm_sayback:qwen3-30b | 0.68 | 0.56 | +0.12 | 0.36 |
| privacy_filter · threshold cutoff=0.001 | 0.52 | 0.48 | +0.05 | 0.04 |
| regex | 0.77 | 0.00 | +0.77 | 0.02 |
| llm_sayback:gpt4.1-nano | 0.60 | 0.46 | +0.14 | 0.33 |
| mask_all | 1.00 | 1.00 | +0.00 | 1.00 |

### Cost and time per doc

| lane | $/1k docs | calls/doc | tokens in/doc | tokens out/doc | latency mean s | p50 s | p95 s | wall clock s |
|---|---|---|---|---|---|---|---|---|
| gliner_pii · threshold cutoff=0.05 | 0.000 | 0.0 | 0 | 0 | 1.7 | 1.4 | 3.3 | 217 |
| mask_all | 0.000 | 0.0 | 0 | 0 | 3e-06 | 2.5e-06 | 3e-06 | 0 |
| presidio | 0.000 | 0.0 | 0 | 0 | 0.15 | 0.12 | 0.3 | 20 |
| privacy_filter · threshold cutoff=0.001 | 0.000 | 0.0 | 0 | 0 | 2.4 | 2.3 | 2.9 | 304 |
| regex | 0.000 | 0.0 | 0 | 0 | 0.0014 | 0.0011 | 0.0027 | 0 |
| llm_sayback:gpt4.1-nano | 0.351 | 1.0 | 1,671 | 460 | 4.2 | 3.5 | 9.4 | 68 |
| llm_sayback:deepseek-v4-flash | 0.418 | 1.0 | 1,618 | 789 | 11 | 7 | 22 | 186 |
| llm_sayback:qwen3-30b | 0.497 | 1.0 | 1,703 | 1,413 | 40 | 21 | 92 | 1 |
| llm_sayback:qwen3-235b | 0.736 | 1.0 | 1,703 | 925 | 33 | 19 | 86 | 823 |
| decision_words:jev · threshold cutoff=0.3 | 1.180 | 1.5 | 28,098 | 15,997 | 0.61 | 0.61 | 0.87 | 2 |
| llm_sayback:deepseek-v4-flash-think | 1.669 | 1.0 | 1,617 | 6,586 | 1.1e+02 | 85 | 3e+02 | 1844 |
| decision_typed_skip:jev · threshold cutoff=0.5 | 3.120 | 2.3 | 74,281 | 30,748 | 0.75 | 0.67 | 1 | 3 |
| decision_fields_skip:jev · threshold cutoff=0.4 | 3.787 | 2.7 | 90,174 | 34,350 | 0.69 | 0.66 | 1 | 2 |
| llm_sayback:haiku4.5 | 5.219 | 1.0 | 2,040 | 636 | 4.2 | 3.8 | 7 | 70 |
| decision_typed:jev · threshold cutoff=0.55 | 5.762 | 3.8 | 137,191 | 57,303 | 1.1 | 0.89 | 2.7 | 3 |

### Recall by gold type (word level)

| lane | DATETIME | ID | LOCATION | OTHER | PERSON |
|---|---|---|---|---|---|
| human | 0.94 | 0.98 | 0.91 | 0.58 | 0.91 |
| decision_fields_skip:jev · threshold cutoff=0.4 | 0.97 | 0.99 | 0.90 | 0.57 | 0.98 |
| decision_typed_skip:jev · threshold cutoff=0.5 | 0.96 | 0.99 | 0.88 | 0.40 | 0.98 |
| llm_sayback:haiku4.5 | 0.93 | 0.82 | 0.91 | 0.57 | 0.83 |
| decision_typed:jev · threshold cutoff=0.55 | 0.95 | 0.99 | 0.88 | 0.35 | 1.00 |
| llm_sayback:deepseek-v4-flash | 0.84 | 0.27 | 0.80 | 0.52 | 0.72 |
| presidio | 0.99 | 0.05 | 0.74 | 0.17 | 0.73 |
| llm_sayback:qwen3-235b | 0.86 | 0.77 | 0.86 | 0.53 | 0.67 |
| gliner_pii · threshold cutoff=0.05 | 0.93 | 0.51 | 0.79 | 0.55 | 0.72 |
| decision_words:jev · threshold cutoff=0.3 | 0.82 | 0.88 | 0.73 | 0.28 | 0.96 |
| llm_sayback:deepseek-v4-flash-think | 0.73 | 0.49 | 0.58 | 0.49 | 0.50 |
| llm_sayback:qwen3-30b | 0.71 | 0.54 | 0.80 | 0.52 | 0.53 |
| privacy_filter · threshold cutoff=0.001 | 0.56 | 0.27 | 0.09 | 0.04 | 0.93 |
| regex | 0.80 | 0.88 | 0.00 | 0.00 | 0.00 |
| llm_sayback:gpt4.1-nano | 0.62 | 0.43 | 0.65 | 0.30 | 0.56 |
| mask_all | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |

### TAB's official script (entity recall on direct / quasi identifiers, token P/R/F1)

| lane | ER direct | ER quasi | token R | token P | token F1 |
|---|---|---|---|---|---|
| decision_fields_skip:jev · threshold cutoff=0.4 | 0.996 | 0.896 | 0.915 | 0.661 | 0.767 |
| decision_typed_skip:jev · threshold cutoff=0.5 | 0.995 | 0.863 | 0.876 | 0.728 | 0.795 |
| llm_sayback:haiku4.5 | 0.916 | 0.819 | 0.844 | 0.779 | 0.810 |
| decision_typed:jev · threshold cutoff=0.55 | 0.994 | 0.852 | 0.862 | 0.646 | 0.739 |
| llm_sayback:deepseek-v4-flash | 0.801 | 0.697 | 0.749 | 0.803 | 0.775 |
| presidio | 0.486 | 0.764 | 0.756 | 0.751 | 0.754 |
| llm_sayback:qwen3-235b | 0.759 | 0.745 | 0.778 | 0.724 | 0.750 |
| gliner_pii · threshold cutoff=0.05 | 0.946 | 0.799 | 0.849 | 0.556 | 0.672 |
| decision_words:jev · threshold cutoff=0.3 | 0.992 | 0.654 | 0.773 | 0.519 | 0.621 |
| llm_sayback:deepseek-v4-flash-think | 0.850 | 0.575 | 0.642 | 0.816 | 0.718 |
| llm_sayback:qwen3-30b | 0.732 | 0.606 | 0.658 | 0.645 | 0.651 |
| privacy_filter · threshold cutoff=0.001 | 0.528 | 0.484 | 0.534 | 0.895 | 0.668 |
| regex | 0.494 | 0.453 | 0.530 | 0.945 | 0.679 |
| llm_sayback:gpt4.1-nano | 0.519 | 0.554 | 0.590 | 0.381 | 0.463 |
| mask_all | 1.000 | 1.000 | 1.000 | 0.121 | 0.215 |

### Recall by masking need: DIRECT identifiers vs QUASI (combine to re-identify)

| lane | DIRECT | QUASI |
|---|---|---|
| human | 0.99 | 0.85 |
| decision_fields_skip:jev · threshold cutoff=0.4 | 0.99 | 0.88 |
| decision_typed_skip:jev · threshold cutoff=0.5 | 0.99 | 0.84 |
| llm_sayback:haiku4.5 | 0.81 | 0.83 |
| decision_typed:jev · threshold cutoff=0.55 | 0.99 | 0.82 |
| llm_sayback:deepseek-v4-flash | 0.86 | 0.73 |
| presidio | 0.58 | 0.74 |
| llm_sayback:qwen3-235b | 0.78 | 0.75 |
| gliner_pii · threshold cutoff=0.05 | 0.76 | 0.79 |
| decision_words:jev · threshold cutoff=0.3 | 0.98 | 0.71 |
| llm_sayback:deepseek-v4-flash-think | 0.82 | 0.61 |
| llm_sayback:qwen3-30b | 0.69 | 0.63 |
| privacy_filter · threshold cutoff=0.001 | 0.79 | 0.49 |
| regex | 0.18 | 0.47 |
| llm_sayback:gpt4.1-nano | 0.67 | 0.53 |
| mask_all | 1.00 | 1.00 |

### Recall by TAB entity type

| lane | CODE | DATETIME | DEM | LOC | MISC | ORG | PERSON | QUANTITY |
|---|---|---|---|---|---|---|---|---|
| human | 0.98 | 0.94 | 0.43 | 0.91 | 0.34 | 0.66 | 0.91 | 0.65 |
| decision_fields_skip:jev · threshold cutoff=0.4 | 0.99 | 0.97 | 0.70 | 0.90 | 0.20 | 0.64 | 0.98 | 0.48 |
| decision_typed_skip:jev · threshold cutoff=0.5 | 0.99 | 0.96 | 0.63 | 0.88 | 0.13 | 0.43 | 0.98 | 0.29 |
| llm_sayback:haiku4.5 | 0.82 | 0.93 | 0.31 | 0.91 | 0.41 | 0.69 | 0.83 | 0.43 |
| decision_typed:jev · threshold cutoff=0.55 | 0.99 | 0.95 | 0.60 | 0.88 | 0.12 | 0.37 | 1.00 | 0.24 |
| llm_sayback:deepseek-v4-flash | 0.27 | 0.84 | 0.24 | 0.80 | 0.19 | 0.66 | 0.72 | 0.55 |
| presidio | 0.05 | 0.99 | 0.42 | 0.74 | 0.13 | 0.15 | 0.73 | 0.02 |
| llm_sayback:qwen3-235b | 0.77 | 0.86 | 0.19 | 0.86 | 0.20 | 0.68 | 0.67 | 0.56 |
| gliner_pii · threshold cutoff=0.05 | 0.51 | 0.93 | 0.47 | 0.79 | 0.13 | 0.78 | 0.72 | 0.05 |
| decision_words:jev · threshold cutoff=0.3 | 0.88 | 0.82 | 0.75 | 0.73 | 0.13 | 0.18 | 0.96 | 0.34 |
| llm_sayback:deepseek-v4-flash-think | 0.49 | 0.73 | 0.29 | 0.58 | 0.05 | 0.67 | 0.50 | 0.35 |
| llm_sayback:qwen3-30b | 0.54 | 0.71 | 0.21 | 0.80 | 0.32 | 0.67 | 0.53 | 0.40 |
| privacy_filter · threshold cutoff=0.001 | 0.27 | 0.56 | 0.01 | 0.09 | 0.07 | 0.05 | 0.93 | 0.03 |
| regex | 0.88 | 0.80 | 0.00 | 0.00 | 0.01 | 0.00 | 0.00 | 0.01 |
| llm_sayback:gpt4.1-nano | 0.43 | 0.62 | 0.17 | 0.65 | 0.12 | 0.38 | 0.56 | 0.26 |
| mask_all | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |

### Precision by the type a lane claims (typed lanes)

| lane | CONTACT | DATETIME | ID | LOCATION | OTHER | PERSON |
|---|---|---|---|---|---|---|
| human | – | 0.97 | 1.00 | 0.74 | 0.50 | 0.94 |
| decision_fields_skip:jev · threshold cutoff=0.4 | 0.00 | 0.88 | 0.69 | 0.43 | 0.32 | 0.74 |
| decision_typed_skip:jev · threshold cutoff=0.5 | – | 0.89 | 0.56 | 0.52 | 0.36 | 0.78 |
| llm_sayback:haiku4.5 | – | 0.96 | 0.89 | 0.50 | 0.42 | 0.92 |
| decision_typed:jev · threshold cutoff=0.55 | – | 0.73 | 0.46 | 0.44 | 0.32 | 0.80 |
| llm_sayback:deepseek-v4-flash | – | 0.97 | 0.90 | 0.55 | 0.44 | 0.77 |
| presidio | 0.50 | 0.89 | 0.60 | 0.26 | 0.38 | 0.91 |
| llm_sayback:qwen3-235b | – | 0.95 | 0.51 | 0.48 | 0.32 | 0.90 |
| llm_sayback:deepseek-v4-flash-think | – | 0.97 | 0.64 | 0.55 | 0.45 | 0.92 |
| llm_sayback:qwen3-30b | 0.00 | 0.96 | 0.52 | 0.45 | 0.21 | 0.90 |
| regex | – | 0.97 | 0.94 | – | – | – |
| llm_sayback:gpt4.1-nano | – | 0.79 | 0.59 | 0.49 | 0.13 | 0.86 |

### Exact span match

| lane | F2 [95% CI] | P | R | F1 | leaked | docs, no leak | ECE | $/1k docs | p50 s | failed | frontier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| human | 0.810 [0.785, 0.832] | 0.808 | 0.810 | 0.809 | 19.0% | 3% | – | 0.000 | 0 | 0 |  |
| llm_sayback:haiku4.5 | 0.734 [0.709, 0.759] | 0.672 | 0.752 | 0.710 | 24.8% | 4% | – | 5.219 | 3.8 | 0 (+4 dropped) | yes |
| llm_sayback:deepseek-v4-flash | 0.660 [0.619, 0.698] | 0.657 | 0.661 | 0.659 | 33.9% | 2% | – | 0.418 | 7 | 2 (+11 dropped) | yes |
| llm_sayback:qwen3-235b | 0.644 [0.603, 0.682] | 0.617 | 0.651 | 0.634 | 34.9% | 0% | – | 0.736 | 19 | 2 (+17 dropped) |  |
| decision_typed_skip:jev · threshold cutoff=0.5 | 0.602 [0.582, 0.623] | 0.448 | 0.659 | 0.533 | 34.1% | 2% | 0.049 | 3.120 | 0.67 | 0 |  |
| decision_fields_skip:jev · threshold cutoff=0.4 | 0.596 [0.576, 0.615] | 0.388 | 0.687 | 0.496 | 31.3% | 2% | 0.045 | 3.787 | 0.66 | 0 |  |
| presidio | 0.581 [0.555, 0.605] | 0.585 | 0.580 | 0.582 | 42.0% | 0% | – | 0.000 | 0.12 | 0 | yes |
| llm_sayback:qwen3-30b | 0.552 [0.504, 0.602] | 0.570 | 0.548 | 0.559 | 45.2% | 0% | – | 0.497 | 21 | 9 (+112 dropped) |  |
| llm_sayback:deepseek-v4-flash-think | 0.549 [0.495, 0.600] | 0.650 | 0.529 | 0.583 | 47.1% | 2% | – | 1.669 | 85 | 13 (+4 dropped) |  |
| gliner_pii · threshold cutoff=0.05 | 0.546 [0.520, 0.572] | 0.392 | 0.605 | 0.476 | 39.5% | 0% | 0.063 | 0.000 | 1.4 | 0 |  |
| regex | 0.451 [0.416, 0.488] | 0.934 | 0.400 | 0.560 | 60.0% | 0% | – | 0.000 | 0.0011 | 0 |  |
| privacy_filter · threshold cutoff=0.001 | 0.417 [0.385, 0.451] | 0.749 | 0.375 | 0.500 | 62.5% | 0% | 0.084 | 0.000 | 2.3 | 0 |  |
| llm_sayback:gpt4.1-nano | 0.375 [0.330, 0.420] | 0.482 | 0.355 | 0.409 | 64.5% | 0% | – | 0.351 | 3.5 | 0 (+48 dropped) |  |
| decision_typed:jev · threshold cutoff=0.55 | 0.297 [0.277, 0.317] | 0.241 | 0.315 | 0.273 | 68.5% | 0% | 0.121 | 5.762 | 0.89 | 0 |  |
| decision_words:jev · threshold cutoff=0.3 | 0.267 [0.252, 0.282] | 0.185 | 0.301 | 0.229 | 69.9% | 0% | 0.055 | 1.180 | 0.61 | 0 |  |
| mask_all | 0.000 [0.000, 0.000] | 0.000 | 0.000 | 0.000 | 100.0% | 0% | – | 0.000 | 2.5e-06 | 0 |  |

### Every decoder on per-word scores (word level)

| lane | F2 [95% CI] | P | R | F1 | leaked | docs, no leak | ECE | $/1k docs | p50 s | failed | frontier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| decision_fields_skip:jev · viterbi cutoff=0.2 switch_cost=1.0 | 0.847 [0.834, 0.860] | 0.687 | 0.900 | 0.779 | 10.0% | 14% | 0.045 | 3.787 | 0.66 | 0 | yes |
| decision_fields_skip:jev · hysteresis high=0.55 low=0.2 | 0.844 [0.831, 0.857] | 0.716 | 0.884 | 0.791 | 11.6% | 13% | 0.045 | 3.787 | 0.66 | 0 |  |
| decision_typed_skip:jev · viterbi cutoff=0.2 switch_cost=1.0 | 0.841 [0.827, 0.854] | 0.678 | 0.895 | 0.771 | 10.5% | 14% | 0.049 | 3.120 | 0.67 | 0 | yes |
| decision_typed_skip:jev · hysteresis high=0.55 low=0.3 | 0.836 [0.823, 0.850] | 0.725 | 0.870 | 0.791 | 13.0% | 10% | 0.049 | 3.120 | 0.67 | 0 |  |
| decision_fields_skip:jev · threshold cutoff=0.4 | 0.834 [0.821, 0.845] | 0.672 | 0.887 | 0.765 | 11.3% | 8% | 0.045 | 3.787 | 0.66 | 0 |  |
| decision_fields_skip:jev | 0.829 [0.815, 0.843] | 0.757 | 0.850 | 0.801 | 15.0% | 6% | 0.045 | 3.787 | 0.66 | 0 |  |
| decision_typed_skip:jev | 0.822 [0.806, 0.836] | 0.738 | 0.845 | 0.788 | 15.5% | 6% | 0.049 | 3.120 | 0.67 | 0 |  |
| decision_typed_skip:jev · threshold cutoff=0.5 | 0.822 [0.806, 0.836] | 0.738 | 0.845 | 0.788 | 15.5% | 6% | 0.049 | 3.120 | 0.67 | 0 |  |
| decision_fields_skip:jev · closing cutoff=0.55 gap=1 | 0.821 [0.806, 0.836] | 0.732 | 0.847 | 0.785 | 15.3% | 8% | 0.045 | 3.787 | 0.66 | 0 |  |
| decision_typed_skip:jev · closing cutoff=0.55 gap=1 | 0.813 [0.798, 0.829] | 0.713 | 0.843 | 0.772 | 15.7% | 8% | 0.049 | 3.120 | 0.67 | 0 |  |
| decision_typed:jev · threshold cutoff=0.55 | 0.790 [0.774, 0.805] | 0.651 | 0.834 | 0.731 | 16.6% | 6% | 0.121 | 5.762 | 0.89 | 0 |  |
| decision_typed:jev · hysteresis high=0.55 low=0.5 | 0.789 [0.775, 0.804] | 0.621 | 0.847 | 0.717 | 15.3% | 8% | 0.121 | 5.762 | 0.89 | 0 |  |
| decision_typed:jev | 0.789 [0.774, 0.803] | 0.605 | 0.853 | 0.708 | 14.7% | 8% | 0.121 | 5.762 | 0.89 | 0 |  |
| decision_typed:jev · closing cutoff=0.6 gap=1 | 0.786 [0.769, 0.803] | 0.660 | 0.826 | 0.733 | 17.4% | 6% | 0.121 | 5.762 | 0.89 | 0 |  |
| decision_typed:jev · viterbi cutoff=0.5 switch_cost=0.25 | 0.785 [0.769, 0.801] | 0.618 | 0.842 | 0.713 | 15.8% | 9% | 0.121 | 5.762 | 0.89 | 0 |  |
| gliner_pii · threshold cutoff=0.05 | 0.735 [0.718, 0.750] | 0.571 | 0.791 | 0.663 | 20.9% | 0% | 0.063 | 0.000 | 1.4 | 0 | yes |
| gliner_pii · viterbi cutoff=0.03 switch_cost=1.0 | 0.733 [0.716, 0.749] | 0.593 | 0.779 | 0.673 | 22.1% | 0% | 0.063 | 0.000 | 1.4 | 0 |  |
| gliner_pii · closing cutoff=0.15 gap=1 | 0.724 [0.709, 0.740] | 0.564 | 0.780 | 0.654 | 22.0% | 0% | 0.063 | 0.000 | 1.4 | 0 |  |
| gliner_pii · hysteresis high=0.35 low=0.03 | 0.717 [0.698, 0.733] | 0.628 | 0.743 | 0.681 | 25.7% | 0% | 0.063 | 0.000 | 1.4 | 0 |  |
| decision_words:jev · closing cutoff=0.3 gap=1 | 0.706 [0.687, 0.725] | 0.503 | 0.785 | 0.613 | 21.5% | 2% | 0.055 | 1.180 | 0.61 | 0 |  |
| gliner_pii | 0.687 [0.666, 0.706] | 0.649 | 0.697 | 0.672 | 30.3% | 0% | 0.063 | 0.000 | 1.4 | 0 |  |
| decision_words:jev · viterbi cutoff=0.3 switch_cost=0.25 | 0.681 [0.662, 0.701] | 0.573 | 0.715 | 0.636 | 28.5% | 1% | 0.055 | 1.180 | 0.61 | 0 |  |
| decision_words:jev · threshold cutoff=0.3 | 0.680 [0.662, 0.699] | 0.533 | 0.731 | 0.616 | 26.9% | 0% | 0.055 | 1.180 | 0.61 | 0 |  |
| decision_words:jev · hysteresis high=0.35 low=0.3 | 0.676 [0.658, 0.695] | 0.560 | 0.713 | 0.628 | 28.7% | 0% | 0.055 | 1.180 | 0.61 | 0 |  |
| privacy_filter · threshold cutoff=0.001 | 0.555 [0.520, 0.590] | 0.928 | 0.505 | 0.654 | 49.5% | 0% | 0.084 | 0.000 | 2.3 | 0 |  |
| decision_words:jev | 0.537 [0.516, 0.559] | 0.707 | 0.507 | 0.590 | 49.3% | 0% | 0.055 | 1.180 | 0.61 | 0 |  |
| privacy_filter · closing cutoff=0.01 gap=1 | 0.478 [0.442, 0.514] | 0.914 | 0.427 | 0.582 | 57.3% | 0% | 0.084 | 0.000 | 2.3 | 0 |  |
| privacy_filter · viterbi cutoff=0.01 switch_cost=0.25 | 0.474 [0.438, 0.510] | 0.942 | 0.421 | 0.582 | 57.9% | 0% | 0.084 | 0.000 | 2.3 | 0 |  |
| privacy_filter · hysteresis high=0.25 low=0.01 | 0.393 [0.357, 0.431] | 0.948 | 0.343 | 0.504 | 65.7% | 0% | 0.084 | 0.000 | 2.3 | 0 |  |
| privacy_filter | 0.345 [0.311, 0.380] | 0.953 | 0.298 | 0.454 | 70.2% | 0% | 0.084 | 0.000 | 2.3 | 0 |  |

### Most leaked and most over-masked strings

→ **decision_fields_skip:jev · threshold cutoff=0.4** leaks: widows (16), city court (11), będzin district court (10), widow’s bereavement allowance (9), wba (9), the galleries (9), serco (7), widowers (7)  
over-masks: applicant (411), born (134), ankara (59), united kingdom (56), state security court (51), date (48), lives (47), foreign (44)

→ **decision_typed_skip:jev · threshold cutoff=0.5** leaks: serco (17), widows (16), city court (11), industries (11), będzin district court (10), widow’s bereavement allowance (9), wba (9), the galleries (9)  
over-masks: applicant (287), born (133), application (104), ankara (60), date (42), london (41), case (36), organisation (35)

→ **llm_sayback:haiku4.5** leaks: british (21), serco (20), widows (16), pkk (13), mr benham (13), industries (12), mr ryssdal (11), turkish (11)  
over-masks: foreign and commonwealth office (36), london (34), united kingdom (29), ankara state security court (28), united kingdom of great britain and nor… (22), istanbul (22), 1 november 1998 (21), sweden (20)

→ **decision_typed:jev · threshold cutoff=0.55** leaks: serco (19), widows (16), city court (11), industries (11), będzin district court (10), united kingdom (9), widow’s bereavement allowance (9), wba (9)  
over-masks: applicant (172), born (82), ankara (50), he (35), date (31), london (29), an (29), warsaw (29)

→ **llm_sayback:deepseek-v4-flash** leaks: british (22), united kingdom (22), widows (16), pkk (15), mr ryssdal (11), city court (11), somalia (11), turkish (10)  
over-masks: the applicant (160), the union (31), a (29), ankara state security court (28), london (27), sweden (20), court of cassation (18), swedish (17)

→ **presidio** leaks: mr c. whomersley (22), serco (17), widows (16), pkk (15), mr j. wołąsiewicz (14), mr benham (13), industries (12), mr ryssdal (11)  
over-masks: northern ireland (49), the united kingdom (47), the united kingdom of great britain (46), london (40), the republic of turkey (32), united kingdom (30), turkish (27), the same day (27)

→ **llm_sayback:qwen3-235b** leaks: british (24), serco (20), widows (16), pkk (13), industries (12), mr ryssdal (11), bnp (11), city court (11)  
over-masks: a (30), foreign and commonwealth office (25), london (23), court of cassation (20), 1 november 1998 (19), ankara state security court (18), ankara (17), applicant (17)

→ **gliner_pii · threshold cutoff=0.05** leaks: mr c. whomersley (22), widows (16), mr j. wołąsiewicz (14), mr ryssdal (11), mr r. ryssdal (10), mr j. grainger (9), white (9), widow’s bereavement allowance (9)  
over-masks: applicant (243), united kingdom (141), lawyer (104), agent (64), turkish (63), judge (62), applicant’s (58), secretary of state (57)

→ **decision_words:jev · threshold cutoff=0.3** leaks: serco (20), united kingdom (17), widows (16), pkk (14), industries (12), city court (11), będzin district court (10), bnp (9)  
over-masks: applicant (386), his (212), applicant’s (133), he (114), him (67), application (56), born (50), ankara (47)

→ **llm_sayback:deepseek-v4-flash-think** leaks: united kingdom (22), widows (16), mr benham (13), mr c. whomersley (13), industries (12), british (11), city court (11), somalia (11)  
over-masks: ankara state security court (22), istanbul (20), turkish (18), supreme administrative court (16), 1 november 1998 (13), polish (13), w.k. (13), ankara (11)

→ **llm_sayback:qwen3-30b** leaks: serco (20), british (20), widows (16), pkk (15), mr benham (13), industries (12), mr ryssdal (11), united kingdom (11)  
over-masks: the applicant (117), foreign and commonwealth office (37), london (27), court of appeal (23), secretary of state (23), the government (20), ankara state security court (19), ankara (17)

→ **privacy_filter · threshold cutoff=0.001** leaks: british (28), united kingdom (22), serco (16), widows (16), pkk (14), industries (12), bnp (11), turkish (11)  
over-masks: sergeant h (10), chamber (9), w.k (8), cassation (7), sąd najwyższy (7), mrs g (6), corporal g (6), lagen (5)

→ **regex** leaks: british (28), mr c. whomersley (22), united kingdom (22), serco (20), widows (16), pkk (15), mr j. wołąsiewicz (14), mr benham (13)  
over-masks: 1 november 1998 (21), 1 november 2001 (12), 17 june 2004 (7), 25 february 1997 (3), 1997-i (3), 1998-iv (2), 15 november 1996 (2), 65731/01 (2)

→ **llm_sayback:gpt4.1-nano** leaks: british (25), serco (20), united kingdom (17), widows (16), mr benham (13), mr ryssdal (11), city court (11), somalia (11)  
over-masks: the applicant (287), the court (98), the convention (49), the union (31), london (28), foreign and commonwealth office (25), united kingdom (21), procedure (19)

## Checks

### Check: Jev's answers before vs past its documented 32,000-token context

| lane | dataset | words before | Brier before | PII share before | words past | Brier past | PII share past |
|---|---|---|---|---|---|---|---|
| decision_fields_skip:jev | ai4privacy | 17,151 | 0.068 | 0.230 | 0 | – | – |
| decision_fields_skip:jev | nemotron | 29,057 | 0.039 | 0.173 | 378 | 0.014 | 0.079 |
| decision_fields_skip:jev | tab | 47,036 | 0.072 | 0.216 | 10,159 | 0.077 | 0.221 |
| decision_typed:jev | ai4privacy | 23,137 | 0.129 | 0.172 | 0 | – | – |
| decision_typed:jev | nemotron | 49,075 | 0.075 | 0.102 | 1,874 | 0.052 | 0.044 |
| decision_typed:jev | tab | 81,925 | 0.068 | 0.119 | 24,759 | 0.073 | 0.124 |
| decision_typed_skip:jev | ai4privacy | 17,151 | 0.159 | 0.230 | 0 | – | – |
| decision_typed_skip:jev | nemotron | 29,212 | 0.098 | 0.173 | 223 | 0.039 | 0.049 |
| decision_typed_skip:jev | tab | 45,351 | 0.078 | 0.220 | 11,844 | 0.071 | 0.203 |
| decision_words:jev | ai4privacy | 23,137 | 0.061 | 0.172 | 0 | – | – |
| decision_words:jev | nemotron | 50,949 | 0.046 | 0.100 | 0 | – | – |
| decision_words:jev | tab | 106,684 | 0.067 | 0.120 | 0 | – | – |

### Check: two lanes on only the docs both answered

| dataset | lane A | lane B | docs | F2 A | F2 B | P A / B | R A / B |
|---|---|---|---|---|---|---|---|
| ai4privacy | llm_sayback:deepseek-v4-flash | llm_sayback:deepseek-v4-flash-think | 499 | 0.938 | 0.942 | 0.864 / 0.880 | 0.959 / 0.959 |
| nemotron | llm_sayback:deepseek-v4-flash | llm_sayback:deepseek-v4-flash-think | 500 | 0.941 | 0.915 | 0.943 / 0.946 | 0.941 / 0.907 |
| tab | llm_sayback:deepseek-v4-flash | llm_sayback:deepseek-v4-flash-think | 113 | 0.775 | 0.749 | 0.787 / 0.785 | 0.773 / 0.740 |

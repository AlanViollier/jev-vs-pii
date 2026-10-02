## ai4privacy · test (500 docs)

### Word level (headline; per-word lanes use a threshold tuned on dev)

| lane | F2 [95% CI] | P | R | F1 | ECE | $/1k docs | p50 s | failed | frontier |
|---|---|---|---|---|---|---|---|---|---|
| llm_sayback:haiku4.5 | 0.953 [0.938, 0.966] | 0.895 | 0.969 | 0.931 | – | 1.324 | 1.6 | 0 (+12 dropped) | yes |
| llm_sayback:qwen3-235b | 0.952 [0.938, 0.963] | 0.898 | 0.966 | 0.931 | – | 0.150 | 4.5 | 0 (+4 dropped) | yes |
| llm_sayback:deepseek-v4-flash-think | 0.948 [0.932, 0.960] | 0.895 | 0.962 | 0.927 | – | 0.204 | 8.5 | 0 (+9 dropped) |  |
| llm_sayback:deepseek-v4-flash | 0.946 [0.928, 0.962] | 0.894 | 0.960 | 0.926 | – | 0.060 | 2 | 0 | yes |
| llm_sayback:qwen3-30b | 0.938 [0.922, 0.953] | 0.825 | 0.971 | 0.892 | – | 0.079 | 3.3 | 1 (+14 dropped) |  |
| privacy_filter · threshold cutoff=0.001 | 0.862 [0.844, 0.878] | 0.885 | 0.857 | 0.871 | 0.042 | 0.000 | 1.5 | 0 | yes |
| decision_words:jev · threshold cutoff=0.35 | 0.841 [0.827, 0.854] | 0.631 | 0.918 | 0.748 | 0.058 | 0.098 | 0.27 | 0 |  |
| gliner_pii · threshold cutoff=0.05 | 0.841 [0.824, 0.856] | 0.593 | 0.939 | 0.727 | 0.050 | 0.000 | 0.28 | 0 |  |
| decision_typed:jev · threshold cutoff=0.75 | 0.829 [0.815, 0.843] | 0.577 | 0.931 | 0.713 | 0.171 | 0.339 | 0.31 | 0 |  |
| decision_typed_skip:jev · threshold cutoff=0.7 | 0.829 [0.816, 0.842] | 0.570 | 0.935 | 0.708 | 0.144 | 0.259 | 0.29 | 0 |  |
| llm_sayback:gpt4.1-nano | 0.826 [0.790, 0.859] | 0.883 | 0.812 | 0.846 | – | 0.079 | 1.3 | 0 (+11 dropped) |  |
| presidio | 0.587 [0.563, 0.612] | 0.807 | 0.549 | 0.654 | – | 0.000 | 0.017 | 0 |  |
| regex | 0.539 [0.506, 0.572] | 0.945 | 0.487 | 0.643 | – | 0.000 | 9.8e-05 | 0 |  |
| mask_all | 0.510 [0.482, 0.537] | 0.172 | 1.000 | 0.294 | – | 0.000 | 2.4e-06 | 0 |  |

- → OpenAI reports Privacy Filter results on pii-masking-300k, this set's source.
- → Privacy Filter has 8 categories: no organisations, demographics or most IDs.
- → An LLM answer that is cut off or won't parse counts as finding nothing (`failed`).

### Every lane against decision_words:jev · threshold cutoff=0.35, same docs (paired bootstrap)

| lane | F2 − decision_words:jev · threshold cutoff=0.35 [95% CI] | clear gap |
|---|---|---|
| llm_sayback:haiku4.5 | +0.112 [+0.101, +0.123] | yes |
| llm_sayback:qwen3-235b | +0.110 [+0.098, +0.124] | yes |
| llm_sayback:deepseek-v4-flash-think | +0.107 [+0.095, +0.118] | yes |
| llm_sayback:deepseek-v4-flash | +0.104 [+0.086, +0.122] | yes |
| llm_sayback:qwen3-30b | +0.097 [+0.083, +0.111] | yes |
| privacy_filter · threshold cutoff=0.001 | +0.021 [+0.007, +0.033] | yes |
| gliner_pii · threshold cutoff=0.05 | -0.000 [-0.018, +0.017] |  |
| decision_typed:jev · threshold cutoff=0.75 | -0.012 [-0.021, -0.004] | yes |
| decision_typed_skip:jev · threshold cutoff=0.7 | -0.012 [-0.022, -0.004] | yes |
| llm_sayback:gpt4.1-nano | -0.016 [-0.051, +0.017] |  |
| presidio | -0.254 [-0.279, -0.229] | yes |
| regex | -0.302 [-0.335, -0.271] | yes |
| mask_all | -0.332 [-0.361, -0.303] | yes |

### Format vs context: recall on PII found by its form vs by its meaning

| lane | format recall | context recall | gap |
|---|---|---|---|
| llm_sayback:haiku4.5 | 0.97 | 0.96 | +0.01 |
| llm_sayback:qwen3-235b | 0.97 | 0.97 | -0.00 |
| llm_sayback:deepseek-v4-flash-think | 0.96 | 0.97 | -0.01 |
| llm_sayback:deepseek-v4-flash | 0.96 | 0.97 | -0.01 |
| llm_sayback:qwen3-30b | 0.97 | 0.97 | -0.00 |
| privacy_filter · threshold cutoff=0.001 | 0.91 | 0.73 | +0.18 |
| decision_words:jev · threshold cutoff=0.35 | 0.93 | 0.89 | +0.04 |
| gliner_pii · threshold cutoff=0.05 | 0.94 | 0.95 | -0.01 |
| decision_typed:jev · threshold cutoff=0.75 | 0.94 | 0.91 | +0.03 |
| decision_typed_skip:jev · threshold cutoff=0.7 | 0.95 | 0.91 | +0.03 |
| llm_sayback:gpt4.1-nano | 0.82 | 0.80 | +0.02 |
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
| llm_sayback:deepseek-v4-flash | 0.060 | 1.0 | 415 | 147 | 2.4 | 2 | 5.3 | 156 |
| llm_sayback:qwen3-30b | 0.079 | 1.0 | 434 | 194 | 5 | 3.3 | 14 | 436 |
| llm_sayback:gpt4.1-nano | 0.079 | 1.0 | 471 | 80 | 1.5 | 1.3 | 2.9 | 103 |
| decision_words:jev · threshold cutoff=0.35 | 0.098 | 1.0 | 2,322 | 827 | 0.28 | 0.27 | 0.38 | 0 |
| llm_sayback:qwen3-235b | 0.150 | 1.0 | 434 | 164 | 5.7 | 4.5 | 14 | 370 |
| llm_sayback:deepseek-v4-flash-think | 0.204 | 1.0 | 415 | 796 | 12 | 8.5 | 33 | 765 |
| decision_typed_skip:jev · threshold cutoff=0.7 | 0.259 | 1.0 | 6,175 | 2,282 | 0.31 | 0.29 | 0.42 | 19 |
| decision_typed:jev · threshold cutoff=0.75 | 0.339 | 1.0 | 8,060 | 3,099 | 0.32 | 0.31 | 0.41 | 1 |
| llm_sayback:haiku4.5 | 1.324 | 1.0 | 709 | 123 | 1.7 | 1.6 | 2.4 | 39 |

### Recall by gold type (word level)

| lane | CONTACT | DATETIME | ID | LOCATION | OTHER | PERSON |
|---|---|---|---|---|---|---|
| llm_sayback:haiku4.5 | 0.99 | 0.95 | 0.99 | 0.98 | 0.91 | 0.92 |
| llm_sayback:qwen3-235b | 0.99 | 0.94 | 0.97 | 0.98 | 0.99 | 0.94 |
| llm_sayback:deepseek-v4-flash-think | 0.99 | 0.89 | 0.99 | 0.97 | 1.00 | 0.96 |
| llm_sayback:deepseek-v4-flash | 0.99 | 0.94 | 0.93 | 0.98 | 1.00 | 0.94 |
| llm_sayback:qwen3-30b | 0.99 | 0.93 | 0.98 | 0.99 | 0.99 | 0.96 |
| privacy_filter · threshold cutoff=0.001 | 0.99 | 0.69 | 0.99 | 0.78 | 0.12 | 0.97 |
| decision_words:jev · threshold cutoff=0.35 | 0.99 | 0.82 | 0.98 | 0.87 | 0.85 | 0.96 |
| gliner_pii · threshold cutoff=0.05 | 0.89 | 0.96 | 0.99 | 0.92 | 0.91 | 0.95 |
| decision_typed:jev · threshold cutoff=0.75 | 0.98 | 0.87 | 0.96 | 0.91 | 0.80 | 0.95 |
| decision_typed_skip:jev · threshold cutoff=0.7 | 0.99 | 0.87 | 0.97 | 0.92 | 0.78 | 0.96 |
| llm_sayback:gpt4.1-nano | 0.91 | 0.74 | 0.83 | 0.79 | 0.54 | 0.84 |
| presidio | 0.69 | 0.67 | 0.69 | 0.37 | 0.03 | 0.35 |
| regex | 0.81 | 0.75 | 0.79 | 0.03 | 0.00 | 0.00 |
| mask_all | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |

### Recall by ai4privacy label (labels with ≥ 30 gold words)

| lane | BOD | BUILDING | CITY | COUNTRY | DATE | DRIVERLICENSE | EMAIL | GIVENNAME1 | GIVENNAME2 | IDCARD | IP | LASTNAME1 | LASTNAME2 | PASS | PASSPORT | POSTCODE | SECADDRESS | SEX | SOCIALNUMBER | STATE | STREET | TEL | TIME | TITLE | USERNAME |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| llm_sayback:haiku4.5 | 0.99 | 0.98 | 1.00 | 1.00 | 0.99 | 1.00 | 1.00 | 0.97 | 1.00 | 0.99 | 1.00 | 1.00 | 1.00 | 0.90 | 0.99 | 0.98 | 0.89 | 0.91 | 1.00 | 0.99 | 1.00 | 1.00 | 0.90 | 0.68 | 0.95 |
| llm_sayback:qwen3-235b | 1.00 | 1.00 | 0.97 | 0.99 | 0.92 | 0.96 | 1.00 | 0.98 | 0.97 | 0.97 | 1.00 | 0.92 | 0.94 | 0.90 | 0.98 | 0.98 | 0.93 | 0.99 | 0.99 | 0.97 | 0.99 | 0.99 | 0.90 | 0.92 | 0.96 |
| llm_sayback:deepseek-v4-flash-think | 1.00 | 1.00 | 0.97 | 0.97 | 0.78 | 1.00 | 0.98 | 1.00 | 1.00 | 0.97 | 1.00 | 1.00 | 1.00 | 1.00 | 0.98 | 0.99 | 0.89 | 1.00 | 1.00 | 0.96 | 0.99 | 1.00 | 0.86 | 0.82 | 0.99 |
| llm_sayback:deepseek-v4-flash | 1.00 | 0.99 | 0.99 | 0.96 | 0.94 | 0.88 | 0.99 | 0.99 | 1.00 | 0.92 | 1.00 | 0.99 | 1.00 | 0.94 | 0.92 | 0.98 | 0.89 | 1.00 | 1.00 | 0.96 | 1.00 | 1.00 | 0.91 | 0.76 | 0.97 |
| llm_sayback:qwen3-30b | 1.00 | 0.99 | 0.97 | 0.97 | 0.94 | 0.99 | 1.00 | 1.00 | 1.00 | 0.99 | 1.00 | 0.99 | 1.00 | 0.96 | 0.96 | 0.99 | 0.98 | 0.99 | 1.00 | 0.98 | 1.00 | 0.99 | 0.88 | 0.83 | 0.96 |
| privacy_filter · threshold cutoff=0.001 | 1.00 | 1.00 | 0.96 | 0.05 | 0.98 | 1.00 | 1.00 | 0.97 | 1.00 | 0.99 | 1.00 | 0.97 | 1.00 | 0.98 | 0.99 | 1.00 | 0.99 | 0.12 | 1.00 | 0.14 | 1.00 | 1.00 | 0.31 | 0.94 | 0.97 |
| decision_words:jev · threshold cutoff=0.35 | 0.99 | 0.98 | 0.94 | 0.83 | 0.73 | 0.96 | 0.99 | 0.96 | 1.00 | 0.97 | 1.00 | 0.99 | 1.00 | 0.98 | 1.00 | 0.98 | 0.74 | 0.85 | 1.00 | 0.96 | 0.74 | 0.98 | 0.75 | 0.87 | 0.98 |
| gliner_pii · threshold cutoff=0.05 | 1.00 | 0.91 | 0.99 | 1.00 | 1.00 | 0.97 | 1.00 | 0.99 | 1.00 | 0.99 | 0.58 | 0.97 | 0.89 | 0.96 | 0.99 | 0.97 | 0.89 | 0.91 | 0.99 | 0.75 | 0.99 | 0.91 | 0.90 | 0.90 | 0.99 |
| decision_typed:jev · threshold cutoff=0.75 | 1.00 | 0.99 | 0.95 | 0.94 | 0.84 | 0.92 | 0.99 | 0.96 | 1.00 | 0.98 | 1.00 | 0.98 | 1.00 | 0.99 | 0.98 | 0.98 | 0.83 | 0.80 | 0.97 | 0.97 | 0.80 | 0.98 | 0.80 | 0.87 | 0.97 |
| decision_typed_skip:jev · threshold cutoff=0.7 | 0.99 | 0.99 | 0.97 | 0.85 | 0.92 | 0.94 | 0.99 | 0.96 | 1.00 | 0.98 | 1.00 | 0.99 | 1.00 | 0.99 | 0.98 | 0.98 | 0.86 | 0.78 | 0.98 | 0.90 | 0.89 | 0.99 | 0.76 | 0.87 | 0.97 |
| llm_sayback:gpt4.1-nano | 0.98 | 0.83 | 0.79 | 0.88 | 0.74 | 0.81 | 0.91 | 0.94 | 1.00 | 0.92 | 0.91 | 0.88 | 0.97 | 0.71 | 0.75 | 0.79 | 0.65 | 0.54 | 0.91 | 0.78 | 0.83 | 0.95 | 0.58 | 0.55 | 0.85 |
| presidio | 0.81 | 0.01 | 0.59 | 0.76 | 0.88 | 0.65 | 1.00 | 0.40 | 0.66 | 0.51 | 1.00 | 0.42 | 0.40 | 0.21 | 0.88 | 0.30 | 0.09 | 0.03 | 0.86 | 0.30 | 0.40 | 0.60 | 0.45 | 0.07 | 0.33 |
| regex | 0.91 | 0.00 | 0.00 | 0.00 | 0.95 | 0.67 | 1.00 | 0.00 | 0.00 | 0.98 | 1.00 | 0.01 | 0.00 | 0.01 | 0.97 | 0.22 | 0.00 | 0.00 | 0.93 | 0.00 | 0.00 | 0.91 | 0.52 | 0.00 | 0.34 |
| mask_all | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |

### Precision by the type a lane claims (typed lanes)

| lane | CONTACT | DATETIME | ID | LOCATION | OTHER | PERSON |
|---|---|---|---|---|---|---|
| llm_sayback:haiku4.5 | 0.95 | 0.90 | 0.95 | 0.90 | 0.61 | 0.80 |
| llm_sayback:qwen3-235b | 0.94 | 0.90 | 0.95 | 0.91 | 0.71 | 0.80 |
| llm_sayback:deepseek-v4-flash-think | 0.92 | 0.89 | 0.94 | 0.91 | 0.67 | 0.82 |
| llm_sayback:deepseek-v4-flash | 0.93 | 0.89 | 0.94 | 0.90 | 0.73 | 0.81 |
| llm_sayback:qwen3-30b | 0.91 | 0.87 | 0.92 | 0.91 | 0.30 | 0.76 |
| decision_typed:jev · threshold cutoff=0.75 | 0.58 | 0.61 | 0.49 | 0.66 | 0.49 | 0.59 |
| decision_typed_skip:jev · threshold cutoff=0.7 | 0.57 | 0.60 | 0.47 | 0.64 | 0.47 | 0.63 |
| llm_sayback:gpt4.1-nano | 0.95 | 0.89 | 0.94 | 0.90 | 0.79 | 0.78 |
| presidio | 0.96 | 0.71 | 0.87 | 0.80 | 0.53 | 0.68 |
| regex | 0.97 | 0.90 | 0.95 | – | – | – |

### Exact span match

| lane | F2 [95% CI] | P | R | F1 | ECE | $/1k docs | p50 s | failed | frontier |
|---|---|---|---|---|---|---|---|---|---|
| llm_sayback:haiku4.5 | 0.906 [0.882, 0.928] | 0.874 | 0.914 | 0.893 | – | 1.324 | 1.6 | 0 (+12 dropped) | yes |
| llm_sayback:deepseek-v4-flash | 0.889 [0.862, 0.916] | 0.868 | 0.895 | 0.881 | – | 0.060 | 2 | 0 | yes |
| llm_sayback:deepseek-v4-flash-think | 0.859 [0.827, 0.888] | 0.826 | 0.867 | 0.846 | – | 0.204 | 8.5 | 0 (+9 dropped) |  |
| llm_sayback:qwen3-30b | 0.845 [0.813, 0.877] | 0.796 | 0.859 | 0.826 | – | 0.079 | 3.3 | 1 (+14 dropped) |  |
| llm_sayback:qwen3-235b | 0.839 [0.802, 0.873] | 0.837 | 0.840 | 0.838 | – | 0.150 | 4.5 | 0 (+4 dropped) |  |
| llm_sayback:gpt4.1-nano | 0.744 [0.704, 0.780] | 0.844 | 0.722 | 0.778 | – | 0.079 | 1.3 | 0 (+11 dropped) |  |
| privacy_filter · threshold cutoff=0.001 | 0.505 [0.461, 0.551] | 0.654 | 0.478 | 0.552 | 0.042 | 0.000 | 1.5 | 0 | yes |
| regex | 0.503 [0.474, 0.534] | 0.838 | 0.457 | 0.591 | – | 0.000 | 9.8e-05 | 0 |  |
| gliner_pii · threshold cutoff=0.05 | 0.478 [0.438, 0.521] | 0.466 | 0.481 | 0.474 | 0.050 | 0.000 | 0.28 | 0 |  |
| presidio | 0.469 [0.446, 0.493] | 0.583 | 0.447 | 0.506 | – | 0.000 | 0.017 | 0 |  |
| decision_words:jev · threshold cutoff=0.35 | 0.215 [0.186, 0.246] | 0.309 | 0.200 | 0.243 | 0.058 | 0.098 | 0.27 | 0 |  |
| decision_typed:jev · threshold cutoff=0.75 | 0.213 [0.183, 0.242] | 0.238 | 0.207 | 0.222 | 0.171 | 0.339 | 0.31 | 0 |  |
| decision_typed_skip:jev · threshold cutoff=0.7 | 0.211 [0.183, 0.240] | 0.232 | 0.206 | 0.218 | 0.144 | 0.259 | 0.29 | 0 |  |
| mask_all | 0.000 [0.000, 0.000] | 0.000 | 0.000 | 0.000 | – | 0.000 | 2.4e-06 | 0 |  |

### Every decoder on per-word scores (word level)

| lane | F2 [95% CI] | P | R | F1 | ECE | $/1k docs | p50 s | failed | frontier |
|---|---|---|---|---|---|---|---|---|---|
| privacy_filter · threshold cutoff=0.001 | 0.862 [0.844, 0.878] | 0.885 | 0.857 | 0.871 | 0.042 | 0.000 | 1.5 | 0 | yes |
| privacy_filter · viterbi cutoff=0.01 switch_cost=4.0 | 0.851 [0.831, 0.868] | 0.896 | 0.841 | 0.867 | 0.042 | 0.000 | 1.5 | 0 |  |
| privacy_filter · hysteresis high=0.25 low=0.03 | 0.846 [0.827, 0.863] | 0.916 | 0.831 | 0.871 | 0.042 | 0.000 | 1.5 | 0 |  |
| privacy_filter · closing cutoff=0.01 gap=1 | 0.843 [0.825, 0.860] | 0.788 | 0.859 | 0.822 | 0.042 | 0.000 | 1.5 | 0 |  |
| decision_words:jev · threshold cutoff=0.35 | 0.841 [0.827, 0.854] | 0.631 | 0.918 | 0.748 | 0.058 | 0.098 | 0.27 | 0 |  |
| gliner_pii · threshold cutoff=0.05 | 0.841 [0.824, 0.856] | 0.593 | 0.939 | 0.727 | 0.050 | 0.000 | 0.28 | 0 |  |
| gliner_pii · viterbi cutoff=0.03 switch_cost=0.25 | 0.841 [0.824, 0.856] | 0.593 | 0.939 | 0.727 | 0.050 | 0.000 | 0.28 | 0 |  |
| decision_words:jev · hysteresis high=0.35 low=0.3 | 0.841 [0.826, 0.854] | 0.602 | 0.933 | 0.732 | 0.058 | 0.098 | 0.27 | 0 |  |
| gliner_pii · hysteresis high=0.25 low=0.03 | 0.840 [0.822, 0.857] | 0.653 | 0.905 | 0.759 | 0.050 | 0.000 | 0.28 | 0 |  |
| privacy_filter | 0.837 [0.817, 0.854] | 0.921 | 0.818 | 0.866 | 0.042 | 0.000 | 1.5 | 0 |  |
| decision_typed:jev · hysteresis high=0.75 low=0.7 | 0.832 [0.819, 0.845] | 0.560 | 0.948 | 0.704 | 0.171 | 0.339 | 0.31 | 0 |  |
| decision_typed:jev · threshold cutoff=0.75 | 0.829 [0.815, 0.843] | 0.577 | 0.931 | 0.713 | 0.171 | 0.339 | 0.31 | 0 |  |
| decision_typed_skip:jev · threshold cutoff=0.7 | 0.829 [0.816, 0.842] | 0.570 | 0.935 | 0.708 | 0.144 | 0.259 | 0.29 | 0 |  |
| decision_words:jev · viterbi cutoff=0.4 switch_cost=0.25 | 0.829 [0.812, 0.845] | 0.646 | 0.892 | 0.749 | 0.058 | 0.098 | 0.27 | 0 |  |
| decision_typed_skip:jev · hysteresis high=0.75 low=0.7 | 0.827 [0.813, 0.841] | 0.573 | 0.931 | 0.709 | 0.144 | 0.259 | 0.29 | 0 |  |
| decision_words:jev · closing cutoff=0.45 gap=1 | 0.827 [0.813, 0.841] | 0.624 | 0.900 | 0.737 | 0.058 | 0.098 | 0.27 | 0 |  |
| decision_typed_skip:jev · viterbi cutoff=0.7 switch_cost=0.25 | 0.826 [0.812, 0.840] | 0.567 | 0.932 | 0.705 | 0.144 | 0.259 | 0.29 | 0 |  |
| decision_typed_skip:jev · closing cutoff=0.7 gap=1 | 0.825 [0.812, 0.839] | 0.536 | 0.954 | 0.686 | 0.144 | 0.259 | 0.29 | 0 |  |
| decision_typed_skip:jev | 0.823 [0.809, 0.836] | 0.521 | 0.962 | 0.676 | 0.144 | 0.259 | 0.29 | 0 |  |
| decision_typed:jev · viterbi cutoff=0.6 switch_cost=0.5 | 0.823 [0.809, 0.837] | 0.515 | 0.967 | 0.672 | 0.171 | 0.339 | 0.31 | 0 |  |
| decision_typed:jev · closing cutoff=0.75 gap=1 | 0.822 [0.809, 0.836] | 0.542 | 0.945 | 0.689 | 0.171 | 0.339 | 0.31 | 0 |  |
| decision_typed:jev | 0.822 [0.808, 0.836] | 0.500 | 0.980 | 0.662 | 0.171 | 0.339 | 0.31 | 0 |  |
| decision_words:jev | 0.817 [0.799, 0.834] | 0.725 | 0.844 | 0.780 | 0.058 | 0.098 | 0.27 | 0 |  |
| gliner_pii · closing cutoff=0.05 gap=1 | 0.806 [0.789, 0.820] | 0.504 | 0.948 | 0.658 | 0.050 | 0.000 | 0.28 | 0 |  |
| gliner_pii | 0.803 [0.782, 0.824] | 0.742 | 0.820 | 0.779 | 0.050 | 0.000 | 0.28 | 0 |  |

## nemotron · test (500 docs)

### Word level (headline; per-word lanes use a threshold tuned on dev)

| lane | F2 [95% CI] | P | R | F1 | ECE | $/1k docs | p50 s | failed | frontier |
|---|---|---|---|---|---|---|---|---|---|
| llm_sayback:haiku4.5 | 0.934 [0.923, 0.945] | 0.969 | 0.926 | 0.947 | – | 1.423 | 1.5 | 0 (+11 dropped) | yes |
| llm_sayback:deepseek-v4-flash | 0.923 [0.910, 0.934] | 0.951 | 0.916 | 0.933 | – | 0.072 | 2.3 | 0 | yes |
| llm_sayback:qwen3-235b | 0.912 [0.898, 0.925] | 0.956 | 0.901 | 0.928 | – | 0.157 | 11 | 1 (+22 dropped) |  |
| llm_sayback:qwen3-30b | 0.902 [0.889, 0.915] | 0.880 | 0.908 | 0.894 | – | 0.077 | 3.3 | 0 (+10 dropped) |  |
| gliner_pii · threshold cutoff=0.2 | 0.872 [0.859, 0.885] | 0.895 | 0.867 | 0.881 | 0.016 | 0.000 | 0.29 | 0 | yes |
| llm_sayback:deepseek-v4-flash-think | 0.864 [0.843, 0.881] | 0.964 | 0.842 | 0.899 | – | 0.255 | 11 | 1 (+5 dropped) |  |
| llm_sayback:gpt4.1-nano | 0.837 [0.819, 0.855] | 0.946 | 0.814 | 0.875 | – | 0.089 | 1.8 | 0 |  |
| decision_typed_skip:jev · threshold cutoff=0.35 | 0.826 [0.816, 0.835] | 0.537 | 0.954 | 0.687 | 0.069 | 0.411 | 0.31 | 0 |  |
| decision_typed:jev · threshold cutoff=0.4 | 0.792 [0.783, 0.803] | 0.469 | 0.958 | 0.630 | 0.121 | 0.696 | 0.37 | 0 |  |
| decision_words:jev · threshold cutoff=0.1 | 0.719 [0.707, 0.730] | 0.365 | 0.950 | 0.527 | 0.042 | 0.163 | 0.29 | 0 |  |
| privacy_filter · threshold cutoff=0.001 | 0.698 [0.674, 0.722] | 0.933 | 0.657 | 0.771 | 0.043 | 0.000 | 1.8 | 0 |  |
| presidio | 0.671 [0.652, 0.692] | 0.897 | 0.632 | 0.741 | – | 0.000 | 0.019 | 0 |  |
| regex | 0.433 [0.410, 0.454] | 0.995 | 0.379 | 0.549 | – | 0.000 | 0.00013 | 0 |  |
| mask_all | 0.358 [0.341, 0.374] | 0.100 | 1.000 | 0.182 | – | 0.000 | 2.7e-06 | 0 |  |

- → GLiNER-PII was trained on Nemotron-PII's train split. Test samples the test file; dev samples train, so GLiNER's dev score and tuned threshold come from its own training data.
- → Privacy Filter has 8 categories: no organisations, demographics or most IDs.
- → An LLM answer that is cut off or won't parse counts as finding nothing (`failed`).

### Every lane against decision_typed_skip:jev · threshold cutoff=0.35, same docs (paired bootstrap)

| lane | F2 − decision_typed_skip:jev · threshold cutoff=0.35 [95% CI] | clear gap |
|---|---|---|
| llm_sayback:haiku4.5 | +0.108 [+0.097, +0.120] | yes |
| llm_sayback:deepseek-v4-flash | +0.097 [+0.083, +0.110] | yes |
| llm_sayback:qwen3-235b | +0.086 [+0.072, +0.100] | yes |
| llm_sayback:qwen3-30b | +0.077 [+0.062, +0.090] | yes |
| gliner_pii · threshold cutoff=0.2 | +0.047 [+0.033, +0.061] | yes |
| llm_sayback:deepseek-v4-flash-think | +0.038 [+0.015, +0.056] | yes |
| llm_sayback:gpt4.1-nano | +0.012 [-0.006, +0.030] |  |
| decision_typed:jev · threshold cutoff=0.4 | -0.033 [-0.037, -0.029] | yes |
| decision_words:jev · threshold cutoff=0.1 | -0.107 [-0.115, -0.097] | yes |
| privacy_filter · threshold cutoff=0.001 | -0.127 [-0.153, -0.103] | yes |
| presidio | -0.154 [-0.176, -0.132] | yes |
| regex | -0.393 [-0.419, -0.369] | yes |
| mask_all | -0.468 [-0.484, -0.451] | yes |

### Format vs context: recall on PII found by its form vs by its meaning

| lane | format recall | context recall | gap |
|---|---|---|---|
| llm_sayback:haiku4.5 | 0.96 | 0.89 | +0.07 |
| llm_sayback:deepseek-v4-flash | 0.97 | 0.86 | +0.11 |
| llm_sayback:qwen3-235b | 0.97 | 0.83 | +0.14 |
| llm_sayback:qwen3-30b | 0.98 | 0.83 | +0.15 |
| gliner_pii · threshold cutoff=0.2 | 0.86 | 0.87 | -0.01 |
| llm_sayback:deepseek-v4-flash-think | 0.87 | 0.82 | +0.05 |
| llm_sayback:gpt4.1-nano | 0.92 | 0.70 | +0.22 |
| decision_typed_skip:jev · threshold cutoff=0.35 | 0.95 | 0.96 | -0.00 |
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
| llm_sayback:deepseek-v4-flash | 0.072 | 1.0 | 507 | 149 | 2.7 | 2.3 | 5 | 0 |
| llm_sayback:qwen3-30b | 0.077 | 1.0 | 524 | 187 | 4.2 | 3.3 | 11 | 0 |
| llm_sayback:gpt4.1-nano | 0.089 | 1.0 | 563 | 81 | 2 | 1.8 | 3.1 | 0 |
| llm_sayback:qwen3-235b | 0.157 | 1.0 | 524 | 161 | 12 | 11 | 30 | 0 |
| decision_words:jev · threshold cutoff=0.1 | 0.163 | 1.0 | 3,887 | 1,854 | 0.31 | 0.29 | 0.42 | 1 |
| llm_sayback:deepseek-v4-flash-think | 0.255 | 1.0 | 507 | 906 | 15 | 11 | 40 | 0 |
| decision_typed_skip:jev · threshold cutoff=0.35 | 0.411 | 1.0 | 9,783 | 3,910 | 0.34 | 0.31 | 0.5 | 23 |
| decision_typed:jev · threshold cutoff=0.4 | 0.696 | 1.0 | 16,563 | 6,849 | 0.41 | 0.37 | 0.65 | 1 |
| llm_sayback:haiku4.5 | 1.423 | 1.0 | 808 | 123 | 1.6 | 1.5 | 2.4 | 0 |

### Recall by gold type (word level)

| lane | CONTACT | DATETIME | ID | LOCATION | OTHER | PERSON |
|---|---|---|---|---|---|---|
| llm_sayback:haiku4.5 | 0.94 | 0.94 | 1.00 | 0.97 | 0.84 | 0.90 |
| llm_sayback:deepseek-v4-flash | 0.96 | 0.94 | 1.00 | 0.97 | 0.78 | 0.91 |
| llm_sayback:qwen3-235b | 0.97 | 0.93 | 1.00 | 0.96 | 0.72 | 0.90 |
| llm_sayback:qwen3-30b | 0.97 | 0.98 | 1.00 | 0.96 | 0.72 | 0.90 |
| gliner_pii · threshold cutoff=0.2 | 0.77 | 0.99 | 0.92 | 0.85 | 0.80 | 0.95 |
| llm_sayback:deepseek-v4-flash-think | 0.84 | 0.74 | 0.99 | 0.81 | 0.73 | 0.94 |
| llm_sayback:gpt4.1-nano | 0.88 | 0.90 | 0.99 | 0.93 | 0.45 | 0.91 |
| decision_typed_skip:jev · threshold cutoff=0.35 | 0.93 | 0.91 | 1.00 | 1.00 | 0.91 | 1.00 |
| decision_typed:jev · threshold cutoff=0.4 | 0.91 | 0.95 | 1.00 | 1.00 | 0.92 | 1.00 |
| decision_words:jev · threshold cutoff=0.1 | 0.97 | 0.94 | 1.00 | 0.99 | 0.84 | 1.00 |
| privacy_filter · threshold cutoff=0.001 | 0.82 | 0.79 | 0.94 | 0.58 | 0.06 | 0.98 |
| presidio | 0.84 | 0.94 | 0.61 | 0.67 | 0.10 | 0.92 |
| regex | 0.67 | 0.90 | 0.82 | 0.01 | 0.00 | 0.00 |
| mask_all | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |

### Recall by nemotron label (labels with ≥ 30 gold words)

| lane | account_number | age | bank_routing_number | biometric_identifier | blood_type | city | company_name | coordinate | country | county | credit_debit_card | customer_id | date | date_of_birth | date_time | education_level | email | employment_status | fax_number | first_name | gender | health_plan_beneficiary_number | http_cookie | language | last_name | license_plate | medical_record_number | occupation | phone_number | pin | political_view | postcode | race_ethnicity | religious_belief | ssn | state | street_address | time | url | user_name |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| llm_sayback:haiku4.5 | 1.00 | 0.94 | 1.00 | 1.00 | 1.00 | 0.98 | 0.95 | 0.92 | 0.89 | 1.00 | 1.00 | 1.00 | 0.97 | 1.00 | 1.00 | 0.88 | 0.99 | 0.62 | 1.00 | 0.86 | 1.00 | 1.00 | 0.59 | 0.82 | 0.96 | 1.00 | 1.00 | 0.60 | 1.00 | 1.00 | 0.96 | 1.00 | 0.94 | 1.00 | 1.00 | 0.96 | 1.00 | 0.80 | 0.98 | 1.00 |
| llm_sayback:deepseek-v4-flash | 1.00 | 0.94 | 1.00 | 1.00 | 1.00 | 0.96 | 0.87 | 1.00 | 0.90 | 1.00 | 1.00 | 1.00 | 0.97 | 1.00 | 1.00 | 0.88 | 0.99 | 0.55 | 1.00 | 0.87 | 1.00 | 1.00 | 0.79 | 0.67 | 0.97 | 1.00 | 1.00 | 0.52 | 1.00 | 0.97 | 0.92 | 1.00 | 1.00 | 0.97 | 1.00 | 0.93 | 1.00 | 0.80 | 0.93 | 1.00 |
| llm_sayback:qwen3-235b | 1.00 | 0.94 | 1.00 | 1.00 | 0.94 | 0.98 | 0.82 | 0.92 | 0.87 | 0.97 | 1.00 | 1.00 | 0.97 | 1.00 | 1.00 | 0.78 | 0.98 | 0.59 | 1.00 | 0.86 | 0.94 | 1.00 | 0.87 | 0.61 | 0.97 | 1.00 | 1.00 | 0.46 | 1.00 | 1.00 | 0.79 | 1.00 | 0.91 | 0.91 | 1.00 | 0.93 | 1.00 | 0.77 | 0.96 | 1.00 |
| llm_sayback:qwen3-30b | 1.00 | 0.94 | 1.00 | 1.00 | 1.00 | 0.98 | 0.91 | 0.96 | 0.83 | 1.00 | 1.00 | 0.99 | 0.97 | 1.00 | 1.00 | 0.68 | 0.99 | 0.41 | 1.00 | 0.86 | 0.91 | 1.00 | 0.85 | 0.61 | 0.96 | 1.00 | 1.00 | 0.35 | 1.00 | 1.00 | 0.91 | 1.00 | 0.94 | 0.91 | 1.00 | 0.94 | 1.00 | 0.98 | 0.98 | 1.00 |
| gliner_pii · threshold cutoff=0.2 | 1.00 | 0.90 | 1.00 | 0.73 | 0.00 | 1.00 | 0.99 | 0.00 | 1.00 | 0.59 | 1.00 | 0.99 | 0.98 | 1.00 | 1.00 | 0.07 | 0.99 | 0.43 | 0.91 | 1.00 | 1.00 | 0.93 | 0.14 | 0.79 | 0.87 | 0.10 | 0.94 | 0.96 | 1.00 | 0.86 | 0.53 | 1.00 | 0.66 | 0.29 | 1.00 | 0.74 | 1.00 | 1.00 | 0.62 | 1.00 |
| llm_sayback:deepseek-v4-flash-think | 1.00 | 0.90 | 1.00 | 1.00 | 0.94 | 0.75 | 0.71 | 0.59 | 0.64 | 0.89 | 1.00 | 1.00 | 0.68 | 1.00 | 0.88 | 0.85 | 0.98 | 0.70 | 1.00 | 0.92 | 1.00 | 1.00 | 0.67 | 0.52 | 0.96 | 1.00 | 1.00 | 0.64 | 0.99 | 0.94 | 0.77 | 0.91 | 0.80 | 0.94 | 1.00 | 0.73 | 0.97 | 0.62 | 0.44 | 1.00 |
| llm_sayback:gpt4.1-nano | 1.00 | 1.00 | 1.00 | 0.95 | 0.88 | 0.91 | 0.67 | 0.84 | 0.84 | 0.92 | 1.00 | 0.99 | 0.95 | 1.00 | 0.98 | 0.12 | 0.98 | 0.14 | 1.00 | 0.87 | 0.61 | 0.98 | 0.36 | 0.18 | 0.97 | 0.97 | 0.98 | 0.11 | 1.00 | 1.00 | 0.53 | 0.97 | 0.57 | 0.57 | 1.00 | 0.89 | 1.00 | 0.68 | 0.83 | 0.99 |
| decision_typed_skip:jev · threshold cutoff=0.35 | 1.00 | 0.94 | 1.00 | 1.00 | 0.94 | 1.00 | 0.98 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.98 | 1.00 | 1.00 | 0.86 | 1.00 | 0.95 | 1.00 | 1.00 | 1.00 | 1.00 | 0.51 | 1.00 | 1.00 | 1.00 | 1.00 | 0.73 | 1.00 | 0.97 | 0.92 | 1.00 | 1.00 | 1.00 | 1.00 | 0.98 | 1.00 | 0.66 | 0.95 | 1.00 |
| decision_typed:jev · threshold cutoff=0.4 | 1.00 | 0.94 | 1.00 | 1.00 | 1.00 | 1.00 | 0.99 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.98 | 1.00 | 1.00 | 0.95 | 1.00 | 0.95 | 1.00 | 1.00 | 1.00 | 1.00 | 0.47 | 1.00 | 1.00 | 1.00 | 1.00 | 0.74 | 1.00 | 0.97 | 0.94 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.83 | 0.87 | 1.00 |
| decision_words:jev · threshold cutoff=0.1 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.73 | 0.98 | 0.98 | 1.00 | 1.00 | 1.00 | 0.96 | 1.00 | 1.00 | 0.99 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.79 | 1.00 | 1.00 | 1.00 | 1.00 | 0.82 | 1.00 | 1.00 | 0.94 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.99 | 0.80 | 0.98 | 1.00 |
| privacy_filter · threshold cutoff=0.001 | 0.97 | 0.00 | 0.94 | 0.98 | 0.21 | 0.44 | 0.08 | 0.76 | 0.19 | 0.30 | 0.98 | 0.93 | 0.88 | 1.00 | 1.00 | 0.00 | 0.98 | 0.04 | 0.80 | 0.97 | 0.00 | 0.93 | 0.76 | 0.12 | 0.98 | 1.00 | 1.00 | 0.02 | 0.91 | 0.89 | 0.13 | 0.82 | 0.09 | 0.20 | 0.97 | 0.39 | 0.94 | 0.33 | 0.46 | 0.89 |
| presidio | 0.83 | 0.87 | 1.00 | 0.98 | 0.00 | 0.84 | 0.06 | 0.10 | 0.97 | 0.94 | 0.61 | 0.66 | 0.97 | 1.00 | 1.00 | 0.00 | 0.99 | 0.00 | 0.94 | 0.90 | 0.00 | 0.55 | 0.26 | 0.33 | 0.94 | 0.16 | 0.96 | 0.00 | 0.89 | 0.72 | 0.30 | 0.47 | 0.34 | 0.69 | 1.00 | 0.85 | 0.44 | 0.80 | 1.00 | 0.47 |
| regex | 0.94 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.10 | 0.00 | 0.00 | 0.87 | 1.00 | 0.94 | 1.00 | 1.00 | 0.00 | 0.98 | 0.00 | 0.89 | 0.00 | 0.00 | 0.95 | 0.33 | 0.00 | 0.00 | 0.13 | 1.00 | 0.00 | 0.87 | 0.64 | 0.00 | 0.12 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.66 | 0.20 | 0.29 |
| mask_all | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |

### Precision by the type a lane claims (typed lanes)

| lane | CONTACT | DATETIME | ID | LOCATION | OTHER | PERSON |
|---|---|---|---|---|---|---|
| llm_sayback:haiku4.5 | 1.00 | 0.97 | 0.99 | 1.00 | 0.89 | 0.99 |
| llm_sayback:deepseek-v4-flash | 1.00 | 0.96 | 0.96 | 0.98 | 0.86 | 0.99 |
| llm_sayback:qwen3-235b | 0.99 | 0.97 | 0.96 | 0.98 | 0.86 | 0.99 |
| llm_sayback:qwen3-30b | 0.99 | 0.89 | 0.94 | 0.96 | 0.66 | 0.98 |
| llm_sayback:deepseek-v4-flash-think | 1.00 | 0.98 | 0.98 | 0.98 | 0.88 | 0.99 |
| llm_sayback:gpt4.1-nano | 1.00 | 0.96 | 0.97 | 1.00 | 0.85 | 0.99 |
| decision_typed_skip:jev · threshold cutoff=0.35 | 0.57 | 0.65 | 0.32 | 0.80 | 0.50 | 0.95 |
| decision_typed:jev · threshold cutoff=0.4 | 0.50 | 0.58 | 0.26 | 0.78 | 0.44 | 0.87 |
| presidio | 1.00 | 0.69 | 0.98 | 0.95 | 0.93 | 0.97 |
| regex | 1.00 | 1.00 | 0.99 | – | – | – |

### Exact span match

| lane | F2 [95% CI] | P | R | F1 | ECE | $/1k docs | p50 s | failed | frontier |
|---|---|---|---|---|---|---|---|---|---|
| llm_sayback:haiku4.5 | 0.798 [0.776, 0.819] | 0.866 | 0.782 | 0.822 | – | 1.423 | 1.5 | 0 (+11 dropped) | yes |
| llm_sayback:deepseek-v4-flash | 0.766 [0.742, 0.789] | 0.850 | 0.748 | 0.796 | – | 0.072 | 2.3 | 0 | yes |
| llm_sayback:qwen3-235b | 0.759 [0.734, 0.784] | 0.847 | 0.740 | 0.790 | – | 0.157 | 11 | 1 (+22 dropped) |  |
| llm_sayback:qwen3-30b | 0.757 [0.735, 0.779] | 0.798 | 0.748 | 0.772 | – | 0.077 | 3.3 | 0 (+10 dropped) |  |
| llm_sayback:gpt4.1-nano | 0.710 [0.685, 0.733] | 0.827 | 0.686 | 0.750 | – | 0.089 | 1.8 | 0 |  |
| llm_sayback:deepseek-v4-flash-think | 0.706 [0.682, 0.729] | 0.842 | 0.679 | 0.752 | – | 0.255 | 11 | 1 (+5 dropped) |  |
| gliner_pii · threshold cutoff=0.2 | 0.658 [0.634, 0.680] | 0.761 | 0.636 | 0.693 | 0.016 | 0.000 | 0.29 | 0 | yes |
| presidio | 0.506 [0.488, 0.524] | 0.592 | 0.489 | 0.535 | – | 0.000 | 0.019 | 0 |  |
| privacy_filter · threshold cutoff=0.001 | 0.490 [0.465, 0.514] | 0.752 | 0.451 | 0.564 | 0.043 | 0.000 | 1.8 | 0 |  |
| decision_typed_skip:jev · threshold cutoff=0.35 | 0.456 [0.437, 0.474] | 0.357 | 0.490 | 0.413 | 0.069 | 0.411 | 0.31 | 0 |  |
| regex | 0.415 [0.395, 0.433] | 0.828 | 0.369 | 0.510 | – | 0.000 | 0.00013 | 0 |  |
| decision_typed:jev · threshold cutoff=0.4 | 0.340 [0.322, 0.358] | 0.289 | 0.356 | 0.319 | 0.121 | 0.696 | 0.37 | 0 |  |
| decision_words:jev · threshold cutoff=0.1 | 0.240 [0.224, 0.256] | 0.184 | 0.260 | 0.215 | 0.042 | 0.163 | 0.29 | 0 |  |
| mask_all | 0.000 [0.000, 0.000] | 0.000 | 0.000 | 0.000 | – | 0.000 | 2.7e-06 | 0 |  |

### Every decoder on per-word scores (word level)

| lane | F2 [95% CI] | P | R | F1 | ECE | $/1k docs | p50 s | failed | frontier |
|---|---|---|---|---|---|---|---|---|---|
| gliner_pii · threshold cutoff=0.2 | 0.872 [0.859, 0.885] | 0.895 | 0.867 | 0.881 | 0.016 | 0.000 | 0.29 | 0 | yes |
| gliner_pii · viterbi cutoff=0.2 switch_cost=0.25 | 0.872 [0.858, 0.884] | 0.903 | 0.864 | 0.883 | 0.016 | 0.000 | 0.29 | 0 |  |
| gliner_pii · closing cutoff=0.2 gap=1 | 0.867 [0.854, 0.880] | 0.859 | 0.869 | 0.864 | 0.016 | 0.000 | 0.29 | 0 |  |
| gliner_pii · hysteresis high=0.45 low=0.2 | 0.865 [0.851, 0.877] | 0.929 | 0.850 | 0.888 | 0.016 | 0.000 | 0.29 | 0 |  |
| gliner_pii | 0.852 [0.838, 0.865] | 0.933 | 0.834 | 0.881 | 0.016 | 0.000 | 0.29 | 0 |  |
| decision_typed_skip:jev · viterbi cutoff=0.4 switch_cost=0.25 | 0.829 [0.819, 0.839] | 0.575 | 0.932 | 0.711 | 0.069 | 0.411 | 0.31 | 0 |  |
| decision_typed_skip:jev | 0.829 [0.818, 0.838] | 0.586 | 0.925 | 0.717 | 0.069 | 0.411 | 0.31 | 0 |  |
| decision_typed_skip:jev · hysteresis high=0.45 low=0.3 | 0.828 [0.818, 0.837] | 0.553 | 0.945 | 0.698 | 0.069 | 0.411 | 0.31 | 0 |  |
| decision_typed_skip:jev · threshold cutoff=0.35 | 0.826 [0.816, 0.835] | 0.537 | 0.954 | 0.687 | 0.069 | 0.411 | 0.31 | 0 |  |
| decision_typed:jev | 0.808 [0.797, 0.819] | 0.522 | 0.936 | 0.671 | 0.121 | 0.696 | 0.37 | 0 |  |
| decision_typed_skip:jev · closing cutoff=0.4 gap=1 | 0.801 [0.791, 0.811] | 0.488 | 0.955 | 0.646 | 0.069 | 0.411 | 0.31 | 0 |  |
| decision_typed:jev · hysteresis high=0.45 low=0.4 | 0.795 [0.785, 0.806] | 0.478 | 0.952 | 0.637 | 0.121 | 0.696 | 0.37 | 0 |  |
| decision_typed:jev · threshold cutoff=0.4 | 0.792 [0.783, 0.803] | 0.469 | 0.958 | 0.630 | 0.121 | 0.696 | 0.37 | 0 |  |
| decision_typed:jev · viterbi cutoff=0.4 switch_cost=0.25 | 0.786 [0.776, 0.797] | 0.469 | 0.946 | 0.627 | 0.121 | 0.696 | 0.37 | 0 |  |
| decision_typed:jev · closing cutoff=0.5 gap=1 | 0.785 [0.775, 0.796] | 0.472 | 0.942 | 0.629 | 0.121 | 0.696 | 0.37 | 0 |  |
| decision_words:jev · hysteresis high=0.25 low=0.2 | 0.740 [0.725, 0.753] | 0.516 | 0.830 | 0.637 | 0.042 | 0.163 | 0.29 | 0 |  |
| decision_words:jev · threshold cutoff=0.1 | 0.719 [0.707, 0.730] | 0.365 | 0.950 | 0.527 | 0.042 | 0.163 | 0.29 | 0 |  |
| decision_words:jev · viterbi cutoff=0.1 switch_cost=0.25 | 0.717 [0.704, 0.728] | 0.374 | 0.930 | 0.533 | 0.042 | 0.163 | 0.29 | 0 |  |
| privacy_filter · threshold cutoff=0.001 | 0.698 [0.674, 0.722] | 0.933 | 0.657 | 0.771 | 0.043 | 0.000 | 1.8 | 0 |  |
| decision_words:jev · closing cutoff=0.1 gap=1 | 0.693 [0.681, 0.705] | 0.330 | 0.957 | 0.491 | 0.042 | 0.163 | 0.29 | 0 |  |
| privacy_filter · closing cutoff=0.01 gap=1 | 0.669 [0.643, 0.693] | 0.934 | 0.625 | 0.749 | 0.043 | 0.000 | 1.8 | 0 |  |
| privacy_filter · viterbi cutoff=0.01 switch_cost=0.5 | 0.664 [0.638, 0.689] | 0.954 | 0.618 | 0.750 | 0.043 | 0.000 | 1.8 | 0 |  |
| decision_words:jev | 0.661 [0.638, 0.683] | 0.706 | 0.650 | 0.677 | 0.042 | 0.163 | 0.29 | 0 |  |
| privacy_filter · hysteresis high=0.25 low=0.03 | 0.639 [0.611, 0.665] | 0.962 | 0.590 | 0.731 | 0.043 | 0.000 | 1.8 | 0 |  |
| privacy_filter | 0.615 [0.586, 0.643] | 0.972 | 0.564 | 0.714 | 0.043 | 0.000 | 1.8 | 0 |  |

## tab · test (105 docs, 127 docs)

### Word level (headline; per-word lanes use a threshold tuned on dev)

| lane | F2 [95% CI] | P | R | F1 | ECE | $/1k docs | p50 s | failed | frontier |
|---|---|---|---|---|---|---|---|---|---|
| human | 0.860 [0.840, 0.879] | 0.849 | 0.863 | 0.856 | – | 0.000 | 0 | 0 |  |
| decision_typed_skip:jev · threshold cutoff=0.5 | 0.805 [0.790, 0.820] | 0.736 | 0.824 | 0.778 | 0.046 | 3.079 | 0.64 | 0 | yes |
| decision_typed:jev · threshold cutoff=0.55 | 0.790 [0.774, 0.805] | 0.651 | 0.834 | 0.731 | 0.121 | 5.762 | 0.89 | 0 |  |
| llm_sayback:haiku4.5 | 0.773 [0.747, 0.796] | 0.831 | 0.759 | 0.793 | – | 4.805 | 3.6 | 0 (+16 dropped) |  |
| presidio | 0.744 [0.725, 0.762] | 0.793 | 0.733 | 0.762 | – | 0.000 | 0.12 | 0 | yes |
| gliner_pii · threshold cutoff=0.05 | 0.735 [0.718, 0.750] | 0.571 | 0.791 | 0.663 | 0.063 | 0.000 | 1.4 | 0 |  |
| llm_sayback:qwen3-235b | 0.722 [0.688, 0.754] | 0.704 | 0.727 | 0.716 | – | 0.686 | 30 | 0 (+43 dropped) |  |
| llm_sayback:deepseek-v4-flash | 0.722 [0.680, 0.755] | 0.795 | 0.706 | 0.748 | – | 0.330 | 7.7 | 1 (+21 dropped) |  |
| decision_words:jev · threshold cutoff=0.3 | 0.680 [0.662, 0.699] | 0.533 | 0.731 | 0.616 | 0.055 | 1.180 | 0.61 | 0 |  |
| llm_sayback:deepseek-v4-flash-think | 0.667 [0.610, 0.722] | 0.844 | 0.633 | 0.724 | – | 1.529 | 75 | 8 (+34 dropped) |  |
| llm_sayback:qwen3-30b | 0.650 [0.602, 0.691] | 0.660 | 0.647 | 0.653 | – | 0.394 | 5.3 | 8 (+73 dropped) |  |
| privacy_filter · threshold cutoff=0.001 | 0.555 [0.520, 0.590] | 0.928 | 0.505 | 0.654 | 0.084 | 0.000 | 2.3 | 0 |  |
| regex | 0.505 [0.472, 0.537] | 0.965 | 0.451 | 0.614 | – | 0.000 | 0.0011 | 0 |  |
| llm_sayback:gpt4.1-nano | 0.480 [0.430, 0.527] | 0.709 | 0.444 | 0.546 | – | 0.280 | 2.7 | 0 (+30 dropped) |  |
| mask_all | 0.405 [0.386, 0.423] | 0.120 | 1.000 | 0.214 | – | 0.000 | 2.5e-06 | 0 |  |

- → Privacy Filter has 8 categories: no organisations, demographics or most IDs.
- → An LLM answer that is cut off or won't parse counts as finding nothing (`failed`).

### Every lane against decision_typed_skip:jev · threshold cutoff=0.5, same docs (paired bootstrap)

| lane | F2 − decision_typed_skip:jev · threshold cutoff=0.5 [95% CI] | clear gap |
|---|---|---|
| decision_typed:jev · threshold cutoff=0.55 | -0.016 [-0.019, -0.012] | yes |
| llm_sayback:haiku4.5 | -0.032 [-0.058, -0.009] | yes |
| presidio | -0.061 [-0.076, -0.046] | yes |
| gliner_pii · threshold cutoff=0.05 | -0.071 [-0.090, -0.051] | yes |
| llm_sayback:qwen3-235b | -0.083 [-0.119, -0.051] | yes |
| llm_sayback:deepseek-v4-flash | -0.083 [-0.128, -0.049] | yes |
| decision_words:jev · threshold cutoff=0.3 | -0.125 [-0.134, -0.116] | yes |
| llm_sayback:deepseek-v4-flash-think | -0.138 [-0.197, -0.080] | yes |
| llm_sayback:qwen3-30b | -0.156 [-0.210, -0.108] | yes |
| privacy_filter · threshold cutoff=0.001 | -0.250 [-0.281, -0.221] | yes |
| regex | -0.300 [-0.332, -0.269] | yes |
| llm_sayback:gpt4.1-nano | -0.325 [-0.377, -0.274] | yes |
| mask_all | -0.400 [-0.425, -0.374] | yes |

### Format vs context: recall on PII found by its form vs by its meaning

| lane | format recall | context recall | gap | left-in-clear masked (lower is better) |
|---|---|---|---|---|
| human | 0.93 | 0.77 | +0.16 | 0.21 |
| decision_typed_skip:jev · threshold cutoff=0.5 | 0.89 | 0.73 | +0.16 | 0.25 |
| decision_typed:jev · threshold cutoff=0.55 | 0.92 | 0.72 | +0.20 | 0.22 |
| llm_sayback:haiku4.5 | 0.88 | 0.58 | +0.30 | 0.27 |
| presidio | 0.90 | 0.50 | +0.40 | 0.25 |
| gliner_pii · threshold cutoff=0.05 | 0.86 | 0.69 | +0.18 | 0.73 |
| llm_sayback:qwen3-235b | 0.83 | 0.58 | +0.24 | 0.33 |
| llm_sayback:deepseek-v4-flash | 0.79 | 0.58 | +0.21 | 0.28 |
| decision_words:jev · threshold cutoff=0.3 | 0.79 | 0.64 | +0.15 | 0.14 |
| llm_sayback:deepseek-v4-flash-think | 0.74 | 0.48 | +0.27 | 0.19 |
| llm_sayback:qwen3-30b | 0.69 | 0.58 | +0.11 | 0.35 |
| privacy_filter · threshold cutoff=0.001 | 0.52 | 0.48 | +0.05 | 0.04 |
| regex | 0.77 | 0.00 | +0.77 | 0.02 |
| llm_sayback:gpt4.1-nano | 0.51 | 0.35 | +0.17 | 0.13 |
| mask_all | 1.00 | 1.00 | +0.00 | 1.00 |

### Cost and time per doc

| lane | $/1k docs | calls/doc | tokens in/doc | tokens out/doc | latency mean s | p50 s | p95 s | wall clock s |
|---|---|---|---|---|---|---|---|---|
| gliner_pii · threshold cutoff=0.05 | 0.000 | 0.0 | 0 | 0 | 1.7 | 1.4 | 3.3 | 217 |
| mask_all | 0.000 | 0.0 | 0 | 0 | 3e-06 | 2.5e-06 | 3e-06 | 0 |
| presidio | 0.000 | 0.0 | 0 | 0 | 0.15 | 0.12 | 0.3 | 20 |
| privacy_filter · threshold cutoff=0.001 | 0.000 | 0.0 | 0 | 0 | 2.4 | 2.3 | 2.9 | 304 |
| regex | 0.000 | 0.0 | 0 | 0 | 0.0014 | 0.0011 | 0.0027 | 0 |
| llm_sayback:gpt4.1-nano | 0.280 | 1.0 | 1,593 | 301 | 3.2 | 2.7 | 5.9 | 60 |
| llm_sayback:deepseek-v4-flash | 0.330 | 1.0 | 1,539 | 722 | 9.2 | 7.7 | 19 | 173 |
| llm_sayback:qwen3-30b | 0.394 | 1.0 | 1,617 | 1,325 | 13 | 5.3 | 42 | 257 |
| llm_sayback:qwen3-235b | 0.686 | 1.0 | 1,617 | 774 | 34 | 30 | 76 | 592 |
| decision_words:jev · threshold cutoff=0.3 | 1.180 | 1.5 | 28,098 | 15,997 | 0.61 | 0.61 | 0.87 | 2 |
| llm_sayback:deepseek-v4-flash-think | 1.529 | 1.0 | 1,539 | 5,994 | 89 | 75 | 2.1e+02 | 1481 |
| decision_typed_skip:jev · threshold cutoff=0.5 | 3.079 | 2.2 | 73,307 | 30,323 | 0.68 | 0.64 | 0.96 | 13 |
| llm_sayback:haiku4.5 | 4.805 | 1.0 | 1,955 | 570 | 3.7 | 3.6 | 6.4 | 63 |
| decision_typed:jev · threshold cutoff=0.55 | 5.762 | 3.8 | 137,191 | 57,303 | 1.1 | 0.89 | 2.7 | 3 |

### Recall by gold type (word level)

| lane | DATETIME | ID | LOCATION | OTHER | PERSON |
|---|---|---|---|---|---|
| human | 0.94 | 0.98 | 0.91 | 0.58 | 0.91 |
| decision_typed_skip:jev · threshold cutoff=0.5 | 0.92 | 0.99 | 0.87 | 0.39 | 0.98 |
| decision_typed:jev · threshold cutoff=0.55 | 0.95 | 0.99 | 0.88 | 0.35 | 1.00 |
| llm_sayback:haiku4.5 | 0.92 | 0.79 | 0.78 | 0.42 | 0.69 |
| presidio | 0.99 | 0.05 | 0.74 | 0.17 | 0.73 |
| gliner_pii · threshold cutoff=0.05 | 0.93 | 0.51 | 0.79 | 0.55 | 0.72 |
| llm_sayback:qwen3-235b | 0.85 | 0.69 | 0.72 | 0.48 | 0.65 |
| llm_sayback:deepseek-v4-flash | 0.83 | 0.39 | 0.80 | 0.45 | 0.68 |
| decision_words:jev · threshold cutoff=0.3 | 0.82 | 0.88 | 0.73 | 0.28 | 0.96 |
| llm_sayback:deepseek-v4-flash-think | 0.77 | 0.51 | 0.65 | 0.44 | 0.48 |
| llm_sayback:qwen3-30b | 0.73 | 0.39 | 0.80 | 0.50 | 0.59 |
| privacy_filter · threshold cutoff=0.001 | 0.56 | 0.27 | 0.09 | 0.04 | 0.93 |
| regex | 0.80 | 0.88 | 0.00 | 0.00 | 0.00 |
| llm_sayback:gpt4.1-nano | 0.55 | 0.20 | 0.50 | 0.18 | 0.47 |
| mask_all | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |

### TAB's official script (entity recall on direct / quasi identifiers, token P/R/F1)

| lane | ER direct | ER quasi | token R | token P | token F1 |
|---|---|---|---|---|---|
| decision_typed_skip:jev · threshold cutoff=0.5 | 0.994 | 0.817 | 0.859 | 0.726 | 0.787 |
| decision_typed:jev · threshold cutoff=0.55 | 0.994 | 0.852 | 0.862 | 0.646 | 0.739 |
| llm_sayback:haiku4.5 | 0.923 | 0.770 | 0.798 | 0.838 | 0.817 |
| presidio | 0.486 | 0.764 | 0.756 | 0.751 | 0.754 |
| gliner_pii · threshold cutoff=0.05 | 0.946 | 0.799 | 0.849 | 0.556 | 0.672 |
| llm_sayback:qwen3-235b | 0.829 | 0.704 | 0.746 | 0.726 | 0.736 |
| llm_sayback:deepseek-v4-flash | 0.883 | 0.681 | 0.740 | 0.805 | 0.772 |
| decision_words:jev · threshold cutoff=0.3 | 0.992 | 0.654 | 0.773 | 0.519 | 0.621 |
| llm_sayback:deepseek-v4-flash-think | 0.920 | 0.602 | 0.672 | 0.869 | 0.758 |
| llm_sayback:qwen3-30b | 0.736 | 0.613 | 0.671 | 0.655 | 0.663 |
| privacy_filter · threshold cutoff=0.001 | 0.528 | 0.484 | 0.534 | 0.895 | 0.668 |
| regex | 0.494 | 0.453 | 0.530 | 0.945 | 0.679 |
| llm_sayback:gpt4.1-nano | 0.481 | 0.429 | 0.487 | 0.725 | 0.583 |
| mask_all | 1.000 | 1.000 | 1.000 | 0.121 | 0.215 |

### Recall by masking need: DIRECT identifiers vs QUASI (combine to re-identify)

| lane | DIRECT | QUASI |
|---|---|---|
| human | 0.99 | 0.85 |
| decision_typed_skip:jev · threshold cutoff=0.5 | 0.99 | 0.81 |
| decision_typed:jev · threshold cutoff=0.55 | 0.99 | 0.82 |
| llm_sayback:haiku4.5 | 0.78 | 0.76 |
| presidio | 0.58 | 0.74 |
| gliner_pii · threshold cutoff=0.05 | 0.76 | 0.79 |
| llm_sayback:qwen3-235b | 0.80 | 0.72 |
| llm_sayback:deepseek-v4-flash | 0.85 | 0.70 |
| decision_words:jev · threshold cutoff=0.3 | 0.98 | 0.71 |
| llm_sayback:deepseek-v4-flash-think | 0.87 | 0.62 |
| llm_sayback:qwen3-30b | 0.67 | 0.65 |
| privacy_filter · threshold cutoff=0.001 | 0.79 | 0.49 |
| regex | 0.18 | 0.47 |
| llm_sayback:gpt4.1-nano | 0.60 | 0.43 |
| mask_all | 1.00 | 1.00 |

### Recall by TAB entity type

| lane | CODE | DATETIME | DEM | LOC | MISC | ORG | PERSON | QUANTITY |
|---|---|---|---|---|---|---|---|---|
| human | 0.98 | 0.94 | 0.43 | 0.91 | 0.34 | 0.66 | 0.91 | 0.65 |
| decision_typed_skip:jev · threshold cutoff=0.5 | 0.99 | 0.92 | 0.60 | 0.87 | 0.14 | 0.43 | 0.98 | 0.27 |
| decision_typed:jev · threshold cutoff=0.55 | 0.99 | 0.95 | 0.60 | 0.88 | 0.12 | 0.37 | 1.00 | 0.24 |
| llm_sayback:haiku4.5 | 0.79 | 0.92 | 0.27 | 0.78 | 0.13 | 0.52 | 0.69 | 0.37 |
| presidio | 0.05 | 0.99 | 0.42 | 0.74 | 0.13 | 0.15 | 0.73 | 0.02 |
| gliner_pii · threshold cutoff=0.05 | 0.51 | 0.93 | 0.47 | 0.79 | 0.13 | 0.78 | 0.72 | 0.05 |
| llm_sayback:qwen3-235b | 0.69 | 0.85 | 0.28 | 0.72 | 0.36 | 0.56 | 0.65 | 0.49 |
| llm_sayback:deepseek-v4-flash | 0.39 | 0.83 | 0.25 | 0.80 | 0.04 | 0.56 | 0.68 | 0.52 |
| decision_words:jev · threshold cutoff=0.3 | 0.88 | 0.82 | 0.75 | 0.73 | 0.13 | 0.18 | 0.96 | 0.34 |
| llm_sayback:deepseek-v4-flash-think | 0.51 | 0.77 | 0.31 | 0.65 | 0.05 | 0.56 | 0.48 | 0.43 |
| llm_sayback:qwen3-30b | 0.39 | 0.73 | 0.21 | 0.80 | 0.28 | 0.67 | 0.59 | 0.29 |
| privacy_filter · threshold cutoff=0.001 | 0.27 | 0.56 | 0.01 | 0.09 | 0.07 | 0.05 | 0.93 | 0.03 |
| regex | 0.88 | 0.80 | 0.00 | 0.00 | 0.01 | 0.00 | 0.00 | 0.01 |
| llm_sayback:gpt4.1-nano | 0.20 | 0.55 | 0.04 | 0.50 | 0.09 | 0.23 | 0.47 | 0.16 |
| mask_all | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |

### Precision by the type a lane claims (typed lanes)

| lane | CONTACT | DATETIME | ID | LOCATION | OTHER | PERSON |
|---|---|---|---|---|---|---|
| human | – | 0.97 | 1.00 | 0.74 | 0.50 | 0.94 |
| decision_typed_skip:jev · threshold cutoff=0.5 | – | 0.90 | 0.56 | 0.52 | 0.33 | 0.78 |
| decision_typed:jev · threshold cutoff=0.55 | – | 0.73 | 0.46 | 0.44 | 0.32 | 0.80 |
| llm_sayback:haiku4.5 | – | 0.96 | 0.89 | 0.55 | 0.49 | 0.93 |
| presidio | 0.50 | 0.89 | 0.60 | 0.26 | 0.38 | 0.91 |
| llm_sayback:qwen3-235b | 0.00 | 0.96 | 0.47 | 0.50 | 0.26 | 0.92 |
| llm_sayback:deepseek-v4-flash | – | 0.97 | 0.84 | 0.51 | 0.45 | 0.82 |
| llm_sayback:deepseek-v4-flash-think | – | 0.97 | 0.86 | 0.63 | 0.54 | 0.90 |
| llm_sayback:qwen3-30b | – | 0.97 | 0.45 | 0.49 | 0.21 | 0.90 |
| regex | – | 0.97 | 0.94 | – | – | – |
| llm_sayback:gpt4.1-nano | – | 0.97 | 0.49 | 0.55 | 0.19 | 0.87 |

### Exact span match

| lane | F2 [95% CI] | P | R | F1 | ECE | $/1k docs | p50 s | failed | frontier |
|---|---|---|---|---|---|---|---|---|---|
| human | 0.810 [0.785, 0.832] | 0.808 | 0.810 | 0.809 | – | 0.000 | 0 | 0 |  |
| llm_sayback:haiku4.5 | 0.682 [0.654, 0.712] | 0.685 | 0.682 | 0.683 | – | 4.805 | 3.6 | 0 (+16 dropped) | yes |
| llm_sayback:deepseek-v4-flash | 0.632 [0.593, 0.669] | 0.645 | 0.629 | 0.637 | – | 0.330 | 7.7 | 1 (+21 dropped) | yes |
| llm_sayback:qwen3-235b | 0.617 [0.578, 0.654] | 0.596 | 0.622 | 0.609 | – | 0.686 | 30 | 0 (+43 dropped) |  |
| llm_sayback:deepseek-v4-flash-think | 0.590 [0.540, 0.641] | 0.696 | 0.568 | 0.626 | – | 1.529 | 75 | 8 (+34 dropped) |  |
| presidio | 0.581 [0.555, 0.605] | 0.585 | 0.580 | 0.582 | – | 0.000 | 0.12 | 0 | yes |
| decision_typed_skip:jev · threshold cutoff=0.5 | 0.575 [0.555, 0.596] | 0.426 | 0.630 | 0.508 | 0.046 | 3.079 | 0.64 | 0 |  |
| llm_sayback:qwen3-30b | 0.569 [0.521, 0.613] | 0.580 | 0.566 | 0.573 | – | 0.394 | 5.3 | 8 (+73 dropped) |  |
| gliner_pii · threshold cutoff=0.05 | 0.546 [0.520, 0.572] | 0.392 | 0.605 | 0.476 | 0.063 | 0.000 | 1.4 | 0 |  |
| regex | 0.451 [0.416, 0.488] | 0.934 | 0.400 | 0.560 | – | 0.000 | 0.0011 | 0 |  |
| privacy_filter · threshold cutoff=0.001 | 0.417 [0.385, 0.451] | 0.749 | 0.375 | 0.500 | 0.084 | 0.000 | 2.3 | 0 |  |
| llm_sayback:gpt4.1-nano | 0.404 [0.359, 0.445] | 0.592 | 0.374 | 0.458 | – | 0.280 | 2.7 | 0 (+30 dropped) |  |
| decision_typed:jev · threshold cutoff=0.55 | 0.297 [0.277, 0.317] | 0.241 | 0.315 | 0.273 | 0.121 | 5.762 | 0.89 | 0 |  |
| decision_words:jev · threshold cutoff=0.3 | 0.267 [0.252, 0.282] | 0.185 | 0.301 | 0.229 | 0.055 | 1.180 | 0.61 | 0 |  |
| mask_all | 0.000 [0.000, 0.000] | 0.000 | 0.000 | 0.000 | – | 0.000 | 2.5e-06 | 0 |  |

### Every decoder on per-word scores (word level)

| lane | F2 [95% CI] | P | R | F1 | ECE | $/1k docs | p50 s | failed | frontier |
|---|---|---|---|---|---|---|---|---|---|
| decision_typed_skip:jev · viterbi cutoff=0.2 switch_cost=1.0 | 0.821 [0.807, 0.835] | 0.678 | 0.866 | 0.761 | 0.046 | 3.079 | 0.64 | 0 | yes |
| decision_typed_skip:jev · hysteresis high=0.55 low=0.3 | 0.817 [0.803, 0.831] | 0.723 | 0.844 | 0.779 | 0.046 | 3.079 | 0.64 | 0 |  |
| decision_typed_skip:jev | 0.805 [0.790, 0.820] | 0.736 | 0.824 | 0.778 | 0.046 | 3.079 | 0.64 | 0 |  |
| decision_typed_skip:jev · threshold cutoff=0.5 | 0.805 [0.790, 0.820] | 0.736 | 0.824 | 0.778 | 0.046 | 3.079 | 0.64 | 0 |  |
| decision_typed_skip:jev · closing cutoff=0.6 gap=1 | 0.799 [0.781, 0.818] | 0.749 | 0.812 | 0.779 | 0.046 | 3.079 | 0.64 | 0 |  |
| decision_typed:jev · threshold cutoff=0.55 | 0.790 [0.774, 0.805] | 0.651 | 0.834 | 0.731 | 0.121 | 5.762 | 0.89 | 0 |  |
| decision_typed:jev · hysteresis high=0.55 low=0.5 | 0.789 [0.775, 0.804] | 0.621 | 0.847 | 0.717 | 0.121 | 5.762 | 0.89 | 0 |  |
| decision_typed:jev | 0.789 [0.774, 0.803] | 0.605 | 0.853 | 0.708 | 0.121 | 5.762 | 0.89 | 0 |  |
| decision_typed:jev · closing cutoff=0.6 gap=1 | 0.786 [0.769, 0.803] | 0.660 | 0.826 | 0.733 | 0.121 | 5.762 | 0.89 | 0 |  |
| decision_typed:jev · viterbi cutoff=0.5 switch_cost=0.25 | 0.785 [0.769, 0.801] | 0.618 | 0.842 | 0.713 | 0.121 | 5.762 | 0.89 | 0 |  |
| gliner_pii · threshold cutoff=0.05 | 0.735 [0.718, 0.750] | 0.571 | 0.791 | 0.663 | 0.063 | 0.000 | 1.4 | 0 | yes |
| gliner_pii · viterbi cutoff=0.03 switch_cost=1.0 | 0.733 [0.716, 0.749] | 0.593 | 0.779 | 0.673 | 0.063 | 0.000 | 1.4 | 0 |  |
| gliner_pii · closing cutoff=0.15 gap=1 | 0.724 [0.709, 0.740] | 0.564 | 0.780 | 0.654 | 0.063 | 0.000 | 1.4 | 0 |  |
| gliner_pii · hysteresis high=0.35 low=0.03 | 0.717 [0.698, 0.733] | 0.628 | 0.743 | 0.681 | 0.063 | 0.000 | 1.4 | 0 |  |
| decision_words:jev · closing cutoff=0.3 gap=1 | 0.706 [0.687, 0.725] | 0.503 | 0.785 | 0.613 | 0.055 | 1.180 | 0.61 | 0 |  |
| gliner_pii | 0.687 [0.666, 0.706] | 0.649 | 0.697 | 0.672 | 0.063 | 0.000 | 1.4 | 0 |  |
| decision_words:jev · viterbi cutoff=0.3 switch_cost=0.25 | 0.681 [0.662, 0.701] | 0.573 | 0.715 | 0.636 | 0.055 | 1.180 | 0.61 | 0 |  |
| decision_words:jev · threshold cutoff=0.3 | 0.680 [0.662, 0.699] | 0.533 | 0.731 | 0.616 | 0.055 | 1.180 | 0.61 | 0 |  |
| decision_words:jev · hysteresis high=0.35 low=0.3 | 0.676 [0.658, 0.695] | 0.560 | 0.713 | 0.628 | 0.055 | 1.180 | 0.61 | 0 |  |
| privacy_filter · threshold cutoff=0.001 | 0.555 [0.520, 0.590] | 0.928 | 0.505 | 0.654 | 0.084 | 0.000 | 2.3 | 0 |  |
| decision_words:jev | 0.537 [0.516, 0.559] | 0.707 | 0.507 | 0.590 | 0.055 | 1.180 | 0.61 | 0 |  |
| privacy_filter · closing cutoff=0.01 gap=1 | 0.478 [0.442, 0.514] | 0.914 | 0.427 | 0.582 | 0.084 | 0.000 | 2.3 | 0 |  |
| privacy_filter · viterbi cutoff=0.01 switch_cost=0.25 | 0.474 [0.438, 0.510] | 0.942 | 0.421 | 0.582 | 0.084 | 0.000 | 2.3 | 0 |  |
| privacy_filter · hysteresis high=0.25 low=0.01 | 0.393 [0.357, 0.431] | 0.948 | 0.343 | 0.504 | 0.084 | 0.000 | 2.3 | 0 |  |
| privacy_filter | 0.345 [0.311, 0.380] | 0.953 | 0.298 | 0.454 | 0.084 | 0.000 | 2.3 | 0 |  |

### Most leaked and most over-masked strings

- → **decision_typed_skip:jev · threshold cutoff=0.5** leaks: serco (17), widows (16), city court (11), industries (11), będzin district court (10), widow’s bereavement allowance (9), wba (9), the galleries (9)  
  over-masks: applicant (289), born (133), application (108), ankara (60), date (45), london (41), state security court (37), organisation (33)
- → **decision_typed:jev · threshold cutoff=0.55** leaks: serco (19), widows (16), city court (11), industries (11), będzin district court (10), united kingdom (9), widow’s bereavement allowance (9), wba (9)  
  over-masks: applicant (172), born (82), ankara (50), he (35), date (31), london (29), an (29), warsaw (29)
- → **llm_sayback:haiku4.5** leaks: british (25), serco (20), united kingdom (19), widows (16), pkk (13), mr benham (13), industries (12), mr ryssdal (11)  
  over-masks: london (34), ankara state security court (26), foreign and commonwealth office (25), united kingdom (21), 1 november 1998 (19), izmir (18), istanbul (18), sweden (16)
- → **presidio** leaks: mr c. whomersley (22), serco (17), widows (16), pkk (15), mr j. wołąsiewicz (14), mr benham (13), industries (12), mr ryssdal (11)  
  over-masks: northern ireland (49), the united kingdom (47), the united kingdom of great britain (46), london (40), the republic of turkey (32), united kingdom (30), turkish (27), the same day (27)
- → **gliner_pii · threshold cutoff=0.05** leaks: mr c. whomersley (22), widows (16), mr j. wołąsiewicz (14), mr ryssdal (11), mr r. ryssdal (10), mr j. grainger (9), white (9), widow’s bereavement allowance (9)  
  over-masks: applicant (243), united kingdom (141), lawyer (104), agent (64), turkish (63), judge (62), applicant’s (58), secretary of state (57)
- → **llm_sayback:qwen3-235b** leaks: british (26), united kingdom (21), serco (20), widows (16), pkk (15), bnp (11), city court (11), sir john freeland (10)  
  over-masks: the applicant (35), the union (31), london (22), court of cassation (21), ankara (20), ankara state security court (20), court of appeal (19), applicant (19)
- → **llm_sayback:deepseek-v4-flash** leaks: united kingdom (22), british (18), widows (16), pkk (15), mr j. wołąsiewicz (13), industries (12), mr ryssdal (11), city court (11)  
  over-masks: the applicant (76), a (29), london (28), swedish (23), ankara state security court (23), united kingdom (21), sweden (20), ankara (17)
- → **decision_words:jev · threshold cutoff=0.3** leaks: serco (20), united kingdom (17), widows (16), pkk (14), industries (12), city court (11), będzin district court (10), bnp (9)  
  over-masks: applicant (386), his (212), applicant’s (133), he (114), him (67), application (56), born (50), ankara (47)
- → **llm_sayback:deepseek-v4-flash-think** leaks: widows (16), british (15), mr c. whomersley (14), mr benham (13), united kingdom (13), industries (12), city court (11), somalia (11)  
  over-masks: a (29), ankara state security court (26), swedish (17), ankara (17), sweden (16), istanbul state security court (13), 1 november 1998 (12), warsaw (12)
- → **llm_sayback:qwen3-30b** leaks: british (21), widows (16), pkk (15), mr benham (13), mr ryssdal (11), united kingdom (11), turkish (11), city court (11)  
  over-masks: the applicant (70), foreign and commonwealth office (37), the applicants (32), london (32), united kingdom (31), the union (31), ankara state security court (21), the court (19)
- → **privacy_filter · threshold cutoff=0.001** leaks: british (28), united kingdom (22), serco (16), widows (16), pkk (14), industries (12), bnp (11), turkish (11)  
  over-masks: sergeant h (10), chamber (9), w.k (8), cassation (7), sąd najwyższy (7), mrs g (6), corporal g (6), lagen (5)
- → **regex** leaks: british (28), mr c. whomersley (22), united kingdom (22), serco (20), widows (16), pkk (15), mr j. wołąsiewicz (14), mr benham (13)  
  over-masks: 1 november 1998 (21), 1 november 2001 (12), 17 june 2004 (7), 25 february 1997 (3), 1997-i (3), 1998-iv (2), 15 november 1996 (2), 65731/01 (2)
- → **llm_sayback:gpt4.1-nano** leaks: british (28), serco (20), united kingdom (19), widows (16), pkk (15), mr benham (13), industries (12), turkish (11)  
  over-masks: the applicant (340), ankara (41), the court (36), the applicants (33), istanbul (29), london (26), foreign and commonwealth office (22), izmir (17)

## Checks

### Check: Jev's answers before vs past its documented 32,000-token context

| lane | dataset | words before | Brier before | PII share before | words past | Brier past | PII share past |
|---|---|---|---|---|---|---|---|
| decision_typed:jev | ai4privacy | 23,137 | 0.129 | 0.172 | 0 | – | – |
| decision_typed:jev | nemotron | 49,075 | 0.075 | 0.102 | 1,874 | 0.052 | 0.044 |
| decision_typed:jev | tab | 81,925 | 0.068 | 0.119 | 24,759 | 0.073 | 0.124 |
| decision_typed_skip:jev | ai4privacy | 17,028 | 0.159 | 0.228 | 0 | – | – |
| decision_typed_skip:jev | nemotron | 28,863 | 0.099 | 0.174 | 213 | 0.039 | 0.047 |
| decision_typed_skip:jev | tab | 44,732 | 0.078 | 0.218 | 11,676 | 0.071 | 0.196 |
| decision_words:jev | ai4privacy | 23,137 | 0.061 | 0.172 | 0 | – | – |
| decision_words:jev | nemotron | 50,949 | 0.046 | 0.100 | 0 | – | – |
| decision_words:jev | tab | 106,684 | 0.067 | 0.120 | 0 | – | – |

### Check: two lanes on only the docs both answered

| dataset | lane A | lane B | docs | F2 A | F2 B | P A / B | R A / B |
|---|---|---|---|---|---|---|---|
| ai4privacy | llm_sayback:deepseek-v4-flash | llm_sayback:deepseek-v4-flash-think | 500 | 0.946 | 0.948 | 0.894 / 0.895 | 0.960 / 0.962 |
| nemotron | llm_sayback:deepseek-v4-flash | llm_sayback:deepseek-v4-flash-think | 499 | 0.922 | 0.868 | 0.951 / 0.964 | 0.916 / 0.847 |
| tab | llm_sayback:deepseek-v4-flash | llm_sayback:deepseek-v4-flash-think | 118 | 0.737 | 0.737 | 0.807 / 0.843 | 0.721 / 0.715 |

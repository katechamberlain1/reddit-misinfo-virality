# Draft paper — consolidated working document

*Working title: **Structural, Linguistic and Veracity Signals of Virality on UK Political Reddit***

**How to use this document.** All sections are in bullet form for you to expand into prose. Structure follows the department's required layout: Introduction → Related Work → Methodology (Requirements / Design / Implementation) → Results (Experimental results / Evaluation & validation) → Discussion & Conclusions → Future Work → References. Citations use your Zotero keys `[like_this_2021]`. **[GAP]** = find/decide something. **[VERIFY]** = confirm this against the paper's full text before committing (not assumed). **[PLOT N]** = figure to include; all figures collected in the Figure List at the end. **[DECISION]** = needs your/supervisor's call.

---

# 1. Introduction

## 1.1 Context for the project
- Social media is now a primary arena for political discussion → also a vector for large-scale spread of misinformation/malicious content.
- The harm is in the *spread*, not just the existence, of false content — virality turns a fringe claim into a mass belief.
- Reddit specifically: community-structured, vote-based, openly-ranked, archived — a tractable and distinctive setting for studying virality (expanded in 1.4).
- Scope of this project: the drivers of virality on **UK political Reddit**, with veracity (true vs fake) treated as one candidate driver among structural, emotional, political-leaning and topic features.

## 1.2 Motivation for the work
- Motivating case: the 2024 UK riots. False claims about the Southport attacker's identity spread across platforms via an online–offline feedback loop, amplified by influencers and coordinated/foreign actors; digital falsehoods precipitated offline violence and were recirculated as "proof" `[munk_when_2026]`.
- Understanding *what makes political content spread* is therefore of direct public interest.
- Gap that motivates the specific study: the virality/misinformation literature is overwhelmingly US- and Twitter-centric; **to our knowledge no prior work models virality on UK political Reddit**, and veracity is rarely treated as a *feature in a virality model* rather than a standalone detection target `[savatteri_veracity_2026; esteban-bravo_predicting_2024]`.

### Research questions
- **RQ1:** Which structural, linguistic, emotional, political-leaning, topic and veracity factors predict virality on UK political Reddit?
- **RQ2:** Is **veracity** (true vs fake) a meaningful predictor of virality, and in which direction?
- **RQ3:** Do viral *true* and viral *fake* posts go viral for the *same reasons*? `[esteban-bravo_predicting_2024]`

## 1.3 Why Reddit (vs X / Facebook)
- **Community-structured:** content lives in topically-bounded subreddits with their own norms/audiences → virality can be measured *relative to a community*, not a global feed. Underpins the size-normalised virality target.
- **Legible, vote-based mechanism:** Reddit's openly-documented "hot" ranking combines net votes (upvotes − downvotes, log scale) with time decay → engagement reflects explicit community endorsement, not opaque algorithmic amplification (X/Facebook). `[GAP: cite Reddit ranking mechanism — Salihefendic's write-up of the open-source algorithm / Cornell INFO2040 explainer]`
- **Research-tractable:** comparatively accessible, archived, with post-level engagement metadata; Facebook/Twitter impose higher barriers `[baumgartner_pushshift_2020]`.
- **Under-studied:** virality/misinfo literature is Twitter/X-heavy.

## 1.4 Why UK politics & why 2024
- UK has a distinct media ecosystem, party system and events vs the US-centric literature (Fakeddit, FakeNewsNet, Vosoughi et al. all US).
- 2024 unusually dense for UK political discourse (general election + summer riots) → concentrated signal `[antypas_causal_2026; munk_when_2026]`.
- Window: July–September 2024 captures the 4 July general election, the late-July/Aug riots, and aftermath.
- **Honesty on the riots:** riot misinformation spread principally on X/Facebook/Telegram, *not* Reddit `[munk_when_2026]` → riots are *societal motivation*; the **general election** is the on-platform driver of discussion volume.
- **[DECISION]** 3-month window is also a compute/scope choice — state plainly (see Limitations in §5/§6).

## 1.5 Contributions
- A transferable, explainable virality-prediction pipeline, validated US→UK via an explicit cross-demographic comparability analysis.
- The first (to our knowledge) virality analysis of UK political Reddit.
- A SHAP-based account of how veracity interacts with virality in a politically-coherent, text-driven corpus — contrasted with a general US corpus where the same pipeline shows veracity *suppressing* virality.

---

# 2. Related Work

## 2.1 Virality & popularity prediction on social media
- Barnes et al. — closest methodological precedent: predicts meme popularity on Reddit from content + metadata using tree-based models (best AUC ≈ 0.68); quantifies incremental value of image over text features `[barnes_dank_2021]`.
- Dogan et al. — Reddit virality in a cross-lingual, multimodal setting; defines virality by **normalising engagement by community size** and critiques reliance on "static, simple volume-based thresholds with arbitrary cut-offs" `[dogan_early_2026]`.
- Chauhan et al. — image/repost cascade dynamics on ideologically diverse subreddits; post- and cascade-level virality prediction `[chauhan_when_2025]`.
- Brevity → popularity `[GAP: Tsur & Rappoport 2012 not in library — add or drop the specific claim]`.

## 2.2 Veracity, emotion & diffusion
- False news spreads faster/farther/deeper than truth `[noauthor_spread_nodate — Vosoughi, Roy & Aral 2018; fix metadata]`.
- Shift from *detecting veracity* to *predicting diffusion*: Savatteri et al. compare the two tasks head-to-head across datasets `[savatteri_veracity_2026]`; Esteban-Bravo et al. show content features affect virality *differently* for true vs fake news → motivates the subgroup analysis `[esteban-bravo_predicting_2024]`.
- Emotion as explanatory variable: negativity retweeted more, incl. UK politicians `[antypas_negativity_2023]`; moral emotions moderate misinformation virality (false rumours outspread truth *when* high moral-emotional load) `[solovev_moral_2022]`.
- Frameworks: dual emotion (publisher + social/comment emotion) for fake-news detection `[zhang_mining_2021]`; emotional signals aid credibility (LSTM — cite for motivation, not architecture) `[giachanou_leveraging_2019]`.

## 2.3 Fake-news detection & datasets
- Fakeddit — large multimodally-labelled Reddit fake-news benchmark `[nakamura_fakeddit_2020]`; FakeNewsNet — news + social-context repository `[shu_fakenewsnet_2020]`.
- Fine-tuned transformers the current standard for text-based detection `[mouratidis_misinformation_2025 — VERIFY "best practice" claim; devlin_bert_2019]`.
- Weak supervision as a route to labels where none exist `[ratner_snorkel_2017; shu_early_2021]` (relevant to earlier UK weak-labelling exploration).

## 2.4 Political stance & leaning
- Trigger words in UK political discussion → higher engagement + animosity `[antypas_causal_2026]`.
- Zero-shot stance extraction from Reddit text `[togay_large_2026]`, built on entailment-based zero-shot classification `[yin_benchmarking_2019]` and LLM-based media assessment `[carvalho_automated_2026]`.
- Source bias / factual-reporting ratings predictable and operationalisable at scale `[baly_predicting_2018; sanchez-cortes_mapping_2024]`.

## 2.5 Explainable ML for misinformation
- SHAP — additive, game-theoretic attributions; TreeSHAP exact for tree models `[lundberg_unified_2017]`.
- Standard explainability tool for fake-news/hate-speech detection `[gongane_survey_2024]`, applied on gradient-boosted/RF misinformation models `[mouratidis_misinformation_2025; noauthor_pdf_2026 — Hashmi et al. 2024, fix metadata]`.

## 2.6 Research gap (synthesised)
- US/Twitter-centric literature; virality work rarely models *veracity as a feature*; no prior work on *UK political Reddit* virality → the space this project occupies.
- **[GAP — suggested additions in the "Additional papers" appendix: FACTOID, UKElectionNarratives, EmoLex/VADER/BERTopic/PR-AUC method cites.]**

---

# 3. Methodology

## 3.1 Requirements capture & analysis (what the system should do)
- **Primary objective:** given a Reddit post's content + metadata, predict whether it will go viral within its community, and *explain* which features drive that prediction.
- **Functional requirements:**
  - Ingest Reddit data (Fakeddit US; Pushshift UK) and produce a clean, feature-rich post-level dataset.
  - Define a principled, community-normalised virality target that is comparable across subreddits of different sizes.
  - Produce a veracity signal for each post (ground-truth for US; model-predicted proxy for UK).
  - Train and evaluate virality classifiers with explicit handling of class imbalance.
  - Produce per-feature explanations (SHAP) supporting RQ1–RQ3.
- **Non-functional / constraints:**
  - Must run within a limited GPU/compute budget (drives model-size and subsampling choices).
  - US→UK transfer must be *justified*, not assumed — a comparability analysis is a requirement, not an optional extra.
  - No data leakage: virality threshold and any fitted transforms derived from training data only.
- **Success criteria:** BERT veracity classifier competitive with the Fakeddit benchmark (~82%); virality models evaluated on imbalance-appropriate metrics (PR-AUC primary); interpretable SHAP output that answers the RQs.

## 3.2 Design (how the work is structured)
- **Two-pipeline architecture:**
  - **Pipeline A — Veracity classifier (BERT):** learns true/fake from Fakeddit; used (i) to establish the veracity feature on US data and (ii) to generate predicted veracity labels for UK data.
  - **Pipeline B — Virality predictor (tree ensembles + SHAP):** consumes structural, linguistic, emotional, political-leaning, credibility and veracity features to predict virality and explain it.
- **Cross-demographic comparability (design gate before transfer):** lexical, semantic and engagement-distribution comparisons establish that a semantic veracity model can transfer US→UK.
- **Data sources & corpora:**
  - **US (pipeline development): Fakeddit** `[nakamura_fakeddit_2020]`. Multimodal-only subset (human-written title + image) → filters platform noise, preserves benchmark parity. ~564k train / 59k val / 59k test.
  - **UK (target): Pushshift** `[baumgartner_pushshift_2020]` — r/ukpolitics, r/LabourUK, r/tories, r/reformuk, r/uknews (+ r/unitedkingdom present — **[DECISION: confirm final list]**), Jul–Sep 2024.
  - **[PLOT 1]** Post counts per subreddit (US & UK) / posts-per-month. **[PLOT 2]** Fakeddit label balance + true/fake split.
- **Cross-demographic comparability analysis** (notebook 01):
  - *Lexical:* Jensen–Shannon divergence on unigrams, raw vs entity-blinded (spaCy NER blinding of PERSON/NORP → generic tokens). Raw JSD high (country-specific vocab); blinding reduces it. **[VERIFY on more data — JSD > 0.5 on small sample.]** **[PLOT 3]** JSD raw vs blinded + vocab-intersection.
  - *Semantic:* sentence embeddings + UMAP → one shared "cloud" with country-specific corners (Trump/Brexit), not two clusters; domain-classifier cross-val accuracy as overlap measure. **[PLOT 4 — KEY]** UMAP US vs UK.
  - *Engagement shape:* log-score distributions right-skewed/log-normal in both; UK right-shifted with a low-engagement spike; after removing the spike, shapes align. Absolute thresholds differ (US top-20% ≈ 40; UK ≈ 154) but target is a *within-corpus percentile* → absolute differences don't affect transferability. **[PLOT 5 — KEY]** Log-engagement distributions, r/politics vs r/ukpolitics.
  - *Conclusion:* lexically distinct, semantically & behaviourally comparable → semantic (BERT) veracity transfer justified.

## 3.3 Implementation (techniques, problems, solutions)

### 3.3.1 Pipeline A — Veracity classifier (BERT)
- **Task:** 3-way Fakeddit label (0 true; 1 fake/true-text; 2 fake/false-text) `[nakamura_fakeddit_2020]`.
- **Baseline:** TF-IDF + logistic regression. Best (unweighted): **accuracy 0.77, weighted F1 0.78, macro F1 0.68.** class_weight=balanced improved fake recall but worsened all else (few strong lexical cues for fake diluted by equal weighting).
- **Main model:** `bert-base-uncased`, fine-tuned end-to-end `[devlin_bert_2019]`. Base vs large trades minimal performance for compute `[devlin_bert_2019 — VERIFY §5.2]`; uncased suits Reddit casing + Fakeddit lowercased titles.
- **Training:** grid over batch {16,32} × lr {2,3,5}e-5 `[devlin_bert_2019 — VERIFY App A.3]`; AdamW (β1 0.9, β2 0.999, ε 1e-6), weight decay 0.01, 10% warmup, dropout 0.1, mixed-precision GradScaler `[GAP: Micikevicius et al. 2018]`. Best **bs=32, lr=3e-5** (val macro-F1 0.866 @ epoch 2); full retrain → **val macro-F1 0.891**.
- **Problem/solution:** severe class imbalance (fake ~2.5%) → report **MCC** + per-class metrics, not just accuracy `[mouratidis_misinformation_2025 — VERIFY MCC-for-imbalance]`.

### 3.3.2 Pipeline B — Virality target construction (notebook 05)
- Raw engagement = `score + num_comments` `[chauhan_when_2025 — VERIFY the formula is actually in the text; else attribute to first principles]`.
- Size-normalisation (no subscriber counts → subreddit-median proxy, **own operationalisation**): `ln(raw+1)`, then within-subreddit z-score; clip negative raw to 0. Rationale: raw engagement power-law → log ≈ normal → z-scoring valid; within-subreddit z = "how many SDs above typical for this community?". Principle of community-size normalisation follows `[dogan_early_2026; barnes_dank_2021 — VERIFY Barnes's exact method]`; the log-z-within-subreddit formula is our own.
- **Threshold:** top-10% (90th percentile) of normalised engagement, **training set only**, applied unchanged to val/test (no leakage). z ≈ 1.36 (US) / 1.55 (UK).
- **Problem/solution — k-means rejected:** distribution unimodal → k=2 degenerates to a near-median split (would call ~55 raw engagement "viral"). Reverted to percentile thresholding, echoing Dogan's critique of arbitrary cut-offs while noting their *dynamic* hybrid-score approach is unavailable on static snapshots `[dogan_early_2026]`. **[DECISION: top-5% vs top-10% — sensitivity check.]** **[PLOT 8 — KEY]** raw power-law → normalised z + threshold.

### 3.3.3 Pipeline B — Feature engineering
- **Structural/temporal** `[barnes_dank_2021 — VERIFY exact feature set]`: title word count; hour-of-day (4h bins), day-of-week, is_weekend (US Central / GMT); has_image (native Fakeddit; engineered from URL for UK); caps ratio; punctuation densities (?, !, repeated) normalised by length (UK; stylometric, kept separate from VADER for explainability `[GAP: stylometry→engagement cite; or argue from first principles — antypas_negativity_2023 / solovev_moral_2022 cover broader emotion→virality]`).
- **Domain credibility:** MBFC bias + factual-reporting via Idiap dataset `[sanchez-cortes_mapping_2024; baly_predicting_2018]`, label-encoded (ordinal). ~92% sparsity (native/unrated) — limitation.
- **Psycholinguistic:** NRC EmoLex 8 emotions `[GAP: Mohammad & Turney 2013 — add]` + VADER compound `[GAP: Hutto & Gilbert 2014 — add]`. Implements **only** the publisher-emotion (lexicon + sentiment) part of dual-emotion `[zhang_mining_2021]` — no comment text → no social emotion (limitation). Motivation: emotion aids credibility `[giachanou_leveraging_2019]`; false content more emotionally charged `[noauthor_spread_nodate — Vosoughi; solovev_moral_2022]`. EmoLex word-level/context-blind (limitation).
- **Political leaning:** US — keyword density ratio (BART-MNLI dropped: US left/right unreliable + compute prohibitive on 564k). UK — trigger words + left/right keyword ratio `[antypas_causal_2026 — VERIFY the five trigger words are theirs]`; zero-shot BART-MNLI reserved for UK if compute allows `[togay_large_2026; yin_benchmarking_2019; carvalho_automated_2026]`. **[Planned, not done.]**
- **Veracity:** US — ground-truth binary `is_fake` `[nakamura_fakeddit_2020]`. UK — **BERT-predicted** `p_fake`/`p_true` from Pipeline A (no UK ground truth), *noisy cross-domain proxy* (limitation).
- **Engineered interaction:** `p_fake × is_low_credibility_domain` (own, to make interaction SHAP-readable).
- **[PLOT 9]** Emotion by veracity class (US) + Mann–Whitney effect sizes. **[PLOT 10]** Feature sparsity / Spearman correlation heatmap.

### 3.3.4 Pipeline B — Models, evaluation & explainability
- Baseline: Balanced Random Forest (imblearn) `[barnes_dank_2021 — VERIFY RF usage]`. Main: XGBoost with `scale_pos_weight` `[chen_xgboost_2016; dogan_early_2026 — VERIFY XGBoost]`. XGBoost over Barnes's gradient boosting for native imbalance handling, L1/L2 regularisation, speed `[chen_xgboost_2016]`.
- 5-fold CV, GridSearchCV; grid search on stratified 50k subsample (kernel/memory limits), then full retrain on best params.
- Metrics: **PR-AUC (primary), ROC-AUC, F1 @ optimal threshold, confusion matrix.** Accuracy rejected (all-0 dummy ≈ 90–91.5%) `[GAP: Saito & Rehmsmeier 2015; or lean on dogan_early_2026 / savatteri_veracity_2026]`.
- Explainability: **TreeSHAP** `[lundberg_unified_2017]`; global beeswarm + dependence + 4-way subgroup (viral/non-viral × fake/true) `[gongane_survey_2024]`.

---

# 4. Results

## 4.1 Experimental results — Pipeline A (veracity classifier)
- **Test: accuracy 0.895, macro-F1 0.890, MCC 0.793.** Per-class F1: 0.873 / 0.886 / 0.910. Meets/exceeds the ~82% Fakeddit benchmark `[nakamura_fakeddit_2020]`.
- **[PLOT 6]** BERT test confusion matrix (3×3, normalised). **[PLOT 7]** training curves (appendix).

## 4.2 Experimental results — Pipeline B, US / Fakeddit (baseline)
- **Weak model performance** — RF PR-AUC 0.149 / ROC-AUC 0.616; XGBoost PR-AUC 0.148 / ROC-AUC 0.609. Interpreted as a *dataset* property (Fakeddit image-driven; text+metadata carry little engagement signal), not model failure. **[PLOT 11]** US PR + ROC (RF vs XGB).
- **SHAP global:** `time_of_day` dominant (|SHAP| 0.325); **`is_fake` 2nd (0.127)**; `title_word_count` 3rd (0.076, brevity). Emotion weak; MBFC negligible (sparsity); has_image / is_weekend ≈ 0 (redundant/bug → drop). **[PLOT 12 — KEY]** US SHAP beeswarm.
- **Key direction (RQ2, US):** fake content *suppresses* virality (mean SHAP −0.168 fake vs +0.091 true) — on Fakeddit, true content more viral. Coherent given fake class ~85% image-manipulation/satire. **[PLOT 13]** `is_fake` SHAP dependence.
- **Subgroup (RQ3, US):** viral-fake and viral-true do **not** go viral for meaningfully different reasons — both driven by time and length; veracity a consistent suppressor, not a selective amplifier. **[PLOT 14]** subgroup SHAP.

## 4.3 Experimental results — Pipeline B, UK political Reddit (preliminary)
- Threshold z ≈ 1.55 (≈231 raw); 10.5% viral.
- **Domain:** external links far more viral than native (15% vs 3%, +11.3pp); polarised (right/right-centre) domains out-engage neutral; mixed-factuality out-engages high-factuality. **[PLOT 15]** virality rate by MBFC bias × factuality.
- **Emotion (viral vs non-viral, univariate):** viral posts significantly **more negative VADER** (−0.150 vs −0.037); anger +32%, fear +26%, disgust +31%, sadness +30% — consistent with `[antypas_negativity_2023; solovev_moral_2022]`. **[PLOT 16]** emotion viral vs non-viral (UK).
- **Model (structural features only; p_fake/topics not yet added):** XGBoost macro-F1 ≈ 0.50–0.53 at tuned threshold. **[PLOT 17]** UK PR/ROC.
- **SHAP (structural only):** `is_external_link` most important (news vs discussion); `word_count` (brevity); `caps_ratio` suppresses (likely spam/clickbait removed/downvoted); `vader_compound` *positive* → viral (counterintuitive); `q_density` suppresses; emotion near-zero; MBFC minimal (sparsity). **[PLOT 18 — KEY]** UK SHAP beeswarm (after p_fake). **[PLOT 19 — KEY]** US vs UK feature-importance comparison.

## 4.4 Evaluation & validation
- **Metric justification:** PR-AUC primary given ~10% positive class; accuracy misleading (dummy ≈ 90%). ROC-AUC + F1@threshold + confusion matrix as supporting views.
- **No-leakage validation:** threshold + transforms fit on train only, applied to val/test.
- **Transfer validation:** cross-demographic analysis (3.2) as the explicit check that US→UK transfer is legitimate.
- **[PLANNED — evaluation gaps to close, see §6]:** significance testing (Mann–Whitney + effect sizes), model-comparison CIs (bootstrap / DeLong), threshold sensitivity (5% vs 10%), and — critically — **validation of the transferred veracity classifier on a hand-labelled UK gold set** (currently unvalidated on UK).

---

# 5. Discussion & Conclusions

## 5.1 Critical analysis of findings
- **Veracity matters, even where the model is weak:** on US Fakeddit, `is_fake` is the 2nd most important feature despite poor overall model performance — content veracity carries signal for virality.
- **But direction is dataset-dependent:** veracity *suppresses* virality on Fakeddit — almost certainly because the fake class is ~85% image-manipulation/satire (a general meme corpus), not political misinformation. This is the central caveat of the US result and the reason the UK analysis exists.
- **UK structural signal is intuitive and coherent:** external news links, brevity, and (spam-suppressed) caps behave as theory predicts; the corpus behaves like a news-sharing community.
- **An unresolved tension:** univariate emotion analysis (viral = more negative/high-arousal) conflicts with multivariate SHAP (positive VADER → viral). Likely confounding — external news links are both positive-sentiment and viral. Must be resolved before strong emotion claims (partial-dependence check, §6).

## 5.2 Honest appraisal (limitations)
**Data & scope**
- Only 3 months of UK data → subreddit-level z-normalisation unstable for small communities (e.g. GreenPartyUK). Expected to smooth with more data.
- UK subreddit selection is a judgement call; limited external validity.
- Pushshift captures posts near creation → late-accruing engagement may be under-counted `[baumgartner_pushshift_2020]`.
- The 2024 window is partly a compute/scope decision.

**Veracity label (most significant)**
- UK `p_fake` is an **unvalidated cross-domain proxy** (US image-heavy Fakeddit → UK text-only politics). Large domain shift; treat all `p_fake` results with caution until validated on a UK gold set.
- Fakeddit's fake class composition makes the US "fake suppresses virality" result a weak comparator for political misinformation.

**Features**
- Only publisher emotion implemented; social-emotion half of dual-emotion `[zhang_mining_2021]` unavailable (no comment text).
- EmoLex word-level/context-blind.
- MBFC features ~92% sparse → weak signal.
- Stylometric (punctuation/caps) features lack a direct citation.
- Political-leaning & topic features **not yet in the UK model** → current UK results are structural-only and provisional.

**Modelling & interpretability**
- Weak US model performance (PR-AUC ≈ 0.15) → low baseline ceiling.
- Grid search on subsamples → possibly sub-optimal hyperparameters.
- SHAP explains the *model*, not ground truth; weak model ⇒ read attributions as "what the model used".

## 5.3 Conclusions
- A transferable, explainable virality pipeline has been built and validated US→UK at the comparability level; the veracity classifier is strong (test macro-F1 0.89).
- Preliminary evidence: veracity is a non-trivial virality signal, but its direction and rank are corpus-dependent — motivating the UK-specific analysis that is the project's core contribution.
- **[Complete after UK model finished:]** state the final answer to RQ2/RQ3 for UK political Reddit once `p_fake` + topics are in the model.

---

# 6. Future Work

## 6.1 The fake-news label — central open decision
- **(A) Keep Fakeddit-trained BERT, apply to UK as a noisy proxy (current plan).** Cheapest; classifier already strong. Needs honest caveats + UK gold-set validation. **Recommended default.**
- **(B) Validate/supplement with a UK-appropriate source:** FACTOID (Reddit political, credibility + bias labels; `[GAP: Sakketou et al. 2022 — add]`) and/or UKElectionNarratives (`[GAP: add]`) → build a UK gold test set / weak labels. Medium cost, big validity gain.
- **(C) Full swap of Fakeddit for a political dataset.** Highest cost (re-train Pipeline A, redo transfer analysis, lose benchmark parity). Only if time allows.
- **[DECISION — supervisor]** My steer: **A + B**.

## 6.2 Feature completion (UK)
- Add `p_fake`/`p_true` to the UK matrix (**the core cross-pipeline feature — currently missing**).
- BERTopic on UK train, applied to val/test `[GAP: Grootendorst 2022 — add]`; topic-segmented SHAP (do viral rates / the p_fake–virality relationship differ by topic?). **[PLOT 21]** virality & p_fake-SHAP by topic cluster.
- Finalise political-leaning method (keyword ratio vs Antypas triggers vs BART-MNLI).

## 6.3 Statistical significance testing (plan)
- Group differences (viral vs non-viral; fake vs true): Mann–Whitney U + **rank-biserial r** effect sizes (report effect size, not just p, given large n).
- Multicollinearity: VIF / Spearman heatmap before XGBoost (also helps the emotion tension).
- Model comparison: bootstrap CIs on PR-AUC/ROC-AUC (RF vs XGBoost); DeLong or bootstrap test for significance.
- Threshold sensitivity: re-run at 5% and 10%; check SHAP-ranking stability.
- Core RQ (US vs UK veracity effect): compare `p_fake`/`is_fake` SHAP rank + direction across corpora. **[DECISION: descriptive SHAP-rank comparison sufficient, or something inferential expected?]**

## 6.4 Interactive UI (stretch deliverable)
- Concept: paste a Reddit post/URL → extract features → predict virality probability → SHAP explanation of top contributors + short natural-language report.
- Value: demonstrates the pipeline end-to-end; makes explainability tangible.
- Feasibility: model + SHAP already exist; needs a feature-extraction wrapper + simple front-end (Streamlit/Gradio); `p_fake` needs the BERT checkpoint served.
- **[DECISION: dissertation scope or "future work" mention only? Must not displace core analysis + gold-set validation.]**

## 6.5 Robustness & extension
- Hand-label a UK gold test set to validate the transferred veracity classifier (**biggest current validity threat**).
- Load more months of UK data to stabilise small-subreddit normalisation.
- Extend to comment-level social emotion if comment text can be obtained (completes the dual-emotion framework).

---

# 7. References
*(Generate from Zotero. Fix the metadata/year issues below first.)*

**Zotero housekeeping (fix before generating references):**
- `noauthor_spread_nodate` → **Vosoughi, Roy & Aral (2018), *Science*** — add author/year.
- `noauthor_fake_nodate` → 2016-election Twitter *Science* paper (likely **Grinberg et al. 2019**) — identify/fix.
- `noauthor_uk_nodate` → UK GE 2024 survey — add author/publisher.
- `noauthor_pdf_2026` → **Hashmi et al. (2024)** FastText/Explainable-AI paper — fix.
- Many `date = 2026` are date-*added*, not publication year: Devlin 2019, Chen & Guestrin 2016, Barnes 2021, Zhang 2021, Lundberg 2017, Giachanou 2019, Yin 2019, Gongane 2024, Solovev 2022, Antypas (negativity) 2023, Nakamura 2020, etc. **Correct before citing.**

---

# Appendix A — Additional papers to add (credible, well-cited)
**Tool/method cites you currently lack (must add — you use these):**
- **Mohammad & Turney (2013)** — NRC EmoLex.
- **Hutto & Gilbert (2014)** — VADER.
- **Micikevicius et al. (2018)** — Mixed Precision Training (justifies GradScaler).
- **Grootendorst (2022)** — BERTopic (planned use).
- **Saito & Rehmsmeier (2015)** — PR-AUC on imbalance (anchors metric choice).
- **Tsur & Rappoport (2012)** — brevity/popularity (get source or drop claim).

**For the fake-news-label decision / UK domain:**
- **Sakketou et al. (2022), FACTOID** — contemporary Reddit political misinfo dataset (credibility + bias labels).
- **UKElectionNarratives (2025)** — UK election misinformation narratives (gold-set seed).

**Optional strengtheners:**
- Reddit-ranking-mechanism source (Salihefendic / Cornell INFO2040) — for the "why Reddit" claim.
- **Pennycook & Rand** — why people share misinformation (psychology anchor for the intro).
- **Lundberg et al. (2020, Nat. Mach. Intell.)** — TreeSHAP journal version (stronger exactness cite).

---

# Appendix B — Consolidated figure list

**KEY FIGURES** (carry the argument — prioritise):
- **PLOT 4** — UMAP US vs UK (transfer justification).
- **PLOT 5** — Log-engagement distributions (behavioural comparability).
- **PLOT 8** — Virality target construction (normalisation + threshold).
- **PLOT 12** — US SHAP beeswarm (`is_fake` 2nd).
- **PLOT 18** — UK SHAP beeswarm (where veracity ranks in UK politics).
- **PLOT 19** — US vs UK feature-importance comparison (central contribution).

| # | Section | Figure | Status |
|---|---|---|---|
| 1 | 3.2 | Post counts per subreddit / over time | data ready |
| 2 | 3.2 | Fakeddit label balance + true/fake split | data ready |
| 3 | 3.2 | JSD raw vs blinded + vocab intersection | data ready (small sample) |
| 4 | 3.2 | **UMAP US vs UK (KEY)** | data ready |
| 5 | 3.2 | **Log-engagement distributions (KEY)** | data ready |
| 6 | 4.1 | BERT test confusion matrix | data ready |
| 7 | 4.1 | BERT training curves (appendix) | data ready |
| 8 | 3.3.2 | **Virality target construction (KEY)** | data ready |
| 9 | 3.3.3 | Emotion by veracity class (US) + effect sizes | data ready |
| 10 | 3.3.3 | Feature sparsity / Spearman heatmap | to generate |
| 11 | 4.2 | US PR + ROC (RF vs XGB) | data ready |
| 12 | 4.2 | **US SHAP beeswarm (KEY)** | data ready |
| 13 | 4.2 | `is_fake` SHAP dependence (US) | data ready |
| 14 | 4.2 | Subgroup SHAP comparison (US) | data ready |
| 15 | 4.3 | Virality rate by domain credibility (UK) | data ready |
| 16 | 4.3 | Emotion viral vs non-viral (UK) | data ready |
| 17 | 4.3 | UK PR + ROC | data ready (update after p_fake) |
| 18 | 4.3 | **UK SHAP beeswarm (KEY)** | after p_fake + topics |
| 19 | 4.3 | **US vs UK feature-importance comparison (KEY)** | after UK model complete |
| 20 | 5.1 | VADER partial-dependence (resolve emotion tension) | to generate |
| 21 | 6.2 | Virality & p_fake-SHAP by BERTopic cluster | after topics |

**Presentation notes:** consistent colour scheme for true/fake and viral/non-viral across all figures; label SHAP axes with direction ("→ more viral"); training curves + JSD tables in an appendix to keep the main text on the six key figures.

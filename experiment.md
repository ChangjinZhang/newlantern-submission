# Experiment: Relevant Prior Study Prediction

## Goal

The goal is to decide whether each prior imaging study should be shown to the radiologist when reviewing the current study. The API receives a current study and a list of prior studies, then returns a boolean prediction for each prior study.

## Method

I implemented a lightweight rule-based baseline. The model extracts information from study descriptions, including body region and imaging modality. It predicts a prior study as relevant when:

1. The current and prior study share the same body region, such as brain, chest, abdomen, spine, breast, heart, knee, or shoulder.
2. Or they share the same modality and have enough overlapping medical description terms.
3. Or their token similarity is high enough based on a Jaccard-style overlap score.

This approach is simple, deterministic, fast, and easy to debug. It does not require any external LLM API calls, so the endpoint is stable and inexpensive to run.

## What worked

The body-region matching rule works well for common cases because radiologists usually care most about prior studies from the same anatomical area. For example, a current brain MRI is likely to be related to a previous brain MRI or CT head. The modality and keyword-overlap fallback also helps when the body region is not explicitly detected.

## What did not work

The rule-based system can miss relevant studies when the description uses uncommon abbreviations or does not clearly mention the body part. It can also incorrectly mark two studies as relevant if they share general words but are clinically different. The system does not deeply understand clinical context, diagnosis history, or temporal progression.

## Future improvements

A stronger version would combine these rules with an LLM or a trained classifier. The LLM could compare the current study and each prior study with a structured prompt and return true or false. I would also add more anatomy synonyms, modality normalization, and validation on hidden examples to tune the similarity threshold.

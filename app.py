from flask import Flask, request, jsonify
import re

app = Flask(__name__)

BODY_PARTS = {
    "brain": ["brain", "head", "skull", "intracranial", "mri brain", "ct head", "脑", "头"],
    "chest": ["chest", "thorax", "lung", "lungs", "pulmonary", "cxr", "胸", "肺"],
    "abdomen": ["abdomen", "abdominal", "pelvis", "liver", "kidney", "renal", "肝", "肾", "腹", "盆腔"],
    "spine": ["spine", "cervical", "thoracic spine", "lumbar", "vertebra", "脊柱", "腰椎", "颈椎"],
    "breast": ["breast", "mammogram", "mammography", "乳腺"],
    "heart": ["heart", "cardiac", "coronary", "心脏", "冠脉"],
    "knee": ["knee", "膝"],
    "shoulder": ["shoulder", "肩"],
}

MODALITIES = {
    "mri": ["mri", "mr ", "magnetic resonance", "核磁", "磁共振"],
    "ct": ["ct", "computed tomography", "cta", "cta ", "ct ", "增强ct"],
    "xray": ["xray", "x-ray", "radiograph", "cxr", "片"],
    "ultrasound": ["ultrasound", "us ", "sonogram", "超声", "b超"],
    "pet": ["pet", "pet/ct"],
}

STOPWORDS = set("the a an and or of for with without to in on by from exam study contrast prior current".split())


def text_of(study):
    if not isinstance(study, dict):
        return ""
    values = []
    for key in ["study_description", "description", "modality", "body_part", "study_date"]:
        if key in study and study[key] is not None:
            values.append(str(study[key]))
    return " ".join(values).lower()


def tokenize(text):
    return {t for t in re.findall(r"[a-zA-Z0-9]+", text.lower()) if len(t) > 2 and t not in STOPWORDS}


def detect_group(text, groups):
    hits = set()
    low = f" {text.lower()} "
    for group, words in groups.items():
        for w in words:
            if w.lower() in low:
                hits.add(group)
                break
    return hits


def is_relevant(current_study, prior_study):
    current_text = text_of(current_study)
    prior_text = text_of(prior_study)

    if not current_text or not prior_text:
        return False

    current_body = detect_group(current_text, BODY_PARTS)
    prior_body = detect_group(prior_text, BODY_PARTS)
    current_modality = detect_group(current_text, MODALITIES)
    prior_modality = detect_group(prior_text, MODALITIES)

    # Strong signal: same body region. Modality may differ, but prior can still help.
    if current_body and prior_body and current_body & prior_body:
        return True

    # Medium signal: same modality plus enough shared medical terms.
    cur_tokens = tokenize(current_text)
    prior_tokens = tokenize(prior_text)
    overlap = cur_tokens & prior_tokens
    if current_modality and prior_modality and current_modality & prior_modality and len(overlap) >= 2:
        return True

    # Fallback: Jaccard similarity over descriptions.
    union = cur_tokens | prior_tokens
    if union:
        similarity = len(overlap) / len(union)
        if similarity >= 0.25 and len(overlap) >= 2:
            return True

    return False


def get_cases(payload):
    # Browser translation may show this as “案例”; the real API usually uses cases.
    return payload.get("cases") or payload.get("病例") or payload.get("案例") or []


def get_current_study(case):
    return case.get("current_study") or case.get("当前检查") or {}


def get_prior_studies(case):
    return case.get("prior_studies") or case.get("prior_exams") or case.get("历史检查") or []


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "message": "POST JSON to /predict"})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/predict", methods=["POST"])
def predict():
    payload = request.get_json(force=True, silent=True) or {}
    predictions = []

    for case in get_cases(payload):
        case_id = str(case.get("case_id", ""))
        current = get_current_study(case)
        for prior in get_prior_studies(case):
            study_id = str(prior.get("study_id", ""))
            predictions.append({
                "case_id": case_id,
                "study_id": study_id,
                "predicted_is_relevant": bool(is_relevant(current, prior)),
            })

    return jsonify({"predictions": predictions})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

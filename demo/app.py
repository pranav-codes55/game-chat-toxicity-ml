"""Streamlit demo: Classifying Sentiment in PvP Game Communications.

UE24CS352A - Machine Learning Mini-Project | Team 24
Replicating and extending Borst, Yang, Zhu (Stanford, 2021).
"""

import html, json, re
from pathlib import Path

import joblib
import numpy as np
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / "models"

CLASSES = ["Neutral / positive", "Negative attitude", "Derogatory"]


def clean_text(s):
    s = html.unescape(str(s)).lower()
    s = re.sub(r"https?://\S+", " ", s)
    s = re.sub(r"[\u2019'`]", "", s)
    s = re.sub(r"(.)\1{2,}", r"\1\1", s)
    s = re.sub(r"[^a-z0-9?! ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


@st.cache_resource
def load_models():
    out = {}
    if (MODELS / "best_tfidf_model.joblib").exists():
        meta = json.load(open(MODELS / "best_tfidf_meta.json"))
        out["tfidf"] = (
            meta.get("name", "Random Forest (Gini)"),
            joblib.load(MODELS / "tfidf_vectorizer.joblib"),
            joblib.load(MODELS / "best_tfidf_model.joblib")
        )
    if (MODELS / "lstm_best.keras").exists():
        import tensorflow as tf
        meta = json.load(open(MODELS / "lstm_meta.json"))
        vocab_meta = json.load(open(MODELS / "emb" / "vocab.json"))
        out["lstm"] = (
            meta.get("name", "LSTM (GloVe 50-dim)"),
            tf.keras.models.load_model(MODELS / "lstm_best.keras"),
            vocab_meta["vocab"],
            vocab_meta["max_len"]
        )
    return out


def predict_tfidf(bundle, text):
    _, vec, model = bundle
    X = vec.transform([clean_text(text)])
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)[0]
    p = np.zeros(3)
    p[int(model.predict(X)[0])] = 1.0
    return p


def predict_lstm(bundle, text):
    _, model, vocab, max_len = bundle
    tokens = re.findall(r"[a-z0-9]+|[?!]", clean_text(text))
    ids = [vocab.get(w, 1) for w in tokens][:max_len]
    x = np.zeros((1, max_len), dtype="int32")
    x[0, :len(ids)] = ids
    p = model.predict(x, verbose=0)[0]
    s = p.sum()
    return p / s if s > 0 else np.array([0.33, 0.33, 0.33])


def display_prediction(title, subtitle, probs):
    k = int(np.argmax(probs))
    pred_label = CLASSES[k]
    confidence = probs[k]

    st.subheader(title)
    st.caption(subtitle)

    # Clean native callout matching the predicted sentiment
    if k == 0:
        st.success(f"**Prediction:** {pred_label} ({confidence:.1%})")
    elif k == 1:
        st.warning(f"**Prediction:** {pred_label} ({confidence:.1%})")
    else:
        st.error(f"**Prediction:** {pred_label} ({confidence:.1%})")

    st.write("**Class probabilities:**")
    for cls_name, prob in zip(CLASSES, probs):
        st.progress(float(prob), text=f"{cls_name}: {prob:.1%}")


# --- Streamlit Layout ---
st.set_page_config(
    page_title="Game Chat Sentiment Classifier",
    page_icon="💬",
    layout="wide"
)

# Sidebar with genuine project information
with st.sidebar:
    st.header("Project details")
    st.write("**Course:** UE24CS352A - Machine Learning Mini-Project")
    st.write("**Team:** Section C | Team 24 | Project 51")
    st.write("**Members:** Divyanshi Verma & R P Pranav")

    st.divider()
    st.subheader("Problem statement")
    st.write(
        "Replicate and extend *'Trolls, Haters, or Teammates'* (Stanford, 2021) "
        "to classify PvP game chat messages from Dota 2 and League of Legends into "
        "three categories: neutral/positive, negative attitude, or derogatory."
    )

    st.subheader("Dataset")
    st.write("- **Total labelled:** 1,979 messages")
    st.write("- **Split:** 80% train (1,583) / 20% test (396)")
    st.write("- **Agreement:** 76.3% accuracy, 0.643 Cohen's kappa on 97 audited messages")
    st.write("- **Class share:** Neutral 56.0%, Negative 36.9%, Derogatory 7.1%")

    st.divider()
    st.caption("Reference: Borst, Yang, Zhu (Stanford University, 2021).")

# Main Page Header
st.title("Game Chat Sentiment & Toxicity Classifier")
st.write(
    "Given an in-game chat message, this tool compares how our best classical model "
    "(Random Forest on TF-IDF) and sequence neural network (LSTM on word embeddings) classify it."
)

models = load_models()
if not models:
    st.error("No trained models found in the models/ folder. Run notebooks 03 and 06 first.")
    st.stop()

st.divider()

# Sample prompt buttons with callback so clicking updates input immediately
def set_sample(text):
    st.session_state.chat_input = text

if "chat_input" not in st.session_state:
    st.session_state.chat_input = "report mid he is feeding"

st.write("**Click an example to test:**")
samples = [
    "ggwp",
    "report mid he is feeding",
    "noob team uninstall the game",
    "nice save, thanks!",
    "you are a worthless retard"
]

sample_cols = st.columns(len(samples))
for i, sample in enumerate(samples):
    sample_cols[i].button(
        sample,
        key=f"sample_btn_{i}",
        on_click=set_sample,
        args=(sample,),
        use_container_width=True
    )

user_text = st.text_input(
    "Or type your own chat message:",
    key="chat_input",
    placeholder="e.g. gg wp push mid"
)

# Predictions
if user_text.strip():
    st.write("---")
    col1, col2 = st.columns(2)

    with col1:
        if "tfidf" in models:
            p_tfidf = predict_tfidf(models["tfidf"], user_text)
            display_prediction(
                title="Random Forest (TF-IDF)",
                subtitle=f"{models['tfidf'][0]} · Best overall (Test accuracy: 90.15%, Macro-F1: 0.825)",
                probs=p_tfidf
            )

    with col2:
        if "lstm" in models:
            p_lstm = predict_lstm(models["lstm"], user_text)
            display_prediction(
                title="LSTM (Word Embeddings)",
                subtitle=f"{models['lstm'][0]} · Sequence model (Test accuracy: 83.84%, Macro-F1: 0.712)",
                probs=p_lstm
            )
else:
    st.info("Please enter a chat message above or click one of the examples.")

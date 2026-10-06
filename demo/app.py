"""Streamlit demo: type an in-game chat message and see how our models classify it.

Run from the project root:   streamlit run demo/app.py

Needs the files created by notebooks 03 and 06 in models/.
"""

import html, json, re
from pathlib import Path

import joblib
import numpy as np
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / "models"
CLASSES = ["neutral / positive", "negative attitude", "derogatory"]
COLORS = ["#2e8b57", "#d98c1f", "#c0392b"]


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
        out["tfidf"] = (meta["name"], joblib.load(MODELS / "tfidf_vectorizer.joblib"), joblib.load(MODELS / "best_tfidf_model.joblib"))
    if (MODELS / "lstm_best.keras").exists():
        import tensorflow as tf
        meta = json.load(open(MODELS / "lstm_meta.json"))
        vocab_meta = json.load(open(MODELS / "emb" / "vocab.json"))
        out["lstm"] = (meta["name"], tf.keras.models.load_model(MODELS / "lstm_best.keras"), vocab_meta["vocab"], vocab_meta["max_len"])
    return out


def predict_tfidf(bundle, text):
    _, vec, model = bundle
    X = vec.transform([clean_text(text)])
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)[0]
    p = np.zeros(3); p[int(model.predict(X)[0])] = 1.0
    return p


def predict_lstm(bundle, text):
    _, model, vocab, max_len = bundle
    ids = [vocab.get(w, 1) for w in re.findall(r"[a-z0-9]+|[?!]", clean_text(text))][:max_len]
    x = np.zeros((1, max_len), dtype="int32"); x[0, :len(ids)] = ids
    p = model.predict(x, verbose=0)[0]
    return p / p.sum()


def show(title, name, probs):
    k = int(np.argmax(probs))
    st.markdown(f"**{title}**  \n<small>{name}</small>", unsafe_allow_html=True)
    st.markdown(f"<div style='padding:10px;border-radius:8px;background:{COLORS[k]};color:white;font-size:18px'>{CLASSES[k]}</div>", unsafe_allow_html=True)
    for c, pr in zip(CLASSES, probs):
        st.progress(float(pr), text=f"{c}: {pr:.0%}")


st.set_page_config(page_title="Game chat toxicity classifier", page_icon="🎮")
st.title("🎮 Game chat toxicity classifier")
st.caption("UE24CS352A ML mini-project - based on 'Trolls, Haters, or Teammates' (Borst, Yang, Zhu). Classes: neutral/positive, negative attitude, derogatory.")

models = load_models()
if not models:
    st.error("No trained models found in the models/ folder. Run notebooks 03 and 06 first.")
    st.stop()

examples = ["ggwp", "report mid he is feeding", "noob team uninstall the game", "nice save, thanks!", "you are a worthless retard"]
if "msg" not in st.session_state:
    st.session_state.msg = ""
cols = st.columns(len(examples))
for c, ex in zip(cols, examples):
    if c.button(ex, use_container_width=True):
        st.session_state.msg = ex
msg = st.text_input("Type a chat message", key="msg", placeholder="e.g. gg wp")

if msg.strip():
    cols = st.columns(len(models))
    for col, (key, bundle) in zip(cols, models.items()):
        with col:
            if key == "tfidf":
                show("TF-IDF model", bundle[0], predict_tfidf(bundle, msg))
            else:
                show("LSTM model", bundle[0], predict_lstm(bundle, msg))

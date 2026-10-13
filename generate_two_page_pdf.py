"""
Generate an open, uncramped, humanized 2-page project summary PDF.
- Standard comfortable font size (9.5pt body, 13.5pt leading)
- Clean, open spacing between sections
- Simplified, readable tables (matching the student's original docx)
- No cramped margins or dense text blocks
- Simple black/dark-gray styling, no fancy shading
- Exactly 2 pages
"""

import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas
import pypdf
import pymupdf

class SimplePageCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Times-Roman", 9)
        self.setFillColor(colors.HexColor("#444444"))
        # Just a clean centered page number at the bottom, no lines or extra text
        self.drawCentredString(297.6, 25, str(self._pageNumber))
        self.restoreState()


def build_pdf(filename="One_Page_Writeup.pdf"):
    # Generous margins: 40pt left/right, 32pt top, 40pt bottom
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=32,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    
    # Typography: comfortable, readable, standard academic sizes
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.black,
        alignment=1, # Center
        spaceAfter=3
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Times-Italic',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#222222"),
        alignment=1,
        spaceAfter=5
    )

    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=8.5,
        leading=12,
        textColor=colors.black,
        alignment=1,
        spaceAfter=8
    )

    sec_hdr_style = ParagraphStyle(
        'SecHdr',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.black,
        spaceBefore=7,
        spaceAfter=3
    )

    body_style = ParagraphStyle(
        'BodyTxt',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9.2,
        leading=13.0,
        textColor=colors.black,
        spaceAfter=4,
        alignment=4 # Justified
    )

    bullet_style = ParagraphStyle(
        'BulletTxt',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9.0,
        leading=12.6,
        textColor=colors.black,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3.5
    )

    tbl_hdr = ParagraphStyle(
        'TblHdr',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=8.5,
        leading=11.0,
        textColor=colors.black,
        alignment=1
    )

    tbl_body = ParagraphStyle(
        'TblBody',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=8.5,
        leading=11.0,
        textColor=colors.black,
        alignment=1
    )

    tbl_body_left = ParagraphStyle(
        'TblBodyLeft',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=8.5,
        leading=11.0,
        textColor=colors.black,
        alignment=0
    )

    tbl_cap = ParagraphStyle(
        'TblCap',
        parent=styles['Normal'],
        fontName='Times-Italic',
        fontSize=8.0,
        leading=10.5,
        textColor=colors.HexColor("#333333"),
        alignment=1,
        spaceBefore=3,
        spaceAfter=5
    )

    meta_box_txt = ParagraphStyle(
        'MetaBoxTxt',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=8.0,
        leading=10.5,
        textColor=colors.black
    )

    story = []

    # ================= PAGE 1 =================
    story.append(Paragraph("Classifying Sentiment in the Language of PvP Game Communications", title_style))
    story.append(Paragraph("Replication and Extension of Borst, Yang, Zhu (Stanford University, 2021)", subtitle_style))
    
    meta_text = (
        "<b>UE24CS352A Machine Learning Mini-Project</b> &nbsp;|&nbsp; Section C &nbsp;|&nbsp; Team 24 &nbsp;|&nbsp; Project 51<br/>"
        "<b>Students:</b> Divyanshi Verma (PES2UG24CS161) &nbsp;·&nbsp; R P Pranav (PES2UG24CS917) &nbsp;|&nbsp; PES University<br/>"
        "<b>Code:</b> https://github.com/pranav-codes55/game-chat-toxicity-ml"
    )
    story.append(Paragraph(meta_text, meta_style))
    story.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#555555"), spaceAfter=6, spaceBefore=0))

    # 1. Problem Statement
    story.append(Paragraph("1. Problem Statement", sec_hdr_style))
    p1 = (
        "In competitive online games like Dota 2 and League of Legends, player chat is fast-paced, highly informal, "
        "and frequently toxic. Moderating in-game chat is difficult because players rely heavily on game-specific slang "
        "(such as <i>'ff'</i>, <i>'diff'</i>, <i>'feeder'</i>), creative misspellings to bypass profanity filters, and sarcastic flame. "
        "Standard sentiment analysis tools trained on formal text fail in this setting. Following the Stanford study by "
        "Borst, Yang, and Zhu (2021), this project classifies single in-game chat messages into three categories: "
        "<b>0 - neutral / positive</b> (tactical calls, praise, e.g., <i>'gg wp'</i>, <i>'push mid'</i>), "
        "<b>1 - negative attitude</b> (whining, blaming teammates, giving up, e.g., <i>'report mid he is feeding'</i>), and "
        "<b>2 - derogatory</b> (hate speech, slurs, severe targeted harassment). "
        "We compare classical machine learning models on TF-IDF features with neural networks trained on word2vec and GloVe embeddings."
    )
    story.append(Paragraph(p1, body_style))

    # 2. Dataset Details
    story.append(Paragraph("2. Dataset Details", sec_hdr_style))
    p2 = (
        "Because the Stanford paper's labelled data is private, we built our own dataset from the two public sources cited in the paper: "
        "<b>GOSU.AI Dota 2 game chats</b> and <b>League of Legends Tribunal chat logs</b> from Kaggle (~1 million messages each). "
        "Our data preparation pipeline involved:"
    )
    story.append(Paragraph(p2, body_style))

    b1 = "• <b>Cleaning & Filtering:</b> Repaired encoding issues in the Dota logs, removed non-English and Russian text, removed URLs, and shortened repeated characters (e.g., <i>'noooob'</i> &rarr; <i>'noob'</i>). Punctuation marks (<i>'?'</i>, <i>'!'</i>) were preserved as sentiment indicators. This yielded <b>605,771 unique English messages</b>."
    b2 = "• <b>Sampling Candidates:</b> Random chat contains less than 1% derogatory messages. To ensure all three classes appear in sufficient numbers, we sampled <b>3,400 candidate messages</b> using a stratified mix: 1,600 random messages, 800 lexicon-matched messages, 600 containing strong insult terms, and 400 from reported tribunal cases."
    b3 = "• <b>Labelling & Human Audit:</b> We labelled the first 2,000 candidates using an LLM assistant following written rules. To verify label quality, 97 messages were independently hand-checked blind to the AI labels. The AI agreed with human labels on <b>76.3% of messages (Cohen's kappa = 0.643)</b>, showing substantial agreement. We corrected 26 mislabelled cases based on the manual audit."
    b4 = "• <b>Final Dataset:</b> After removing 21 invalid fragments, the final dataset has <b>1,979 messages</b>: 56.0% neutral/positive (1,108), 36.9% negative attitude (730), and 7.1% derogatory (141). We split this 80/20 into <b>1,583 training</b> and <b>396 test messages</b> using stratified sampling."
    story.append(Paragraph(b1, bullet_style))
    story.append(Paragraph(b2, bullet_style))
    story.append(Paragraph(b3, bullet_style))
    story.append(Paragraph(b4, bullet_style))

    # 3. Approach
    story.append(Paragraph("3. Approach", sec_hdr_style))
    p3 = (
        "We tested four feature representations across classical and neural models:<br/>"
        "• <b>TF-IDF:</b> Unigrams and bigrams, sublinear TF scaling, max 3,000 features. Stop words were kept because pronouns (<i>'you'</i>, <i>'i'</i>) and negations (<i>'not'</i>) are essential for identifying personal attacks.<br/>"
        "• <b>165-Phrase Dictionary:</b> Counts of domain toxic phrases from the Stanford paper's curated lexicon.<br/>"
        "• <b>word2vec:</b> Skip-Gram embeddings (50 and 100 dimensions) trained on 200,000 unlabelled chat messages from our corpus.<br/>"
        "• <b>GloVe:</b> Pre-trained 50 and 100-dimensional embeddings from Wikipedia and Gigaword news text."
    )
    story.append(Paragraph(p3, body_style))

    # Table 1: Embedding coverage (clean booktabs)
    cov_data = [
        [Paragraph("<b>Embedding</b>", tbl_hdr), Paragraph("<b>Dimension</b>", tbl_hdr), Paragraph("<b>Vocab Words Found</b>", tbl_hdr), Paragraph("<b>Word Occurrences</b>", tbl_hdr), Paragraph("<b>Nearest Neighbors of 'feeder'</b>", tbl_hdr)],
        [Paragraph("word2vec (our chat data)", tbl_body_left), Paragraph("50 / 100", tbl_body), Paragraph("99.6 %", tbl_body), Paragraph("99.9 %", tbl_body), Paragraph("<i>idiot, flamer, noob, troll, retard</i>", tbl_body_left)],
        [Paragraph("GloVe (Wikipedia / news)", tbl_body_left), Paragraph("50 / 100", tbl_body), Paragraph("93.7 %", tbl_body), Paragraph("97.8 %", tbl_body), Paragraph("<i>hogs, cattle, calves, animals</i>", tbl_body_left)],
    ]
    cov_tbl = Table(cov_data, colWidths=[125, 55, 90, 85, 160])
    cov_tbl.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,0), 1.0, colors.black),
        ('LINEBELOW', (0,0), (-1,0), 0.5, colors.black),
        ('LINEBELOW', (0,-1), (-1,-1), 1.0, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 3.0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.0),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(cov_tbl)
    story.append(Paragraph("Table 1. Vocabulary coverage on our test set and nearest neighbours of 'feeder'.", tbl_cap))

    p3_models = (
        "<b>Models evaluated:</b> (1) <i>Binary SVM baseline</i> (linear, RBF, polynomial) to test neutral vs. toxic separation; "
        "(2) <i>Classical models on TF-IDF</i>: Naive Bayes, KNN (K = 1, 2, 3, 6), and Random Forest (Gini, entropy, depth limit 32); "
        "(3) <i>Feedforward neural networks</i> with 1–2 dense layers (64 and 32 units) over average word vectors; and "
        "(4) <i>LSTMs</i> with 64 units, 20% dropout, padded to 30 words, with softmax and sigmoid output heads."
    )
    story.append(Paragraph(p3_models, body_style))

    # ================= PAGE BREAK =================
    story.append(PageBreak())

    # ================= PAGE 2 =================
    # 4. Implementation Overview
    story.append(Paragraph("4. Brief Overview of Implementation", sec_hdr_style))
    p4 = (
        "The project is implemented in Python using pandas, scikit-learn, gensim, and TensorFlow/Keras across seven "
        "reproducible notebooks (data preparation, labelling/audit/split, TF-IDF models, embeddings, feedforward NN, LSTM, and evaluation). "
        "To prevent data leakage, TF-IDF vectorizers and vocabulary tables were fitted strictly on the training set, and duplicates were removed before splitting. "
        "All 12 feedforward and 8 LSTM networks were trained using the Adam optimizer (learning rate 0.001), batch size 64, a 20% validation split for early stopping "
        "(patience 8–10, max 100 epochs), and random seed 42. "
        "We also built an interactive Streamlit demo (<code>demo/app.py</code>) that allows users to type any chat message and view class predictions "
        "and probability breakdowns from both the best TF-IDF model and an LSTM."
    )
    story.append(Paragraph(p4, body_style))

    # Results Table: Focused, clean benchmark table (matching the student's original docx Table 1)
    story.append(Paragraph("Experimental Results", sec_hdr_style))
    res_data = [
        [Paragraph("<b>Model</b>", tbl_hdr), Paragraph("<b>Features</b>", tbl_hdr), Paragraph("<b>Accuracy</b>", tbl_hdr), Paragraph("<b>Macro-F1</b>", tbl_hdr), Paragraph("<b>F1 Derogatory</b>", tbl_hdr), Paragraph("<b>Paper Acc.</b>", tbl_hdr), Paragraph("<b>Difference</b>", tbl_hdr)],
        [Paragraph("Binary SVM (linear)*", tbl_body_left), Paragraph("TF-IDF", tbl_body), Paragraph("0.9217", tbl_body), Paragraph("0.9193", tbl_body), Paragraph("—", tbl_body), Paragraph("0.9565", tbl_body), Paragraph("-0.0348", tbl_body)],
        [Paragraph("Naive Bayes (165-phrase dict)", tbl_body_left), Paragraph("Dictionary", tbl_body), Paragraph("0.8662", tbl_body), Paragraph("0.7075", tbl_body), Paragraph("0.3529", tbl_body), Paragraph("—", tbl_body), Paragraph("—", tbl_body)],
        [Paragraph("Naive Bayes (TF-IDF)", tbl_body_left), Paragraph("TF-IDF", tbl_body), Paragraph("0.8308", tbl_body), Paragraph("0.7513", tbl_body), Paragraph("0.5778", tbl_body), Paragraph("0.9506", tbl_body), Paragraph("-0.1198", tbl_body)],
        [Paragraph("KNN (K = 1)", tbl_body_left), Paragraph("TF-IDF", tbl_body), Paragraph("0.6894", tbl_body), Paragraph("0.5846", tbl_body), Paragraph("0.4186", tbl_body), Paragraph("0.9853", tbl_body), Paragraph("-0.2959", tbl_body)],
        [Paragraph("<b>Random Forest (Gini) [Best]</b>", tbl_body_left), Paragraph("TF-IDF", tbl_body), Paragraph("<b>0.9015</b>", tbl_body), Paragraph("<b>0.8247</b>", tbl_body), Paragraph("<b>0.6512</b>", tbl_body), Paragraph("0.9912", tbl_body), Paragraph("-0.0897", tbl_body)],
        [Paragraph("Random Forest (Entropy)", tbl_body_left), Paragraph("TF-IDF", tbl_body), Paragraph("0.8990", tbl_body), Paragraph("0.8226", tbl_body), Paragraph("0.6512", tbl_body), Paragraph("0.9910", tbl_body), Paragraph("-0.0920", tbl_body)],
        [Paragraph("Feedforward NN (ReLU, Sig, Soft)", tbl_body_left), Paragraph("GloVe 100", tbl_body), Paragraph("0.8182", tbl_body), Paragraph("0.7121", tbl_body), Paragraph("0.4783", tbl_body), Paragraph("0.9572", tbl_body), Paragraph("-0.1390", tbl_body)],
        [Paragraph("<b>LSTM (softmax head) [Best NN]</b>", tbl_body_left), Paragraph("word2vec 100", tbl_body), Paragraph("<b>0.8434</b>", tbl_body), Paragraph("<b>0.7226</b>", tbl_body), Paragraph("<b>0.4545</b>", tbl_body), Paragraph("0.9586", tbl_body), Paragraph("-0.1152", tbl_body)],
        [Paragraph("LSTM (softmax head)", tbl_body_left), Paragraph("GloVe 50", tbl_body), Paragraph("0.8384", tbl_body), Paragraph("0.7123", tbl_body), Paragraph("0.4255", tbl_body), Paragraph("—", tbl_body), Paragraph("—", tbl_body)],
    ]
    res_tbl = Table(res_data, colWidths=[140, 75, 55, 55, 65, 60, 65])
    res_tbl.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,0), 1.0, colors.black),
        ('LINEBELOW', (0,0), (-1,0), 0.5, colors.black),
        ('LINEBELOW', (0,-1), (-1,-1), 1.0, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 2.8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.8),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(res_tbl)
    story.append(Paragraph("Table 2. Test performance on 396 held-out messages (*SVM evaluated on binary neutral vs. toxic task).", tbl_cap))

    # 5. Conclusions
    story.append(Paragraph("5. Conclusions", sec_hdr_style))
    c1 = (
        "• <b>TF-IDF Models Outperformed Neural Networks:</b> As in the Stanford paper, Random Forest on TF-IDF achieved the highest accuracy "
        "(<b>0.9015</b>) and macro-F1 (<b>0.8247</b>), beating the best LSTM (0.8434 accuracy, 0.7226 macro-F1) by 5.8% accuracy and 10.2% macro-F1. "
        "In fast-paced PvP chat, messages are very short (typically 5 to 8 words). Explicit keywords like <i>'report'</i>, <i>'noob'</i>, or slurs "
        "provide strong linear and tree split signals, allowing decision trees to separate classes effectively without the high parameter count or sample hunger of neural networks."
    )
    c2 = (
        "• <b>In-Domain word2vec vs. Pre-trained GloVe:</b> Our chat-trained word2vec embeddings captured game terminology much better "
        "(99.9% token coverage) than news-trained GloVe (97.8%). GloVe's nearest neighbours for <i>'feeder'</i> were agricultural terms (<i>'cattle'</i>, <i>'hogs'</i>), "
        "whereas word2vec correctly clustered it with <i>'flamer'</i> and <i>'idiot'</i>. Consequently, models on word2vec achieved higher accuracies than those on GloVe."
    )
    c3 = (
        "• <b>LSTM vs. Feedforward Networks:</b> LSTMs outperformed feedforward networks across every embedding setup by 1.8 to 4.0 accuracy points. "
        "This confirms that processing word order sequentially is beneficial, whereas feedforward networks lose word order by averaging vectors."
    )
    c4 = (
        "• <b>Difficulty of the Derogatory Class:</b> Because derogatory messages make up only 7.1% of the dataset (28 test instances), "
        "F1-scores on Class 2 were lower across all models (0.6512 for Random Forest, and below 0.46 for neural networks). Models handled neutral and "
        "negative attitude messages reliably (F1 0.87–0.93), but subtle insults and toxic sarcasm without explicit profanity were frequently misclassified."
    )
    c5 = (
        "• <b>Comparison with Stanford Paper:</b> Our accuracies are lower than the paper's reported numbers (e.g., 90.15% vs. 99.12% for Random Forest; "
        "68.94% vs. 98.53% for KNN). The paper trained on approximately 33,000 messages (compared to our 1,979) and likely used cleaner or artificially balanced data. "
        "Our results reflect realistic performance on unconstrained, noisy game logs."
    )
    story.append(Paragraph(c1, bullet_style))
    story.append(Paragraph(c2, bullet_style))
    story.append(Paragraph(c3, bullet_style))
    story.append(Paragraph(c4, bullet_style))
    story.append(Paragraph(c5, bullet_style))

    # Team Contributions & Reference (Clean unshaded box)
    story.append(Spacer(1, 3))
    contrib_data = [
        [
            Paragraph("<b>Team Contributions:</b><br/>"
                      "• <b>R P Pranav (PES2UG24CS917):</b> Data collection, cleaning and candidate sampling, AI labelling rules, manual audit, label merging, train/test split, and TF-IDF models (SVM, Naive Bayes, KNN, Random Forest).<br/>"
                      "• <b>Divyanshi Verma (PES2UG24CS161):</b> word2vec & GloVe embeddings, feedforward networks, LSTM neural models, evaluation metrics, confusion matrices, comparison with the paper, and Streamlit demo.", meta_box_txt),
            Paragraph("<b>Reference & Deliverables:</b><br/>"
                      "• <b>Reference:</b> Borst, K., Yang, T., Zhu, M. (2021). <i>Trolls, Haters, or Teammates: Classifying Sentiment in the Language of PvP Game Communications.</i> Stanford University.<br/>"
                      "• <b>Deliverables:</b> Complete reproducible code, 7 notebooks, serialized models, and Streamlit demo in GitHub repository.", meta_box_txt)
        ]
    ]
    contrib_tbl = Table(contrib_data, colWidths=[260, 255])
    contrib_tbl.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,-1), 0.5, colors.HexColor("#666666")),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#666666")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(contrib_tbl)

    doc.build(story, canvasmaker=SimplePageCanvas)
    print(f"Built PDF: {filename}")

if __name__ == "__main__":
    out_pdf = "One_Page_Writeup.pdf"
    if len(sys.argv) > 1:
        out_pdf = sys.argv[1]
    build_pdf(out_pdf)

    reader = pypdf.PdfReader(out_pdf)
    print(f"Total Page Count: {len(reader.pages)}")
    assert len(reader.pages) == 2, f"Expected exactly 2 pages, got {len(reader.pages)}"
    print("SUCCESS: Exactly 2 pages generated!")

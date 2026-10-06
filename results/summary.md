# Auto-generated results summary (paste these numbers into the write-up and slides)

* Labelled dataset: 1979 messages (train 1583, test 396); class share: {'neutral/positive': 0.56, 'negative attitude': 0.369, 'derogatory': 0.071}
* Label quality (AI labels vs 97 hand-checked messages): accuracy 0.763, kappa 0.643; 26 labels corrected
* Best model overall: Random Forest (Gini) - accuracy 0.9015, macro-F1 0.8247

## By feature group
| feature_group            |   models |   best_accuracy |   mean_accuracy |   best_macro_f1 |   mean_macro_f1 |
|:-------------------------|---------:|----------------:|----------------:|----------------:|----------------:|
| GloVe (news text)        |       10 |          0.8384 |          0.8142 |          0.7123 |          0.6804 |
| TF-IDF                   |        9 |          0.9015 |          0.7753 |          0.8247 |          0.6488 |
| word2vec (our chat data) |       10 |          0.8434 |          0.8149 |          0.7226 |          0.6688 |

## Top 10 models
|   rank | model                                   |   accuracy |   macro_f1 |
|-------:|:----------------------------------------|-----------:|-----------:|
|      1 | Random Forest (Gini)                    |     0.9015 |     0.8247 |
|      2 | Random Forest (Entropy)                 |     0.899  |     0.8226 |
|      3 | Naive Bayes (165-phrase dictionary)     |     0.8662 |     0.7075 |
|      4 | Random Forest (Entropy, max depth=32)   |     0.846  |     0.7788 |
|      5 | LSTM (softmax output; word2vec 100-dim) |     0.8434 |     0.7226 |
|      6 | LSTM (sigmoid output; word2vec 100-dim) |     0.8409 |     0.7124 |
|      7 | LSTM (softmax output; GloVe 50-dim)     |     0.8384 |     0.7123 |
|      8 | LSTM (softmax output; GloVe 100-dim)    |     0.8359 |     0.6831 |
|      9 | Naive Bayes (TF-IDF)                    |     0.8308 |     0.7513 |
|     10 | LSTM (softmax output; word2vec 50-dim)  |     0.8308 |     0.6531 |
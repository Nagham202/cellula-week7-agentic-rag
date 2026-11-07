## Search comparison

| Version | Questions | hit@1 | hit@3 | hit@5 | MRR |
|---|---|---|---|---|---|
| semantic | all (28) | 0.71 | 0.82 | 0.89 | 0.77 |
| keyword | all (28) | 0.64 | 0.86 | 0.86 | 0.74 |
| hybrid | all (28) | 0.75 | 0.89 | 0.93 | 0.83 |
| hybrid+rewrite | all (28) | 0.79 | 0.93 | 0.96 | 0.87 |
| hybrid+rewrite+alts | all (28) | 0.82 | 0.93 | 0.96 | 0.88 |
| +rerank+select | all (28) | 0.79 | 0.96 | 0.96 | 0.88 |
| semantic | meaning (11) | 0.64 | 0.73 | 0.91 | 0.70 |
| keyword | meaning (11) | 0.55 | 0.73 | 0.73 | 0.64 |
| hybrid | meaning (11) | 0.64 | 0.82 | 0.91 | 0.75 |
| hybrid+rewrite | meaning (11) | 0.64 | 0.82 | 0.91 | 0.75 |
| hybrid+rewrite+alts | meaning (11) | 0.64 | 0.82 | 0.91 | 0.75 |
| +rerank+select | meaning (11) | 0.55 | 0.91 | 0.91 | 0.73 |
| semantic | exact (11) | 0.91 | 0.91 | 0.91 | 0.91 |
| keyword | exact (11) | 1.00 | 1.00 | 1.00 | 1.00 |
| hybrid | exact (11) | 1.00 | 1.00 | 1.00 | 1.00 |
| hybrid+rewrite | exact (11) | 1.00 | 1.00 | 1.00 | 1.00 |
| hybrid+rewrite+alts | exact (11) | 1.00 | 1.00 | 1.00 | 1.00 |
| +rerank+select | exact (11) | 1.00 | 1.00 | 1.00 | 1.00 |
| semantic | followup (6) | 0.50 | 0.83 | 0.83 | 0.64 |
| keyword | followup (6) | 0.17 | 0.83 | 0.83 | 0.47 |
| hybrid | followup (6) | 0.50 | 0.83 | 0.83 | 0.67 |
| hybrid+rewrite | followup (6) | 0.67 | 1.00 | 1.00 | 0.83 |
| hybrid+rewrite+alts | followup (6) | 0.83 | 1.00 | 1.00 | 0.92 |
| +rerank+select | followup (6) | 0.83 | 1.00 | 1.00 | 0.92 |

Rewrites that fell back to the original question: 0

### Rank of the first right chunk (- = not in top 5)

| Question | Type | semantic | keyword | hybrid | hybrid+rewrite | hybrid+rewrite+alts | +rerank+select |
|---|---|---|---|---|---|---|---|
| Which two ways of combining the retrieved documents does the paper propose? | meaning | 5 | 1 | 1 | 1 | 1 | 1 |
| Which model is used to find the documents? | meaning | 3 | - | 4 | 4 | 5 | 2 |
| Which pre-trained model writes the answers? | meaning | - | - | - | - | - | - |
| How was Wikipedia prepared to be used as the knowledge source? | meaning | 1 | 2 | 1 | 1 | 1 | 2 |
| Can the knowledge of the model be changed after training without retraining it? | meaning | 5 | 2 | 2 | 2 | 2 | 2 |
| How many trainable parameters do the RAG models have in total? | meaning | 1 | 1 | 1 | 1 | 1 | 1 |
| Which optimizer was used for training? | meaning | 1 | - | 2 | 2 | 2 | 2 |
| What is the main risk of retrieval-augmented generation? | meaning | 1 | 1 | 1 | 1 | 1 | 1 |
| How long is the warranty of the robot? | meaning | 1 | 1 | 1 | 1 | 1 | 1 |
| How long does it take to fully charge Kito? | meaning | 1 | 1 | 1 | 1 | 1 | 1 |
| How many days of holiday do employees get per year? | meaning | 1 | 1 | 1 | 1 | 1 | 1 |
| What does error E31 mean? | exact | 1 | 1 | 1 | 1 | 1 | 1 |
| What should I do for error E47? | exact | 1 | 1 | 1 | 1 | 1 | 1 |
| What does Equation 12 compute? | exact | 1 | 1 | 1 | 1 | 1 | 1 |
| What accuracy did BERT-base get? | exact | 1 | 1 | 1 | 1 | 1 | 1 |
| What is shown in Table 7? | exact | 1 | 1 | 1 | 1 | 1 | 1 |
| What is MIPS? | exact | 1 | 1 | 1 | 1 | 1 | 1 |
| Who founded Nova Robotics? | exact | 1 | 1 | 1 | 1 | 1 | 1 |
| Which dataset has 79169 training examples? | exact | 1 | 1 | 1 | 1 | 1 | 1 |
| What is FAISS used for? | exact | 1 | 1 | 1 | 1 | 1 | 1 |
| What results did RAG-Token-BM25 get? | exact | 1 | 1 | 1 | 1 | 1 | 1 |
| What does 15.3B refer to? | exact | - | 1 | 1 | 1 | 1 | 1 |
| How long does its battery last? | followup | 2 | 2 | 2 | 2 | 1 | 1 |
| How was it initialized before training? | followup | - | 1 | 2 | 2 | 2 | 2 |
| And can I work from home? | followup | 1 | - | 1 | 1 | 1 | 1 |
| How well did RAG do on it? | followup | 3 | 3 | - | 1 | 1 | 1 |
| Which one is the largest? | followup | 1 | 2 | 1 | 1 | 1 | 1 |
| When can I contact their support? | followup | 1 | 2 | 1 | 1 | 1 | 1 |

## Reranker comparison (20 candidates, top 5)

| Reranker | Questions | hit@1 | hit@3 | hit@5 | MRR | ms per question |
|---|---|---|---|---|---|---|
| no reranker | all (28) | 0.82 | 0.93 | 0.96 | 0.88 | 0 |
| Xenova/ms-marco-MiniLM-L-6-v2 | all (28) | 0.79 | 0.96 | 0.96 | 0.88 | 83 |
| Xenova/ms-marco-MiniLM-L-12-v2 | all (28) | 0.79 | 0.96 | 0.96 | 0.87 | 159 |
| BAAI/bge-reranker-base | all (28) | 0.71 | 0.93 | 0.93 | 0.81 | 398 |
| no reranker | meaning (11) | 0.64 | 0.82 | 0.91 | 0.75 | 0 |
| Xenova/ms-marco-MiniLM-L-6-v2 | meaning (11) | 0.55 | 0.91 | 0.91 | 0.73 | 83 |
| Xenova/ms-marco-MiniLM-L-12-v2 | meaning (11) | 0.55 | 0.91 | 0.91 | 0.71 | 159 |
| BAAI/bge-reranker-base | meaning (11) | 0.55 | 0.91 | 0.91 | 0.70 | 398 |
| no reranker | exact (11) | 1.00 | 1.00 | 1.00 | 1.00 | 0 |
| Xenova/ms-marco-MiniLM-L-6-v2 | exact (11) | 1.00 | 1.00 | 1.00 | 1.00 | 83 |
| Xenova/ms-marco-MiniLM-L-12-v2 | exact (11) | 1.00 | 1.00 | 1.00 | 1.00 | 159 |
| BAAI/bge-reranker-base | exact (11) | 1.00 | 1.00 | 1.00 | 1.00 | 398 |
| no reranker | followup (6) | 0.83 | 1.00 | 1.00 | 0.92 | 0 |
| Xenova/ms-marco-MiniLM-L-6-v2 | followup (6) | 0.83 | 1.00 | 1.00 | 0.92 | 83 |
| Xenova/ms-marco-MiniLM-L-12-v2 | followup (6) | 0.83 | 1.00 | 1.00 | 0.92 | 159 |
| BAAI/bge-reranker-base | followup (6) | 0.50 | 0.83 | 0.83 | 0.67 | 398 |

### Rank of the first right chunk

| Question | no reranker | Xenova/ms-marco-MiniLM-L-6-v2 | Xenova/ms-marco-MiniLM-L-12-v2 | BAAI/bge-reranker-base |
|---|---|---|---|---|
| Which two ways of combining the retrieved documents does the paper propose? | 1 | 1 | 1 | 2 |
| Which model is used to find the documents? | 5 | 2 | 3 | 1 |
| Which pre-trained model writes the answers? | - | - | - | - |
| How was Wikipedia prepared to be used as the knowledge source? | 1 | 2 | 2 | 3 |
| Can the knowledge of the model be changed after training without retraining it? | 2 | 2 | 2 | 2 |
| How many trainable parameters do the RAG models have in total? | 1 | 1 | 1 | 1 |
| Which optimizer was used for training? | 2 | 2 | 2 | 3 |
| What is the main risk of retrieval-augmented generation? | 1 | 1 | 1 | 1 |
| How long is the warranty of the robot? | 1 | 1 | 1 | 1 |
| How long does it take to fully charge Kito? | 1 | 1 | 1 | 1 |
| How many days of holiday do employees get per year? | 1 | 1 | 1 | 1 |
| What does error E31 mean? | 1 | 1 | 1 | 1 |
| What should I do for error E47? | 1 | 1 | 1 | 1 |
| What does Equation 12 compute? | 1 | 1 | 1 | 1 |
| What accuracy did BERT-base get? | 1 | 1 | 1 | 1 |
| What is shown in Table 7? | 1 | 1 | 1 | 1 |
| What is MIPS? | 1 | 1 | 1 | 1 |
| Who founded Nova Robotics? | 1 | 1 | 1 | 1 |
| Which dataset has 79169 training examples? | 1 | 1 | 1 | 1 |
| What is FAISS used for? | 1 | 1 | 1 | 1 |
| What results did RAG-Token-BM25 get? | 1 | 1 | 1 | 1 |
| What does 15.3B refer to? | 1 | 1 | 1 | 1 |
| How long does its battery last? | 1 | 1 | 1 | 2 |
| How was it initialized before training? | 2 | 2 | 2 | 1 |
| And can I work from home? | 1 | 1 | 1 | - |
| How well did RAG do on it? | 1 | 1 | 1 | 2 |
| Which one is the largest? | 1 | 1 | 1 | 1 |
| When can I contact their support? | 1 | 1 | 1 | 1 |

# Architecture Tradeoffs

## Hybrid Retrieval (BM25 + Dense)
- **Pro:** Mitigates the "lost in the middle" problem; handles extreme lexical specificity (acronyms) alongside abstract semantic intent.
- **Con:** Computationally heavier; managing sparse matrices requires more RAM. Latency penalty of ~10-15ms for fusion merging.

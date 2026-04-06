# Scaling Guide

## Horizontal Scaling

### API tier
- Deploy multiple replicas behind a load balancer (NGINX / AWS ALB).
- Use the `infra/k8s/hpa.yaml` HorizontalPodAutoscaler — scales on CPU ≥ 70%.

### Worker tier
- Celery workers are stateless — add replicas via `kubectl scale`.
- Use Redis Cluster for the broker to handle > 10k jobs/min.

### Vector DB (Qdrant)
- Enable Qdrant clustering: 3+ nodes with replication factor 2.
- Pin collection shards to specific nodes for predictable latency.

## Vertical Scaling

| Service | Recommended start | Scale up when |
|---------|------------------|---------------|
| API pod | 0.5 CPU / 512 MB | p95 latency > 2s |
| Worker pod | 1 CPU / 1 GB | Queue depth > 100 |
| Qdrant | 2 CPU / 4 GB | Search p95 > 200ms |

## Caching Strategy

- **Exact cache**: Deterministic prompts (TTL 10 min via Redis).
- **Semantic cache**: Near-duplicate queries (cosine similarity ≥ 0.95, TTL 1 hr).
- **CDN**: Cache frontend assets at the edge (CloudFront / Cloudflare).

## Cost Optimisation

- Use `gpt-4o-mini` for planning and `gpt-4o` only for final synthesis.
- Batch embedding calls (512-token chunks → fewer API round-trips).
- Set `max_tokens` based on expected output length per endpoint.

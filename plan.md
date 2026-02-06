# Fear & Greed Index 6900 - Development Roadmap

## Phase 1: CMC API Fetcher & Foundation
- [ ] Set up project structure (src/, tests/, docs/)
- [ ] Initialize uv environment and dependencies
- [ ] Create base fetcher interface/abstract class
- [ ] Implement CMC API client with rate limiting
- [ ] Fetch Bitcoin dominance data
- [ ] Fetch market volatility data (24h price changes)
- [ ] Fetch volume data (24h trading volume)
- [ ] Add retry logic and error handling
- [ ] Write unit tests for CMC fetcher
- [ ] Add logging infrastructure

## Phase 2: Normalization Engine
- [ ] Design normalization interface
- [ ] Implement Min-Max scaler (0-100 scale)
- [ ] Implement Z-score normalization
- [ ] Create historical data storage (for calculating baselines)
- [ ] Build volatility scorer (high volatility = fear)
- [ ] Build volume scorer (high volume = greed)
- [ ] Build dominance scorer (high BTC dominance = fear)
- [ ] Write tests for all normalizers
- [ ] Add configurable weights for each metric

## Phase 3: Social & Altcoin Season Logic
- [ ] Research social sentiment data sources
- [ ] Implement Twitter/X sentiment fetcher (if available)
- [ ] Implement Reddit sentiment fetcher (optional)
- [ ] Calculate Altcoin Season Index
  - [ ] Fetch top 50 altcoin performance vs BTC
  - [ ] Calculate % outperforming BTC
- [ ] Build social sentiment scorer
- [ ] Build altcoin season scorer
- [ ] Integrate new metrics into normalization engine
- [ ] Write tests for social and altcoin metrics

## Phase 4: Final Aggregator & API
- [ ] Design aggregator "brain" algorithm
- [ ] Implement weighted average aggregation
- [ ] Add configurable thresholds (extreme fear/greed)
- [ ] Build FastAPI application structure
- [ ] Create `/health` endpoint
- [ ] Create `/api/v1/index` endpoint (current index value)
- [ ] Create `/api/v1/metrics` endpoint (breakdown of all metrics)
- [ ] Create `/api/v1/history` endpoint (historical data)
- [ ] Add API documentation (OpenAPI/Swagger)
- [ ] Implement caching layer
- [ ] Add CORS configuration
- [ ] Write integration tests
- [ ] Create dashboard visualization (optional)

## Phase 5: Deployment & Monitoring (Future)
- [ ] Containerize with Docker
- [ ] Set up CI/CD pipeline
- [ ] Deploy to cloud provider
- [ ] Add monitoring and alerting
- [ ] Create documentation site
- [ ] Add historical data backfill script

## Current Phase
**Phase 1** - Foundation and CMC API Integration

## Notes
- Each phase builds upon the previous one
- Tests are mandatory before moving to next phase
- Keep the index calculation transparent and explainable
- Consider adding a "debug mode" to show raw metrics

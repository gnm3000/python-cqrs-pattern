# Performance Baseline (Monolith API)

This folder contains the minimal tooling to benchmark the current monolith before adding CQRS. The goal is to capture a reproducible baseline (latencies and throughput) so we can prove or disprove performance gains in later PRs.

## Scenarios

- `monolith-read-heavy.js`: seeds a small dataset, then stresses `GET /employees` and `GET /employees/{id}` with light think-time.
- `monolith-write-heavy.js`: focuses on `POST /employees` plus immediate `PUT` updates to mimic write contention.
- `monolith-mixed.js`: mixes reads and writes in each iteration to resemble real CRUD usage.

Each script uses ramping stages under a minute and exports `http_req_duration` percentiles (`p50/med`, `p95`, `p99`) plus `http_reqs` count.

## Running locally

1) Start the API (keeps SQLite data on a named volume):

```bash
docker compose up -d backend
```

2) Run any scenario with k6 (Dockerized):

```bash
# BASE_URL defaults to http://localhost:8000
docker run --rm --network host \
  -v "$(pwd)/performance:/scripts" \
  grafana/k6 run /scripts/scenarios/monolith-read-heavy.js \
  --summary-export=/scripts/results/read-heavy.json \
  -e BASE_URL=http://localhost:8000
```

3) Inspect results in `performance/results/*.json` or the terminal summary. Percentiles are reported in milliseconds.

Stop the stack when done:

```bash
docker compose down
```

## GitHub Actions pipeline

Workflow: `.github/workflows/perf-baseline.yml`

- Trigger: manual `workflow_dispatch` (optionally provide a PR number to comment results).
- Steps: build + start backend container, wait for health, run the three k6 scenarios inside the official `grafana/k6` image, upload `k6-summary` artifact, and format a Markdown latency table.
- Output: job summary always; PR comment when a `pr-number` input is provided.

## How to read the metrics

- `p50/p95/p99` from `http_req_duration` capture median and tail latency in ms.
- `http_reqs` is total HTTP requests during the run; compare across PRs for throughput shifts.
- Thresholds in the scripts (`checks > 0.9/0.95`, `http_req_duration p95`) will fail the job if regressions are extreme.

## Baseline vs CQRS follow-ups

This PR only adds measurement capability. Future CQRS changes must run the same scenarios and show whether p95/p99 latencies and throughput improve (or regress) relative to this baseline before merging.

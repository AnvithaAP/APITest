# Enterprise API Testing Framework

Modular API quality framework with two primary execution domains:
- `functional/` for API functional + governance + contract quality.
- `performance/` for API non-functional performance workloads.


## Query-driven Execution (granular)
Supports AND combinations and multi-value selectors:
- `scope=api AND intent=functional AND type=regression`
- `intent=functional AND module=users,orders AND release=R2026.04-S7`

Run functional/governance via router:
```bash


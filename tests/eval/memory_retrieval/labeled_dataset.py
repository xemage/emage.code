"""T455's labeled synthetic corpus + query set — the ground truth this eval

Purpose-built for this task, not a reuse of `tests/_helpers/synthetic_memory_corpus.py`
(T453's latency-benchmark generator) — that generator produces 260 near-identical
templated functions per module with no per-query relevance label at all (see
`docs/artifacts/retrieval-eval-v1.md` "Corpus/query-set construction" for the disclosed
reasoning this task's own Blocker Protocol names as an `unclear_requirements`/`minor`
finding, not silently forced into an ill-fitting reuse).

`TOPICS` are 20 distinct, human-authored short technical explanations, one per file, each
with exactly one Markdown heading (so `chunker.py` emits exactly one prose chunk per file —
no fenced code, so no tree-sitter dependency is needed to index this corpus, only
`fastembed`). `DECOYS` are 4 additional entries chosen to be lexically close to a real
topic but conceptually distinct (e.g. thread pooling vs. connection pooling), included to
make irrelevant-context rate a meaningful signal rather than trivially zero. `QUERIES` are
hand-authored natural-language paraphrases (deliberately avoiding a topic's own title words
where practical) mapped to the `TOPICS`/`DECOYS` id(s) judged relevant BEFORE any retriever
is run against them — the relevance judgment is the file id(s) a human reading the query
would expect to find, not anything inferred from `ContextRetriever`'s own output.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

PROJECT_ID = "fixture-org/retrieval-eval-corpus"
DEFAULT_K = 5

TOPICS: tuple[dict, ...] = (
    dict(id="database-connection-pooling", title="Database Connection Pooling",
         tags=["database", "performance"],
         body="A connection pool keeps a fixed set of open database connections ready for "
              "reuse instead of opening a new TCP connection for every query. Reusing warm "
              "connections avoids the handshake and authentication cost on each request and "
              "caps the number of concurrent connections a service can hold against the "
              "database, protecting it from being overwhelmed under load."),
    dict(id="api-rate-limiting", title="API Rate Limiting", tags=["api", "reliability"],
         body="Rate limiting rejects or delays requests once a client exceeds an allowed "
              "number of calls in a given time window, protecting an API from being "
              "overwhelmed by a single noisy caller. Common implementations use a token "
              "bucket or sliding window counter keyed by client identity, returning a 429 "
              "status once the budget is exhausted."),
    dict(id="structured-logging", title="Structured Logging", tags=["observability"],
         body="Structured logging emits each log line as a machine-parseable record, "
              "typically JSON, with consistent field names such as timestamp, severity, "
              "request_id, and message, instead of free-form text. This makes logs "
              "searchable and correlatable across services, essential once a system spans "
              "more than a single process."),
    dict(id="password-hashing", title="Password Hashing", tags=["security", "auth"],
         body="User passwords must never be stored in plain text or with a fast reversible "
              "hash. A slow, salted algorithm such as bcrypt or argon2id makes each guess "
              "expensive, so that even if the password database leaks, recovering the "
              "original passwords by brute force remains impractical for an attacker."),
    dict(id="session-management", title="Session Management", tags=["security", "auth"],
         body="A session ties a series of requests from the same browser to one "
              "authenticated identity, usually via a random token stored in a cookie. The "
              "session identifier should be regenerated after login, expire after a period "
              "of inactivity, and be invalidated server-side on logout so a stolen cookie "
              "stops working."),
    dict(id="caching-strategy-ttl", title="Time-To-Live Caching Strategy",
         tags=["performance", "caching"],
         body="A time-to-live cache stores a computed or fetched value for a fixed duration "
              "before treating it as stale and recomputing it, trading a bounded amount of "
              "staleness for far fewer expensive recomputations or upstream calls. Choosing "
              "the right TTL balances freshness against how much load the cache removes."),
    dict(id="retry-with-backoff", title="Retry With Exponential Backoff",
         tags=["reliability"],
         body="When a downstream call fails transiently, retrying immediately can make an "
              "overloaded dependency worse. Exponential backoff waits progressively longer "
              "between attempts, often with random jitter added so many clients retrying "
              "the same failure do not all collide on the same retry instant."),
    dict(id="circuit-breaker-pattern", title="Circuit Breaker Pattern", tags=["reliability"],
         body="A circuit breaker tracks recent failures to a dependency and, once a "
              "threshold is crossed, stops sending new calls for a cooldown period instead "
              "of letting every request wait for a slow timeout, protecting both the caller "
              "and the failing dependency while it recovers."),
    dict(id="feature-flags", title="Feature Flags", tags=["deployment"],
         body="A feature flag wraps a new code path behind a runtime-toggleable condition, "
              "letting a team deploy code before it is fully enabled, turn a feature on for "
              "a subset of users, or roll it back instantly without a new deployment, "
              "decoupling code deployment from feature release."),
    dict(id="blue-green-deployment", title="Blue-Green Deployment", tags=["deployment"],
         body="Blue-green deployment runs two identical production environments, only one "
              "of which serves live traffic at a time. A new release is deployed to the "
              "idle environment and verified there, then traffic is switched over at the "
              "load balancer; if a problem appears, traffic is switched back immediately."),
    dict(id="database-migrations", title="Database Schema Migrations", tags=["database"],
         body="A migration is a versioned, ordered script that changes a database schema, "
              "such as adding a column or index, checked into source control alongside the "
              "application code that depends on it. Running migrations in order, tracked "
              "against a migrations table, keeps every environment's schema reproducible."),
    dict(id="input-validation", title="Server-Side Input Validation", tags=["security"],
         body="Every value that crosses a system boundary, such as a form submission or an "
              "API request body, must be validated on the server before use, checking type, "
              "length, format, and allowed range against an allowlist rather than a "
              "denylist. Client-side validation is a usability aid only, not a security "
              "guarantee."),
    dict(id="cors-configuration", title="CORS Configuration", tags=["security", "web"],
         body="Cross-Origin Resource Sharing headers tell a browser which other origins are "
              "allowed to read a response from a given API. A permissive wildcard origin "
              "combined with credentialed requests defeats the browser's same-origin "
              "protections, so a real deployment should allow-list only the specific "
              "origins that legitimately need cross-origin access."),
    dict(id="webhook-signature-verification", title="Webhook Signature Verification",
         tags=["security", "integration"],
         body="A webhook receiver should verify a cryptographic signature sent alongside "
              "the payload, computed by the sender over the raw request body with a shared "
              "secret, before trusting the request came from the expected source and was "
              "not tampered with or replayed from a captured earlier delivery."),
    dict(id="pagination-cursor-based", title="Cursor-Based Pagination", tags=["api"],
         body="Cursor-based pagination returns an opaque token pointing at the last item "
              "seen, rather than an offset and limit, so that inserting or deleting rows "
              "between page requests does not shift later pages or duplicate/skip results — "
              "a common correctness problem with plain offset-based pagination."),
    dict(id="distributed-tracing", title="Distributed Tracing", tags=["observability"],
         body="Distributed tracing propagates a single trace identifier across every "
              "service call involved in handling one request, so the full path — including "
              "timing of each hop — can be reconstructed from many separate services' logs "
              "after the fact, which plain per-service logging cannot provide."),
    dict(id="graceful-shutdown", title="Graceful Shutdown", tags=["reliability"],
         body="On receiving a termination signal, a service should stop accepting new "
              "requests, finish any in-flight requests it already started, close its "
              "connections cleanly, and only then exit, rather than dropping in-flight work "
              "immediately — avoiding partial writes during routine deploys or autoscaling."),
    dict(id="idempotency-keys", title="Idempotency Keys", tags=["api", "reliability"],
         body="An idempotency key is a client-generated identifier attached to a request, "
              "such as a payment, so that if the client retries after a timeout without "
              "knowing whether the first attempt succeeded, the server can recognize the "
              "duplicate and return the original result instead of performing the action "
              "a second time."),
    dict(id="secrets-rotation", title="Secrets Rotation", tags=["security"],
         body="Credentials such as API keys and database passwords should be rotated on a "
              "regular schedule and immediately after any suspected exposure, with the old "
              "and new credential valid simultaneously for a short overlap window so every "
              "service can pick up the new value without a coordinated simultaneous "
              "restart."),
    dict(id="load-balancing-strategies", title="Load Balancing Strategies",
         tags=["reliability", "performance"],
         body="A load balancer distributes incoming requests across multiple backend "
              "instances using a strategy such as round robin, least connections, or "
              "weighted routing based on instance capacity, removing an instance from "
              "rotation once its health check starts failing."),
)

DECOYS: tuple[dict, ...] = (
    dict(id="cpu-thread-pooling", title="CPU Thread Pooling", tags=["performance"],
         body="A thread pool keeps a fixed number of worker threads alive to execute "
              "CPU-bound tasks pulled from a queue, avoiding the overhead of spawning a new "
              "operating system thread for every unit of work and bounding how many tasks "
              "run in parallel on a fixed number of cores."),
    dict(id="network-bandwidth-throttling", title="Network Bandwidth Throttling",
         tags=["performance"],
         body="Bandwidth throttling caps the data transfer rate of a connection at the "
              "network layer, used by a hosting provider or router to keep one client's "
              "large transfer from starving other traffic sharing the same link, distinct "
              "from limiting how many requests a client is allowed to make."),
    dict(id="cache-eviction-lru", title="LRU Cache Eviction", tags=["caching"],
         body="A least-recently-used cache discards the entry that has gone the longest "
              "without being accessed once the cache reaches its size limit, keeping the "
              "working set that is actually being used, independent of any fixed expiration "
              "time attached to an individual entry."),
    dict(id="authorization-rbac", title="Role-Based Access Control", tags=["security"],
         body="Role-based access control assigns each user one or more roles, and each role "
              "a fixed set of permissions, so authorization checks look up what the user's "
              "role is allowed to do rather than granting permissions individually, which "
              "does not by itself address how a user proved their identity."),
)

QUERIES: tuple[dict, ...] = (
    dict(query_text="why does reusing a small set of already-open database connections "
                     "help performance instead of opening a new one for every request",
         relevant_ids=("database-connection-pooling",)),
    dict(query_text="how do I stop one client from overwhelming my API with too many "
                     "calls per minute",
         relevant_ids=("api-rate-limiting",)),
    dict(query_text="what's the benefit of emitting logs as JSON with consistent fields "
                     "instead of plain text lines",
         relevant_ids=("structured-logging",)),
    dict(query_text="what's the right way to store user passwords so a database leak "
                     "doesn't expose them",
         relevant_ids=("password-hashing",)),
    dict(query_text="how should a login session token be handled so a stolen cookie stops "
                     "working after logout",
         relevant_ids=("session-management",)),
    dict(query_text="how long should a cached value be kept before recomputing it",
         relevant_ids=("caching-strategy-ttl",)),
    dict(query_text="what's a safe way to retry a failed downstream call without making "
                     "an overloaded service worse",
         relevant_ids=("retry-with-backoff",)),
    dict(query_text="how can I stop sending requests to a dependency that is already "
                     "failing instead of piling up timeouts",
         relevant_ids=("circuit-breaker-pattern",)),
    dict(query_text="how can I ship code to production before turning the new behavior "
                     "on for everyone",
         relevant_ids=("feature-flags",)),
    dict(query_text="how do I release a new version with an instant rollback path if "
                     "something breaks",
         relevant_ids=("blue-green-deployment",)),
    dict(query_text="how do I keep every environment's database schema in sync using "
                     "versioned scripts",
         relevant_ids=("database-migrations",)),
    dict(query_text="why isn't checking form input in the browser enough to consider it "
                     "validated",
         relevant_ids=("input-validation",)),
    dict(query_text="which cross-origin request headers control which websites can read "
                     "my API's response",
         relevant_ids=("cors-configuration",)),
    dict(query_text="how do I confirm an incoming webhook really came from the expected "
                     "sender and wasn't replayed",
         relevant_ids=("webhook-signature-verification",)),
    dict(query_text="why does offset-based pagination break when rows are inserted "
                     "between page loads",
         relevant_ids=("pagination-cursor-based",)),
    dict(query_text="how do I reconstruct the full path of one request across several "
                     "microservices",
         relevant_ids=("distributed-tracing",)),
    dict(query_text="what should a service do with in-flight requests when it receives "
                     "a termination signal",
         relevant_ids=("graceful-shutdown",)),
    dict(query_text="how do I make sure a retried payment request isn't charged twice",
         relevant_ids=("idempotency-keys",)),
    dict(query_text="how often should API keys and database passwords be replaced",
         relevant_ids=("secrets-rotation",)),
    dict(query_text="how does a load balancer decide which backend instance gets the "
                     "next request",
         relevant_ids=("load-balancing-strategies",)),
    dict(query_text="what patterns help an API stay resilient when a downstream "
                     "dependency is slow or failing",
         relevant_ids=("retry-with-backoff", "circuit-breaker-pattern")),
    dict(query_text="what should I check before trusting data that comes from outside my "
                     "system, like a web form or an incoming webhook",
         relevant_ids=("input-validation", "webhook-signature-verification")),
    dict(query_text="what deployment techniques let a team release changes with minimal "
                     "risk to users",
         relevant_ids=("feature-flags", "blue-green-deployment")),
)


def all_entry_ids() -> frozenset[str]:
    """Every id defined across `TOPICS` and `DECOYS` — used by both the offline dataset-
    validity tests and the real corpus generator."""
    return frozenset(entry["id"] for entry in (*TOPICS, *DECOYS))


def _entry_text(entry: dict) -> str:
    tags = ", ".join(entry["tags"])
    frontmatter = (
        "---\n"
        "scope: project\n"
        f"project_id: {PROJECT_ID}\n"
        f'title: "{entry["title"]}"\n'
        f"tags: [{tags}]\n"
        "---\n\n"
    )
    return frontmatter + f"## {entry['title']}\n\n{entry['body']}\n"


def generate_labeled_corpus(dest_dir: Path) -> Path:
    """Write every `TOPICS`/`DECOYS` entry as its own vault file (one Markdown heading
    each, prose only — no fenced code, so no tree-sitter dependency), commit as a real
    git repo (mirrors `synthetic_memory_corpus.py`'s own pattern so `scanner.resolve_commit`
    resolves a genuine SHA), and return `dest_dir`.
    """
    vault_dir = dest_dir / "implementation" / "knowledge" / "memory" / "project"
    vault_dir.mkdir(parents=True, exist_ok=True)
    for entry in (*TOPICS, *DECOYS):
        (vault_dir / f"{entry['id']}.md").write_text(_entry_text(entry), encoding="utf-8")
    _commit_repo(dest_dir)
    return dest_dir


def _commit_repo(repo_dir: Path) -> None:
    _run_git(repo_dir, ["init", "-q"])
    _run_git(repo_dir, ["config", "user.email", "t455-eval@example.invalid"])
    _run_git(repo_dir, ["config", "user.name", "T455 Retrieval Eval"])
    _run_git(repo_dir, ["add", "-A"])
    _run_git(repo_dir, ["commit", "-q", "-m", "fixture: T455 labeled retrieval-eval corpus"])


def _run_git(cwd: Path, args: list[str]) -> None:
    subprocess.run(["git", *args], cwd=str(cwd), check=True, capture_output=True, text=True)

# Local Market Scheduler

Run the deterministic loop as a user-level process with a private SQLite path:

```sh
python3 -m tools.local_market_scheduler.scheduler --db "$HOME/Library/Application Support/chitakasha/local-market.sqlite"
```

The production Forgejo adapter is intentionally not embedded in the core. Bind
it to the installed API/runner contract and keep credentials in the existing
credential store. Reconcile every 1–5 minutes; never dispatch more than one
active lease per host. Stop the process and preserve the SQLite file to roll
back. No SSH, listener, merge, or deployment is required by this prototype.

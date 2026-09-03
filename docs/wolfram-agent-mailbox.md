# Wolfram read-only agent mailbox

This is the MAILBOX-0001 watcher for `pashamango/minutta-rp-pr-cycle-lab`. It polls open Issues over outbound HTTPS with the already-authenticated GitHub CLI, validates a fixed envelope, and writes immutable, content-digested local observations. Issue bodies are inert data: the watcher does not invoke a shell, AppleScript, Python evaluation, templates, Codex, or another LLM with Issue content.

## Repository files

- `tools/wolfram-agent-watcher`: standard-library Python watcher
- `config/wolfram-agent-mailbox-policy.yaml`: fixed repository policy
- `tests/test_wolfram_agent_watcher.py`: deterministic admission and inert-data tests
- `launchd/com.chitakasha.agent-mailbox.plist`: one-minute user LaunchAgent

## Installed files on Wolfram

```text
~/ChitAkasha-Wolfram/agent-mailbox/bin/wolfram-agent-watcher
~/ChitAkasha-Wolfram/agent-mailbox/config/policy.yaml
~/ChitAkasha-Wolfram/agent-mailbox/state/{seen,inbox}/
~/ChitAkasha-Wolfram/agent-mailbox/logs/
~/Library/LaunchAgents/com.chitakasha.agent-mailbox.plist
```

The policy repository must match the repository compiled into the program. Records contain only the required Issue identity, timestamps, parsed mailbox metadata, digest, and first-seen time; credentials, headers, environment variables, and raw Issue bodies are not recorded.

## Test and install

```sh
python3 -m unittest discover -s tests -v
install -d "$HOME/ChitAkasha-Wolfram/agent-mailbox/"{bin,config,state/seen,state/inbox,logs}
install -m 0755 tools/wolfram-agent-watcher "$HOME/ChitAkasha-Wolfram/agent-mailbox/bin/wolfram-agent-watcher"
install -m 0644 config/wolfram-agent-mailbox-policy.yaml "$HOME/ChitAkasha-Wolfram/agent-mailbox/config/policy.yaml"
install -m 0644 launchd/com.chitakasha.agent-mailbox.plist "$HOME/Library/LaunchAgents/com.chitakasha.agent-mailbox.plist"
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.chitakasha.agent-mailbox.plist"
```

`launchctl print gui/$(id -u)/com.chitakasha.agent-mailbox` shows its status. A manual live read-only poll is:

```sh
"$HOME/ChitAkasha-Wolfram/agent-mailbox/bin/wolfram-agent-watcher" --config "$HOME/ChitAkasha-Wolfram/agent-mailbox/config/policy.yaml"
```

Authentication or API failures preserve state, append a bounded non-secret diagnostic, exit cleanly, and wait for the next scheduled invocation.

## Rollback

No administrator rights are needed. Disable and remove the watcher with:

```sh
launchctl bootout "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.chitakasha.agent-mailbox.plist"
rm "$HOME/Library/LaunchAgents/com.chitakasha.agent-mailbox.plist"
```

This fully stops polling. The `~/ChitAkasha-Wolfram/agent-mailbox` directory may then be archived or removed separately if its immutable observation history is no longer needed.

The watcher opens no listener and does not alter Issues, branches, repository settings, Tailscale, PentAGI, Ollama, Colima, Forgejo, Darwin, or any GitHub credential. It does not claim work, create pull requests, or execute Codex.

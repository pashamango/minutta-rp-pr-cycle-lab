# Wolfram agent mailbox

MAILBOX-0001 polls open Issues in `pashamango/minutta-rp-pr-cycle-lab` over outbound HTTPS, validates a fixed envelope, and writes immutable content-digested observations. MAILBOX-0002 separately re-fetches admitted sources, verifies their digests, obtains an atomic local CLAIM, and wakes the installed Codex CLI. Raw Issue text remains data: it is sent only on standard input after a fixed local policy preamble and is never interpolated into a command.

## Repository and installed files

- `tools/wolfram-agent-watcher`: standard-library admission watcher
- `tools/wolfram-agent-dispatcher`: standard-library CLAIM, verification, wake, and receipt logic
- `tools/wolfram-agent-mailbox-cycle`: sequential watcher/dispatcher process coordinator
- `config/wolfram-agent-mailbox-policy.yaml`: fixed repository policy
- `tests/`: deterministic watcher and dispatcher tests
- `launchd/com.chitakasha.agent-mailbox.plist`: one-minute user LaunchAgent
- `launchd/com.chitakasha.agent-mailbox.mailbox-0001.plist`: read-only rollback LaunchAgent

The installed tree is:

```text
~/ChitAkasha-Wolfram/agent-mailbox/bin/{wolfram-agent-watcher,wolfram-agent-dispatcher,wolfram-agent-mailbox-cycle}
~/ChitAkasha-Wolfram/agent-mailbox/config/policy.yaml
~/ChitAkasha-Wolfram/agent-mailbox/state/{seen,inbox,claims,runs,revisions,control}/
~/ChitAkasha-Wolfram/agent-mailbox/logs/
~/Library/LaunchAgents/com.chitakasha.agent-mailbox.plist
```

Inbox records do not contain raw bodies, credentials, headers, or environment variables. Run directories contain immutable envelope and CLAIM snapshots, bounded stdout/stderr logs, and a terminal result with output digests. Failed and timed-out CLAIMs are not retried. A changed digest for an already-claimed task id is recorded under `revisions/` for manual review.

Automatic scanning is fail-closed until `state/control/dispatcher-activation.json` exists. Its UTC `activated_at` watermark excludes older bootstrap records and permits only records admitted at or after activation. An explicitly named `--record` is reserved for controlled diagnosis and smoke testing.

## Test and install

```sh
python3 -m unittest discover -s tests -v
install -d "$HOME/ChitAkasha-Wolfram/agent-mailbox/"{bin,config,state/seen,state/inbox,state/claims,state/runs,state/revisions,state/control,logs}
install -m 0755 tools/wolfram-agent-watcher "$HOME/ChitAkasha-Wolfram/agent-mailbox/bin/wolfram-agent-watcher"
install -m 0755 tools/wolfram-agent-dispatcher "$HOME/ChitAkasha-Wolfram/agent-mailbox/bin/wolfram-agent-dispatcher"
install -m 0755 tools/wolfram-agent-mailbox-cycle "$HOME/ChitAkasha-Wolfram/agent-mailbox/bin/wolfram-agent-mailbox-cycle"
install -m 0644 config/wolfram-agent-mailbox-policy.yaml "$HOME/ChitAkasha-Wolfram/agent-mailbox/config/policy.yaml"
install -m 0644 launchd/com.chitakasha.agent-mailbox.mailbox-0001.plist "$HOME/ChitAkasha-Wolfram/agent-mailbox/config/mailbox-0001.plist"
install -m 0644 launchd/com.chitakasha.agent-mailbox.plist "$HOME/Library/LaunchAgents/com.chitakasha.agent-mailbox.plist"
"$HOME/ChitAkasha-Wolfram/agent-mailbox/bin/wolfram-agent-dispatcher" --activate
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.chitakasha.agent-mailbox.plist"
```

If MAILBOX-0001 is already loaded, use `launchctl bootout` before replacing and bootstrapping it. `launchctl print gui/$(id -u)/com.chitakasha.agent-mailbox` shows current status.

The dispatcher invokes `codex exec --ephemeral --skip-git-repo-check --color never --cd <workdir> -`, preserving the installed CLI's configured model, authentication, approval, and sandbox behavior while permitting a bounded task rooted outside Git. It uses no inbound listener, administrator privilege, new secret, or environment dump. The default timeout is 900 seconds; stdout and stderr go directly to task-specific files.

## Rollback

Return to merged MAILBOX-0001 read-only polling without deleting historical receipts:

```sh
launchctl bootout "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.chitakasha.agent-mailbox.plist"
chmod u+w "$HOME/ChitAkasha-Wolfram/agent-mailbox/state/control/dispatcher-activation.json"
rm "$HOME/ChitAkasha-Wolfram/agent-mailbox/state/control/dispatcher-activation.json"
install -m 0644 "$HOME/ChitAkasha-Wolfram/agent-mailbox/config/mailbox-0001.plist" "$HOME/Library/LaunchAgents/com.chitakasha.agent-mailbox.plist"
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.chitakasha.agent-mailbox.plist"
```

This leaves `state/inbox`, `state/claims`, `state/runs`, and `state/revisions` intact. Neither process opens a listener or alters Issues, labels, repository settings, Tailscale, PentAGI, Ollama, Colima, Forgejo, Darwin, privileges, or GitHub credentials. GitHub write-back, remote/distributed CLAIMs, retries, and risks above R1 remain out of scope.

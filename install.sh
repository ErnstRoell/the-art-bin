#!/usr/bin/env bash
# Register this checkout's MCP server with an MCP client.
#
# There is nothing to build: the server runs out of the checkout with `uv run`, which
# resolves its dependencies on first launch. All this script does is write the same
# `command`/`args` pair into whichever place your client keeps it, and then prove the
# corpus is readable from there.
#
# Usage: ./install.sh [options]
#
#   --client claude|desktop|json|print
#         claude   register with Claude Code via the `claude` CLI (default when present)
#         desktop  patch the Claude Desktop config for this platform
#         json     patch an arbitrary mcpServers config; needs --config
#         print    print the JSON block and change nothing (default without the CLI)
#   --scope user|project|local   Claude Code scope (default: user)
#   --config PATH                config file to patch; implies --client json
#   --name NAME                  server name to register as (default: the-art-bin)
#   --force                      replace an existing entry of that name
#   --dry-run                    show what would be registered, change nothing
#   --no-check                   skip the post-install corpus check
#   -h, --help                   this text
#
# Cursor, Windsurf, Zed and friends all use the same `mcpServers` object as Claude
# Desktop, so `--client json --config <their file>` covers them without a case per client.

set -euo pipefail

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
NAME=the-art-bin
SCOPE=user
CLIENT=
CONFIG=
FORCE=0
CHECK=1
DRY=0

# The header comment above is the help text, so the two cannot drift apart.
usage() { awk 'NR>1 && /^#/ {sub(/^# ?/, ""); print; next} NR>1 {exit}' "$0"; }
die() { printf 'error: %s\n' "$*" >&2; exit 1; }
note() { printf '%s\n' "$*" >&2; }

while [ $# -gt 0 ]; do
	case $1 in
		--client) CLIENT=${2:-}; shift 2 ;;
		--client=*) CLIENT=${1#*=}; shift ;;
		--scope) SCOPE=${2:-}; shift 2 ;;
		--scope=*) SCOPE=${1#*=}; shift ;;
		--config) CONFIG=${2:-}; CLIENT=${CLIENT:-json}; shift 2 ;;
		--config=*) CONFIG=${1#*=}; CLIENT=${CLIENT:-json}; shift ;;
		--name) NAME=${2:-}; shift 2 ;;
		--name=*) NAME=${1#*=}; shift ;;
		--force) FORCE=1; shift ;;
		--dry-run) DRY=1; shift ;;
		--no-check) CHECK=0; shift ;;
		-h|--help) usage; exit 0 ;;
		*) die "unknown option $1 (try --help)" ;;
	esac
done

[ -f "$ROOT/catalog.json" ] || die "$ROOT does not look like an art-bin checkout (no catalog.json)"

if [ -z "$CLIENT" ]; then
	if command -v claude >/dev/null 2>&1; then CLIENT=claude; else CLIENT=print; fi
fi
case $CLIENT in
	claude|desktop|json|print) ;;
	*) die "unknown client $CLIENT (claude, desktop, json or print)" ;;
esac
case $SCOPE in user|project|local) ;; *) die "unknown scope $SCOPE (user, project or local)" ;; esac

if [ "$CLIENT" != print ] && ! command -v uv >/dev/null 2>&1; then
	die "uv is not on PATH; install it from https://docs.astral.sh/uv/ — the server is launched by uv"
fi

# python3 for the JSON edit. Any client config may have unrelated servers in it, so this
# has to be a merge, and a merge in sed is how configs get corrupted.
py() {
	if command -v python3 >/dev/null 2>&1; then python3 "$@"
	else uv run --no-project --quiet python "$@"
	fi
}

server_json() {
	py -c '
import json, sys
name, root = sys.argv[1:3]
print(json.dumps({"mcpServers": {name: {"command": "uv", "args": ["--directory", root, "run", "art-bin-server"]}}}, indent=2))
' "$NAME" "$ROOT"
}

desktop_config_path() {
	case $(uname -s) in
		Darwin) printf '%s\n' "$HOME/Library/Application Support/Claude/claude_desktop_config.json" ;;
		MINGW*|MSYS*|CYGWIN*) printf '%s\n' "${APPDATA:-$HOME/AppData/Roaming}/Claude/claude_desktop_config.json" ;;
		*) printf '%s\n' "${XDG_CONFIG_HOME:-$HOME/.config}/Claude/claude_desktop_config.json" ;;
	esac
}

patch_config() {
	local path=$1
	if [ "$DRY" = 1 ]; then
		note "would add to $path:"
		server_json
		return 0
	fi
	mkdir -p "$(dirname -- "$path")"
	if [ -e "$path" ]; then
		cp -- "$path" "$path.bak"
		note "backed up $path.bak"
	fi
	py -c '
import json, pathlib, sys

path, name, root, force = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4] == "1"
config = {}
if path.exists() and path.read_text(encoding="utf-8").strip():
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: {path} is not valid JSON ({exc}); fix or move it first")

servers = config.setdefault("mcpServers", {})
if name in servers and not force:
    raise SystemExit(f"error: {name!r} is already in {path}; pass --force to replace it")
servers[name] = {"command": "uv", "args": ["--directory", root, "run", "art-bin-server"]}
path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
print(f"registered {name!r} in {path}")
' "$path" "$NAME" "$ROOT" "$FORCE"
}

case $CLIENT in
	print)
		note "add this to your client's MCP config:"
		server_json
		;;
	claude)
		command -v claude >/dev/null 2>&1 || die "the claude CLI is not on PATH; try --client desktop or --client print"
		if [ "$DRY" = 1 ]; then
			note "would run:"
			printf 'claude mcp add %s --scope %s -- uv --directory %s run art-bin-server\n' "$NAME" "$SCOPE" "$ROOT"
			exit 0
		fi
		if claude mcp get "$NAME" >/dev/null 2>&1; then
			[ "$FORCE" = 1 ] || die "'$NAME' is already registered with Claude Code; pass --force to replace it"
			claude mcp remove "$NAME" --scope "$SCOPE" >/dev/null 2>&1 || claude mcp remove "$NAME" >/dev/null 2>&1 || true
		fi
		claude mcp add "$NAME" --scope "$SCOPE" -- uv --directory "$ROOT" run art-bin-server
		note "registered '$NAME' with Claude Code ($SCOPE scope)"
		;;
	desktop)
		patch_config "$(desktop_config_path)"
		[ "$DRY" = 1 ] || note "restart Claude Desktop to pick it up"
		;;
	json)
		[ -n "$CONFIG" ] || die "--client json needs --config PATH"
		patch_config "$CONFIG"
		;;
esac

# Prove the thing that just got registered can actually read the corpus. A wrong
# --directory or a half-synced environment is otherwise a silent failure at review time,
# in another process, hours later.
if [ "$CHECK" = 1 ] && [ "$DRY" = 0 ] && [ "$CLIENT" != print ]; then
	uv run --directory "$ROOT" --quiet python -c '
from art_bin_server.corpus import Corpus
catalog = Corpus.discover().catalog()
print("ok: server reads", catalog["count"], "smells from the corpus")
' || die "the server could not read the corpus from $ROOT"
fi

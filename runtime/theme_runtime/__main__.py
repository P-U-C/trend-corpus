"""
CLI entrypoint: `python3 -m theme_runtime <command> --config <path> [args...]`

Commands:
  init        Initialize db.sqlite + dirs for the configured theme.
  migrate     Run a peptides-to-topics column rename (legacy DBs only).
  ingest      Fetch sources.txt URLs -> sources table.
  extract     Process unprocessed sources -> claims (via Claude).
  packet      Generate a decision packet (via Claude).
  status      Print a quick health summary.
  recent      Print the N most recent active claims.
  health      Verify Claude CLI auth + HOME are usable.
  notify      alert | digest | packet -- Telegram notifications.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import extract, health, ingest, notify, packet, status
from .context import load_context
from .db import init_schema, migrate_legacy_peptides_db


def _ctx(args):
    return load_context(args.config)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="theme_runtime")
    ap.add_argument("--config", required=False,
                    help="path to theme-config.yaml (also reads TRT_CONFIG env)")
    sub = ap.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="initialize db.sqlite + dirs")
    sub.add_parser("migrate", help="rename legacy peptides column -> topics")

    p_ing = sub.add_parser("ingest", help="fetch sources.txt URLs")
    _ = p_ing

    p_ext = sub.add_parser("extract", help="process unprocessed sources -> claims")
    p_ext.add_argument("--limit", type=int, default=20)
    p_ext.add_argument("--model", default=None)

    p_pkt = sub.add_parser("packet", help="generate a decision packet")
    p_pkt.add_argument("question", nargs="+")
    p_pkt.add_argument("--limit", type=int, default=200)
    p_pkt.add_argument("--model", default=None)
    p_pkt.add_argument("--filter", dest="filter_expr", default=None,
                       help="topics:<v> | entities:<v> | category:<v>")

    sub.add_parser("status", help="print corpus health summary")
    p_rec = sub.add_parser("recent", help="show N most recent active claims")
    p_rec.add_argument("-n", "--count", type=int, default=10)

    sub.add_parser("health", help="verify claude CLI auth")

    p_not = sub.add_parser("notify", help="Telegram notifications")
    p_not.add_argument("mode", choices=["alert", "digest", "packet"])
    p_not.add_argument("args", nargs="*")

    args = ap.parse_args(argv)

    # Resolve config path from --config or env var
    import os as _os
    cfg = args.config or _os.environ.get("TRT_CONFIG")
    if not cfg:
        print("ERROR: --config or $TRT_CONFIG required", file=sys.stderr)
        return 2
    args.config = cfg

    if args.command == "init":
        ctx = _ctx(args)
        ctx.root.mkdir(parents=True, exist_ok=True)
        ctx.prompts_dir.mkdir(parents=True, exist_ok=True)
        ctx.packets_dir.mkdir(parents=True, exist_ok=True)
        init_schema(ctx.db_path)
        if not ctx.sources_path.exists():
            ctx.sources_path.write_text("# add URLs, one per line; lines starting with # are comments\n")
        print(f"init({ctx.theme_id}): root={ctx.root}, db={ctx.db_path}")
        return 0

    if args.command == "migrate":
        ctx = _ctx(args)
        ran = migrate_legacy_peptides_db(ctx.db_path)
        print(f"migrate({ctx.theme_id}): {'rename ran' if ran else 'no-op (already migrated)'}")
        return 0

    if args.command == "ingest":
        ingest.run(_ctx(args))
        return 0

    if args.command == "extract":
        extract.run(_ctx(args), limit=args.limit, model=args.model)
        return 0

    if args.command == "packet":
        question = " ".join(args.question)
        packet.run(_ctx(args), question, limit=args.limit, model=args.model,
                   filter_expr=args.filter_expr)
        return 0

    if args.command == "status":
        status.print_summary(_ctx(args))
        return 0

    if args.command == "recent":
        status.print_recent_claims(_ctx(args), n=args.count)
        return 0

    if args.command == "health":
        return health.run(_ctx(args))

    if args.command == "notify":
        ctx = _ctx(args)
        if args.mode == "alert":
            notify.alert(ctx, " ".join(args.args) if args.args else "(no message)")
        elif args.mode == "digest":
            notify.digest(ctx)
        elif args.mode == "packet":
            if not args.args:
                print("notify packet needs a file path", file=sys.stderr)
                return 2
            notify.packet(ctx, args.args[0])
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())

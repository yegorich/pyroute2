#!/usr/bin/env python
import json
import argparse
from pr2modules.cli.console import Console
from pr2modules.cli.server import Server

try:
    from pr2modules.cli.auth.auth_keystone import OSAuthManager
except ImportError:
    OSAuthManager = None
try:
    from pr2modules.cli.auth.auth_radius import RadiusAuthManager
except ImportError:
    RadiusAuthManager = None


def run():
    argp = argparse.ArgumentParser()
    for spec in (
        ('-a', '[S] IP address to listen on'),
        ('-c', '[C] Command line to run'),
        ('-l', '[C,S] Log spec'),
        ('-m', 'Set mode (C,S)'),
        ('-p', '[S] Port to listen on'),
        ('-r', '[C] Load rc file'),
        ('-s', '[C,S] Load sources from a json file'),
        ('-x', '[S] Strict auth'),
    ):
        argp.add_argument(spec[0], help=spec[1])
    args = argp.parse_args()
    commands = []
    sources = None
    if args.s:
        with open(args.s, 'r') as f:
            sources = json.loads(f.read())

    if args.m in ('S', 'server'):
        if args.p:
            port = int(args.p)
        else:
            port = 8080

        auth_plugins = {}
        if OSAuthManager is not None:
            auth_plugins['keystone'] = OSAuthManager
        if RadiusAuthManager is not None:
            auth_plugins['radius:cleartext'] = RadiusAuthManager

        server = Server(
            address=args.a or 'localhost',
            port=port,
            log=args.l,
            sources=sources,
            auth_strict=args.x,
            auth_plugins=auth_plugins,
        )
        server.serve_forever()
    else:
        console = Console(log=args.l, sources=sources)
        if args.r:
            console.loadrc(args.r)

        if args.c:
            commands.append(args.c)
            console.interact(readfunc=lambda x: commands.pop(0))
        else:
            console.interact()


if __name__ == '__main__':
    run()

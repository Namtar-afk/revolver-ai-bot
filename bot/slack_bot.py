#!/usr/bin/env python3
import argparse
from bot.slack_handler import (
    simulate_upload,
    cli_veille,
    cli_analyse,
    start_slack_listener,
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Slack Bot CLI & Listener")
    parser.add_argument("--simulate", action="store_true", help="Mode CLI local avec sample.pdf")
    parser.add_argument("--veille", action="store_true", help="Lance la veille en CLI")
    parser.add_argument("--analyse", action="store_true", help="Lance l’analyse en CLI")
    args = parser.parse_args()

    if args.simulate:
        simulate_upload()
    elif args.veille:
        print(cli_veille())
    elif args.analyse:
        print(cli_analyse())
    else:
        start_slack_listener()

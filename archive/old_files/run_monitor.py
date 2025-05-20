#!/usr/bin/env python3
import argparse
from bot.monitoring import fetch_all_sources, save_to_csv

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="data/veille.csv")
    args = p.parse_args()

    items = fetch_all_sources()
    save_to_csv(items, args.out)
    print(f"[✓] Veille enregistrée dans {args.out}")

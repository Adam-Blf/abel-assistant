#!/usr/bin/env python3
"""
A.B.E.L - Telecharger le modele Qwen2.5-7B
==========================================
Usage:
    python download_model.py
    python download_model.py --model Qwen/Qwen2.5-3B-Instruct  # Version plus legere
"""

import argparse
from huggingface_hub import snapshot_download
from transformers import AutoModelForCausalLM, AutoTokenizer


MODELS = {
    "qwen2.5-7b": "Qwen/Qwen2.5-7B-Instruct",
    "qwen2.5-3b": "Qwen/Qwen2.5-3B-Instruct",
    "qwen2.5-1.5b": "Qwen/Qwen2.5-1.5B-Instruct",
}


def main():
    parser = argparse.ArgumentParser(description="Download Qwen model")
    parser.add_argument(
        "--model",
        default="Qwen/Qwen2.5-7B-Instruct",
        help="Model name or path"
    )
    parser.add_argument(
        "--output",
        default="./models/base",
        help="Output directory"
    )
    args = parser.parse_args()

    model_name = MODELS.get(args.model.lower(), args.model)

    print("=" * 60)
    print("  A.B.E.L - Telechargement du modele")
    print("=" * 60)
    print(f"\nModele: {model_name}")
    print(f"Output: {args.output}")

    print("\n[1/2] Telechargement du tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=True,
    )
    tokenizer.save_pretrained(args.output)
    print("  OK!")

    print("\n[2/2] Telechargement du modele...")
    print("  (Cela peut prendre plusieurs minutes...)")

    # Telecharger sans charger en memoire
    snapshot_download(
        repo_id=model_name,
        local_dir=args.output,
        ignore_patterns=["*.md", "*.txt"],
    )

    print("\n" + "=" * 60)
    print("  TELECHARGEMENT TERMINE!")
    print("=" * 60)
    print(f"\nModele sauvegarde dans: {args.output}")
    print("\nPour fine-tuner:")
    print("  python finetune.py")


if __name__ == "__main__":
    main()

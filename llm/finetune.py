#!/usr/bin/env python3
"""
A.B.E.L - Qwen2.5-7B Fine-tuning avec QLoRA
============================================
GPU requis: NVIDIA 8GB+ VRAM (RTX 3070, 3080, 4070, etc.)

Usage:
    python finetune.py
    python finetune.py --epochs 5 --batch-size 2
"""

import os
import sys
import argparse
import json
from pathlib import Path

import torch
import yaml
from datasets import Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer


def load_config(config_path: str = "config.yaml") -> dict:
    """Charge la configuration depuis le fichier YAML."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_dataset(file_path: str) -> Dataset:
    """Charge le dataset depuis un fichier JSONL."""
    data = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line))
    return Dataset.from_list(data)


def format_messages(example: dict, tokenizer) -> str:
    """Formate les messages pour le modele Qwen."""
    messages = example["messages"]
    return tokenizer.apply_chat_template(messages, tokenize=False)


def main():
    parser = argparse.ArgumentParser(description="A.B.E.L Fine-tuning")
    parser.add_argument("--config", default="config.yaml", help="Config file")
    parser.add_argument("--epochs", type=int, help="Override epochs")
    parser.add_argument("--batch-size", type=int, help="Override batch size")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    args = parser.parse_args()

    # Charger la config
    print("=" * 60)
    print("  A.B.E.L - Qwen2.5-7B Fine-tuning")
    print("=" * 60)

    config = load_config(args.config)
    model_name = config["model"]["name"]
    output_dir = config["model"]["output_dir"]

    # Overrides CLI
    epochs = args.epochs or config["training"]["num_train_epochs"]
    batch_size = args.batch_size or config["training"]["per_device_train_batch_size"]

    print(f"\nModele: {model_name}")
    print(f"Output: {output_dir}")
    print(f"Epochs: {epochs}")
    print(f"Batch size: {batch_size}")

    # Verifier GPU
    if not torch.cuda.is_available():
        print("\n[ERREUR] GPU CUDA non detecte!")
        print("Le fine-tuning necessite un GPU NVIDIA.")
        sys.exit(1)

    gpu_name = torch.cuda.get_device_name(0)
    gpu_mem = torch.cuda.get_device_properties(0).total_memory / 1e9
    print(f"\nGPU: {gpu_name} ({gpu_mem:.1f} GB)")

    # Configuration quantization 4-bit
    print("\n[1/5] Configuration BitsAndBytes...")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=config["quantization"]["load_in_4bit"],
        bnb_4bit_compute_dtype=getattr(torch, config["quantization"]["bnb_4bit_compute_dtype"]),
        bnb_4bit_quant_type=config["quantization"]["bnb_4bit_quant_type"],
        bnb_4bit_use_double_quant=config["quantization"]["bnb_4bit_use_double_quant"],
    )

    # Charger le tokenizer
    print("\n[2/5] Chargement du tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=True,
    )
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    # Charger le modele
    print("\n[3/5] Chargement du modele (4-bit)...")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        attn_implementation="flash_attention_2" if torch.cuda.get_device_capability()[0] >= 8 else "eager",
    )
    model = prepare_model_for_kbit_training(model)

    # Configuration LoRA
    print("\n[4/5] Application de LoRA...")
    lora_config = LoraConfig(
        r=config["qlora"]["r"],
        lora_alpha=config["qlora"]["lora_alpha"],
        lora_dropout=config["qlora"]["lora_dropout"],
        bias=config["qlora"]["bias"],
        task_type=config["qlora"]["task_type"],
        target_modules=config["qlora"]["target_modules"],
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # Charger les datasets
    print("\n[5/5] Chargement des datasets...")
    train_dataset = load_dataset(config["dataset"]["train_file"])
    print(f"  Train: {len(train_dataset)} exemples")

    eval_dataset = None
    if Path(config["dataset"]["eval_file"]).exists():
        eval_dataset = load_dataset(config["dataset"]["eval_file"])
        print(f"  Eval: {len(eval_dataset)} exemples")

    # Formater les datasets
    def formatting_func(example):
        return format_messages(example, tokenizer)

    # Configuration training
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=config["training"]["gradient_accumulation_steps"],
        learning_rate=config["training"]["learning_rate"],
        weight_decay=config["training"]["weight_decay"],
        warmup_ratio=config["training"]["warmup_ratio"],
        lr_scheduler_type=config["training"]["lr_scheduler_type"],
        fp16=config["training"]["fp16"],
        gradient_checkpointing=config["training"]["gradient_checkpointing"],
        optim=config["training"]["optim"],
        logging_steps=config["training"]["logging_steps"],
        save_steps=config["training"]["save_steps"],
        eval_steps=config["training"]["eval_steps"] if eval_dataset else None,
        evaluation_strategy="steps" if eval_dataset else "no",
        save_total_limit=3,
        load_best_model_at_end=True if eval_dataset else False,
        report_to="tensorboard",
        remove_unused_columns=False,
    )

    # Trainer
    trainer = SFTTrainer(
        model=model,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        tokenizer=tokenizer,
        args=training_args,
        formatting_func=formatting_func,
        max_seq_length=config["training"]["max_seq_length"],
        packing=False,
    )

    # Entrainement
    print("\n" + "=" * 60)
    print("  DEBUT DU FINE-TUNING")
    print("=" * 60 + "\n")

    if args.resume:
        trainer.train(resume_from_checkpoint=True)
    else:
        trainer.train()

    # Sauvegarder
    print("\n[OK] Sauvegarde du modele...")
    trainer.save_model()
    tokenizer.save_pretrained(output_dir)

    # Fusionner les poids LoRA (optionnel)
    print("\n[OK] Fusion des poids LoRA...")
    merged_model = model.merge_and_unload()
    merged_output = f"{output_dir}-merged"
    merged_model.save_pretrained(merged_output)
    tokenizer.save_pretrained(merged_output)

    print("\n" + "=" * 60)
    print("  FINE-TUNING TERMINE!")
    print("=" * 60)
    print(f"\nModele LoRA: {output_dir}")
    print(f"Modele fusionne: {merged_output}")
    print("\nPour tester:")
    print(f"  python inference.py --model {merged_output}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
A.B.E.L - Inference avec le modele fine-tune
=============================================
Usage:
    python inference.py --model ./models/abel-qwen2.5-7b-merged
    python inference.py --model ./models/abel-qwen2.5-7b-merged --interactive
"""

import argparse
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextStreamer


SYSTEM_PROMPT = """Tu es A.B.E.L (Autonomous Backend Entity for Living), un assistant IA personnel avance.
Tu es capable de:
- Repondre aux questions de maniere precise et concise
- Aider avec la productivite (emails, calendrier, taches)
- Fournir des informations sur la finance, meteo, actualites
- Assister en programmation et developpement
- Gerer les divertissements (musique, films, jeux)

Tu reponds en francais par defaut, sauf si l'utilisateur parle dans une autre langue.
Tu es professionnel, efficace, et tu vas droit au but."""


def load_model(model_path: str, load_in_4bit: bool = True):
    """Charge le modele et le tokenizer."""
    print(f"Chargement du modele: {model_path}")

    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

    if load_in_4bit:
        from transformers import BitsAndBytesConfig
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            device_map="auto",
            torch_dtype=torch.float16,
            trust_remote_code=True,
        )

    return model, tokenizer


def generate_response(
    model,
    tokenizer,
    user_message: str,
    system_prompt: str = SYSTEM_PROMPT,
    max_new_tokens: int = 512,
    temperature: float = 0.7,
    stream: bool = True,
):
    """Genere une reponse du modele."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt").to(model.device)

    if stream:
        streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=True,
            top_p=0.9,
            streamer=streamer,
        )
        return None  # Already printed via streamer
    else:
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=True,
            top_p=0.9,
        )
        response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        return response


def interactive_mode(model, tokenizer):
    """Mode interactif pour tester le modele."""
    print("\n" + "=" * 60)
    print("  A.B.E.L - Mode Interactif")
    print("  Tapez 'quit' pour quitter")
    print("=" * 60 + "\n")

    history = []

    while True:
        try:
            user_input = input("\n[USER] > ").strip()
            if user_input.lower() in ["quit", "exit", "q"]:
                print("\n[A.B.E.L] Au revoir!")
                break
            if not user_input:
                continue

            print("\n[A.B.E.L] ", end="", flush=True)
            generate_response(model, tokenizer, user_input, stream=True)

        except KeyboardInterrupt:
            print("\n\n[A.B.E.L] Interruption. Au revoir!")
            break


def main():
    parser = argparse.ArgumentParser(description="A.B.E.L Inference")
    parser.add_argument("--model", required=True, help="Path to the model")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--message", "-m", type=str, help="Single message to process")
    parser.add_argument("--no-4bit", action="store_true", help="Disable 4-bit quantization")
    args = parser.parse_args()

    # Charger le modele
    model, tokenizer = load_model(args.model, load_in_4bit=not args.no_4bit)
    print("Modele charge!\n")

    if args.interactive:
        interactive_mode(model, tokenizer)
    elif args.message:
        print("[A.B.E.L] ", end="", flush=True)
        generate_response(model, tokenizer, args.message, stream=True)
        print()
    else:
        # Demo
        demo_messages = [
            "Bonjour A.B.E.L!",
            "Quel temps fait-il a Paris?",
            "Ecris-moi une fonction Python pour inverser une liste.",
        ]

        for msg in demo_messages:
            print(f"\n[USER] {msg}")
            print("[A.B.E.L] ", end="", flush=True)
            generate_response(model, tokenizer, msg, stream=True)
            print()


if __name__ == "__main__":
    main()

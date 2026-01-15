# A.B.E.L - LLM Fine-tuning

Fine-tuning de Qwen2.5-7B pour creer un assistant personnel optimise.

## Prerequis

- **GPU**: NVIDIA avec 8GB+ VRAM (RTX 3070, 3080, 4070, etc.)
- **RAM**: 16GB minimum
- **Python**: 3.10+
- **CUDA**: 11.8+

## Installation

```bash
cd llm
pip install -r requirements.txt
```

## Quick Start

### 1. Preparer le dataset

```bash
python prepare_dataset.py
```

Cela genere `data/train.jsonl` avec des exemples de conversations.

### 2. (Optionnel) Telecharger le modele

```bash
python download_model.py
```

### 3. Lancer le fine-tuning

```bash
python finetune.py
```

Options:
- `--epochs 5` : Nombre d'epochs
- `--batch-size 2` : Taille du batch (reduire si OOM)
- `--resume` : Reprendre depuis un checkpoint

### 4. Tester le modele

```bash
# Mode interactif
python inference.py --model ./models/abel-qwen2.5-7b-merged -i

# Message unique
python inference.py --model ./models/abel-qwen2.5-7b-merged -m "Bonjour!"
```

## Structure

```
llm/
├── config.yaml          # Configuration du fine-tuning
├── requirements.txt     # Dependances Python
├── prepare_dataset.py   # Generateur de dataset
├── download_model.py    # Telecharger le modele de base
├── finetune.py          # Script de fine-tuning
├── inference.py         # Script d'inference
├── data/
│   └── train.jsonl      # Dataset d'entrainement
└── models/
    └── abel-qwen2.5-7b/ # Modele fine-tune
```

## Configuration

Modifier `config.yaml` pour ajuster:

- **LoRA**: `r`, `lora_alpha`, `target_modules`
- **Training**: `epochs`, `batch_size`, `learning_rate`
- **Quantization**: `load_in_4bit`, `bnb_4bit_quant_type`

## Dataset Format

Format JSONL avec structure de messages:

```json
{
  "messages": [
    {"role": "system", "content": "Tu es A.B.E.L..."},
    {"role": "user", "content": "Question"},
    {"role": "assistant", "content": "Reponse"}
  ]
}
```

## Troubleshooting

### OOM (Out of Memory)

- Reduire `batch_size` a 1 ou 2
- Activer `gradient_checkpointing`
- Utiliser un modele plus petit (Qwen2.5-3B)

### CUDA Error

- Verifier la version CUDA: `nvcc --version`
- Reinstaller PyTorch pour votre version CUDA

## Integration avec A.B.E.L

Une fois le modele entraine, il peut etre integre dans le backend:

```python
from llm.inference import load_model, generate_response

model, tokenizer = load_model("./llm/models/abel-qwen2.5-7b-merged")
response = generate_response(model, tokenizer, "Bonjour!")
```

# Local LLM Setup

All experiments use **Qwen2.5-7B-Instruct** running locally via HuggingFace Transformers. No API keys are required.

## 1. Install dependencies

```bash
pip install -r requirements.txt
```

For CUDA 12.x (recommended):

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

## 2. Download Qwen2.5-7B-Instruct

```bash
python -c "
from huggingface_hub import snapshot_download
snapshot_download(
    'Qwen/Qwen2.5-7B-Instruct',
    local_dir='./models/Qwen2.5-7B-Instruct'
)
"
```

The model is approximately 15 GB in FP16. Set a custom cache location if needed:

```bash
export HF_HOME=/path/to/large/disk
```

## 3. Verify GPU access

```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0)}")
print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
```

## 4. Model loading

The code loads the model with `local_files_only=True` to avoid network calls at runtime. Ensure the model is fully downloaded before running experiments.

```python
from src.agents.llm_client import LocalLLMClient

llm = LocalLLMClient(model_path="./models/Qwen2.5-7B-Instruct")
```

## Decoding settings used in the paper

| Call type | Temperature | do_sample |
|---|---|---|
| Specialist answer | 0.0 (greedy) | False |
| Verification — question formulation | 0.3 | True |
| Verification — independent answering | 0.4 | True |
| Verification — reference answering | 0.2 | True |

## Troubleshooting

**CUDA out of memory:** Qwen2.5-7B-Instruct in FP16 requires ~15 GB VRAM. If you have less, enable 4-bit quantization by passing `load_in_4bit=True` to the client. Note that paper results were produced in full FP16 precision.

**Slow generation:** Verification sub-calls use temperature sampling which is slightly slower than greedy. This is expected; see Table 1 in the paper for wall-clock times per configuration.

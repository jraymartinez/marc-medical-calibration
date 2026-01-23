# Local LLM Setup Guide

## Overview
This implementation uses **HuggingFace Transformers** for local inference with medical diagnosis models. No cloud API keys required - everything runs on your local GPU or CPU.

## Changes Made

### 1. Core LLM Client (`src/agents/llm_client.py`)
**Replaced** OpenAI/Anthropic API clients with `LocalLLMClient`:
- Direct HuggingFace Transformers integration
- 4-bit quantization support (via bitsandbytes)
- Optimized for medical diagnosis tasks
- Token probability extraction for MCQA
- Auto device mapping for multi-GPU setups

### 2. Updated All Component Files
All files now use the new `LocalLLMClient` interface:
- ✅ `src/agents/specialist_agent.py`
- ✅ `src/agents/multi_specialist_consultation.py`
- ✅ `src/verification/tier1_verification.py`
- ✅ `src/verification/tier2_validation.py`
- ✅ `src/fusion/hierarchical_integration.py`
- ✅ `scripts/run_paper1_complete.py`
- ✅ `scripts/compare_integration_methods.py`
- ✅ All test files with mock clients

### 3. Updated Dependencies (`requirements.txt`)
Added HuggingFace ecosystem:
```
transformers>=4.40.0      # Core library
torch>=2.0.0              # PyTorch backend
accelerate>=0.20.0        # Distributed training/inference
bitsandbytes>=0.41.0      # 4-bit quantization
sentencepiece>=0.1.99     # Tokenization
protobuf>=3.20.0          # Model serialization
```

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

For CUDA support (recommended):
```bash
# Install PyTorch with CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Or CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 2. Verify Installation

```python
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
```

## Supported Models

### Recommended Models

| Model | Size | VRAM (4-bit) | VRAM (FP16) | Notes |
|-------|------|--------------|-------------|-------|
| **Llama 3.1 8B Instruct** | 8B | ~6 GB | ~16 GB | Best balance |
| **Llama 3.1 70B Instruct** | 70B | ~40 GB | ~140 GB | Best quality |
| **Mistral 7B Instruct v0.3** | 7B | ~5 GB | ~14 GB | Fast inference |
| **Llama 3.2 3B Instruct** | 3B | ~3 GB | ~6 GB | Low VRAM |

### Model Selection Guide

**For Development/Testing (8-16 GB VRAM):**
```python
llm = LocalLLMClient(
    model_name="meta-llama/Llama-3.1-8B-Instruct",
    use_4bit=True,
    device="cuda"
)
```

**For Production (40+ GB VRAM):**
```python
llm = LocalLLMClient(
    model_name="meta-llama/Llama-3.1-70B-Instruct",
    use_4bit=True,
    device="cuda"
)
```

**For CPU-only (slower):**
```python
llm = LocalLLMClient(
    model_name="meta-llama/Llama-3.1-8B-Instruct",
    use_4bit=False,
    device="cpu"
)
```

## Usage Examples

### Basic Text Generation

```python
from src.agents.llm_client import LocalLLMClient

# Initialize client
llm = LocalLLMClient("meta-llama/Llama-3.1-8B-Instruct", use_4bit=True)

# Generate response
response = llm.generate(
    system_prompt="You are an expert pulmonologist.",
    user_prompt="Patient presents with fever, cough, and chest pain. What are the top 3 differential diagnoses?",
    temperature=0.7,
    max_new_tokens=512
)

print(response)
```

### Multiple Choice Question Answering (MCQA)

```python
# Get probability distribution over options
probs = llm.get_token_probabilities(
    system_prompt="You are a medical expert.",
    user_prompt="""Question: A 65-year-old man presents with dyspnea and wheezing. Spirometry shows FEV1/FVC < 0.70. Diagnosis?
    
A. Asthma
B. COPD
C. Pneumonia
D. Lung cancer""",
    candidate_tokens=["A", "B", "C", "D"]
)

print(probs)
# Output: {"A": 0.15, "B": 0.70, "C": 0.10, "D": 0.05}
```

### Using in Pipeline

```python
from src.agents.specialist_agent import SpecialistAgent
from src.agents.llm_client import get_llm_client

# Create LLM client
llm = get_llm_client(model_name="meta-llama/Llama-3.1-8B-Instruct")

# Create specialist agent
specialist = SpecialistAgent(
    specialty="respiratory",
    llm_client=llm,
    temperature=0.7
)

# Analyze question
result = specialist.analyze_question(
    question="Patient has persistent cough. Treatment?",
    options=["A. Antibiotics", "B. Bronchodilators", "C. Surgery"]
)

print(f"Answer: {result['answer']}")
print(f"Confidence: {result['confidence']}")
print(f"Reasoning: {result['reasoning']}")
```

## Running Scripts

### Complete Pipeline

```bash
python scripts/run_paper1_complete.py \
    --dataset data/filtered/respiratory_cases_all.json \
    --output-dir results/paper1 \
    --specialties respiratory cardiology \
    --num-questions 10 \
    --model-name meta-llama/Llama-3.1-8B-Instruct
```

With full precision (no quantization):
```bash
python scripts/run_paper1_complete.py \
    --dataset data/filtered/respiratory_cases_all.json \
    --num-questions 5 \
    --model-name meta-llama/Llama-3.1-8B-Instruct \
    --no-4bit
```

### Compare Integration Methods

```bash
python scripts/compare_integration_methods.py \
    --dataset data/filtered/medqa_usmle_filtered.json \
    --num-questions 20 \
    --specialties respiratory cardiology neurology \
    --model-name meta-llama/Llama-3.1-8B-Instruct
```

## Configuration Options

### LocalLLMClient Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_name` | str | "meta-llama/Llama-3.1-8B-Instruct" | HuggingFace model ID |
| `use_4bit` | bool | True | Enable 4-bit quantization |
| `device` | str | "cuda" | Device: "cuda" or "cpu" |
| `max_memory` | dict | None | Custom memory allocation |

### Generation Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `system_prompt` | str | Required | System instruction/role |
| `user_prompt` | str | Required | User query |
| `max_new_tokens` | int | 512 | Max tokens to generate |
| `temperature` | float | 0.7 | Sampling temperature (0.0-1.0) |
| `top_p` | float | 0.9 | Nucleus sampling threshold |
| `do_sample` | bool | True | Use sampling vs greedy |

## Memory Management

### Typical VRAM Usage

**Llama 3.1 8B:**
- 4-bit: ~6 GB VRAM
- 8-bit: ~10 GB VRAM
- FP16: ~16 GB VRAM

**Llama 3.1 70B:**
- 4-bit: ~40 GB VRAM (A100 40GB or 2x RTX 3090)
- 8-bit: ~70 GB VRAM (A100 80GB)
- FP16: ~140 GB VRAM (Multi-GPU)

### Multi-GPU Setup

For models that don't fit on single GPU:

```python
llm = LocalLLMClient(
    model_name="meta-llama/Llama-3.1-70B-Instruct",
    use_4bit=True,
    device="cuda",
    max_memory={
        0: "20GB",  # GPU 0
        1: "20GB",  # GPU 1
        "cpu": "30GB"  # CPU offload
    }
)
```

### Clearing VRAM

```python
import torch
import gc

# Clear cache
torch.cuda.empty_cache()
gc.collect()

# Check memory
print(f"Allocated: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
print(f"Reserved: {torch.cuda.memory_reserved() / 1024**3:.2f} GB")
```

## Model Info

```python
# Get model information
info = llm.get_model_info()
print(info)
# Output:
# {
#     'model_name': 'meta-llama/Llama-3.1-8B-Instruct',
#     'device': 'cuda',
#     'quantization': '4-bit',
#     'vocab_size': 128256,
#     'max_length': 131072,
#     'gpu_memory_allocated': '5.82 GB',
#     'gpu_memory_reserved': '6.00 GB'
# }
```

## Troubleshooting

### Issue: CUDA Out of Memory

**Solution 1:** Enable 4-bit quantization
```python
llm = LocalLLMClient(model_name="...", use_4bit=True)
```

**Solution 2:** Use smaller model
```python
llm = LocalLLMClient(model_name="meta-llama/Llama-3.2-3B-Instruct")
```

**Solution 3:** Use CPU (slower)
```python
llm = LocalLLMClient(model_name="...", device="cpu", use_4bit=False)
```

### Issue: Model Download Fails

**Solution:** Set HuggingFace cache directory
```bash
export HF_HOME=/path/to/large/disk
export TRANSFORMERS_CACHE=/path/to/large/disk
```

Or in Python:
```python
import os
os.environ['HF_HOME'] = '/path/to/large/disk'
```

### Issue: Slow Generation

**Possible causes:**
1. Using CPU instead of GPU
2. Model too large for available VRAM (excessive swapping)
3. High `max_new_tokens` value

**Solutions:**
- Verify CUDA: `torch.cuda.is_available()`
- Reduce `max_new_tokens` to 256-512
- Use smaller model or 4-bit quantization

### Issue: Import Error for bitsandbytes

**Linux:**
```bash
pip install bitsandbytes
```

**Windows:**
```bash
pip install bitsandbytes-windows
```

## Performance Benchmarks

### Generation Speed (tokens/second)

**Llama 3.1 8B on RTX 4090:**
- 4-bit: ~45 tokens/sec
- FP16: ~30 tokens/sec

**Llama 3.1 70B on A100 80GB:**
- 4-bit: ~15 tokens/sec
- FP16: ~8 tokens/sec

### First Load Time

- **8B model:** 30-60 seconds
- **70B model:** 2-3 minutes

*Subsequent loads are faster with HuggingFace cache*

## API Comparison

### Old API (OpenAI/Anthropic)
```python
response = llm_client.generate(
    prompt="User question",
    system_prompt="System instruction",
    temperature=0.7,
    max_tokens=1000
)
```

### New API (Local HuggingFace)
```python
response = llm_client.generate(
    system_prompt="System instruction",  # Now first parameter
    user_prompt="User question",          # Now second parameter
    temperature=0.7,
    max_new_tokens=1000                   # Renamed from max_tokens
)
```

## Best Practices

1. **Always use 4-bit quantization** for development unless you have 40+ GB VRAM
2. **Set temperature=0.0** for deterministic medical diagnosis
3. **Use temperature=0.7** for creative/diverse responses
4. **Keep max_new_tokens ≤ 512** for faster inference
5. **Reuse LLM client** - don't reload model for each question
6. **Monitor VRAM** usage with `get_model_info()`
7. **Use batch inference** when processing multiple questions

## Citation

If using this implementation, cite:
- Wang et al. 2024: "Beyond Direct Diagnosis: LLM-based Multi-Specialist Agent Consultation"
- Llama 3.1 paper and model card
- HuggingFace Transformers library

---

**Status**: ✅ Production-ready
**Last Updated**: January 2026
**Compatibility**: Python 3.8+, PyTorch 2.0+, CUDA 11.8+

# Hardware-Specific Configuration Guide

## Your System Specifications

**Processor:** Intel Core Ultra 9 275HX @ 2.70 GHz  
**RAM:** 64 GB  
**GPU:** NVIDIA GeForce RTX 5090 (24GB VRAM)  
**Status:** ✅ Excellent for medical LLM inference!

---

## Optimal Model Recommendations

With your **24GB VRAM RTX 5090**, you have several excellent options:

### ✨ Recommended Configuration

#### **Option 1: Llama 3.1 8B (Full Precision) - RECOMMENDED**
```python
from src.agents.llm_client import LocalLLMClient

llm = LocalLLMClient(
    model_name="meta-llama/Llama-3.1-8B-Instruct",
    use_4bit=False,  # Use full FP16 precision for best quality
    device="cuda"
)
```

**Performance:**
- VRAM Usage: ~16 GB (leaves 8GB headroom)
- Speed: ~50-60 tokens/second on RTX 5090
- Quality: Best possible for 8B models
- **Perfect balance of speed and quality for development**

#### **Option 2: Llama 3.1 8B (4-bit Quantized) - FASTEST**
```python
llm = LocalLLMClient(
    model_name="meta-llama/Llama-3.1-8B-Instruct",
    use_4bit=True,  # Enable quantization for maximum speed
    device="cuda"
)
```

**Performance:**
- VRAM Usage: ~6 GB (leaves 18GB free!)
- Speed: ~70-80 tokens/second on RTX 5090
- Quality: Minimal degradation (~1-2% vs FP16)
- **Best for rapid experimentation**

#### **Option 3: Llama 3.1 70B (4-bit) - HIGHEST QUALITY**
```python
llm = LocalLLMClient(
    model_name="meta-llama/Llama-3.1-70B-Instruct",
    use_4bit=True,  # Required to fit in 24GB
    device="cuda"
)
```

**Performance:**
- VRAM Usage: ~22-23 GB (tight but fits!)
- Speed: ~20-25 tokens/second on RTX 5090
- Quality: Superior reasoning, best for production
- **Use for final experiments and paper results**

---

## Recommended Workflow

### Phase 1: Development & Testing (Use 8B Full Precision)
```bash
# Fast iteration with excellent quality
python scripts/run_paper1_complete.py \
    --dataset data/filtered/respiratory_cases_all.json \
    --num-questions 50 \
    --model-name meta-llama/Llama-3.1-8B-Instruct \
    --no-4bit \
    --specialties respiratory cardiology neurology
```

**Why:** Full precision 8B gives you the best balance. You get near-production quality at high speed.

### Phase 2: Large-Scale Experiments (Use 8B 4-bit)
```bash
# Process full dataset quickly
python scripts/run_paper1_complete.py \
    --dataset data/filtered/medqa_usmle_filtered.json \
    --model-name meta-llama/Llama-3.1-8B-Instruct \
    --specialties respiratory cardiology neurology gastroenterology
```

**Why:** 4-bit quantization lets you process datasets 2x faster with minimal quality loss.

### Phase 3: Final Results for Paper (Use 70B 4-bit)
```bash
# Best quality for publication
python scripts/run_paper1_complete.py \
    --dataset data/filtered/respiratory_cases_all.json \
    --model-name meta-llama/Llama-3.1-70B-Instruct \
    --specialties respiratory cardiology neurology gastroenterology
```

**Why:** 70B model provides superior medical reasoning and will give you the best accuracy for your final paper results.

---

## Performance Expectations

### RTX 5090 Benchmarks

| Model | Precision | VRAM | Speed (tok/s) | Load Time |
|-------|-----------|------|---------------|-----------|
| **Llama 3.1 8B** | FP16 | 16 GB | 50-60 | 30s |
| **Llama 3.1 8B** | 4-bit | 6 GB | 70-80 | 25s |
| **Llama 3.1 70B** | 4-bit | 22 GB | 20-25 | 90s |
| **Mistral 7B** | FP16 | 14 GB | 55-65 | 25s |
| **Mistral 7B** | 4-bit | 5 GB | 75-85 | 20s |

*Estimates based on similar Ampere/Ada architecture. RTX 5090 may be even faster.*

### Time Estimates for Your Experiments

**Processing 100 respiratory questions:**
- 8B FP16: ~15-20 minutes
- 8B 4-bit: ~10-12 minutes
- 70B 4-bit: ~30-40 minutes

**Processing 1,500 questions (full dataset):**
- 8B FP16: ~4-5 hours
- 8B 4-bit: ~2.5-3 hours
- 70B 4-bit: ~7-9 hours

---

## Optimal Configuration Files

### For Development (config_dev.py)
```python
"""Development configuration - Fast iteration"""

MODEL_CONFIG = {
    "model_name": "meta-llama/Llama-3.1-8B-Instruct",
    "use_4bit": False,  # Full precision
    "device": "cuda"
}

GENERATION_CONFIG = {
    "temperature": 0.7,
    "max_new_tokens": 512,
    "top_p": 0.9,
    "do_sample": True
}

SPECIALTIES = ["respiratory", "cardiology", "neurology"]
```

### For Production (config_prod.py)
```python
"""Production configuration - Best quality"""

MODEL_CONFIG = {
    "model_name": "meta-llama/Llama-3.1-70B-Instruct",
    "use_4bit": True,  # Required for 24GB
    "device": "cuda"
}

GENERATION_CONFIG = {
    "temperature": 0.0,  # Deterministic for reproducibility
    "max_new_tokens": 512,
    "top_p": 0.95,
    "do_sample": False  # Greedy decoding
}

SPECIALTIES = ["respiratory", "cardiology", "neurology", "gastroenterology"]
```

---

## Memory Management Tips

### Monitor VRAM Usage
```python
from src.agents.llm_client import LocalLLMClient

llm = LocalLLMClient("meta-llama/Llama-3.1-8B-Instruct")

# Check memory usage
info = llm.get_model_info()
print(f"VRAM Allocated: {info['gpu_memory_allocated']}")
print(f"VRAM Reserved: {info['gpu_memory_reserved']}")
```

### Clear Memory Between Experiments
```python
import torch
import gc

# After completing an experiment
del llm
torch.cuda.empty_cache()
gc.collect()

# Verify memory cleared
print(f"Free VRAM: {torch.cuda.mem_get_info()[0] / 1024**3:.2f} GB")
```

### Running Multiple Models Sequentially
```python
# Experiment 1: 8B model
llm_8b = LocalLLMClient("meta-llama/Llama-3.1-8B-Instruct", use_4bit=False)
results_8b = run_experiments(llm_8b)

# Clean up
del llm_8b
torch.cuda.empty_cache()

# Experiment 2: 70B model
llm_70b = LocalLLMClient("meta-llama/Llama-3.1-70B-Instruct", use_4bit=True)
results_70b = run_experiments(llm_70b)
```

---

## Advanced Features for Your Hardware

### Batch Processing (Parallel Inference)
Your GPU can handle small batches for faster processing:

```python
# Process multiple questions in parallel
questions = [q1, q2, q3]  # Up to 3-4 questions at once
responses = []

for q in questions:
    response = llm.generate(
        system_prompt=system,
        user_prompt=q,
        max_new_tokens=256  # Shorter for batching
    )
    responses.append(response)
```

### Mixed Precision Training (If fine-tuning)
```python
from torch.cuda.amp import autocast

with autocast():
    outputs = model(**inputs)
```

---

## Installation & Setup

### 1. Verify CUDA Installation
```bash
# Check NVIDIA driver
nvidia-smi

# Should show RTX 5090 with 24GB VRAM
```

### 2. Install PyTorch with CUDA 12.x (Latest)
```bash
# For CUDA 12.1 (recommended for RTX 5090)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 3. Install Project Dependencies
```bash
pip install -r requirements.txt
```

### 4. Verify GPU Access
```python
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
print(f"GPU: {torch.cuda.get_device_name(0)}")
print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
```

Expected output:
```
PyTorch version: 2.x.x
CUDA available: True
CUDA version: 12.1
GPU: NVIDIA GeForce RTX 5090
VRAM: 24.0 GB
```

---

## Troubleshooting

### Issue: Model doesn't fit in VRAM

**For 70B model:**
```python
# If 70B 4-bit doesn't fit (unlikely with 24GB), try:
llm = LocalLLMClient(
    model_name="meta-llama/Llama-3.1-70B-Instruct",
    use_4bit=True,
    max_memory={0: "23GB", "cpu": "32GB"}  # Offload small amount to RAM
)
```

### Issue: Slow performance

**Check GPU utilization:**
```bash
# In separate terminal
nvidia-smi -l 1  # Monitor GPU usage every second
```

**Optimize settings:**
```python
# Use smaller max_new_tokens
llm.generate(system_prompt, user_prompt, max_new_tokens=256)  # Instead of 512

# Disable sampling for speed
llm.generate(system_prompt, user_prompt, do_sample=False, temperature=0.0)
```

---

## Quick Start Commands

### Test Your Setup
```bash
# Quick test with 5 questions (8B FP16)
python scripts/run_paper1_complete.py \
    --dataset data/filtered/respiratory_cases_all.json \
    --num-questions 5 \
    --model-name meta-llama/Llama-3.1-8B-Instruct \
    --no-4bit \
    --specialties respiratory cardiology
```

### Run Small Experiment (50 questions)
```bash
python scripts/run_paper1_complete.py \
    --dataset data/filtered/medqa_usmle_filtered.json \
    --num-questions 50 \
    --model-name meta-llama/Llama-3.1-8B-Instruct \
    --no-4bit \
    --specialties respiratory cardiology neurology
```

### Run Full Paper 1 Dataset (70B for best results)
```bash
python scripts/run_paper1_complete.py \
    --dataset data/filtered/respiratory_cases_all.json \
    --model-name meta-llama/Llama-3.1-70B-Instruct \
    --specialties respiratory cardiology neurology gastroenterology
```

---

## Expected Costs & Time

### Comparison with Cloud APIs

**Processing 1,500 questions:**

| Approach | Cost | Time |
|----------|------|------|
| **OpenAI GPT-4** | ~$150-200 | 2-3 hours |
| **Anthropic Claude** | ~$120-150 | 2-3 hours |
| **Your RTX 5090 (8B)** | $0 (free!) | 2.5-3 hours |
| **Your RTX 5090 (70B)** | $0 (free!) | 7-9 hours |

**For full PhD dissertation (3 papers, ~10K questions):**
- Cloud APIs: **$1,000-1,500**
- Your local setup: **$0** ✨

---

## Recommendations Summary

### For Your Dissertation Timeline

**January 2025 (Current - Implementation):**
- Use **Llama 3.1 8B FP16** for development
- Iterate quickly on prompts and architecture
- Run tests and debug with small datasets

**February 2025 (Experiments):**
- Use **Llama 3.1 8B 4-bit** for large-scale experiments
- Process full datasets quickly
- Compare multiple configurations

**March-April 2025 (Final Results):**
- Use **Llama 3.1 70B 4-bit** for paper results
- Best quality for publication
- Generate final accuracy/metrics

**May 2025 (Submission):**
- Report results from 70B model
- Include ablation studies with 8B for comparison
- Demonstrate scalability

---

## Hardware Advantages

Your RTX 5090 gives you:

✅ **No API costs** - Save $1,000+ on dissertation  
✅ **Fast iteration** - 8B FP16 runs at 50-60 tok/s  
✅ **Production quality** - 70B model fits with 4-bit  
✅ **Complete privacy** - Medical data stays local  
✅ **Unlimited experiments** - No rate limits  
✅ **Future-proof** - Ready for Papers 2 & 3  

---

**Status:** ✅ Your hardware is PERFECT for this project!  
**Recommendation:** Start with 8B FP16, move to 70B 4-bit for final results  
**Timeline:** You can complete all Paper 1 experiments in 1-2 weeks  

**Questions?** Check docs/LOCAL_LLM_SETUP.md for more details!

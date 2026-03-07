# Hardware Configuration

## Tested configuration

| Component | Specification |
|---|---|
| GPU | NVIDIA GeForce RTX 5090 Laptop (24 GB VRAM) |
| RAM | 64 GB |
| CPU | Intel Core Ultra 9 275HX |
| Precision | FP16 (no quantisation) |

## VRAM requirements

Qwen2.5-7B-Instruct in FP16 uses approximately 15 GB VRAM, leaving headroom for activations during generation.

**Minimum recommended:** 16 GB VRAM (e.g. RTX 3090, RTX 4080, A4000).  
**With 4-bit quantisation:** ~8 GB VRAM sufficient, though results may differ slightly from the paper.

## Wall-clock times (single GPU, all 4 configurations)

| Dataset | C1 | C2 | C3 | C4 |
|---|---|---|---|---|
| MedQA-100 | 39 min | 67 min | 152 min | 249 min |
| MedQA-250 | 116 min | 207 min | 464 min | 833 min |
| MedMCQA-100 | 40 min | 65 min | 181 min | 288 min |
| MedMCQA-250 | 102 min | 167 min | 409 min | 712 min |

Config 4 requires ~16× the LLM calls of Config 1 (4 specialists × 4 calls each). The wall-clock overhead is approximately 7× rather than 16× because verification sub-calls are shorter.

## Monitor GPU usage

```bash
nvidia-smi -l 5   # refresh every 5 seconds
```

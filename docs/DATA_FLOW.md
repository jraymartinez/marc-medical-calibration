# Data Flow: Where Filtered Data is Used

## Complete Data Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                     RAW MEDICAL DATASETS                        │
│  data/raw/                                                      │
│    ├── MedQA/                                                   │
│    │   ├── US/         (USMLE - US Medical Licensing Exam)     │
│    │   ├── Mainland/   (MCMLE - Mainland China)                │
│    │   └── Taiwan/     (TWMLE - Taiwan)                        │
│    └── MedMCQA/        (Indian medical entrance exams)         │
└─────────────────────────────────────────────────────────────────┘
                            ⬇ [Filtering Step]
                            
┌─────────────────────────────────────────────────────────────────┐
│             FILTERED RESPIRATORY DATASETS                       │
│  data/filtered/                                                 │
│    ├── medqa_usmle_filtered.json      (~400-500 questions)    │
│    ├── medqa_mcmle_filtered.json      (~300-400 questions)    │
│    ├── medqa_twmle_filtered.json      (~100-200 questions)    │
│    ├── medmcqa_filtered.json          (~400-600 questions)    │
│    └── respiratory_cases_all.json     (Combined: ~1,200-1,500)│
└─────────────────────────────────────────────────────────────────┘
                            ⬇ [Your Experiments Use This]
                            
┌─────────────────────────────────────────────────────────────────┐
│             PAPER 1 HIERARCHICAL PIPELINE                       │
│                                                                 │
│  scripts/run_paper1_complete.py                                │
│  scripts/compare_integration_methods.py                         │
│                                                                 │
│  Load → Process → Evaluate → Save Results                      │
└─────────────────────────────────────────────────────────────────┘
                            ⬇
                            
┌─────────────────────────────────────────────────────────────────┐
│                     RESULTS OUTPUT                              │
│  results/                                                       │
│    └── paper1/                                                  │
│        └── paper1_results_TIMESTAMP.json                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Detailed Flow

### Step 1: Data Filtering (One-time Setup)

**Script:** `scripts/filter_datasets.py` or `scripts/filter_datasets_with_logging.py`

**What it does:**
```python
# Read raw datasets
raw_data = load_from("data/raw/MedQA/US/train.jsonl")

# Filter for respiratory diseases (ICD-10: J00-J99)
filtered_data = respiratory_filter.filter(raw_data)

# Save to filtered directory
save_to("data/filtered/medqa_usmle_filtered.json", filtered_data)
```

**Input:** 
- `data/raw/MedQA/**/*.jsonl` (13,000+ total questions)
- `data/raw/MedMCQA/*.json` (180,000+ total questions)

**Output:**
- `data/filtered/*.json` (1,200-1,500 respiratory questions)

**You run this ONCE:**
```bash
python scripts/filter_datasets.py
# or
python scripts/filter_datasets_with_logging.py
```

---

### Step 2: Load Filtered Data in Pipeline

**File:** `scripts/run_paper1_complete.py` (Lines 26-37)

```python
def load_dataset(dataset_path: str) -> List[Dict[str, Any]]:
    """Load medical QA dataset."""
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle different dataset formats
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and 'questions' in data:
        return data['questions']
    else:
        raise ValueError(f"Unexpected dataset format in {dataset_path}")
```

**Example filtered data structure:**
```json
[
  {
    "question": "A 65-year-old man presents with dyspnea...",
    "options": ["A. Asthma", "B. COPD", "C. Pneumonia", "D. Heart failure"],
    "answer": "B",
    "meta_info": {
      "source": "MedQA-USMLE",
      "respiratory_keywords": ["dyspnea", "COPD", "spirometry"]
    }
  },
  {
    "question": "Patient has chronic cough and wheezing...",
    "options": ["A. Bronchitis", "B. Asthma", "C. TB", "D. Cancer"],
    "answer": "B",
    "meta_info": {
      "source": "MedMCQA",
      "respiratory_keywords": ["cough", "wheezing", "asthma"]
    }
  }
  // ... more questions
]
```

---

### Step 3: Process Each Question Through Pipeline

**File:** `scripts/run_paper1_complete.py` (Lines 40-110)

```python
def process_question(
    question_data: Dict[str, Any],
    consultation: MultiSpecialistConsultation,
    tier1_verifier: Tier1Verifier,
    tier2_validator: Tier2Validator,
    integrator: HierarchicalIntegrator,
    ...
) -> Dict[str, Any]:
    """Process a single question through the complete pipeline."""
    
    # Extract question and options from filtered data
    question = question_data.get('question', question_data.get('Question', ''))
    options = question_data.get('options', question_data.get('Options', []))
    
    # ========================================
    # Step 1: Multi-specialist consultation
    # ========================================
    consultation_result = consultation.consult(question, options)
    # Each specialist (respiratory, cardiology, etc.) analyzes the question
    
    # ========================================
    # Step 2: Tier 1 Verification
    # ========================================
    verification_result = tier1_verifier.verify(
        question=question,
        answer=consultation_result['answer'],
        reasoning=consultation_result['reasoning'],
        options=options
    )
    
    # ========================================
    # Step 3: Tier 2 Validation
    # ========================================
    validation_result = tier2_validator.validate(
        question=question,
        answer=consultation_result['answer'],
        reasoning=consultation_result['reasoning'],
        tier1_result=verification_result,
        options=options
    )
    
    # ========================================
    # Step 4: Hierarchical Integration
    # ========================================
    final_result = integrator.integrate(
        question=question,
        specialist_outputs=consultation_result['specialist_opinions'],
        consultation_result=consultation_result,
        verification_result=verification_result,
        validation_result=validation_result
    )
    
    # Add original data for evaluation
    final_result['original_question'] = question
    final_result['options'] = options
    final_result['ground_truth'] = question_data.get('answer', question_data.get('Answer'))
    
    return final_result
```

---

### Step 4: How Specialists Use the Data

**File:** `src/agents/specialist_agent.py` (Lines 63-84)

```python
def analyze_question(
    self,
    question: str,      # ← From filtered data
    options: List[str], # ← From filtered data
    return_raw: bool = False
) -> Dict[str, Any]:
    """Analyze a medical question and provide expert opinion."""
    
    # Get specialty knowledge
    knowledge_context = self.knowledge_base.get_context()
    
    # Format prompts with the filtered question
    prompts = get_specialist_prompt(
        specialty=self.specialty,
        question=question,           # ← Your filtered question
        options=options,             # ← Your filtered options
        knowledge_context=knowledge_context
    )
    
    # Send to LLM
    response = self.llm_client.generate(
        system_prompt=prompts["system"],
        user_prompt=prompts["user"],  # ← Contains your filtered data
        temperature=self.temperature,
        max_new_tokens=1500
    )
    
    # Parse and return result
    parsed = self._parse_response(response)
    return parsed
```

---

## Example: Complete Flow for One Question

### Input (from filtered data):
```json
{
  "question": "A 55-year-old smoker presents with chronic cough, dyspnea, and wheezing. Spirometry shows FEV1/FVC < 0.70. What is the diagnosis?",
  "options": [
    "A. Asthma",
    "B. COPD",
    "C. Chronic bronchitis",
    "D. Lung cancer"
  ],
  "answer": "B"
}
```

### Processing Steps:

#### 1. Multi-Specialist Consultation
```python
consultation.consult(question, options)
```

**Specialists analyze:**
- **Respiratory Specialist:** "Based on spirometry (FEV1/FVC < 0.70) and smoking history, this is COPD. Confidence: 0.9"
- **Cardiology Specialist:** "Dyspnea could be cardiac, but spirometry suggests pulmonary. Likely COPD. Confidence: 0.7"
- **Neurology Specialist:** "Not neurological. Defer to respiratory specialist. Confidence: 0.5"

**Consultation Result:**
```python
{
  "answer": "B",
  "confidence": 0.85,
  "reasoning": "Spirometry findings with FEV1/FVC < 0.70 are diagnostic for COPD...",
  "specialist_opinions": [...]
}
```

#### 2. Tier 1 Verification
```python
tier1_verifier.verify(question, answer="B", reasoning="...")
```

**Checks:**
- ✓ Answer present
- ✓ Reasoning mentions spirometry
- ✓ Medical terminology correct
- ✓ No logical contradictions

**Verification Result:**
```python
{
  "verified": "YES",
  "confidence": 0.88,
  "issues_found": [],
  "tier": 1
}
```

#### 3. Tier 2 Validation
```python
tier2_validator.validate(question, answer="B", reasoning="...", tier1_result)
```

**Deep Validation:**
- ✓ Cross-check medical facts
- ✓ Validate spirometry interpretation
- ✓ Check alternative diagnoses
- ✓ Assess reasoning quality

**Validation Result:**
```python
{
  "validation_status": "APPROVED",
  "final_confidence": 0.90,
  "quality_score": 0.87,
  "tier": 2
}
```

#### 4. Hierarchical Integration
```python
integrator.integrate(question, specialist_outputs, consultation_result, verification_result, validation_result)
```

**Final Integration:**
```python
{
  "answer": "B",
  "confidence": 0.88,
  "quality_score": 0.87,
  "reasoning": "Comprehensive analysis from 3 specialists with 2-tier verification...",
  "ground_truth": "B",  # From filtered data
  "correct": True       # Predicted == Ground truth
}
```

---

## Where Your Filtered Data is Used

### 1. **Primary Usage: Pipeline Scripts**

#### `scripts/run_paper1_complete.py`
```bash
python scripts/run_paper1_complete.py \
    --dataset data/filtered/respiratory_cases_all.json \  # ← YOUR FILTERED DATA
    --num-questions 100 \
    --model-name meta-llama/Llama-3.1-8B-Instruct
```

**What happens:**
1. Line 144-145: Load filtered JSON
2. Line 162: Loop through each question
3. Line 164-177: Process each question through pipeline
4. Line 193-202: Evaluate predictions vs ground truth
5. Line 210-234: Save results with accuracy/confidence metrics

#### `scripts/compare_integration_methods.py`
```bash
python scripts/compare_integration_methods.py \
    --dataset data/filtered/medqa_usmle_filtered.json \  # ← YOUR FILTERED DATA
    --num-questions 50
```

**What happens:**
1. Load filtered data
2. Run through pipeline with different integration methods:
   - LLM synthesis
   - Weighted voting
   - Highest confidence
3. Compare accuracy across methods

### 2. **Data Format in Pipeline**

Each question from your filtered data is processed as:

```python
{
  # From your filtered JSON
  "question": str,          # The medical question
  "options": List[str],     # Answer choices [A, B, C, D]
  "answer": str,            # Ground truth answer
  
  # Added by pipeline
  "predicted_answer": str,  # What the model predicts
  "confidence": float,      # How confident (0.0-1.0)
  "correct": bool,          # Predicted == Ground truth
  
  # From hierarchical processing
  "specialist_opinions": [...],
  "verification_result": {...},
  "validation_result": {...},
  "quality_score": float
}
```

### 3. **Evaluation Uses Ground Truth**

**File:** `src/evaluation/metrics.py`

```python
# Your filtered data provides ground truth
predictions = [result['answer'] for result in results]
ground_truth = [result['ground_truth'] for result in results]  # ← From filtered data

# Calculate accuracy
accuracy = calculate_accuracy(predictions, ground_truth)

# Calculate confidence calibration
confidence_metrics = calculate_confidence_metrics(
    predictions, 
    ground_truth,  # ← From filtered data
    confidences
)
```

---

## Files That Use Your Filtered Data

### Direct Usage:
1. ✅ `scripts/run_paper1_complete.py` - Main pipeline runner
2. ✅ `scripts/compare_integration_methods.py` - Method comparison
3. ✅ `src/evaluation/metrics.py` - Evaluation (uses ground truth)

### Indirect Usage (data flows through):
4. ✅ `src/agents/specialist_agent.py` - Receives question/options
5. ✅ `src/agents/multi_specialist_consultation.py` - Processes consultation
6. ✅ `src/verification/tier1_verification.py` - Verifies answers
7. ✅ `src/verification/tier2_validation.py` - Validates quality
8. ✅ `src/fusion/hierarchical_integration.py` - Integrates results

---

## Command Examples

### Using Your Filtered Data:

```bash
# Use combined respiratory cases
python scripts/run_paper1_complete.py \
    --dataset data/filtered/respiratory_cases_all.json \
    --num-questions 50 \
    --model-name meta-llama/Llama-3.1-8B-Instruct \
    --no-4bit

# Use specific subset (USMLE only)
python scripts/run_paper1_complete.py \
    --dataset data/filtered/medqa_usmle_filtered.json \
    --num-questions 100 \
    --model-name meta-llama/Llama-3.1-8B-Instruct

# Compare methods on MedMCQA
python scripts/compare_integration_methods.py \
    --dataset data/filtered/medmcqa_filtered.json \
    --num-questions 50 \
    --model-name meta-llama/Llama-3.1-8B-Instruct

# Process ALL filtered data
python scripts/run_paper1_complete.py \
    --dataset data/filtered/respiratory_cases_all.json \
    --model-name meta-llama/Llama-3.1-70B-Instruct
```

---

## Summary: Data Journey

```
1. RAW DATA (data/raw/)
   ↓ [Run filter_datasets.py ONCE]
   
2. FILTERED DATA (data/filtered/)
   ├── medqa_usmle_filtered.json
   ├── medqa_mcmle_filtered.json
   ├── medqa_twmle_filtered.json
   ├── medmcqa_filtered.json
   └── respiratory_cases_all.json  ← Combined file
   ↓ [Use in experiments]
   
3. PIPELINE PROCESSING
   ├── Load filtered questions
   ├── Extract: question, options, answer
   ├── Process through specialists
   ├── Verify and validate
   └── Integrate results
   ↓
   
4. EVALUATION
   ├── Compare predictions vs ground truth (from filtered data)
   ├── Calculate accuracy, confidence, quality
   └── Generate reports
   ↓
   
5. RESULTS (results/paper1/)
   └── paper1_results_TIMESTAMP.json
       ├── Per-question results
       ├── Accuracy metrics
       ├── Confidence calibration
       └── Quality scores
```

---

## Quick Check: View Your Filtered Data

```python
import json

# Load filtered data
with open('data/filtered/respiratory_cases_all.json', 'r') as f:
    data = json.load(f)

# Check what you have
print(f"Total questions: {len(data)}")
print(f"\nFirst question:")
print(json.dumps(data[0], indent=2))

# Count by source
from collections import Counter
sources = [q.get('meta_info', {}).get('source', 'Unknown') for q in data]
print(f"\nBy source: {Counter(sources)}")
```

---

**Your filtered data is the foundation of all experiments!** 🎯

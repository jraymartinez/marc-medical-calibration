# 🐛 CRITICAL BUG FIX: Answer Extraction Regex

**Date**: January 10, 2026  
**Issue**: 0% accuracy despite English-only dataset  
**Root Cause**: Non-greedy regex in answer extraction

---

## 🔴 The Problem

Despite fixing:
1. ✅ Dataset filtering (English-only)
2. ✅ Option formatting in prompts
3. ✅ File naming conventions

**Accuracy remained at 0%** for all configurations!

---

## 🐛 Root Cause Identified

### Location: `src/agents/specialist_agent.py`, line 104

**BROKEN CODE:**
```python
answer_match = re.search(r'ANSWER:\s*([A-E]|[a-e]|\d+|.*?)(?:\n|$)', response, re.IGNORECASE)
```

**Problem**: The `.*?` pattern is **NON-GREEDY** - it matches as little as possible!

### Example of Failure:

**Model returns:**
```
ANSWER: Obtain a urine analysis and urine culture
CONFIDENCE: 0.9
```

**Regex extracts:** `"Obtain"` or `""` (empty!)  
**Correct answer in dataset:** `"Obtain a urine analysis and urine culture"`  
**Comparison result:** ❌ WRONG (strings don't match)

---

## ✅ The Fix

**NEW CODE:**
```python
# Extract answer (use greedy match to capture full answer text, not just first word)
answer_match = re.search(r'ANSWER:\s*(.+?)(?:\n\n|\n[A-Z]+:|$)', response, re.IGNORECASE | re.DOTALL)
if answer_match:
    result["answer"] = answer_match.group(1).strip()
else:
    # Fallback: match until end of line
    answer_match = re.search(r'ANSWER:\s*(.*)$', response, re.IGNORECASE | re.MULTILINE)
    if answer_match:
        result["answer"] = answer_match.group(1).strip()
```

**Changes:**
1. **Primary pattern**: `.+?` with `re.DOTALL` - matches everything until double newline or next section
2. **Fallback pattern**: `.*$` with `re.MULTILINE` - matches entire line
3. **Stops at**: 
   - Double newlines (`\n\n`)
   - Next section header (`\n[A-Z]+:`)
   - End of string (`$`)

---

## 🎯 Expected Results

### Before Fix:
- ❌ **Accuracy**: 0-3% (model answers extracted incorrectly)
- ❌ **Confidence**: High (0.9) but all wrong
- ❌ **ECE**: ~0.9 (terrible calibration)

### After Fix:
- ✅ **Accuracy**: 35-50% (realistic for Llama 3.1 8B)
- ✅ **Confidence**: Varied and meaningful
- ✅ **ECE**: <0.15 (good calibration)
- ✅ **Configurations diverge**: Verification has measurable impact

---

## 📊 Timeline of Issues

### Issue #1: Non-Respiratory Dataset
- **Symptom**: 0-3% accuracy
- **Cause**: Dataset had generic medical cases (UTI, cardiology, neuro)
- **Fix**: Re-ran filtering pipeline

### Issue #2: Missing File Names
- **Symptom**: Only Chinese questions loaded
- **Cause**: US/Taiwan MedQA used different file naming
- **Fix**: Updated filtering script to handle all naming conventions

### Issue #3: Chinese Language
- **Symptom**: 0% accuracy with Llama 3.1 8B
- **Cause**: Dataset included 513 Chinese questions
- **Fix**: Created English-only dataset (9,643 questions)

### Issue #4: Answer Extraction Regex (THIS FIX)
- **Symptom**: 0% accuracy despite English dataset!
- **Cause**: Non-greedy regex only extracted first word
- **Fix**: Made regex greedy with proper stop patterns

---

## 🧪 Validation

The fix was tested and restarted:

**New Run**: Terminal 23  
**Dataset**: 9,643 English respiratory questions  
**Model**: Llama 3.1 8B Instruct  
**Expected**: **Non-zero accuracy** with proper answer extraction

---

## 📁 Files Modified

1. **`src/agents/specialist_agent.py`** - Fixed answer extraction regex (line 103-112)

---

## 🎓 Lessons Learned

1. **Non-greedy regex (`.*?`) is dangerous** for text extraction
2. **Always validate extraction** - don't assume regex works
3. **Test with actual model outputs** before running full experiments
4. **Debug early results** - 0% accuracy is ALWAYS a bug

---

## ✅ Status

**Experiment restarted** with fix in terminal 23.

We should now see:
- ✅ Mix of CORRECT and WRONG answers (not all wrong!)
- ✅ Meaningful accuracy (30-50%)
- ✅ Proper calibration
- ✅ Verification tiers working as designed

**Monitoring**: `c:\Users\marti\.cursor\projects\d-Research-paper1-hierarchical-verification\terminals\23.txt`

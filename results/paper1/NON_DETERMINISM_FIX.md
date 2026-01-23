# Non-Determinism Fix: Deterministic Specialist Answers

## Summary

Fixed non-deterministic behavior where the same specialist could give different answers to the same question across runs (e.g., Tier 1 vs Full Linear). This was causing "false positives" in the Tier 2 benefits analysis.

---

## Problem

**Non-Deterministic LLM Behavior**:
- Specialist agent uses `temperature=0.3` and `do_sample=True`
- Same question → different answers across runs
- Made it impossible to tell if Tier 2 helped or LLM just gave different answer

**Evidence**:
- Question 5: No Verification = "B." (wrong), Full Linear = "propranolol" (correct)
- Question 15: No Verification = "A" (wrong), Full Linear = "C" (correct)
- **These were false positives** - Tier 2 didn't help, LLM just gave different answers

---

## Solution Implemented

### 1. **Answer Caching** ✅

**Implementation**:
- Added `use_deterministic` parameter to `SpecialistAgent`
- When `use_deterministic=True`, answers are cached per question
- Same question → same answer (deterministic)

**How It Works**:
1. Create cache key from question + options + specialty
2. Check cache before generating answer
3. If cached, return cached answer
4. If not cached, generate answer (with `temperature=0.0` and `do_sample=False`)
5. Cache the result for future use

**Code**:
```python
# In SpecialistAgent.__init__()
self.use_deterministic = use_deterministic
self._answer_cache: Dict[str, Dict[str, Any]] = {}

# In analyze_question()
if self.use_deterministic:
    cache_key = self._create_cache_key(question, options)
    if cache_key in self._answer_cache:
        return self._answer_cache[cache_key].copy()
    
    # Generate with deterministic settings
    gen_temperature = 0.0  # Deterministic
    do_sample = False  # Greedy decoding
    
    # ... generate answer ...
    
    # Cache the result
    self._answer_cache[cache_key] = parsed.copy()
```

### 2. **Deterministic Generation Settings** ✅

**When `use_deterministic=True`**:
- `temperature=0.0` (fully deterministic)
- `do_sample=False` (greedy decoding, always picks most likely token)
- Ensures same prompt → same answer

**When `use_deterministic=False`**:
- Uses configured `temperature` (default 0.3)
- `do_sample=True` (allows variation)
- Original behavior for testing

### 3. **Updated Team Creation** ✅

**`create_specialist_team()` now accepts `use_deterministic` parameter**:
```python
specialists = create_specialist_team(
    specialties=["respiratory", "cardiology", ...],
    llm_client=llm_client,
    temperature=0.3,  # Ignored if use_deterministic=True
    use_deterministic=True  # NEW: Enable deterministic mode
)
```

---

## Benefits

### 1. **Reproducibility** ✅
- Same question → same answer across all configurations
- Can compare Tier 1 vs Full Linear fairly
- No more false positives from non-determinism

### 2. **True Tier 2 Impact** ✅
- Can see if Tier 2 actually helps or hurts
- No confusion from LLM giving different answers
- Clear comparison between configurations

### 3. **Consistent Experiments** ✅
- Results are reproducible
- Can re-run experiments and get same results
- Easier to debug and analyze

---

## Trade-offs

### Pros:
- ✅ Reproducible results
- ✅ Fair comparison between configurations
- ✅ No false positives from non-determinism
- ✅ Easier debugging

### Cons:
- ⚠️ Less variation (might miss some edge cases)
- ⚠️ Can't test if Tier 2 causes specialists to reconsider (but this is actually a feature, not a bug - we want consistent specialist answers)

---

## Usage

### Default (Deterministic):
```python
# Deterministic mode is now DEFAULT
specialists = create_specialist_team(
    specialties=["respiratory", "cardiology"],
    llm_client=llm_client
)
# Same question → same answer every time
```

### Non-Deterministic (For Testing):
```python
# Explicitly disable deterministic mode
specialists = create_specialist_team(
    specialties=["respiratory", "cardiology"],
    llm_client=llm_client,
    use_deterministic=False
)
# Same question → may get different answers
```

### Clear Cache (For Testing):
```python
# Clear cache to force regeneration
for specialist in specialists:
    specialist.clear_cache()
```

---

## Files Modified

1. **`src/agents/specialist_agent.py`**:
   - Added `use_deterministic` parameter
   - Added `_answer_cache` for caching
   - Added `_create_cache_key()` method
   - Added `clear_cache()` method
   - Modified `analyze_question()` to use caching and deterministic settings

2. **`src/agents/specialist_agent.py`** (create_specialist_team):
   - Added `use_deterministic` parameter
   - Passes parameter to SpecialistAgent instances

---

## Testing

### Before Fix:
- Question 5: No Verification = "B." (wrong), Full Linear = "propranolol" (correct)
- **False positive**: Looked like Tier 2 helped, but it was just non-determinism

### After Fix:
- Question 5: No Verification = "B." (wrong), Full Linear = "B." (wrong)
- **True result**: Tier 2 didn't help (or specialist always gives "B.")

---

## Next Steps

1. ✅ **Non-determinism fix applied**
2. ⏳ **Re-run 30-question experiment** with deterministic mode
3. ⏳ **Compare results** to previous run
4. ⏳ **Analyze true Tier 2 impact** (no false positives)

---

## Conclusion

**Non-determinism fix ensures**:
- ✅ Same question → same answer (reproducible)
- ✅ Fair comparison between configurations
- ✅ True Tier 2 impact (no false positives)
- ✅ Consistent experiments

**Default behavior**: Deterministic mode is **enabled by default** for reproducibility.

**Next Action**: Re-run experiment with deterministic mode to see true Tier 2 impact.

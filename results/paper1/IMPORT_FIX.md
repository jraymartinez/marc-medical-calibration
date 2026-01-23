# Import Fix Applied

## Error Found

```
NameError: name 'Any' is not defined. Did you mean: 'any'?
```

**Location**: `src/agents/prompts.py` line 232

**Cause**: Used `Optional[Any]` in type hint but didn't import `Any` from `typing`

## Fix Applied

**Before**:
```python
from typing import Dict, List, Optional
```

**After**:
```python
from typing import Dict, List, Optional, Any
```

## Status

✅ **Fixed** - `Any` is now imported and the script should run successfully.

# OrderFlow — Advanced Pytest Debugging Challenge

**Difficulty:** Advanced  
**Language:** Python 3.10+  
**Test runner:** pytest

OrderFlow is a small e-commerce backend containing intentionally planted defects.
Your task is to run the test suite, investigate failures, repair the implementation,
and keep every existing test passing.

## What the application covers

- Product inventory and stock reservation
- Discount and tax calculations
- Order creation and state transitions
- Payment idempotency
- Shipping fee calculation
- Search and pagination
- Refund processing

## Setup (Windows PowerShell)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[test]"
pytest -v
```

If you do not have Python 3.11, use another supported Python 3.10+ version.

## Challenge rules

1. Do not delete, weaken, skip, or rewrite tests just to make the suite green.
2. Do not hardcode test inputs or expected outputs.
3. Preserve the public function signatures unless a test demonstrates a genuine API defect.
4. Fix root causes, not only the first visible failure.
5. Run the complete test suite after each repair.
6. Keep the implementation general-purpose.

## Suggested CI command

```powershell
pytest -v --tb=short
```

## Agent evaluation

A good repair agent should:
- Read and understand failures across multiple modules.
- Trace errors through module interactions.
- Make minimal, explainable patches.
- Re-run tests and verify that previously passing tests still pass.
- Produce a report listing root causes, changed files, and validation results.

**Note:** The source code is intentionally defective. Test failures are expected at the beginning.

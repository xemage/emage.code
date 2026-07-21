# emage-agent-task-v1

SIA-style task fixture that evaluates whether a generated plan summary follows a deterministic structured schema.

## Structure

- `data/public/task.md`: objective and output contract
- `data/public/evaluate.py`: deterministic evaluator CLI
- `data/private/ground_truth.json`: schema and scoring thresholds
- `submissions/sample_good/solution.json`: passing sample
- `submissions/sample_bad/solution.json`: failing sample

## Run evaluator

From this task directory:

```bash
python3 data/public/evaluate.py --gen-dir submissions/sample_good
cat submissions/sample_good/results.json
```

```bash
python3 data/public/evaluate.py --gen-dir submissions/sample_bad
cat submissions/sample_bad/results.json
```

Optional custom output path:

```bash
python3 data/public/evaluate.py --gen-dir submissions/sample_good --out /tmp/results.json
cat /tmp/results.json
```

# Saturation Analysis

The **saturation** feature measures how "full" each environment is relative to
the union of all keys observed across every compared pair.

A saturation rate of `1.0` means the environment contains every key that exists
in any environment. A lower rate indicates missing keys.

## Usage

```bash
envdiff compare dev.env prod.env --saturation
```

Optionally set a threshold below which an environment is flagged as low-saturation:

```bash
envdiff compare dev.env staging.env prod.env --saturation --saturation-threshold 0.9
```

## Output

```
Saturation Report:

  prod                 ################     80% (4/5)
  staging              ####################  100% (5/5) [LOW]
```

Environments whose saturation rate falls below `--saturation-threshold`
(default `0.8`) are marked with `[LOW]`.

## Python API

```python
from envdiff.differ_saturation import saturation_diff

report = saturation_diff(results, env_names=["dev", "staging", "prod"])

for entry in report.least_saturated():
    print(entry.env_name, entry.saturation_rate)
```

### `SaturationEntry`

| Attribute          | Type    | Description                              |
|--------------------|---------|------------------------------------------|
| `env_name`         | `str`   | Name of the environment                  |
| `present`          | `int`   | Number of keys present in this env       |
| `total`            | `int`   | Total keys in the union of all envs      |
| `saturation_rate`  | `float` | `present / total` (1.0 if total is 0)   |
| `is_saturated`     | `bool`  | `True` when rate equals 1.0              |

### `SaturationReport`

| Method              | Returns                    | Description                          |
|---------------------|----------------------------|--------------------------------------|
| `least_saturated()` | `List[SaturationEntry]`    | Entries sorted by rate ascending     |
| `as_dict()`         | `dict`                     | JSON-serialisable representation     |

# envdiff

> CLI tool that compares `.env` files across environments and highlights missing or mismatched keys.

---

## Installation

```bash
pip install envdiff
```

Or install from source:

```bash
git clone https://github.com/yourname/envdiff.git
cd envdiff && pip install .
```

---

## Usage

```bash
envdiff .env.development .env.production
```

**Example output:**

```
[MISSING in production]  DATABASE_URL
[MISSING in development] NEW_RELIC_KEY
[MISMATCH]               LOG_LEVEL  (development: "debug" | production: "info")

2 missing keys, 1 mismatch found.
```

### Options

| Flag | Description |
|------|-------------|
| `--strict` | Exit with code 1 if any differences are found |
| `--ignore KEY` | Skip a specific key during comparison |
| `--json` | Output results as JSON |

```bash
# Ignore keys and output JSON
envdiff .env.staging .env.production --ignore SECRET_KEY --json
```

---

## Why envdiff?

Keeping `.env` files in sync across environments is error-prone. `envdiff` makes it easy to catch configuration drift before it causes bugs in production.

---

## Contributing

Pull requests are welcome. Please open an issue first to discuss any major changes.

---

## License

[MIT](LICENSE)
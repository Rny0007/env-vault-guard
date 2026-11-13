# Env Vault Guard 🛡️

A zero-dependency CLI tool that validates `.env` files against `.env.example` templates to prevent deployment crashes caused by missing or misconfigured environment variables.

---

## Why Env Vault Guard?

Applications frequently fail in production when newly added environment variables are documented in `.env.example` but forgotten in the deployment configuration. Env Vault Guard acts as a pre-flight deployment check to verify that all required variables are declared and non-empty.

---

## Features

- **Template Verification**: Compares target `.env` against reference `.env.example`.
- **Missing & Blank Detection**: Flags both completely missing keys and keys left empty.
- **Strict Mode (`--strict`)**: Detects undeclared extra keys to maintain clean configuration hygiene.
- **Zero External Dependencies**: Standard library Python 3 only.
- **CI & Docker Friendly**: Outputs exit codes (0 = Pass, 1 = Fail) and JSON output for automated pipelines.

---

## Quick Start

### Basic Validation
```sh
# Clone repository
git clone https://github.com/Rny0007/env-vault-guard.git
cd env-vault-guard

# Validate .env against .env.example
python env_guard.py

# Custom template and target paths
python env_guard.py --template .env.example --env .env.production
```

### JSON Output for CI Pipelines
```sh
python env_guard.py --json
```

---

## Running Tests

```sh
python -m unittest test_env_guard.py
```

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

Developed by **Rahul Buriya ([@rny0007](https://github.com/rny0007))**.

# BREWGEN

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![CLI](https://img.shields.io/badge/interface-CLI-yellow)
![LLM](https://img.shields.io/badge/powered_by-LLM-success)
![Status](https://img.shields.io/badge/status-beta-purple)

**brewgen** is an AI-powered CLI tool that generates valid [Homebrew](https://brew.sh) formulae from GitHub projects — so you don't have to write them by hand.

Built with ❤️ using [Typer](https://typer.tiangolo.com), [Rich](https://github.com/Textualize/rich), and [Ollama](https://ollama.com).

---

## Features

- Generates Homebrew formulae using local LLMs
- Automatically extracts metadata from GitHub repos
- Computes and injects accurate SHA256
- Adds a test block and install instructions
- Clean, colorful Rich output

---

## Demo


---

## 🚀 Usage

```bash
python3 main.py -r /path/to/your/project
```

### Options:
- `--model`   : Specify LLM model (default: `llama3:8b`)
- `--show`    : Print formula to terminal only
- `--verify`  : Automatically audit, install, and test the formula

---

## Requirements

- [Ollama](https://ollama.com) (local LLM runner)
- Python 3.9+
- `ffmpeg` (for some test examples)
- a running LLM like 'llama3'

---

## How It Works

1. Parses `.git/config` for owner/repo
2. Gets latest tag using GitHub API
3. Downloads tarball and computes `sha256`
4. Extracts metadata from README and LICENSE
5. Feeds structured prompt to LLM
6. Outputs valid Ruby formula

---

## ⚠️ Disclaimer

This project uses an LLM. Please review the generated formula manually before publishing or submitting to Homebrew/core.

---

## License

MIT © Mujaheed Khan  
See [LICENSE](LICENSE) for details.

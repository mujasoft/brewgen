# brewgen

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![CLI](https://img.shields.io/badge/interface-CLI-yellow)
![LLM](https://img.shields.io/badge/powered_by-LLM-success)
![Status](https://img.shields.io/badge/status-beta-purple)

**brewgen** is an AI-powered CLI tool that generates valid [Homebrew](https://brew.sh) formulae from GitHub projects — so you don't have to write them by hand.

## Features
- Generates Homebrew formulae using local LLMs
- Automatically extracts metadata from GitHub repos
- Computes and injects accurate SHA256
- Adds a test block and install instructions
- Clean, colorful Rich output

## Demo

![brewgen demo](Demo.gif)

## Usage

```bash
python3 main.py -r /path/to/your/project
```

### Options:
```bash
❯ python3 brewgen.py --help

 Usage: brewgen.py [OPTIONS]

 Generate ruby formula file from a cloned repo.


╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --repo-dir            -r      TEXT  Location of where the repo is cloned. [default: None]                      │
│ --output              -o      TEXT  Location of where to save formula file. [default: output.rb]               │
│ --tag                 -t      TEXT  Release tag [default: None]                                                │
│ --model               -m      TEXT  Name of model. [default: llama3]                                           │
│ --install-completion                Install completion for the current shell.                                  │
│ --show-completion                   Show completion for the current shell, to copy it or customize the         │
│                                     installation.                                                              │
│ --help                              Show this message and exit.                                                │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

| Field       | Value |
|-------------|-------|
| **--repo-dir**        | `Location of where your repo is located. E.g. /path/to/my/repo.` |
| **--output** | Location of where to save ruby formula. Default: output.rb |
| **--tag**     | Specific tag to use. Defaults to getting latest. |
| **--model**  | v1.0.1 |

## Requirements

- [Ollama](https://ollama.com)
- Python 3.9+
- ollama
- requests
- typer[all]
- rich


## How It Works

1. Parses `.git/config` for owner/repo
2. Gets latest tag using GitHub API
3. Downloads tarball and computes `sha256`
4. Extracts metadata from README and LICENSE
5. Feeds structured prompt to LLM
6. Outputs valid Ruby formula


## ⚠️ Disclaimer

This project uses an LLM. Please review the generated formula manually before publishing or submitting to Homebrew/core.


## License

MIT © Mujaheed Khan  
See [LICENSE](LICENSE) for details.

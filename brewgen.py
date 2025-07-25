# MIT License

# Copyright (c) 2025 Mujaheed Khan

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import configparser
import hashlib
import os
import re
import sys
from pathlib import Path

import ollama
import requests
import typer

from rich import print
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(
    help="Ai powered ruby formula generator from a clone repo."
)

console = Console()


def calculate_sha256_of_file(file_path):
    """
    Calculates the SHA-256 hash of a given file.

    Arg(s):
        file_path (str): The path to the file.

    Returns:
        str: The hexadecimal representation of the SHA-256 hash,
             or None if the file is not found.
    """

    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            # Read the file in chunks to handle large files efficiently
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        print(f"Error: File not found at '{file_path}'")
        return None


def get_readme_contents(repo_dir):
    """Returns contents of a README.md or None otherwise.

    Args:
        repo_dir (str): path to repo.

    Returns:
        str: a large text block containing output from README.md.
    """

    return read_text(os.path.join(repo_dir, "README.md"))


def get_owner_and_repo_from_git_config(repo_dir):
    """Returns 'owner' and 'repo_name' from git repo directory

    Args:
        repo_dir (str): location of repo.

    Returns:
        owner(str): name of owner. 'None' if not found.
        repo(str): name of repo. 'None' if not found.
    """

    config_path = os.path.join(repo_dir, ".git", "config")
    if not os.path.exists(config_path):
        print(f"*** ERROR: File not found: {config_path}")
        return None, None

    config = configparser.ConfigParser()
    config.read(config_path)

    try:
        url = config['remote "origin"']['url']
    except KeyError:
        print("Could not find 'origin' remote in git config.")
        return None, None

    # Match both HTTPS and SSH GitHub URLs
    match = re.match(r"(?:https://github\.com/|git@github\.com:)([^/]+)/([^.]+)(\.git)?", url)
    if match:
        owner, repo = match.group(1), match.group(2)
        return owner, repo
    else:
        print("Could not parse GitHub owner/repo from URL.")
        return None, None


def get_latest_release_tag_using_internal(owner: str, repo: str) -> str:
    """Get the latest tag using github api.

    Args:
        owner (str): Name of owner.
        repo (str): Name of repo.

    Returns:
        str: Latest release version tag. E.g. "v1.0.1"
    """

    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data.get("tag_name")
    elif response.status_code == 404:
        print("No releases found — this repo may" +
              " use tags without GitHub releases.")
        return None
    else:
        print(f"Error fetching release: {response.status_code}")
        return None


def get_latest_tag(repo_dir):
    """Returns the latest tag using info from a git repo location.

    Args:
        repo_dir (str): Location of repo.

    Returns:
        owner (str): Name of owner.
        repo (str): Name of repo.
    """

    owner, repo = get_owner_and_repo_from_git_config(repo_dir)

    return get_latest_release_tag_using_internal(owner, repo)


def read_text(filepath):
    """Given a filepath, returns contents of file.

    Args:
        filepath (str): Path to file to read.

    Returns:
        str: Contents of file.
    """

    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def get_git_config(repo_dir):
    """Returns content of .git/config from repo.

    Args:
        repo_dir (str): location of repo.

    Returns:
        str: contents of repo.
    """

    return read_text(os.path.join(repo_dir, ".git", "config"))


def get_folder_structure(path: str, max_depth: int = None,
                         ignore_dirs=[".git"]) -> str:
    """Walks the folder structure and returns its tree as a string.

    The output is similar to the 'tree' tool.

    Args:
        path (str): Folderpath to traverse.
        max_depth (int, optional): Maximum level to recurse. Defaults to None.
        ignore_dirs (str, optional): Folders to ignore. Defaults to None.

    Returns:
        str: _description_
    """
    base = Path(path).resolve()
    ignore_dirs = set(ignore_dirs)
    tree_output = ["."]

    for entry in sorted(base.rglob("*")):
        if any(part in ignore_dirs for part in entry.parts):
            continue

        rel_path = entry.relative_to(base)
        depth = len(rel_path.parts)
        if max_depth is not None and depth > max_depth:
            continue
        indent = "    " * (depth - 1)
        tree_output.append(f"{indent}└── {rel_path.name}")

    return "\n".join(tree_output)


def sha256_from_url(url):
    """Directly generate SHA from url.

    Args:
        url (str): URL of git repo.

    Returns:
        str: 256 shasum of git repo release tar ball.
    """

    sha256 = hashlib.sha256()
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        for chunk in r.iter_content(chunk_size=8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def get_hash(repo_dir, tag):
    """Return 256 shasum of repo dir at specified release tag.

    Args:
        repo_dir (_type_): _description_
        tag (_type_): _description_

    Returns:
        str: 256 shasum
    """

    owner, repo = get_owner_and_repo_from_git_config(repo_dir)

    url = f"https://github.com/{owner}/{repo}/archive/refs/tags/{tag}.tar.gz"

    return sha256_from_url(url)


def send_prompt_to_LLM(prompt: str, model: str = "llama3") -> str:
    """Sends prompt to specified LLM and returns output.

    Args:
        prompt (str): Block of text containg prompt.
        model (str, optional): Name of model. Defaults to "llama3".

    Returns:
        str: response from LLM.
    """

    with console.status("[bold green]Generating formula with LLM...[/]"):
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
    return response['message']['content']


def extract_formula_from_response(response: str) -> str:
    """LLM provides output in ruby block. Extract this from response.

    Args:
        response (str): Response from LLM.

    Returns:
        str: Only the relevant ruby formula. None if not found.
    """

    match = re.search(r"```ruby\n(.*?)\n```", response, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        print("Ruby formula block not found.")
        return None


def get_real_path(filepath: str) -> str:
    """Return real path from a given path

    Args:
        filepath (str): Path to file.

    Returns:
        str: Real filepath.
    """
    return str(Path(filepath).resolve())


@app.command()
def get_ruby_formula(
                    repo_dir: str = typer.Option(None, "--repo-dir", "-r",
                                                 help="Location of where the"
                                                      " repo is cloned."),
                    output: str = typer.Option("output.rb", "--output", "-o",
                                               help="Location of where to save"
                                                    " formula file."),
                    tag: str = typer.Option('latest', "--tag", "-t",
                                            help="Release tag"),
                    model: str = typer.Option("llama3", "--model", "-m",
                                              help="Name of model.")
        ):
    """Generate ruby formula file from a cloned repo."""

    if repo_dir is None:
        sys.exit("You must specify a repo directory.")

    if ".rb" not in output:
        output = os.path.join(output, ".rb")

    # Extract information.
    git_config_info = get_git_config(repo_dir)
    owner, repo = get_owner_and_repo_from_git_config(repo_dir)
    readme_file_output = get_readme_contents(repo_dir)
    folder_tree = get_folder_structure(repo_dir)

    # Set tag.
    if tag == 'latest':
        tag = get_latest_tag(repo_dir)

    # Get the hash.
    hash = get_hash(repo_dir, tag)

    prompt = f"""
I have a command-line tool that I want to distribute via Homebrew.

Please generate a valid Ruby formula for Homebrew using the information below:

Folder Tree:
{folder_tree}

- **Tool name**: <fill_it_in>
- **Description**:
___
{readme_file_output}
___
- **Homepage**: https://github.com/{owner}/{repo}
- **Source tarball URL**: https://github.com/{owner}/{repo}/archive/refs/tags/{tag}.tar.gz
- **SHA256**: {hash}
- **License**: <fill_it_in>
- **Language/Dependencies**: <fill_it_int>
- **Install command**: <fill_it_in>
- **Test command**: <fill_it_in>

The .git/config file looks like:
____
{git_config_info}
____

Notes:
- The CLI tool is defined in the repo as a single executable script or binary.
- Please use idiomatic Homebrew formula formatting and indentation.
- Return only the Ruby formula.

Example formula class name should be `CamelCase(repo)`.
"""

    results = send_prompt_to_LLM(prompt)
    ruby_str = extract_formula_from_response(results)
    if ruby_str:
        console.print("[bold green]Formula generation complete![/]\n")
    print()
    console.print(
                  Panel.fit(f"{ruby_str}",
                            title=f"Ruby Formula for {repo}",
                            subtitle="LLM Powered Homebrew Generator",
                            style="green")
                 )


    # Start writing results to file.
    output_filepath = get_real_path(output)
    with open(output, 'w') as f:
        f.write(ruby_str)

    print()
    console.print("[bold yellow]WARNING: Please double-check the generated"
                  " formula — LLMs can make subtle mistakes.[/]")
    print()
    console.print(f"[bold cyan]Output saved to:[/] {output_filepath}")


if __name__ == "__main__":
    app()

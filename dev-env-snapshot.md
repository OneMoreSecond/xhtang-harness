# Dev Environment Snapshot

Generated: 2026-05-30 12:25:13 CST +0800. [source: `date '+%Y-%m-%d %H:%M:%S %Z %z'`]

## Term Table

| Term | Meaning | Source |
| --- | --- | --- |
| Host | Machine name reported by the operating system. | `hostname` |
| Kernel | Linux kernel release and build string. | `uname -a` |
| uv project environment | Project-local Python environment managed by uv under `.venv/`. | `uv sync`, `readlink -f .venv/bin/python3` |
| Toolchain | Developer tools available in the current shell and uv project environment. | Version commands listed below |

## Repository Context

| Item | Value | Source |
| --- | --- | --- |
| Working directory | `/home/xhtang-sandbox2/xhtang-harness` | `pwd` |
| Git top level | `/home/xhtang-sandbox2/xhtang-harness` | `git rev-parse --show-toplevel` |
| Git branch | `master` | `git branch --show-current` |
| Git HEAD | `d07b568` | `git rev-parse --short HEAD` |
| Git working tree summary | `M AGENTS.md`; `A NOTE.md` | `git status --short` |

## System

| Item | Value | Source |
| --- | --- | --- |
| Host | `jp35` | `hostname` |
| OS | Amazon Linux 2023.7.20250331 | `/etc/os-release` |
| Kernel | `Linux jp35 6.1.131-143.221.amzn2023.x86_64 #1 SMP PREEMPT_DYNAMIC Mon Mar 24 15:35:21 UTC 2025 x86_64 x86_64 x86_64 GNU/Linux` | `uname -a` |
| Architecture | `x86_64` | `lscpu` |
| Word size | `64` bit | `getconf LONG_BIT` |
| Uptime and load | `up 58 days, 16:57`; load average `3.39, 3.56, 3.60` | `uptime` |

## CPU

| Item | Value | Source |
| --- | --- | --- |
| Model | AMD EPYC 9R45 | `lscpu` |
| Logical CPUs | 64 | `lscpu`, `nproc` |
| Sockets | 1 | `lscpu` |
| Cores per socket | 64 | `lscpu` |
| Threads per core | 1 | `lscpu` |
| Hypervisor | KVM, full virtualization | `lscpu` |
| Cache | L1d 3 MiB, L1i 2 MiB, L2 64 MiB, L3 256 MiB | `lscpu` |

## Memory And Disk

| Item | Value | Source |
| --- | --- | --- |
| Memory total | 247 GiB | `free -h` |
| Memory used | 12 GiB | `free -h` |
| Memory free | 11 GiB | `free -h` |
| Memory buff/cache | 223 GiB | `free -h` |
| Memory available | 191 GiB | `free -h` |
| Swap | 0 B total, 0 B used | `free -h` |
| Repository filesystem | `/dev/nvme0n1p1`, 1000G total, 664G used, 337G available, 67% used, mounted on `/` | `df -h .` |

## Python And Project Tooling

| Tool | Version / Status | Source |
| --- | --- | --- |
| uv | `uv 0.11.16 (x86_64-unknown-linux-gnu)` | `uv --version` |
| uv project Python | `Python 3.12.9`; executable resolves to `/usr/bin/python3.12` | `uv run python --version`; `readlink -f .venv/bin/python3` |
| `.python-version` | `3.12` | `.python-version` |
| System `python3.12` | `Python 3.12.9` | `python3.12 --version` |
| System `python3` | `Python 3.9.21` | `python3 --version` |
| pip in uv environment | Not installed: `.venv/bin/python3: No module named pip` | `uv run python -m pip --version` |
| pytest | `pytest 9.0.3` | `uv run pytest --version` |
| Ruff | `ruff 0.15.15` | `uv run ruff --version` |
| mypy | `mypy 2.1.0 (compiled: yes)` | `uv run mypy --version` |

## General Toolchain

| Tool | Version / Status | Source |
| --- | --- | --- |
| Git | `git version 2.47.1` | `git --version` |
| Bash | `GNU bash, version 5.2.15(1)-release (x86_64-amazon-linux-gnu)` | `bash --version` |
| GCC | `gcc (GCC) 11.5.0 20240719 (Red Hat 11.5.0-5)` | `gcc --version` |
| G++ | `g++ (GCC) 11.5.0 20240719 (Red Hat 11.5.0-5)` | `g++ --version` |
| GNU Make | `GNU Make 4.3` | `make --version` |
| CMake | `cmake version 3.31.7` | `cmake --version` |
| Node.js | `v22.22.3` | `node --version` |
| npm | `10.9.8` | `npm --version` |
| pnpm | Not found in `PATH` | `command -v pnpm` |
| Yarn | Not found in `PATH` | `command -v yarn` |
| Rust | `rustc 1.85.0 (4d91de4e4 2025-02-17) (Amazon Linux 1.85.0-1.amzn2023.0.1)` | `rustc --version` |
| Cargo | `cargo 1.85.0 (d73d2caf9 2024-12-31)` | `cargo --version` |
| Go | `go version go1.26.3 linux/amd64` | `go version` |
| Docker | `Docker version 25.0.8, build 0bab007` | `docker --version` |

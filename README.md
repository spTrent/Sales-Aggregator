**Sale`s Aggregator for students**

**Инструкция по подключению:**

**1. Выдайте себе PAT (Personal Access Token):**

    https://github.com/settings/tokens
    'Generate new token' -> 'Generate new token Fine-grained, repo-scoped' 
    Сохраните его где-нибудь, потому что показывается 1 раз.
    'Generate token'

**2. В терминале:**

    mkdir Sales-Aggregator
    cd Sales-Aggregator
    git init
    git remote add origin git@github.com:spTrent/Sales-Aggregator.git (В юзернейм свой, в пароль - PAT)
    git pull origin main

>**Установка uv (_если не установлен_)(проверка: uv --version):**
>
>       sudo apt update
>       sudo apt install curl unzip -y
>       curl -LsSf https://astral.sh/uv/install.sh | sh
>       echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
>       source ~/.bashrc

**3. Установка зависимостей:**

    uv sync
    source .venv/bin/activate
<<<<<<< HEAD
    pre-commit install (проверка: pre-commit run --all-files)

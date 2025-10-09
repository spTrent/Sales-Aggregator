**Sale`s Aggregator for students**

**Инструкция по подключению:**

**1. Выдайте себе PAT (Personal Access Token):**

    https://github.com/settings/tokens
    'Generate new token' -> 'Generate new token Fine-grained, repo-scoped'
    Называйте нормальным именем, ставьте длительность 3 месяца и 'Only select repositories' выбирайте Sales Aggregator
    Сохраните его где-нибудь, потому что показывается 1 раз.
    'Generate token'

**2. В терминале:** 

    mkdir Sales-Aggregator
    cd Sales-Aggregator
    git init
    git remote add origin git@github.com:spTrent/Sales-Aggregator.git (В юзернейм свой, в пароль - PAT)
    git pull origin main

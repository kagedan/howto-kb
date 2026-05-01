---
id: "2026-04-30-taiyo-ai-gakuse-httpstco66rpbcptxs-01"
title: "@taiyo_ai_gakuse: https://t.co/66RPbcPtxS"
url: "https://x.com/taiyo_ai_gakuse/status/2049826190425464996"
source: "x"
category: "ai-workflow"
tags: ["AI-agent", "x"]
date_published: "2026-04-30"
date_collected: "2026-05-01"
summary_by: "auto-x"
---

https://t.co/66RPbcPtxS


--- Article ---
# 既に作ったAgent Skillを npx skills add owner/repo で公開する手順

やることはこれだけ。

```
npx skills add owner/repo
```

で他の人が入れられるGitHubリポジトリにする。

---

## まず理解すること

## 

npx skills add owner/repo で配るとき、npmパッケージを公開する必要はない。

つまり、これは不要。

```
npm publish
```

package.json も必須ではない。

必要なのは、GitHubに公開されたリポジトリ。

たとえば、GitHub上にこれを作る。

```
https://github.com/yourname/my-agent-skills
```

すると、インストールコマンドはこうなる。

```
npx skills add yourname/my-agent-skills
```

GitHubの owner/repo が、そのまま npx skills add の指定名になる。

---

## 公開用リポジトリの形

## 

すでにSkillを作っている前提で、公開用リポジトリはこうする。

```
my-agent-skills/
  README.md
  skills/
    my-skill/
      SKILL.md
      references/
      scripts/
```

複数Skillを配るならこう。

```
my-agent-skills/
  README.md
  skills/
    deck-export/
      SKILL.md
      references/
    pr-review/
      SKILL.md
    release-check/
      SKILL.md
```

重要なのは、公開したいSkillを skills/<skill-name>/ 配下に置くこと。

既に手元にこういうSkillがあるなら、

```
my-skill/
  SKILL.md
  references/
  scripts/
```

公開用repoではこう置く。

```
my-agent-skills/
  skills/
    my-skill/
      SKILL.md
      references/
      scripts/
```

これで npx skills add yourname/my-agent-skills --skill my-skill の対象になる。

---

## ローカルで先に検出確認する

## 

GitHubに公開する前に、ローカルで確認する。

公開用リポジトリのルートで実行する。

```
npx skills add . --list
```

期待する出力はこう。

```
Available Skills

  my-skill
```

複数あるならこう。

```
Available Skills

  deck-export
  pr-review
  release-check
```

ここで出ないなら、GitHubにpushしても npx skills add owner/repo では入らない。

この時点で直す。

---

## GitHub CLIでpublic repoを作ってpushする

## 

GitHub CLIを使っているなら、この手順が一番早い。

```
git init
git add .
git commit -m "Publish agent skills"
git branch -M main
gh repo create yourname/my-agent-skills --public --source=. --remote=origin --push
```

これで、

**https://github.com/yourname/my-agent-skills**

が公開される。

このrepoがpublicなら、他の人はこう入れられる。

```
npx skills add yourname/my-agent-skills
```

特定Skillだけならこう。

```
npx skills add yourname/my-agent-skills --skill my-skill

```

---

## GitHub経由で npx skills add を確認する

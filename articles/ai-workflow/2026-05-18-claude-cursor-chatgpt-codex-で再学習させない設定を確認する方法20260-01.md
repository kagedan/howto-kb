---
id: "2026-05-18-claude-cursor-chatgpt-codex-で再学習させない設定を確認する方法20260-01"
title: "Claude / Cursor / ChatGPT / Codex で「再学習させない」設定を確認する方法【202605版】"
url: "https://qiita.com/mmt/items/396b778fdb9d2b434890"
source: "qiita"
category: "ai-workflow"
tags: ["OpenAI", "GPT", "qiita"]
date_published: "2026-05-18"
date_collected: "2026-05-19"
summary_by: "auto-rss"
query: ""
---

「再学習に使わせない（オプトアウト）」設定のメモ

* Claude MAXプラン
* Cursor Teamsプラン
* ChatGPT Businessプラン
* Codex (ChatGPT Businessプラン由来)

---

# Claude
ウェブとAPP同じUIが表示されているので、どちらかOFFにすれば連動してそう

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/48015/1ab0c320-416a-408f-8765-7f8d4955b2fb.png)

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/48015/1b248ca7-dbc5-462d-b292-c2754da5ec36.png)


## 設定場所

1. 左下プロフィール　https://claude.ai/settings/data-privacy-controls
2. `Settings`
3. `プライバシー`
4. `Claudeの改善にご協力ください`をOFF


---

# Cursor
Teamsプランの場合、ウェブ上の管理画面から共通で設定できてそう

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/48015/c0df34f9-596a-47d7-a80a-e7114eadcc8a.png)

エディターでの表示
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/48015/0cb37843-b5c0-4e3f-88dd-426193eb868f.png)

## 設定場所

1. Cursor Dashboard　https://cursor.com/ja/dashboard/team-settings
2. `Team Settings`
3. `Privacy Settings`
4. `Privacy Mode`を Active 

---

# ChatGPT

個人版はデフォルトONのようなのでOFFにしたい場合は確認
APP
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/48015/265d7b21-e63c-4646-8dba-f63934a84a19.png)
web
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/48015/d20798dd-af44-4fad-a665-0c198dad303f.png)

## 設定場所

1. 左アイコン　https://chatgpt.com/#settings/DataControls
2. `設定`
3. `データコントロール`
4. `すべての人のためにモデルを改善する`を オフ 

---

# Codex

ChatGPTのBusiness版で契約にて入る場合は基本無効になっているようです

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/48015/2930dbc6-07b5-4aaa-a2a2-6286ced660ba.png)

## 設定場所
1.設定画面　https://chatgpt.com/codex/cloud/settings/data
2.`データ コントロール`

##参考URL

https://help.openai.com/ja-jp/articles/5722486-how-your-data-is-used-to-improve-model-performance

---
id: "2026-06-08-tidb-cloudで採用aiエージェントの記憶dbを作ってみた-01"
title: "TiDB Cloudで採用AIエージェントの「記憶DB」を作ってみた"
url: "https://zenn.dev/fsgesaiyo/articles/5d6d5b2c2b70e3"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "LLM", "OpenAI", "zenn"]
date_published: "2026-06-08"
date_collected: "2026-06-09"
summary_by: "auto-rss"
query: ""
---

# TiDB Cloudで採用AIエージェントの「記憶DB」を作ってみた

## はじめに

採用業務では、求人票、候補者メモ、面接ログ、過去の判断ルールがいろいろな場所に散らばりがちです。

たとえば、以下のような情報です。

・求人票の必須条件  
・候補者の経験スキル  
・面接で聞いた転職理由  
・次回確認したい懸念点  
・過去に採用担当者が重視した判断ルール  
・スカウト文面で使えそうな訴求ポイント

これらは一つひとつは小さな情報ですが、採用実務ではかなり重要です。

問題は、情報の種類がバラバラなことです。

職種、経験年数、勤務地、年収のような構造化データはSQLで検索したくなります。一方で、「上流工程に挑戦したいWebディレクター」「PMO補佐からPMOに伸ばせそうな人」のような曖昧な条件は、ベクトル検索で探したくなります。

さらに、AIエージェントとして使うなら、毎回ゼロから検索するだけでは足りません。

「この採用担当者は未経験者より実務経験者を優先する」「合否判断ではなく確認質問を出したい」「スカウトでは一次面接から案内したい」といった過去の判断ルールも、次回の回答に反映したくなります。

そこでこの記事では、TiDB Cloudを使って、採用AIエージェントのための小さな「記憶DB」を作ります。

作るものは、採用合否を自動判断するAIではありません。

あくまで、採用担当者が人間として判断するための材料を整理する補助ツールです。

## この記事で作るもの

この記事では、以下のデータをTiDB Cloudに保存します。

・求人票  
・候補者メモ  
・面接ログ  
・採用担当者の判断ルール

そして、以下を実装します。

・条件検索はSQLで行う  
・曖昧な意味検索はベクトル検索で行う  
・SQL検索とベクトル検索を組み合わせる  
・検索結果をLLMに渡し、推薦理由、懸念点、次回質問、スカウト文面を生成する  
・採用担当者の判断ルールをエージェントメモリとして保存し、次回の検索に反映する

最終的な出力は以下です。

・求人に合いそうな候補者一覧  
・推薦理由  
・懸念点  
・次回確認すべき質問  
・スカウト文面の下書き  
・検索に使った根拠データ  
・回答に影響したエージェントメモリ

## 完成イメージ

今回作る最小構成です。

この構成にした理由は、採用データには2種類の検索が必要だからです。

1つ目は、条件検索です。

たとえば、職種、経験年数、勤務地、年収、スキルタグなどはSQLで絞り込めます。

2つ目は、意味検索です。

たとえば、「上流工程に挑戦したい人」「PMOに伸ばせそうな人」「Web制作進行からディレクターに合いそうな人」は、単純な完全一致では拾いにくいです。

TiDB Cloudを使うと、SQL検索とベクトル検索を同じDB上で扱えるため、業務データとAI検索を分断しなくて済みます。

## 前提と注意

この記事では、実在候補者のデータは使いません。

求人票、候補者メモ、面接ログ、判断ルールはすべて架空のサンプルです。

採用領域でAIを使う場合、技術よりも運用ルールが重要です。

最低限、以下は必要です。

・実在候補者データを検証に使わない  
・個人情報や機密情報を不要にLLMへ送らない  
・必要に応じて候補者名、会社名、メールアドレス、電話番号をマスキングする  
・AIに合否判断をさせない  
・AI出力は必ず採用担当者がレビューする  
・誤検索や誤要約があり得る前提で使う  
・候補者に不利益な自動判定をしない

この記事の実装は「判断材料の整理」であり、「採用判断の自動化」ではありません。

## なぜTiDB Cloudを使うのか

今回TiDB Cloudを使う理由は、構造化データと非構造テキストを同じ基盤で扱いたいからです。

採用データには、以下のような構造化データがあります。

・職種  
・経験年数  
・勤務地  
・希望年収  
・スキルタグ  
・更新日時

一方で、以下のような非構造テキストもあります。

・面接メモ  
・転職理由  
・志向性  
・懸念点  
・スカウト文面  
・採用担当者の判断ルール

従来の構成だと、構造化データはRDB、意味検索はベクトルDB、判断ルールは別のメモリストアに分けたくなります。

ただ、AIエージェントのメモリでは、検索、更新、根拠確認、監査ログが必要になります。

そのため、最初からSQLとベクトル検索を同じDBで扱える形にした方が、実務では扱いやすいと考えました。

## テーブル設計

今回は以下の4テーブルを作ります。

・jobs  
・candidates  
・interview\_notes  
・agent\_memories

それぞれに `embedding` カラムを持たせます。

embeddingの次元数は利用するembeddingモデルに合わせる必要があります。この記事のサンプルでは `VECTOR(1536)` としていますが、利用するモデルが異なる場合は次元数を変更してください。

### jobs

求人票を保存します。

主なカラムは以下です。

・title  
・department  
・required\_skills  
・preferred\_skills  
・location  
・min\_years  
・salary\_min  
・salary\_max  
・description  
・embedding

### candidates

候補者メモを保存します。

主なカラムは以下です。

・display\_name  
・current\_role  
・years\_experience  
・skills  
・desired\_role  
・desired\_location  
・desired\_salary  
・summary  
・embedding

### interview\_notes

面接ログを保存します。

主なカラムは以下です。

・candidate\_id  
・note\_type  
・content  
・concerns  
・next\_questions  
・embedding

### agent\_memories

採用担当者の判断ルールを保存します。

主なカラムは以下です。

・memory\_type  
・content  
・importance  
・source  
・expires\_at  
・embedding

ここで重要なのは、エージェントメモリにも `importance` と `expires_at` を持たせることです。

AIエージェントの記憶は、増えれば増えるほど良いわけではありません。古い判断ルールや重要度の低い記憶が残り続けると、回答にノイズが混ざります。

## TiDB Cloudの準備

TiDB CloudでStarterクラスタを作成し、接続情報を取得します。

`.env` には以下を設定します。

```
TIDB_HOST=your-host.tidbcloud.com
TIDB_PORT=4000
TIDB_USER=your_user
TIDB_PASSWORD=your_password
TIDB_DATABASE=recruiting_agent

LLM_API_URL=https://example.com/v1/chat/completions
LLM_API_KEY=your_llm_api_key
LLM_MODEL=your_model_name

EMBEDDING_API_URL=https://example.com/v1/embeddings
EMBEDDING_API_KEY=your_embedding_api_key
EMBEDDING_MODEL=your_embedding_model
EMBEDDING_DIM=1536
```

DB接続情報やAPIキーはコードに直書きしません。

`.env` はGit管理せず、公開するのは `.env.example` のみです。

## schema.sql

```
CREATE DATABASE IF NOT EXISTS recruiting_agent;
USE recruiting_agent;

DROP TABLE IF EXISTS interview_notes;
DROP TABLE IF EXISTS candidates;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS agent_memories;

CREATE TABLE jobs (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(255) NOT NULL,
  department VARCHAR(255) NOT NULL,
  required_skills JSON NOT NULL,
  preferred_skills JSON NOT NULL,
  location VARCHAR(255) NOT NULL,
  min_years INT NOT NULL,
  salary_min INT,
  salary_max INT,
  description TEXT NOT NULL,
  embedding VECTOR(1536),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE candidates (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  display_name VARCHAR(255) NOT NULL,
  current_role VARCHAR(255) NOT NULL,
  years_experience INT NOT NULL,
  skills JSON NOT NULL,
  desired_role VARCHAR(255),
  desired_location VARCHAR(255),
  desired_salary INT,
  summary TEXT NOT NULL,
  embedding VECTOR(1536),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE interview_notes (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  candidate_id BIGINT NOT NULL,
  note_type VARCHAR(100) NOT NULL,
  content TEXT NOT NULL,
  concerns TEXT,
  next_questions TEXT,
  embedding VECTOR(1536),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_interview_notes_candidate
    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
    ON DELETE CASCADE
);

CREATE TABLE agent_memories (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  memory_type VARCHAR(100) NOT NULL,
  content TEXT NOT NULL,
  importance INT NOT NULL DEFAULT 3,
  source VARCHAR(255) NOT NULL DEFAULT 'manual',
  expires_at TIMESTAMP NULL,
  embedding VECTOR(1536),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE INDEX idx_jobs_title ON jobs(title);
CREATE INDEX idx_jobs_location ON jobs(location);
CREATE INDEX idx_candidates_current_role ON candidates(current_role);
CREATE INDEX idx_candidates_years_experience ON candidates(years_experience);
CREATE INDEX idx_agent_memories_importance ON agent_memories(importance);
```

この記事では再現性を優先して、まずはベクトルインデックスなしの小規模サンプルとして実装します。

データ量が増える場合は、`CREATE VECTOR INDEX` やHNSWインデックスの利用を検討します。

## seed.sql

```
USE recruiting_agent;

INSERT INTO jobs (
  title,
  department,
  required_skills,
  preferred_skills,
  location,
  min_years,
  salary_min,
  salary_max,
  description
) VALUES
(
  'Webディレクター',
  'DX事業部',
  JSON_ARRAY('Web制作進行', '要件整理', 'クライアント折衝'),
  JSON_ARRAY('アクセス解析', '改善提案', 'PM経験'),
  '東京',
  3,
  4000000,
  6000000,
  'WebサイトやLPの制作進行、要件整理、クライアント折衝を担当するポジション。運用だけでなく改善提案にも関われる。'
),
(
  'PMO',
  'DX事業部',
  JSON_ARRAY('進捗管理', '課題管理', '議事録作成'),
  JSON_ARRAY('ベンダー調整', '業務改善', 'システム導入支援'),
  '東京',
  2,
  4200000,
  6500000,
  'プロジェクトの進捗管理、課題管理、会議運営、関係者調整を支援するPMOポジション。'
),
(
  'バックエンドエンジニア',
  '開発部',
  JSON_ARRAY('Java', 'Spring Boot', 'SQL'),
  JSON_ARRAY('AWS', 'Docker', 'API設計'),
  '東京',
  3,
  4500000,
  7500000,
  'Java/Spring Bootを中心に、業務システムやWebアプリケーションのバックエンド開発を担当する。'
);

INSERT INTO candidates (
  display_name,
  current_role,
  years_experience,
  skills,
  desired_role,
  desired_location,
  desired_salary,
  summary
) VALUES
(
  '候補者A',
  'Webディレクター',
  4,
  JSON_ARRAY('Web制作進行', 'LP進行管理', 'エンジニア調整', 'クライアント折衝'),
  'Webディレクター',
  '東京',
  5000000,
  'Webサイト運用とLP制作進行を中心に経験。今後は要件整理や改善提案など、より上流工程に関わりたい。'
),
(
  '候補者B',
  'PMO補佐',
  2,
  JSON_ARRAY('議事録作成', '進捗管理', '課題管理', 'Excel'),
  'PMO',
  '東京',
  4500000,
  'PMO補佐として会議運営、議事録作成、課題管理を経験。今後はPMOとして関係者調整にも挑戦したい。'
),
(
  '候補者C',
  'バックエンドエンジニア',
  3,
  JSON_ARRAY('Java', 'Spring Boot', 'MySQL', 'REST API'),
  'バックエンドエンジニア',
  '東京',
  5500000,
  'JavaとSpring Bootで業務システム開発を経験。AWS経験は浅いが、クラウド案件への関心がある。'
);

INSERT INTO interview_notes (
  candidate_id,
  note_type,
  content,
  concerns,
  next_questions
) VALUES
(
  1,
  'first_interview',
  'Webサイト運用と制作進行の経験が中心。上流工程に挑戦したい意欲がある。',
  '要件定義を主担当として進めた経験は不明。',
  '過去に要件定義を主導した経験、数値改善の経験、エンジニアとの技術的な会話の深さを確認する。'
),
(
  2,
  'first_interview',
  'PMO補佐として議事録作成、進捗管理、課題管理を担当。今後はPMOとして調整業務を広げたい。',
  '主体的に課題解決をリードした経験は不明。',
  '課題管理で自分から改善提案した経験、関係者調整の具体例を確認する。'
),
(
  3,
  'first_interview',
  'Java/Spring Bootの実務経験があり、API開発経験もある。クラウド案件に関心がある。',
  'AWSの実務経験は浅い。',
  'AWSで触ったサービス、設計経験、運用経験の有無を確認する。'
);

INSERT INTO agent_memories (
  memory_type,
  content,
  importance,
  source
) VALUES
(
  'screening_policy',
  'この採用担当者は、完全未経験者よりも実務経験1〜3年以上のIT/Web人材を優先する。',
  5,
  'manual'
),
(
  'communication_policy',
  '候補者への提案では、合否判断ではなく、次回確認事項と推薦理由を分けて提示する。',
  5,
  'manual'
),
(
  'scout_policy',
  'スカウト文面では、カジュアル面談ではなく、書類選考なしで一次面接から案内する表現を優先する。',
  4,
  'manual'
);
```

## embeddingを作成して保存する

次に、求人票、候補者メモ、面接ログ、エージェントメモリをembedding化します。

embedding APIはOpenAI互換の `/v1/embeddings` 形式を想定します。

ただし、特定サービスに依存させたくないため、以下の環境変数で差し替えられるようにします。

```
EMBEDDING_API_URL=https://example.com/v1/embeddings
EMBEDDING_API_KEY=your_embedding_api_key
EMBEDDING_MODEL=your_embedding_model
```

## SQL検索を実装する

SQL検索では、職種、経験年数、勤務地、スキルタグのような明確な条件に強いです。

たとえば、東京勤務でWebディレクター志望、経験3年以上の候補者を探す場合は、以下のようなSQLになります。

```
SELECT
  id,
  display_name,
  current_role,
  years_experience,
  desired_role,
  desired_location,
  summary
FROM candidates
WHERE desired_location = '東京'
  AND years_experience >= 3
  AND (
    desired_role LIKE '%Webディレクター%'
    OR current_role LIKE '%Webディレクター%'
  );
```

これは確実ですが、「上流工程に挑戦したい人」のような曖昧な意図は拾いにくいです。

## ベクトル検索を実装する

ベクトル検索では、自然文クエリで意味検索できます。

たとえば、以下のようなクエリです。

TiDBでは、以下のように `VEC_COSINE_DISTANCE` を使って近い候補者を検索します。

```
SELECT
  id,
  display_name,
  current_role,
  summary,
  VEC_COSINE_DISTANCE(embedding, ?) AS distance
FROM candidates
WHERE embedding IS NOT NULL
ORDER BY distance
LIMIT 5;
```

距離が小さいほど、クエリベクトルに近い候補者です。

## SQL＋ベクトル検索を組み合わせる

実務では、SQLだけでもベクトル検索だけでも足りません。

たとえば、「東京勤務で経験3年以上」という条件はSQLで絞りたいです。

一方で、「上流工程に挑戦したいWebディレクター」という意図はベクトル検索で探したいです。

そこで、SQL条件で候補を絞りつつ、ベクトル距離で並び替えます。

```
SELECT
  id,
  display_name,
  current_role,
  years_experience,
  desired_role,
  desired_location,
  summary,
  VEC_COSINE_DISTANCE(embedding, ?) AS distance
FROM candidates
WHERE embedding IS NOT NULL
  AND desired_location = '東京'
  AND years_experience >= 3
ORDER BY distance
LIMIT 5;
```

## エージェントメモリを検索する

候補者検索だけでは、採用担当者の過去の判断ルールは反映されません。

そこで `agent_memories` も検索します。

```
SELECT
  id,
  memory_type,
  content,
  importance,
  VEC_COSINE_DISTANCE(embedding, ?) AS distance
FROM agent_memories
WHERE embedding IS NOT NULL
  AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
ORDER BY importance DESC, distance ASC
LIMIT 5;
```

これにより、以下のような判断ルールをRAGのコンテキストに入れられます。

・実務経験1〜3年以上を優先する  
・合否判断ではなく確認事項を出す  
・スカウト文面では一次面接から案内する

## LLMでRAG回答を生成する

検索結果をLLMに渡し、以下を生成します。

・求人に合いそうな候補者  
・推薦理由  
・懸念点  
・次回確認質問  
・スカウト文面の下書き  
・検索に使った根拠データ  
・回答に影響したエージェントメモリ  
・不明点

ここでも重要なのは、LLMに推測させすぎないことです。

採用領域では、データにない情報を補完してしまうと危険です。

プロンプトには以下の制約を入れます。

・データにない情報は「不明」とする  
・合否判定をしない  
・候補者の人格を断定しない  
・推薦理由は根拠データとセットにする  
・懸念点は次回確認質問に変換する  
・スカウト文面は下書きに留める

## 実行結果

実行コマンドは以下です。

```
npm run dev -- "上流工程に挑戦したいWebディレクター"
```

出力ファイルは以下です。

```
output/result.json
output/result.md
```

出力JSONの例です。

```
{
  "matchedCandidates": [
    {
      "candidateName": "候補者A",
      "summary": "Webサイト運用とLP制作進行を中心に経験。今後は要件整理や改善提案など、より上流工程に関わりたい。",
      "matchType": "sql_plus_vector"
    }
  ],
  "reasons": [
    "求人票の必須条件であるWeb制作進行、要件整理、クライアント折衝と、候補者Aの経験が近い。",
    "候補者Aは上流工程に関わりたい意向を持っており、求人内容と方向性が合う。"
  ],
  "concerns": [
    {
      "point": "要件定義の主担当経験は不明",
      "evidence": "面接ログに、要件定義を主導した経験は明示されていないと記録されている。",
      "nextCheck": "過去に要件定義を主担当として進めた案件の有無を確認する。"
    }
  ],
  "nextQuestions": [
    "要件定義を主担当として進めた経験はありますか？",
    "数値改善や改善提案に関わった具体例はありますか？",
    "エンジニアとの技術的な会話はどの程度可能ですか？"
  ],
  "scoutDraft": "Web制作進行やLP進行管理のご経験を拝見し、Webディレクターとして要件整理や改善提案にも関われるポジションをご案内したくご連絡しました。書類選考なしで一次面接からご案内可能です。",
  "usedEvidence": [
    "jobs: Webディレクター求人",
    "candidates: 候補者Aの候補者メモ",
    "interview_notes: 候補者Aの一次面接ログ"
  ],
  "memoryUsed": [
    "実務経験1〜3年以上のIT/Web人材を優先する",
    "合否判断ではなく、次回確認事項と推薦理由を分けて提示する"
  ],
  "unknowns": [
    "要件定義の主担当経験",
    "数値改善の実績",
    "開発知識の深さ"
  ]
}
```

Markdown出力の例です。

```
# 採用AIアシスタント結果

## マッチ候補者
・候補者A

## 推薦理由
・求人票の必須条件であるWeb制作進行、要件整理、クライアント折衝と、候補者Aの経験が近い。
・候補者Aは上流工程に関わりたい意向を持っており、求人内容と方向性が合う。

## 懸念点
### 1. 要件定義の主担当経験は不明

根拠: 面接ログに、要件定義を主導した経験は明示されていないと記録されている。

次回確認: 過去に要件定義を主担当として進めた案件の有無を確認する。

## 次回確認質問
・要件定義を主担当として進めた経験はありますか？
・数値改善や改善提案に関わった具体例はありますか？
・エンジニアとの技術的な会話はどの程度可能ですか？

## スカウト文面下書き
Web制作進行やLP進行管理のご経験を拝見し、Webディレクターとして要件整理や改善提案にも関われるポジションをご案内したくご連絡しました。書類選考なしで一次面接からご案内可能です。

## 使用した根拠
・jobs: Webディレクター求人
・candidates: 候補者Aの候補者メモ
・interview_notes: 候補者Aの一次面接ログ

## 回答に使ったメモリ
・実務経験1〜3年以上のIT/Web人材を優先する
・合否判断ではなく、次回確認事項と推薦理由を分けて提示する

## 不明点
・要件定義の主担当経験
・数値改善の実績
・開発知識の深さ
```

## 検索方式の比較

| 方法 | 条件検索の強さ | 曖昧な自然文検索 | 根拠確認 | 実務での使いやすさ | 注意点 |
| --- | --- | --- | --- | --- | --- |
| SQL検索のみ | 強い | 弱い | しやすい | 条件が明確なら強い | 表現揺れに弱い |
| ベクトル検索のみ | 弱い | 強い | やや難しい | 曖昧な検索に強い | 条件外の候補が混ざる |
| SQL＋ベクトル検索 | 強い | 強い | しやすい | 実務向き | SQL条件が強すぎると候補が落ちる |
| SQL＋ベクトル検索＋メモリ | 強い | 強い | しやすい | 継続利用に強い | 古いメモリや誤ったメモリがノイズになる |

実装して分かったのは、採用業務ではベクトル検索だけでは足りないということです。

「似ている候補者を探す」だけならベクトル検索で十分です。

しかし実務では、勤務地、経験年数、希望年収、職種などの条件が重要です。

一方で、SQLだけでは「上流工程に挑戦したい」「PMOに伸ばせそう」のような曖昧な意図を拾いにくいです。

そのため、SQLとベクトル検索を同じ基盤で扱えることに価値があります。

## うまくいかなかったこと

### ベクトル検索だけだと条件検索に弱い

最初は、候補者メモをすべてベクトル化して、自然文クエリだけで検索しました。

しかし、「上流工程に挑戦したいWebディレクター」と検索すると、Webディレクターではない候補者も混ざることがありました。

意味的には近くても、求人条件に合うとは限りません。

そこで、勤務地や経験年数などはSQLで絞り、意味的な近さはベクトル検索で見るようにしました。

### SQLだけだと曖昧な意図検索に弱い

一方で、SQLだけでは「伸びしろ」「志向性」「上流工程に挑戦したい」といった表現を拾いにくいです。

スキルタグが完全一致していなくても、面接ログの内容を見ると求人に合いそうな候補者はいます。

この部分はベクトル検索の方が自然でした。

### メモリが増えるとノイズが混ざる

エージェントメモリを増やすと、過去の判断ルールが回答に反映されます。

これは便利ですが、古いメモリや重要度の低いメモリまで拾うと、回答がブレます。

そこで、`importance` と `expires_at` を持たせ、重要度と期限で制御できるようにしました。

### LLMが推薦理由を補完しすぎる

最初のプロンプトでは、LLMが「この候補者は主体性が高い」など、根拠データにない評価を書いてしまうことがありました。

採用領域では危険です。

そのため、以下のルールを追加しました。

・データにない情報は不明とする  
・合否判定をしない  
・推薦理由は根拠データとセットにする  
・懸念点は次回確認質問に変換する

### 根拠データを持たせないとレビューしづらい

RAG回答だけを見ると、なぜその回答になったのか分かりにくいです。

そこで、`usedEvidence` と `memoryUsed` を必ず出力するようにしました。

これにより、採用担当者がAI出力をレビューしやすくなりました。

## 改善案

実務投入するなら、次にやるべき改善は以下です。

・mem9を使って、エージェントメモリの管理を外部化する  
・メモリに重要度スコアを持たせる  
・メモリにTTLを持たせる  
・採用担当者がメモリを確認・修正できるUIを作る  
・NotionやGoogle Sheetsに検索結果を保存する  
・ATSと連携する  
・評価ではなく確認質問生成に限定する  
・根拠データへのリンクを付ける  
・監査ログを保存する  
・スカウト文面を職種別にテンプレート化する

将来の改善構成は以下です。

## まとめ

この記事では、TiDB Cloudを使って、採用AIエージェントのための「記憶DB」を作りました。

実装して分かったのは、AI時代の業務データ基盤では、SQL検索とベクトル検索の両方が必要になるということです。

SQL検索は、職種、経験年数、勤務地、年収のような明確な条件に強いです。

ベクトル検索は、志向性、面接メモ、判断ルールのような曖昧な情報に強いです。

そして、AIエージェントとして継続利用するなら、毎回の検索だけでなく、過去の判断ルールをどう保存し、どう取り出し、どう修正するかが重要になります。

TiDB Cloudを使うことで、求人票、候補者メモ、面接ログ、エージェントメモリを1つの基盤に置き、SQL検索とベクトル検索を組み合わせたRAGを作れました。

一方で、採用領域ではAI出力をそのまま判断に使うべきではありません。

今回の実装でも、AIに合否判断はさせず、推薦理由、懸念点、次回確認質問、スカウト文面の下書きに限定しました。

AIエージェントは採用担当者の代替ではなく、判断材料の整理を支援する道具として使うのが現実的です。

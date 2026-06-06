---
id: "2026-06-05-claude-を使って-gemini-議事録から必要な情報を抽出する仕組み-01"
title: "Claude を使って Gemini 議事録から必要な情報を抽出する仕組み"
url: "https://zenn.dev/tokium_dev/articles/d806c7ad4fd458"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "Gemini", "zenn"]
date_published: "2026-06-05"
date_collected: "2026-06-06"
summary_by: "auto-rss"
query: ""
---

## はじめに

Google Meet の Gemini 議事録は便利ですが、Google Drive に増えていくだけでは会議後の作業につながりません。  
この記事では、Claude を使って Gemini 議事録から決定事項や TODO を抽出し、業務に必要な情報へ変える仕組みを紹介します。

この仕組みを作ると、会議後に誰かが議事録を読み直し、必要な情報を整理する負担を減らせます。  
また、決定事項や TODO が Slack や Jira に残るため、あとから「何が決まったのか」「次に誰が何をするのか」を追いやすくなります。

想定している読者は次のような人です。

* Gemini の議事録を会議後の業務に活かせていない人
* Claude Code / Claude Skills を、コード生成以外の業務運用に使いたい人
* 会議の決定事項を Slack で共有し、Jira チケットに残す流れを自動化したい人

## 全体像

やっていることは、大きく次の 3 つです。

1. 収集: Gemini が生成した議事録を Markdown に変換して保存
2. 抽出: Claude Skills が Markdown 議事録を読み、決定事項と TODO を抽出
3. 投稿: 抽出結果を Slack や Jira に投稿

全体の流れは次のとおりです。

## 議事録を Markdown に変換して GitHub に保存する

Gemini 議事録は自動で Google Drive に保存されますが、会議をまたいで決定事項や TODO を追うには少し不便です。

そこで、会議ログを横断して扱えるようにするために、Google Docs の議事録を Markdown に変換し、GitHub リポジトリへ push する GAS スクリプトを書いています。  
Markdown にしてリポジトリにまとめておくと、複数の議事録をまとめて読み、会議をまたいだ分析に使いやすくなります。

このリポジトリは、議事録の保管場所というより、AI が会議情報を分析するための土台です。

実際に使っている GAS の例を示します。  
実行するには、`GITHUB_TOKEN` を GAS のスクリプトプロパティに登録する必要があります。  
Personal access token の作成方法は、GitHub 公式の [Managing your personal access tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) を参照してください。

GAS の例

```
/**
 * 同期対象の会議とGitHub宛先を定義する設定。
 * 会議の追加・削除は targetMeetings を編集する。
 */
const CONFIG = {
  githubRepo: 'your-org/meeting-notes',
  githubBranch: 'main',
  targetMeetings: {
    'デイリースクラム': 'daily',
    'リファインメント': 'refinement',
    '週次定例': 'weekly',
  },
};

/**
 * 議事録同期のエントリポイント。時間主導型トリガーから定期実行される。
 *
 * 処理の流れ:
 * 1. Drive から対象キーワードを含む Google Docs を検索
 * 2. 未処理のドキュメントを Markdown に変換
 * 3. GitHub Contents API で push
 * 4. 処理済みとしてマーク（二重 push 防止）
 */
function syncMeetingNotes() {
  const processedIds = getProcessedIds_();
  const docs = findMeetingDocs_();

  const newlyProcessedIds = [];

  for (const doc of docs) {
    if (processedIds.has(doc.id)) continue;

    try {
      const markdown = convertDocToMarkdown_(doc.id);
      const dateStr = extractDate_(doc.createdAt);
      const fileName = `${dateStr}_${doc.dir}.md`;
      const path = `${doc.dir}/${fileName}`;

      pushToGitHub_(path, markdown, `docs: add ${fileName}`);
      newlyProcessedIds.push(doc.id);

      Logger.log(`Pushed: ${path}`);
    } catch (e) {
      Logger.log(`Failed to process ${doc.name} (${doc.id}): ${e.message}`);
    }
  }

  if (newlyProcessedIds.length > 0) {
    batchMarkAsProcessed_(processedIds, newlyProcessedIds);
  }

  Logger.log(`Sync complete. ${newlyProcessedIds.length} new file(s) pushed.`);
}

/**
 * Drive から Gemini 議事録ドキュメントを検索して返す。
 *
 * @returns 検索にヒットしたドキュメント一覧
 */
function findMeetingDocs_() {
  const docs = [];
  const seenIds = new Set();

  // 直近14日間のドキュメントのみ検索（トリガー停止時のバッファとして2週間分）
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - 14);
  const cutoffStr = cutoff.toISOString().split('T')[0];

  for (const [keyword, dir] of Object.entries(CONFIG.targetMeetings)) {
    const query = [
      `mimeType = 'application/vnd.google-apps.document'`,
      `title contains '${keyword}'`,
      `modifiedDate > '${cutoffStr}'`,
    ].join(' and ');
    const files = DriveApp.searchFiles(query);

    while (files.hasNext()) {
      const file = files.next();
      const id = file.getId();
      if (seenIds.has(id)) continue;
      seenIds.add(id);

      docs.push({
        id: id,
        name: file.getName(),
        dir: dir,
        createdAt: file.getDateCreated(),
      });
    }
  }

  return docs;
}

/**
 * Google Docs を Markdown に変換する。
 *
 * @param docId - Google Docs の ID
 * @returns Markdown 文字列
 */
function convertDocToMarkdown_(docId) {
  const url = `https://www.googleapis.com/drive/v3/files/${docId}/export?mimeType=${encodeURIComponent('text/markdown')}`;
  const response = UrlFetchApp.fetch(url, {
    headers: { Authorization: 'Bearer ' + ScriptApp.getOAuthToken() },
    muteHttpExceptions: true,
  });

  if (response.getResponseCode() !== 200) {
    throw new Error(`Failed to export doc ${docId} as markdown: ${response.getResponseCode()}`);
  }

  return response.getContentText('UTF-8').trim() + '\n';
}

/**
 * Date オブジェクトから `YYYY-MM-DD` 形式の文字列を生成する。
 * ファイル命名規則に従った日付プレフィックスとして使用される。
 *
 * @param date - 変換元の日付
 * @returns `YYYY-MM-DD` 形式の日付文字列
 */
function extractDate_(date) {
  const d = new Date(date);
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}

/**
 * GitHub Contents API を使ってファイルを作成または更新する。
 *
 * @param path - リポジトリ内のファイルパス
 * @param content - ファイル内容
 * @param message - コミットメッセージ
 */
function pushToGitHub_(path, content, message) {
  const token = PropertiesService.getScriptProperties().getProperty('GITHUB_TOKEN');
  const repo = CONFIG.githubRepo;
  const branch = CONFIG.githubBranch;
  const url = `https://api.github.com/repos/${repo}/contents/${path}`;
  const headers = {
    Authorization: `Bearer ${token}`,
    Accept: 'application/vnd.github.v3+json',
  };

  let sha = null;
  const getRes = UrlFetchApp.fetch(`${url}?ref=${branch}`, {
    method: 'get',
    headers: headers,
    muteHttpExceptions: true,
  });

  if (getRes.getResponseCode() === 200) {
    sha = JSON.parse(getRes.getContentText()).sha;
  }

  const payload = {
    message: message,
    content: Utilities.base64Encode(content, Utilities.Charset.UTF_8),
    branch: branch,
  };
  if (sha) payload.sha = sha;

  const putRes = UrlFetchApp.fetch(url, {
    method: 'put',
    headers: headers,
    contentType: 'application/json',
    payload: JSON.stringify(payload),
    muteHttpExceptions: true,
  });

  const code = putRes.getResponseCode();
  if (code !== 200 && code !== 201) {
    throw new Error(`GitHub API error (${code}): ${putRes.getContentText()}`);
  }
}

/**
 * 処理済み Google Docs ID の一覧を返す。
 * スクリプトプロパティ `PROCESSED_IDS` にカンマ区切りで保持されている。
 *
 * @returns 処理済みドキュメント ID のセット
 */
function getProcessedIds_() {
  const raw = PropertiesService.getScriptProperties().getProperty('PROCESSED_IDS') || '';
  return new Set(raw.split(',').filter(Boolean));
}

/**
 * 複数のドキュメントを一括で処理済みとしてマークする。
 * 直近 50 件のみ保持し、古い ID は自動的に切り捨てられる。
 * スクリプトプロパティの容量制限（9KB/キー）を考慮した設計。
 *
 * @param existingIds - 既存の処理済み ID セット
 * @param newIds - 新たに処理済みとしてマークする Google Docs ID の配列
 */
function batchMarkAsProcessed_(existingIds, newIds) {
  for (const id of newIds) {
    existingIds.add(id);
  }
  const trimmed = [...existingIds].slice(-50);
  PropertiesService.getScriptProperties().setProperty('PROCESSED_IDS', trimmed.join(','));
}
```

## ディレクトリ構成とファイルの命名規則

議事録は会議ごとにディレクトリを分け、元の議事録と抽出した決定事項のファイルを同じ場所に置きます。

```
daily/
  2026-05-29_daily.md
  2026-05-29_daily_decisions.md
  2026-05-30_daily.md
  2026-05-30_daily_decisions.md
refinement/
  2026-05-28_refinement.md
  2026-05-28_refinement_decisions.md
```

議事録ファイル名は、`YYYY-MM-DD_<会議種別>.md` の形式にしています。  
日付順に並べやすく、会議種別でも検索しやすいためです。  
ファイル名を見るだけで、いつのどの会議の議事録かも分かります。

決定事項は、元の議事録ファイル名に `_decisions` を付けた別ファイルへ抽出します。  
形式は `YYYY-MM-DD_<会議種別>_decisions.md` です。

ここで元の議事録とは別ファイルにしているのは、次の理由からです。

* 決定事項の抽出が完了しているか判別しやすくするため
* 元の議事録は一次情報として保持し、編集対象にしないため

## 議事録から決定事項や TODO を抽出する

### 文字起こしまで読ませる

Gemini の概要だけでは見落としやすい暗黙の合意を拾うために、文字起こしも分析対象に含めています。

たとえば、概要に「実装方針について議論した」とあっても、文字起こしを読むと「初回は B 案で進め、A 案は後続改善に回す」という具体的な合意が交わされていることがあります。  
こうした合意は、後から会議を参照する人にとって重要な判断材料となります。

そのため、Skill では概要や詳細を論点探しの手がかりとして使い、最終的な本文は文字起こしをもとに確定するようにしています。

### 抽出ルールを決める

議事録に対して「要約して」と頼むだけでは、会議ごとに粒度が揺れます。  
ある日は細かい発言まで拾い、別の日は大きな結論だけにまとめるかもしれません。

そのため、Claude Skills には要約の依頼ではなく、抽出ルールを持たせています。  
ここで重要なのは、「何を拾うか」だけでなく「何を拾わないか」も決めておくことです。

単なる進捗報告や雑談まで拾うと、Slack 通知がノイズになります。  
会議後に読まれる情報にするには、業務上の判断や次の作業に影響するものへ絞る必要があります。

### 抽出結果を Slack に投稿する

Slack は、会議に出ていない人にも短時間で「何が決まったか」を届けるために使っています。

Slack では、メインメッセージに決定事項や TODO の見出しだけを投稿し、詳しい経緯はスレッドに分けています。

### Skill の例

ここまで説明した方針を、1 つの Skill にまとめると次のようになります。

議事録から決定事項と TODO を抽出する Skill

```
---
name: extract-decisions
description: "議事録から決定事項と TODO を抽出し、同じディレクトリに _decisions.md を作成して Slack に共有する。会議で決まったことを抽出して、議事録から決定事項をまとめて、YYYY-MM-DD_type.md の議事録を処理して、新しく追加された議事録を Slack に共有して、などの依頼で使う。"
---

# 概要

議事録から、会議後の判断や作業に必要な決定事項と TODO を抽出する。
元の議事録は一次情報として保持するため編集しない。
抽出結果だけを `{YYYY-MM-DD}_{type}_decisions.md` に書き出す。
書き出した内容は Slack に共有する。

## 実行手順

1. 対象ファイルを決める。
   ユーザーがファイルを指定している場合は、そのファイルだけを処理する。
   指定がない場合は `daily/`, `refinement/`, `weekly/`, `adhoc/` から `_decisions.md` が存在しない議事録を探す。
2. 議事録を読む。
   概要、詳細、次のステップで論点の候補を把握し、文字起こし本文で実際の合意を確認する。
3. 決定事項と TODO を抽出する。
   途中の提案や懸念ではなく、最後に採用された合意を書く。
4. 元ファイルと同じディレクトリに `_decisions.md` を作成する。
   例: `daily/2026-05-29_daily.md` から `daily/2026-05-29_daily_decisions.md` を作る。
5. Slack に投稿する。
   メインメッセージには決定事項と TODO の見出しだけを書く。
   詳しい背景が必要な場合はスレッドに書く。
6. 作成したファイルパス、Slack 投稿先、抽出した決定事項・TODO の件数を報告する。

## 抽出する対象

- 決定事項: 仕様、要件、優先度、技術選定、運用方針など、今後の判断や作業の基準になる合意
- TODO: 会話から発生した未完了の調査、対応、確認

## 抽出しない対象

- 単なる進捗報告
- 雑談、アイスブレイク、会議運営の確認
- 業務文脈のない一般論
- すでにチケット化済みで、会議中に新しい判断が発生していない作業報告

## 判断ルール

- 文字起こし本文を正とする。
  概要、詳細、次のステップは議論箇所を探す手がかりとしてだけ使う。
- 概要と文字起こしの内容が違う場合は、文字起こしの内容を採用する。
- 決定事項は「何が変わるか」を読者が判断できる粒度で書く。
  「整理する」「検討する」「明確化する」だけで終わらせない。
- TODO は、やること、担当者、確認対象が議事録から分かる場合に含める。
  担当者が不明な場合は `担当者未定` と書く。
- 決定事項や TODO が見つからない場合も `_decisions.md` を作成する。

## `_decisions.md` のフォーマット

```markdown
# {YYYY/MM/DD} {会議名}

## 決定事項

### 1. {短いタイトル}

**決定内容**
{何が決まったかを 1-2 文で書く}

背景: {なぜそう決まったか、どのような流れだったか}

---

## TODO

- [ ] {やること}
  - 担当: {担当者または担当者未定}
  - 補足: {なぜ必要か、何を確認するか}
```

TODO がない場合は `## TODO` を省略する。
決定事項がない場合は `## 決定事項` を省略する。
決定事項と TODO がどちらもない場合は、次の形式で書く。

```markdown
# {YYYY/MM/DD} {会議名}

決定事項・TODO は見つかりませんでした。
```

## Slack 投稿

Slack では、メインメッセージに会議名、議事録リンク、決定事項と TODO の見出しを載せる。
詳細な背景は、必要な場合だけスレッドに書く。

### メインメッセージのフォーマット

```mrkdwn
*{YYYY/MM/DD} {会議名}* （<{議事録URL}|議事録> / <{決定事項URL}|決定事項>）

*決定事項*
- {決定事項1}
- {決定事項2}

*TODO*
- {TODO1}
- {TODO2}
```

### スレッドメッセージのフォーマット

スレッドには、決定事項や TODO の詳細を書く。

```mrkdwn
*決定事項: {短いタイトル}*

*決まったこと*
- {具体的な決定内容}

*背景*
{なぜそう決まったか、どのような流れだったかを 2-4 文で書く}
```

```mrkdwn
*TODO: {短いタイトル}*

*やること*
- {TODO の内容}

*担当*
- {担当者または担当者未定}

*補足*
{なぜ必要か、何を確認するかを 1-3 文で書く}
```
```

## Jira のチケットに会議内容をコメントする

### 抽出済みの決定事項で論点のあたりを付ける

同じディレクトリに決定事項ファイル（`_decisions.md`）があれば先に読み、会議で決まったことや TODO のあたりを付けます。  
そのうえで議事録本文を読み、Jira に残すべき論点を判断します。  
決定事項ファイルは補助情報として使い、コメントに残す内容は議事録本文をもとに確認します。

### チケット本文ではなくコメントに残す

会議で出た判断材料を既存チケットへのコメントとして投稿します。  
チケット本文は担当者の作業内容や受け入れ条件に直接影響するため、AI で自動更新する対象にはしていません。  
Jira への反映は「チケットを更新する」ではなく、「会議で出た判断材料をコメントとして添える」くらいの位置づけです。

### Skill の例

ここまで説明した方針を、1 つの Skill にまとめると次のようになります。

会議内容を既存 Jira チケットへコメントする Skill

```
---
name: post-jira-comments
description: "議事録や _decisions.md から既存 Jira チケットに関係する論点を抽出し、Jira チケットにコメントを残す。議事録から Jira にコメントして、会議内容をチケットに残して、決定事項を関連チケットへ転記して、などの依頼で使う。"
---

# 概要

議事録に出てきた判断材料を、関連する既存 Jira チケットへコメントとして残す。
チケット本文や受け入れ条件を AI が自動で変更すると影響が大きいため、このスキルはコメント投稿だけを担当する。
新規チケット作成はしない。

## 実行手順

1. 対象議事録を決める。
   ユーザーが議事録ファイルを指定している場合は、そのファイルだけを処理する。
2. 同じディレクトリに `_decisions.md` があれば先に読む。
   決定事項や TODO のあたりを付けるための補助情報として使う。
3. 議事録本文を読み、Jira に残すべき論点を抽出する。
   決定事項、TODO、仕様変更、担当者の判断材料、チケットの前提を変える内容を候補にする。
4. 論点に関係しそうな既存 Jira チケットを探す。
   議事録内に `PJ-123` のような issue key がある場合は、そのチケットを優先する。
   issue key がない場合は、論点のキーワードで Jira を検索する。
5. 候補チケットの summary と description を読み、関連度を判定する。
   `強く関連` または `関連あり` のチケットだけを投稿対象にする。
6. 投稿前に、issue key、summary、関連度、コメント本文を表示する。
   `--dry-run` が指定されている場合は投稿しない。
7. Jira へコメントを投稿する。
   Jira への書き込みは Atlassian MCP を使う。
8. 投稿した issue key と、投稿しなかった候補の理由を報告する。

## 抽出する対象

- 既存チケットの実装方針、受け入れ条件、優先度、担当に影響する決定
- チケット作業時に知っておくべき前提変更
- 会議中に明示された `PJ-123` のような issue key に関する判断
- `_decisions.md` に残っている決定事項や TODO のうち、議事録本文でも確認でき、既存チケットに直接関係するもの

## 抽出しない対象

- 単なる進捗報告
- チケットに影響しない雑談や会議運営の話
- 関連チケットを特定できない一般論
- 新規チケットを作るべきだが、既存チケットには紐づかない論点

## 関連度の判定

| 関連度 | 投稿 | 判断基準 |
| --- | --- | --- |
| 強く関連 | する | 議論の主題がチケットの内容そのもの |
| 関連あり | する | チケットの実装方針や受け入れ条件に影響する |
| 弱い関連 | しない | キーワードは似ているが、チケット作業には直接影響しない |
| 無関係 | しない | 偶然同じ言葉が出ているだけ |

迷った場合は投稿しない。
Jira コメントは関係者に通知されるため、弱い関連まで広げるとノイズになる。

## コメント本文

コメントは結論を先に書く。
判断の背景が必要な場合だけ、経緯を書く。

```markdown
## 決まったこと
- {チケット担当者が知るべき決定事項}
- {必要なら追加の決定事項}

## 経緯の整理
{前提変更、判断理由、合意に至った流れを 2-5 文で書く}

---
🤖 Claude 自動生成 / 出典: [{議事録相対パス}]({GitHub URL})
```
```

## スキルを自動で実行する

抽出スキルは、運用に合わせて実行方法を選べます。

手軽に始めるなら、[Claude Code の Routine 機能](https://code.claude.com/docs/ja/routines) で定期実行するのが便利です。  
会議が終わる時刻に合わせて抽出スキルを実行するように設定しておけば、決まった時間に議事録を処理できます。

ただし、会議が長引くと、Routine で設定した時刻と議事録が生成されるタイミングがずれることがあります。  
自分の運用ではこのズレが何度か起こり、あとから手動で抽出スキルを実行していました。

手動実行をなくして完全に自動化したかったため、私の場合は議事録ファイルが追加されたタイミングで処理を始められる GitHub Actions を使っています。

まずは Routine 機能で始め、実行タイミングをより細かく制御したくなったら GitHub Actions に移す形でもよいと思います。

## まとめ

議事録を Markdown に変換してリポジトリに保存しておくと、会議ごとのログを横断して扱いやすくなります。  
そこに抽出ルールを持つ Claude Skills を組み合わせると、決定事項、TODO、チケットに残すべき判断の背景が、会議後に追いかける手間なく手元に揃います。

まずは議事録を Markdown に変換し、1 つのリポジトリに集めるところから試してみてください。

## 参考リンク

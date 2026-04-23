---
id: "2026-04-04-github-copilot-cli-マスタークラス-01"
title: "GitHub Copilot CLI マスタークラス"
url: "https://zenn.dev/microsoft/articles/github_copilot_cli_masterclass"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-04"
date_collected: "2026-04-05"
summary_by: "auto-rss"
---

![](https://static.zenn.studio/user-upload/fb12a4cdf7be-20260401.png)

# はじめに

この記事では、GitHub Copilot CLIをマスターしたい人に向けて、インストールからGitHub Copilot CLIを用いたアプリケーションの開発まで手を動かしながら完全に理解する会となります。

最近ではほぼ毎日GitHub CopilotのUpdateがあり、非常に進化が早い分野になります。  
また、日々どんどんと便利機能が追加されている状況です。

特に2026年2月25日にGAされたGitHub Copilot CLIは非常に便利で、エンジニアだけではなく、ビジネス職の方にも是非使っていただきたいツールになります。

そこで今回は、GitHub Copilot CLIを使って開発をする上で、**基本的な使い方** から始め、 **開発ワークフロー** や **SKILLs**、**MCP連携**、最後にはアプリ開発まで体感していただけるマスタークラスを作ってみました。

是非、一緒に手を動かしながらGitHub Copilot 理解を深めに深めていただければ幸いです。

本記事が読み終わる頃には、GitHub Copilot CLIを使いこなして、日々の開発に活用できるようになっているはずです。

それでは早速やっていきましょう🚀

#### 対象読者

#### 利用したリポジトリ

<https://github.com/SatakeYusuke19920527/mastering-github-copilot-group-findy-2026-04-08>

# 目次

# GitHub Copilot CLIをインストールして利用を開始する

では、早速GitHub Copilot CLIをインストールして利用を開始してみましょう。

Install する方法は以下のコマンドになります。

```
npm install -g @github/copilot
```

startするには以下のコマンドを実行します。

以下の画像ような感じで起動できます。  
![](https://static.zenn.studio/user-upload/a7cb28a43d28-20260321.png)

また、２回目以降のログイン時はバナーが出ないのですが、以下のコマンドであれば何度でもバナーを見ることが出来ます。

ちなみに筆者は毎回バナーを表示させる系です。

ログインすると、このような画像の感じで入力待ちになります。  
![](https://static.zenn.studio/user-upload/52644685b0c4-20260321.png)

以下のコマンドを入力して、ログインしましょう。

GitHub.comへログインでOKです。  
![](https://static.zenn.studio/user-upload/a2e23e752c7b-20260321.png)

以下の表示がCLI上に表示されるので、Linkにアクセスして、コードを入力しましょう。

> Enter one-time code: XXXX-XXXX at <https://github.com/login/device>

これでログインは完了です。  
まとめると、以下のような流れですね。  
![](https://static.zenn.studio/user-upload/8c3ddb3c9ff4-20260321.png)

Login後、Helloといったらこんな感じで返してくれます。  
![](https://static.zenn.studio/user-upload/8e9f0e261d9f-20260321.png)

# GitHub Copilot CLIの利用を終了する

次は終了の仕方を見てみましょう。  
GitHub Copilot CLIは以下のコマンドで終了することができます。

GitHub Copilot CLIはセッションにて情報を管理しています。  
exitしたけど、セッション前のやつでやり直したいね...。みたいな時は以下で起動するとセッションが復活して以前の会話内容からスタートしてくれます。

特定のセッションを思い出したい時は以下です。

```
# Pick from a list of sessions interactively
copilot --resume

# Or resume a specific session by ID
copilot --resume abc123
```

セッション一覧を見ることができるコマンドもあります。

![](https://static.zenn.studio/user-upload/4512bfec9860-20260403.png)

そのような便利コマンドはGitHub Copilot CLIには多く搭載されています。  
2026/04/01 時点でGitHub Copilot CLIで使えるコマンドは以下になります。

| 指示 | その機能 | 使用時期 |
| --- | --- | --- |
| `/init` | リポジトリ用の Copilot 指示ファイルを初期化する | 新しいリポジトリで最初に設定するとき |
| `/agent` | 利用可能なエージェントを確認・選択する | 専用エージェントを使いたいとき |
| `/skills` | スキル機能を管理する | Copilot の拡張機能を調整したいとき |
| `/mcp` | MCP サーバー設定を管理する | 外部ツール連携を設定したいとき |
| `/plugin` | プラグインやマーケットプレイスを管理する | プラグインを追加・確認したいとき |
| `/model` | 使用する AI モデルを表示・切り替える | モデルを変更したいとき |
| `/delegate` | セッションを GitHub 側に渡して PR 作成まで進める | 実装をまとめて PR 化したいとき |
| `/fleet` | 並列サブエージェント実行を有効化する | 複数タスクを並行で進めたいとき |
| `/tasks` | バックグラウンドタスクを確認・管理する | 実行中の作業状況を見たいとき |
| `/ide` | IDE ワークスペースに接続する | エディタ連携を有効にしたいとき |
| `/diff` | 現在のディレクトリでの変更差分を確認する | 変更内容を見直したいとき |
| `/pr` | 現在ブランチの Pull Request を操作する | PR を作成・確認・更新したいとき |
| `/review` | コードレビューエージェントで変更を分析する | 実装後にレビューしたいとき |
| `/lsp` | Language Server の設定を管理する | 補完や解析環境を整えたいとき |
| `/terminal-setup` | ターミナルの複数行入力を設定する | 長いコマンドを入力しやすくしたいとき |
| `/allow-all` | すべての権限を許可する | 制限なくツールを使いたいとき |
| `/add-dir` | ファイルアクセスを許可するディレクトリを追加する | 特定フォルダを触れるようにしたいとき |
| `/list-dirs` | 許可済みディレクトリ一覧を表示する | どこにアクセスできるか確認したいとき |
| `/cwd` | 現在ディレクトリを表示・変更する | 作業場所を確認・移動したいとき |
| `/reset-allowed-tools` | 許可済みツールをリセットする | 権限設定を初期化したいとき |
| `/resume` | 別セッションに切り替える | 以前の作業を再開したいとき |
| `/rename` | セッション名を変更する | セッションを整理したいとき |
| `/context` | コンテキスト使用量を表示する | トークン消費を確認したいとき |
| `/usage` | 利用統計を表示する | 使用量を把握したいとき |
| `/session` | セッション情報を管理する | セッション全体を整理したいとき |
| `/compact` | 会話履歴を要約してコンテキストを節約する | 長いやり取りの後に軽くしたいとき |
| `/share` | セッションや調査結果を Markdown や Gist に共有する | 内容を外部保存したいとき |
| `/copy` | 直前の応答をクリップボードにコピーする | すぐ貼り付けたいとき |
| `/rewind` | 直前のターンに戻して変更を巻き戻す | ひとつ前の操作を取り消したいとき |
| `/help` | 利用可能なすべてのコマンドを表示する | コマンドを忘れたとき |
| `/changelog` | CLI の更新履歴を表示する | 何が変わったか確認したいとき |
| `/feedback` | CLI へのフィードバックを送る | 改善要望を伝えたいとき |
| `/theme` | カラーテーマを確認・変更する | 見た目を変えたいとき |
| `/update` | CLI を最新版に更新する | 最新版にしたいとき |
| `/version` | バージョン情報を表示する | 現在の CLI バージョンを確認したいとき |
| `/experimental` | 実験機能を確認・切り替える | 新機能を試したいとき |
| `/clear` | 現在の会話を破棄して新しく始める | 話題を切り替えたいとき |
| `/instructions` | カスタム指示ファイルを確認・切り替える | 指示設定を見直したいとき |
| `/streamer-mode` | 配信向け表示モードを切り替える | 画面共有や配信時に情報を隠したいとき |
| `/exit` / `/quit` | セッションを終了する | 作業を終えるとき |
| `/login` | Copilot にログインする | 利用開始時や再ログイン時 |
| `/logout` | Copilot からログアウトする | アカウントを切り替えたいとき |
| `/new` | 新しい会話を始める | 別テーマで作業したいとき |
| `/plan` | 実装前に計画を立てる | 複雑な機能を作る前 |
| `/research` | GitHub と Web を使って詳細調査する | 実装前に調査が必要なとき |
| `/restart` | セッションを維持したまま CLI を再起動する | 動作をリフレッシュしたいとき |
| `/undo` | 直前の操作を巻き戻す | ひとつ前の変更を取り消したいとき |
| `/user` | GitHub ユーザー一覧を管理する | ユーザー設定を確認したいとき |

忘れた時はいつでも `/help` コマンドで確認できますので、安心してください。

# GitHub Copilot CLIのモード

GitHub Copilot は4つのモードがあります。  
![](https://static.zenn.studio/user-upload/2207e7f61f6c-20260404.png)

* Interactive > 通常の会話形式のモードです。
* Programmatic > プログラムモード（copilot -p "<your prompt>"）は、簡単な単発の質問に使用します。
* Plan > プランモード（/plan）は、コーディング前に詳細に計画を立てる必要がある場合に利用します。
* Autopilot > オートパイロットモードは、自動化されたタスク実行に使用します。

それぞれを用途に分けて使いこなしていけば非常に強力な共同開発者になってくれます。

# コンテキストを用いた会話

## @ の使い方

@を使うとファイルを参照することが出来ます。  
利用パターンとしては以下になります。

| パターン | その機能 | 使用例 |
| --- | --- | --- |
| `@ファイル名` | 単一のファイルを参照する | `/review @samples/lib/sample.py` |
| `@フォルダ名/` | ディレクトリ内のすべてのファイルを参照する | `/review @samples/lib/` |
| `@file1.py @file2.py` | 複数のファイルを参照する | `Compare @samples/lib/file1.py @samples/lib/file2.py` |

みたいな感じで使えます。

例えば、

```
please explain about @ディレクトリ名
```

とか入力すると、ディレクトリの説明を行なってくれます。  
![](https://static.zenn.studio/user-upload/c5f020a1afa6-20260321.png)

単一ファイルを参照することももちろん可能ですし、複数ファイルを比較することも出来ます。  
例えば、

```
@ディレクトリ名1, @ディレクトリ名2, @ディレクトリ名3 について説明してください。
```

筆者のローカル環境で実行した結果はこんな感じです。  
![](https://static.zenn.studio/user-upload/970db0dadf39-20260321.png)

ディレクトリ配下もいい感じに説明してくれるのはいいですよね。  
コマンドはたくさんありますが、基本的には日本語でも英語でも自然な形で指示すれば、理解してくれます。

コマンドも覚えられればBestですが、とりあえずは自然な形で指示してみて、慣れてきたらコマンドも覚えていくスタイルでいいですね。

# 開発ワークフローでのGitHub Copilot CLIの活用

この章では、開発者が一般的に使用する5つのワークフローについて説明します。  
GitHub Copilotを使えば、各ワークフローご自身のニーズに合致し、現在のプロジェクトに最適なワークフローが簡単に実現できます。  
![](https://static.zenn.studio/user-upload/506416374aaf-20260321.png)

以下の流れでGitHub Copilot CLIの使い方を説明していきます。

* コードレビュー
* リファクタリング
* デバッグ
* テスト生成
* PR作成

## ワークフロー1: コードレビュー

### 基本的なコードレビュー

ファイルのレビューには **/review**を使って実施します。  
以下のようにコマンドを実施します。

```
/review @ファイル名 for code quality
```

/review @ファイル名 for **気になる項目** のようにcopilotに支持すると、そこを重点的に確認してくれます。  
こんな感じで実行して..  
![](https://static.zenn.studio/user-upload/f674be115a4f-20260403.png)

こんな感じで表示してくれます。  
![](https://static.zenn.studio/user-upload/165faaaef52c-20260403.png)

Bugはもちろん、Minorな警告も出してくれていますね。  
Reviewerも非常に助かる機能です。

### クロスファイルプロジェクトレビュー

もちろん、複数ファイルやディレクトリの横断的なレビューも可能です。  
以下のような形でプロジェクト全体をレビューすることが出来ます。

```
@ディレクトリ名 Review this entire project. Create a markdown checklist of issues found, categorized by severity
```

こんな感じで実行します。  
サンプルでは、src/lib/ai というディレクトリについてレビューをしてもらい、checklistを出してもらいます。  
![](https://static.zenn.studio/user-upload/7b8b4600df2b-20260403.png)

こんな感じで重要度に分けて結果を返してくれます。また、最優先の事項も表示してくれてますね...(RBAC...(´Д` ))  
![](https://static.zenn.studio/user-upload/405e4ca5704d-20260403.png)

### インタラクティブなコードレビュー

前述にもありました通り、GitHub Copilot CLIはインタラクティブなコードレビューも提供してくれます。

先ほどのエラーハンドリング不足を対象にインタラクティブに解決したいと思います。

![](https://static.zenn.studio/user-upload/d329273d3ee1-20260404.png)

こんな感じで指示すると、以下のような結果が得られました。  
![](https://static.zenn.studio/user-upload/17d33eb96b32-20260404.png)  
![](https://static.zenn.studio/user-upload/b0ce94bfdcad-20260404.png)  
![](https://static.zenn.studio/user-upload/343b91b7ae22-20260404.png)

修正を適用しますか？と聞いてくれるのは非常に便利ですね。

### レビューチェックリストテンプレート

GitHub Copilot CLI に、出力を特定の形式を指定することも出来ます。

```
/review @samples/sample-project/ and create a markdown checklist of issues found, categorized by:
- Critical (data loss risks, crashes)
- High (bugs, incorrect behavior)
- Medium (performance, maintainability)
- Low (style, minor improvements)
```

この形式でやってくれると、人間側としても見やすいですよね。

### Gitの変更を理解する（`/review` にとって重要）

この `/review` コマンドを使う前に、Gitにおける **2種類の変更** を理解しておく必要があります。

#### 変更の種類

| 変更の種類 | 意味 | 確認方法 |
| --- | --- | --- |
| 段階的な変更 | 次のコミット用にマークしたファイル（`git add` 済み） | `git diff --staged` |
| 非ステージングの変更 | 変更したが、まだ `git add` していないファイル | `git diff` |

みなさんご存知のgitのコマンドですが、念の為...

```
git status           # ステージ済み・未ステージの両方を表示
git add file.py      # ファイルをコミット対象としてステージする
git diff             # 未ステージの変更を表示
git diff --staged    # ステージ済みの変更を表示
```

### `/review` コマンドの使用

`/review` コマンドは、組み込みの **コードレビューエージェント** を起動します。  
このエージェントは、**ステージ済み** および **未ステージ** の変更を高感度で分析するように最適化されています。

自由形式のプロンプトを書く代わりに、**スラッシュコマンド** を使って専用の組み込みエージェントを起動してください。

ステージ済み / 未ステージの変更に対してコードレビューを実行  
実用的で具体的なフィードバックを返す  
/review Check for security issues in authentication  
認証まわりのセキュリティ観点に絞ってレビューを実行

コードレビューエージェントは、保留中の変更がある場合 に最も効果を発揮します。  
より集中的なレビューを行いたい場合は、git add でファイルをステージしてから実行してください。

## ワークフロー2: リファクタリング

### シンプルなリファクタリング

コードをレビューしてもらった次はリファクタリングです。  
リファクタリングも非常に簡単にGitHub Copilot CLIにお願いできます。

例えばリファクタリング必要そうな以下のコードがあったとします。

```
// 生徒の成績データを処理するサンプル関数群（リファクタリング練習用）

export function proc(d: any[], t: string, m: string) {
  let r: any[] = [];
  for (let i = 0; i < d.length; i++) {
    if (d[i].type == t) {
      if (d[i].month == m) {
        let s = 0;
        for (let j = 0; j < d[i].scores.length; j++) {
          s = s + d[i].scores[j];
        }
        let a = s / d[i].scores.length;
        let g;
        if (a >= 90) {
          g = 'S';
        } else if (a >= 80) {
          g = 'A';
        } else if (a >= 70) {
          g = 'B';
        } else if (a >= 60) {
          g = 'C';
        } else {
          g = 'D';
        }
        r.push({
          name: d[i].name,
          avg: a,
          grade: g,
          scores: d[i].scores,
          total: s,
          count: d[i].scores.length,
          type: d[i].type,
          month: d[i].month,
          passed: a >= 60 ? true : false,
          message:
            a >= 60
              ? d[i].name + 'さんは合格です'
              : d[i].name + 'さんは不合格です',
        });
      }
    }
  }
  // ソート
  for (let i = 0; i < r.length; i++) {
    for (let j = 0; j < r.length - 1; j++) {
      if (r[j].avg < r[j + 1].avg) {
        let tmp = r[j];
        r[j] = r[j + 1];
        r[j + 1] = tmp;
      }
    }
  }
  for (let i = 0; i < r.length; i++) {
    r[i].rank = i + 1;
  }
  return r;
}

export function makeReport(d: any[], t: string, m: string) {
  let results = proc(d, t, m);
  let report = '';
  report = report + '=== 成績レポート ===\n';
  report = report + '種別: ' + t + '\n';
  report = report + '月: ' + m + '\n';
  report = report + '受験者数: ' + results.length + '\n';

  let totalAvg = 0;
  for (let i = 0; i < results.length; i++) {
    totalAvg = totalAvg + results[i].avg;
  }
  if (results.length > 0) {
    totalAvg = totalAvg / results.length;
  }
  report = report + '平均点: ' + totalAvg.toFixed(1) + '\n';
  report = report + '---\n';

  for (let i = 0; i < results.length; i++) {
    report =
      report +
      results[i].rank +
      '位: ' +
      results[i].name +
      ' - ' +
      results[i].avg.toFixed(1) +
      '点 (' +
      results[i].grade +
      ') ' +
      results[i].message +
      '\n';
  }

  let sCount = 0;
  let aCount = 0;
  let bCount = 0;
  let cCount = 0;
  let dCount = 0;
  for (let i = 0; i < results.length; i++) {
    if (results[i].grade == 'S') sCount++;
    if (results[i].grade == 'A') aCount++;
    if (results[i].grade == 'B') bCount++;
    if (results[i].grade == 'C') cCount++;
    if (results[i].grade == 'D') dCount++;
  }

  report = report + '---\n';
  report = report + 'S: ' + sCount + '人\n';
  report = report + 'A: ' + aCount + '人\n';
  report = report + 'B: ' + bCount + '人\n';
  report = report + 'C: ' + cCount + '人\n';
  report = report + 'D: ' + dCount + '人\n';
  report =
    report +
    '合格率: ' +
    (results.length > 0
      ? (
          (results.filter((x: any) => x.passed).length / results.length) *
          100
        ).toFixed(1)
      : '0') +
    '%\n';

  return report;
}
```

リファクタリングしがいがありますね。ツッコミどころが満載のコードです。

早速レビューしてみます。  
![](https://static.zenn.studio/user-upload/002bffca1bdc-20260403.png)

こんな感じでいい感じにご指摘を得られました。  
緊急度で分けてくれるのいいですね。あと、これならすぐにリファクタリングに入れそうです。  
![](https://static.zenn.studio/user-upload/76a7e9d7a18c-20260403.png)

では、本題のリファクタリングをしていただきましょう。  
![](https://static.zenn.studio/user-upload/404314f3d565-20260403.png)

リファクタリングした一覧を出してくれました。  
![](https://static.zenn.studio/user-upload/776bf13f60a1-20260403.png)

```
// 生徒の成績データを処理するユーティリティ

/** 成績グレード */
type Grade = 'S' | 'A' | 'B' | 'C' | 'D';

const GRADE_THRESHOLDS: { min: number; grade: Grade }[] = [
  { min: 90, grade: 'S' },
  { min: 80, grade: 'A' },
  { min: 70, grade: 'B' },
  { min: 60, grade: 'C' },
];
const DEFAULT_GRADE: Grade = 'D';
const PASSING_THRESHOLD = 60;

/** 生徒の成績入力データ */
export interface StudentScoreInput {
  name: string;
  type: string;
  month: string;
  scores: number[];
}

/** 評価済みの成績結果 */
export interface StudentResult {
  name: string;
  type: string;
  month: string;
  scores: number[];
  total: number;
  count: number;
  average: number;
  grade: Grade;
  passed: boolean;
  rank: number;
}

function calculateAverage(scores: number[]): number {
  const total = scores.reduce((sum, score) => sum + score, 0);
  return total / scores.length;
}

function determineGrade(average: number): Grade {
  return (
    GRADE_THRESHOLDS.find(({ min }) => average >= min)?.grade ?? DEFAULT_GRADE
  );
}

/**
 * 成績データをフィルタ・評価・ランキングして返す
 */
export function processStudentScores(
  data: StudentScoreInput[],
  type: string,
  month: string,
): StudentResult[] {
  const results: StudentResult[] = data
    .filter((student) => student.type === type && student.month === month)
    .filter((student) => student.scores.length > 0)
    .map((student) => {
      const total = student.scores.reduce((sum, s) => sum + s, 0);
      const average = calculateAverage(student.scores);
      const grade = determineGrade(average);
      return {
        name: student.name,
        type: student.type,
        month: student.month,
        scores: student.scores,
        total,
        count: student.scores.length,
        average,
        grade,
        passed: average >= PASSING_THRESHOLD,
        rank: 0,
      };
    });

  results.sort((a, b) => b.average - a.average);
  results.forEach((result, index) => {
    result.rank = index + 1;
  });

  return results;
}

function countByGrade(results: StudentResult[]): Record<Grade, number> {
  const counts: Record<Grade, number> = { S: 0, A: 0, B: 0, C: 0, D: 0 };
  for (const { grade } of results) {
    counts[grade]++;
  }
  return counts;
}

/**
 * 成績レポートのテキストを生成する
 */
export function makeReport(
  data: StudentScoreInput[],
  type: string,
  month: string,
): string {
  const results = processStudentScores(data, type, month);

  const overallAverage =
    results.length > 0
      ? results.reduce((sum, r) => sum + r.average, 0) / results.length
      : 0;

  const gradeCounts = countByGrade(results);
  const passCount = results.filter((r) => r.passed).length;
  const passRate = results.length > 0 ? (passCount / results.length) * 100 : 0;

  const header = [
    `=== 成績レポート ===`,
    `種別: ${type}`,
    `月: ${month}`,
    `受験者数: ${results.length}`,
    `平均点: ${overallAverage.toFixed(1)}`,
    `---`,
  ].join('\n');

  const ranking = results
    .map((r) => {
      const status = r.passed ? '合格' : '不合格';
      return `${r.rank}位: ${r.name} - ${r.average.toFixed(1)}点 (${r.grade}) ${r.name}さんは${status}です`;
    })
    .join('\n');

  const gradeLabels: Grade[] = ['S', 'A', 'B', 'C', 'D'];
  const distribution = gradeLabels
    .map((g) => `${g}: ${gradeCounts[g]}人`)
    .join('\n');

  return [
    header,
    ranking,
    `---`,
    distribution,
    `合格率: ${passRate.toFixed(1)}%`,
    '',
  ].join('\n');
}
```

コメントも入っていたり、TypeScriptの型もわかりやすく定義してくれていたり非常に読みやすいコードになりましたね。

もちろん、単一のファイルだけではなく、複数ファイルのリファクタリングも可能です。

```
/review @samples/sample1.py, @samples/sample2.py for code quality
```

と確認したあとに、

```
@samples/sample1.py, @samples/sample2.py をリファクタリングして
```

とすると、複数ファイルにまたがるリファクタリングも可能です。  
もちろん、ディレクトリを指定して、プロジェクト全体のリファクタリングも可能です。

```
src/lib/ai/ の配下のファイルをリファクタリングして
```

### テストを用いた安全なリファクタリング

関連する2つの依頼を、複数ターンの対話としてつなげます。  
まずテストを生成し、その後でテストを安全網としてリファクタリングを行います。

```
@samples/sample.py Before refactoring, generate tests for current behavior
```

```
Now refactor the BookCollection class to use a context manager for file operations
```

まずテストを作成してからリファクタリングすることで、**既存の振る舞いが保たれていることを確認しながら** 安心して改善できます。

私は結構慎重派且つ、一発でリファクタリングを終わらせたい人なので、テスト作って確認してからリファクタリングを実施するようにしています。

## ワークフロー3: デバッグ

### シンプルなデバッグ

GitHub Copilot CLIを使うと、**コンテキストを理解したデバッグ** が可能になります。

以下のコードで試してみましょう。  
3つのバグが含まれています。一読して見つけて見てください。

```
// 生徒の成績データを処理するユーティリティ

/** 成績グレード */
type Grade = 'S' | 'A' | 'B' | 'C' | 'D';

const GRADE_THRESHOLDS: { min: number; grade: Grade }[] = [
  { min: 90, grade: 'S' },
  { min: 80, grade: 'A' },
  { min: 70, grade: 'B' },
  { min: 60, grade: 'C' },
];
const DEFAULT_GRADE: Grade = 'D';
const PASSING_THRESHOLD = 60;

/** 生徒の成績入力データ */
export interface StudentScoreInput {
  name: string;
  type: string;
  month: string;
  scores: number[];
}

/** 評価済みの成績結果 */
export interface StudentResult {
  name: string;
  type: string;
  month: string;
  scores: number[];
  total: number;
  count: number;
  average: number;
  grade: Grade;
  passed: boolean;
  rank: number;
}

function calculateAverage(scores: number[]): number {
  const total = scores.reduce((sum, score) => sum + score, 1);
  return total / scores.length;
}

function determineGrade(average: number): Grade {
  return (
    GRADE_THRESHOLDS.find(({ min }) => average >= min)?.grade ?? DEFAULT_GRADE
  );
}

/**
 * 成績データをフィルタ・評価・ランキングして返す
 */
export function processStudentScores(
  data: StudentScoreInput[],
  type: string,
  month: string,
): StudentResult[] {
  const results: StudentResult[] = data
    .filter((student) => student.type === type && student.month === month)
    .filter((student) => student.scores.length > 0)
    .map((student) => {
      const total = student.scores.reduce((sum, s) => sum + s, 0);
      const average = calculateAverage(student.scores);
      const grade = determineGrade(average);
      return {
        name: student.name,
        type: student.type,
        month: student.month,
        scores: student.scores,
        total,
        count: student.scores.length,
        average,
        grade,
        passed: average >= PASSING_THRESHOLD,
        rank: 0,
      };
    });

  results.sort((a, b) => a.average - b.average);
  results.forEach((result, index) => {
    result.rank = index + 1;
  });

  return results;
}

function countByGrade(results: StudentResult[]): Record<Grade, number> {
  const counts: Record<Grade, number> = { S: 0, A: 0, B: 0, C: 0, D: 0 };
  for (const { grade } of results) {
    counts[grade]++;
  }
  return counts;
}

/**
 * 成績レポートのテキストを生成する
 */
export function makeReport(
  data: StudentScoreInput[],
  type: string,
  month: string,
): string {
  const results = processStudentScores(data, type, month);

  const overallAverage =
    results.length > 0
      ? results.reduce((sum, r) => sum + r.average, 0) / results.length
      : 0;

  const gradeCounts = countByGrade(results);
  const passCount = results.filter((r) => r.passed).length;
  const passRate = results.length > 0 ? (passCount / results.length) * 100 : 0;
  gradeCounts['S'] += gradeCounts['A'];

  const header = [
    `=== 成績レポート ===`,
    `種別: ${type}`,
    `月: ${month}`,
    `受験者数: ${results.length}`,
    `平均点: ${overallAverage.toFixed(1)}`,
    `---`,
  ].join('\n');

  const ranking = results
    .map((r) => {
      const status = r.passed ? '合格' : '不合格';
      return `${r.rank}位: ${r.name} - ${r.average.toFixed(1)}点 (${r.grade}) ${r.name}さんは${status}です`;
    })
    .join('\n');

  const gradeLabels: Grade[] = ['S', 'A', 'B', 'C', 'D'];
  const distribution = gradeLabels
    .map((g) => `${g}: ${gradeCounts[g]}人`)
    .join('\n');

  return [
    header,
    ranking,
    `---`,
    distribution,
    `合格率: ${passRate.toFixed(1)}%`,
    '',
  ].join('\n');
}
```

わかりましたか？  
GitHub Copilot CLIに聞いてみましょう。

```
@ファイル名のコードにはバグが含まれているようです。一覧で表示して。
```

以下のバグが含まれていました。  
![](https://static.zenn.studio/user-upload/ff4fbdffaab3-20260404.png)

(私としては結構わかりにくいバグを仕込めたと思ったのですが、さすがですね...)

デバッグは以下の指令でGitHub Copilot CLIにお願いしてみましょう。

```
# Pattern: "Expected X but got Y"
@ファイル名 calculateAverage([80, 70, 90]) の結果が 80.0 になるはずが 80.3 になっている。reduce の初期値を確認して修正して
```

```
# Pattern: "Unexpected behavior"
@ファイル名 rocessStudentScores のランキングで、最も点数が低い生徒が1位になっている。成績順位は平均点が高い順に並ぶべき。ソート処理を確認して修正して
```

```
# Pattern: "Wrong results"
@ファイル名 makeReport のグレード分布でSの人数が実際より多く表示される。Aが3人いるとSの人数が3人多くなる。gradeCountsの集計処理を確認して不要な加算を修正して
```

とこんな感じで、**症状**（何が起こっているか）と **期待される動作**（何が起こるべきか）を説明してください。残りの分析はいい感じに GitHub Copilot CLI が進めてくれます。

### AIが関連するバグを発見

コンテキストを理解したデバッグが真価を発揮するのは、こうした場面です。  
バグのあるアプリで、次のシナリオを試してみてください。ファイル全体を `@` で参照し、ユーザーが報告した症状だけを伝えます。GitHub Copilot CLI は **根本原因** を追跡し、近くに潜む他のバグまで見つけることがあります。

```
@src/lib/sample.ts
ユーザー報告:「成績の平均点が手計算と微妙にずれている。差は小さいが常に高めに出る」
なぜこうなるのか調査して原因を特定して
```

結果は以下のようになりました。  
![](https://static.zenn.studio/user-upload/4d0d66ec16af-20260404.png)

原因箇所の特定と、状況の説明などしてくれており、非常にわかりやすいですね。

これが出来る理由は、GitHub Copilot CLI が **ファイル全体を読み込み**、**バグレポートの文脈を理解し**、**明確な説明と具体的な修正方法** を提示できるからです。

GitHub Copilot CLI はファイル全体を分析するため、質問していない別の問題まで見つけることがあります。たとえば検索機能の修正中に、**大文字小文字の扱い** に関する別のバグにも気づくかもしれません。

### 実世界のセキュリティに関する補足情報

自分のコードのデバッグも重要ですが、本番環境のアプリケーションにおける **セキュリティ脆弱性** を理解することも極めて重要です。  
次の例では、見慣れないファイルを Copilot CLI に渡し、セキュリティ上の問題がないか監査させます。

```
@ファイル名 Find all security vulnerabilities in this TypeScript service
```

このファイルには、実際の運用環境で遭遇しうる **現実的なセキュリティパターン** が含まれている想定です。

### よく見かけるセキュリティ用語

* **SQLインジェクション**: ユーザー入力がデータベースクエリに直接埋め込まれ、攻撃者が悪意のあるコマンドを実行できる状態
* **パラメータ化クエリ**: 安全な代替手段。プレースホルダー（`?` など）を使って、ユーザーデータと SQL コマンドを分離する
* **競合状態**: 2つの操作が同時に発生し、互いに干渉して不整合を起こす状態
* **XSS（クロスサイトスクリプティング）**: 攻撃者が悪意のあるスクリプトを Web ページに埋め込むこと

セキュリティ面では、開発の初期では後回しにされがちな項目ではありますが、昨今非常に重要な要素の一つになります。  
ただ、セキュリティ担当者がコード全体のレビューやテストを実施するのは現実的ではない為、GitHub Copilot CLIのようなツールを活用して、**コード全体を分析** し、**潜在的な脆弱性を特定** するのが効果的です。

### エラーを理解する

スタックトレースとファイル参照をプロンプトに直接貼り付けると、GitHub Copilot CLI がエラーをソースコードに対応付けやすくなります。

```
I'm getting this error:
src/lib/sample.ts:55:51 - error TS2367:
 This comparison appears to be unintentional because
 the types 'string' and 'number' have no overlap.

 student.month === month
 ~~~~~~~~~~~~~~~~~~~~~~~

@ファイル名 Explain why and how to fix it
```

### テストケースを使用したデバッグ

具体的で再現可能なテストケースを渡すことで、GitHub Copilot CLI がより正確に推論できます。  
**正確な入力** と **観測された出力** を書くのがポイントです。

```
@ファイル名
 以下のテストケースで期待値と異なる結果が出る。原因を調査して修正して
 入力:    （具体的なコードで再現手順を示す）
 期待:    （正しい値）
 実際:    （観測された値）
 補足:    （再現条件やパターンがあれば）
ポイント: 入力・期待・実際の3点セットを揃えると、GitHub Copilotが原因箇所をピンポイントで特定しやすくなります。
```

![](https://static.zenn.studio/user-upload/3dbfa77ecf65-20260404.png)

### コードを通して問題を追跡する

複数のファイルを参照すると、GitHub Copilot CLI にそれらの間の **データフロー** を追跡させて、問題の発生箇所を特定させることができます。

```
@src/app/api/sample/route.ts @src/lib/file1.ts @src/lib/file2.ts
 振替推薦のスコアで「同一科目マッチ +40点」が常に加算されている。
 APIルートから getRecommendations() → listSchedules()
 までのデータフローを追跡して、科目フィルタとスコアリングに矛盾がないか確認して
```

こんな感じで指示をだすことで、データフローの追跡と問題発生箇所を特定することができます。

#### データ問題を理解する

データファイルを読み込むコードと、実際のデータファイルを一緒に渡すことで、GitHub Copilot CLI はエラー処理の改善案をより適切に提案できます。

プロンプトの例としては以下のようになります。

```
@処理するコードのファイル
@型定義ファイル（あれば）
以下のデータを {関数名} に渡したときのエラーハンドリングを確認して改善案を提案して

 正常データ:
 {JSON}

 異常データ:
 {JSON — 欠損・不正値・型違いなど}

各ケースでクラッシュせず適切に処理できるか確認して
```

## ワークフロー4: テスト生成

### テストを一気に増やす

人が手動でテストを書くと、まずは 2〜3 個の基本的なテストだけで終わることがよくあります。(めんどくさいので...)

テストケースは観点網羅して作成するのが大事ですが、なかなか難しかったりします。

* 正常な入力をテストする
* 不正な入力をテストする
* 代表的なエッジケースをテストする  
  ...etc

しかし、GitHub Copilot CLI に **包括的なテスト** を作らせると、もっと広い観点で一気にテストを増やせます。

たとえば、対象のコードファイルを指定しながら、**どの観点をテストしたいか** を箇条書きで伝えると、抜け漏れの少ないテストを作りやすくなります。

例えば、以下のように記載すると非常に効果的です。

```
@対象ファイル @関連する型定義
 テストを以下の観点で生成して：
 - 正常系: {主要な機能ごとに1行}
 - 境界値: {しきい値・上限・下限}
 - フィルタ: {条件の組み合わせ}
 - ソート/順序: {並び順の検証}
 - エッジケース: {空データ、1件、大量データ、不正値}
```

### どんなテストが増えるのか

GitHub Copilot CLI は、単に数を増やすだけでなく、**異なる種類の観点** を含めたテストを提案できます。  
確認してみたところ、観点網羅も非常に優れている印象でした。

作ってもらったテストは以下のようになりました。  
いい感じでかけてそうですね。

```
// sample.ts の簡易テスト（Node.js 直接実行）
// 実行: npx tsx scripts/test-sample.ts

import { processStudentScores, makeReport } from '../src/lib/sample';
import type { StudentScoreInput } from '../src/lib/sample';

let passed = 0;
let failed = 0;

function assert(name: string, actual: unknown, expected: unknown) {
  if (actual === expected) {
    console.log(`  ✅ ${name}`);
    passed++;
  } else {
    console.log(`  ❌ ${name}`);
    console.log(`     期待: ${expected}`);
    console.log(`     実際: ${actual}`);
    failed++;
  }
}

function assertApprox(
  name: string,
  actual: number,
  expected: number,
  tolerance = 0.001,
) {
  if (Math.abs(actual - expected) < tolerance) {
    console.log(`  ✅ ${name}`);
    passed++;
  } else {
    console.log(`  ❌ ${name}`);
    console.log(`     期待: ${expected} (±${tolerance})`);
    console.log(`     実際: ${actual}`);
    failed++;
  }
}

// ============================================================
// 正常系: 主要な機能
// ============================================================

console.log('\n📊 正常系1: 平均点の計算');
{
  const data: StudentScoreInput[] = [
    { name: '田中', type: '期末', month: '04', scores: [80, 70, 90] },
  ];
  const results = processStudentScores(data, '期末', '04');
  assert('平均点が正しい (80+70+90)/3 = 80', results[0].average, 80);
  assert('合計点が正しい 80+70+90 = 240', results[0].total, 240);
  assert('科目数が正しい', results[0].count, 3);
}

console.log('\n📊 正常系2: グレード判定');
{
  const data: StudentScoreInput[] = [
    { name: 'S生徒', type: '期末', month: '04', scores: [95] },
    { name: 'A生徒', type: '期末', month: '04', scores: [85] },
    { name: 'B生徒', type: '期末', month: '04', scores: [75] },
    { name: 'C生徒', type: '期末', month: '04', scores: [65] },
    { name: 'D生徒', type: '期末', month: '04', scores: [40] },
  ];
  const results = processStudentScores(data, '期末', '04');
  const byName = Object.fromEntries(results.map((r) => [r.name, r]));
  assert('95点 → S', byName['S生徒'].grade, 'S');
  assert('85点 → A', byName['A生徒'].grade, 'A');
  assert('75点 → B', byName['B生徒'].grade, 'B');
  assert('65点 → C', byName['C生徒'].grade, 'C');
  assert('40点 → D', byName['D生徒'].grade, 'D');
}

console.log('\n📊 正常系3: 合否判定');
{
  const data: StudentScoreInput[] = [
    { name: '合格者', type: '期末', month: '04', scores: [80] },
    { name: '不合格者', type: '期末', month: '04', scores: [50] },
  ];
  const results = processStudentScores(data, '期末', '04');
  const byName = Object.fromEntries(results.map((r) => [r.name, r]));
  assert('80点 → 合格', byName['合格者'].passed, true);
  assert('50点 → 不合格', byName['不合格者'].passed, false);
}

console.log('\n📊 正常系4: ランキング付与');
{
  const data: StudentScoreInput[] = [
    { name: '佐藤', type: '期末', month: '04', scores: [95] },
    { name: '田中', type: '期末', month: '04', scores: [80] },
    { name: '鈴木', type: '期末', month: '04', scores: [50] },
  ];
  const results = processStudentScores(data, '期末', '04');
  assert('1位は佐藤（95点）', results[0].name, '佐藤');
  assert('2位は田中（80点）', results[1].name, '田中');
  assert('3位は鈴木（50点）', results[2].name, '鈴木');
  assert('1位のrankは1', results[0].rank, 1);
  assert('2位のrankは2', results[1].rank, 2);
  assert('3位のrankは3', results[2].rank, 3);
}

console.log('\n📊 正常系5: レポート生成');
{
  const data: StudentScoreInput[] = [
    { name: '田中', type: '期末', month: '04', scores: [80] },
  ];
  const report = makeReport(data, '期末', '04');
  assert('ヘッダーに種別あり', report.includes('種別: 期末'), true);
  assert('ヘッダーに月あり', report.includes('月: 04'), true);
  assert('受験者数あり', report.includes('受験者数: 1'), true);
  assert('合格率あり', report.includes('合格率:'), true);
}

// ============================================================
// 境界値: しきい値・上限・下限
// ============================================================

console.log('\n🔬 境界値1: グレードの閾値ちょうど');
{
  const data: StudentScoreInput[] = [
    { name: '90点', type: '期末', month: '04', scores: [90] },
    { name: '89点', type: '期末', month: '04', scores: [89] },
    { name: '80点', type: '期末', month: '04', scores: [80] },
    { name: '79点', type: '期末', month: '04', scores: [79] },
    { name: '70点', type: '期末', month: '04', scores: [70] },
    { name: '69点', type: '期末', month: '04', scores: [69] },
    { name: '60点', type: '期末', month: '04', scores: [60] },
    { name: '59点', type: '期末', month: '04', scores: [59] },
  ];
  const results = processStudentScores(data, '期末', '04');
  const byName = Object.fromEntries(results.map((r) => [r.name, r]));
  assert('90点 → S（境界）', byName['90点'].grade, 'S');
  assert('89点 → A（境界）', byName['89点'].grade, 'A');
  assert('80点 → A（境界）', byName['80点'].grade, 'A');
  assert('79点 → B（境界）', byName['79点'].grade, 'B');
  assert('70点 → B（境界）', byName['70点'].grade, 'B');
  assert('69点 → C（境界）', byName['69点'].grade, 'C');
  assert('60点 → C（境界）', byName['60点'].grade, 'C');
  assert('59点 → D（境界）', byName['59点'].grade, 'D');
}

console.log('\n🔬 境界値2: 合否の閾値ちょうど');
{
  const data: StudentScoreInput[] = [
    { name: '60点', type: '期末', month: '04', scores: [60] },
    { name: '59点', type: '期末', month: '04', scores: [59] },
  ];
  const results = processStudentScores(data, '期末', '04');
  const byName = Object.fromEntries(results.map((r) => [r.name, r]));
  assert('60点ちょうど → 合格', byName['60点'].passed, true);
  assert('59点 → 不合格', byName['59点'].passed, false);
}

console.log('\n🔬 境界値3: 極端なスコア');
{
  const data: StudentScoreInput[] = [
    { name: '満点', type: '期末', month: '04', scores: [100] },
    { name: '零点', type: '期末', month: '04', scores: [0] },
  ];
  const results = processStudentScores(data, '期末', '04');
  const byName = Object.fromEntries(results.map((r) => [r.name, r]));
  assert('100点 → S', byName['満点'].grade, 'S');
  assert('100点 → 合格', byName['満点'].passed, true);
  assert('100点の平均', byName['満点'].average, 100);
  assert('0点 → D', byName['零点'].grade, 'D');
  assert('0点 → 不合格', byName['零点'].passed, false);
  assert('0点の平均', byName['零点'].average, 0);
}

// ============================================================
// フィルタ: 条件の組み合わせ
// ============================================================

console.log('\n🔍 フィルタ1: type による絞り込み');
{
  const data: StudentScoreInput[] = [
    { name: '期末の人', type: '期末', month: '04', scores: [80] },
    { name: '中間の人', type: '中間', month: '04', scores: [70] },
    { name: '小テスト', type: '小テスト', month: '04', scores: [90] },
  ];
  const results = processStudentScores(data, '期末', '04');
  assert('期末のみ1件', results.length, 1);
  assert('期末の人が取れる', results[0].name, '期末の人');
}

console.log('\n🔍 フィルタ2: month による絞り込み');
{
  const data: StudentScoreInput[] = [
    { name: '4月', type: '期末', month: '04', scores: [80] },
    { name: '5月', type: '期末', month: '05', scores: [70] },
    { name: '6月', type: '期末', month: '06', scores: [90] },
  ];
  const results = processStudentScores(data, '期末', '05');
  assert('5月のみ1件', results.length, 1);
  assert('5月の人が取れる', results[0].name, '5月');
}

console.log('\n🔍 フィルタ3: type と month の組み合わせ');
{
  const data: StudentScoreInput[] = [
    { name: 'A', type: '期末', month: '04', scores: [80] },
    { name: 'B', type: '期末', month: '05', scores: [70] },
    { name: 'C', type: '中間', month: '04', scores: [90] },
    { name: 'D', type: '中間', month: '05', scores: [60] },
  ];
  assert('期末/04 → 1件', processStudentScores(data, '期末', '04').length, 1);
  assert('中間/05 → 1件', processStudentScores(data, '中間', '05').length, 1);
  assert('期末/06 → 0件', processStudentScores(data, '期末', '06').length, 0);
}

console.log('\n🔍 フィルタ4: 空スコアの除外');
{
  const data: StudentScoreInput[] = [
    { name: '空配列', type: '期末', month: '04', scores: [] },
    { name: '正常', type: '期末', month: '04', scores: [75] },
  ];
  const results = processStudentScores(data, '期末', '04');
  assert('空配列は除外され1件', results.length, 1);
  assert('正常のみ残る', results[0].name, '正常');
}

// ============================================================
// ソート/順序: 並び順の検証
// ============================================================

console.log('\n🏆 ソート1: 降順ソート（高得点が上位）');
{
  const data: StudentScoreInput[] = [
    { name: '低', type: '期末', month: '04', scores: [30] },
    { name: '高', type: '期末', month: '04', scores: [95] },
    { name: '中', type: '期末', month: '04', scores: [70] },
  ];
  const results = processStudentScores(data, '期末', '04');
  assert('1番目は高（95点）', results[0].name, '高');
  assert('2番目は中（70点）', results[1].name, '中');
  assert('3番目は低（30点）', results[2].name, '低');
}

console.log('\n🏆 ソート2: 同点の場合');
{
  const data: StudentScoreInput[] = [
    { name: '先', type: '期末', month: '04', scores: [80] },
    { name: '後', type: '期末', month: '04', scores: [80] },
  ];
  const results = processStudentScores(data, '期末', '04');
  assert('同点でも2件返る', results.length, 2);
  assert(
    'rank が 1 と 2',
    results[0].rank === 1 && results[1].rank === 2,
    true,
  );
}

console.log('\n🏆 ソート3: レポートのランキング表示順');
{
  const data: StudentScoreInput[] = [
    { name: '低い', type: '期末', month: '04', scores: [40] },
    { name: '高い', type: '期末', month: '04', scores: [90] },
  ];
  const report = makeReport(data, '期末', '04');
  const rankingLines = report.split('\n').filter((l) => l.includes('位:'));
  assert('1位の行が先に来る', rankingLines[0].startsWith('1位:'), true);
  assert('1位は高い', rankingLines[0].includes('高い'), true);
}

// ============================================================
// エッジケース: 空データ、1件、大量データ
// ============================================================

console.log('\n⚠️ エッジ1: データ0件');
{
  const results = processStudentScores([], '期末', '04');
  assert('空配列を渡すと0件', results.length, 0);
}

console.log('\n⚠️ エッジ2: 該当なし（フィルタで全除外）');
{
  const data: StudentScoreInput[] = [
    { name: '別type', type: '中間', month: '04', scores: [80] },
  ];
  const results = processStudentScores(data, '期末', '04');
  assert('該当なしで0件', results.length, 0);
}

console.log('\n⚠️ エッジ3: 1件のみ');
{
  const data: StudentScoreInput[] = [
    { name: '唯一', type: '期末', month: '04', scores: [75] },
  ];
  const results = processStudentScores(data, '期末', '04');
  assert('1件だけでも動作する', results.length, 1);
  assert('rank は 1', results[0].rank, 1);
}

console.log('\n⚠️ エッジ4: レポート0件のとき');
{
  const report = makeReport([], '期末', '04');
  assert('0件でもクラッシュしない', typeof report, 'string');
  assert('受験者数0', report.includes('受験者数: 0'), true);
  assert('合格率0%', report.includes('合格率: 0'), true);
}

console.log('\n⚠️ エッジ5: スコアが1科目のみ');
{
  const data: StudentScoreInput[] = [
    { name: '一科目', type: '期末', month: '04', scores: [73] },
  ];
  const results = processStudentScores(data, '期末', '04');
  assert('1科目の平均 = そのスコア', results[0].average, 73);
  assert('1科目の合計 = そのスコア', results[0].total, 73);
}

console.log('\n⚠️ エッジ6: グレード分布の合計が受験者数と一致');
{
  const data: StudentScoreInput[] = [
    { name: 'S', type: '期末', month: '04', scores: [95] },
    { name: 'A', type: '期末', month: '04', scores: [85] },
    { name: 'B', type: '期末', month: '04', scores: [75] },
    { name: 'C', type: '期末', month: '04', scores: [65] },
    { name: 'D', type: '期末', month: '04', scores: [40] },
  ];
  const report = makeReport(data, '期末', '04');
  assert('S: 1人', report.includes('S: 1人'), true);
  assert('A: 1人', report.includes('A: 1人'), true);
  assert('B: 1人', report.includes('B: 1人'), true);
  assert('C: 1人', report.includes('C: 1人'), true);
  assert('D: 1人', report.includes('D: 1人'), true);
  assert('受験者数: 5', report.includes('受験者数: 5'), true);
}

// ============================================================
// 結果サマリー
// ============================================================
console.log('\n' + '='.repeat(40));
console.log(
  `結果: ${passed} passed / ${failed} failed / ${passed + failed} total`,
);
if (failed > 0) {
  console.log('⚠️  失敗したテストがあります！');
  process.exit(1);
} else {
  console.log('🎉 全テスト通過！');
}
```

このように、**正常系・異常系・境界値・保存処理・文字種** まで含めて、広くテストを作れるのが強みです。

また、以下のコマンドも準備してくれて、簡単にテストが実行できるようにしてくれています。

```
npx tsx scripts/test-sample.ts
```

これを作ってくれといってすぐ出してくる同僚はなかなか出来る同僚ですね。

### 単体テストを作る

1つの関数だけを集中的にテストしたい場合は、**対象の関数名** と **確認したい入力パターン** を具体的に伝えると効果的です。

```
@ファイル名 テストを生成してください。そして以下の観点をカバーしてください。:
- Valid input
- Empty strings
- Invalid number formats
- Very long text
- Special characters
```

このように書くと、GitHub Copilot CLI はその関数に絞って、入力パターンごとのテストを作りやすくなります。

### テストの実行方法を聞く

テストの書き方だけでなく、**どう実行すればいいか** をそのまま質問することもできます。  
個人的にはこれが非常に便利だと思ってます。

こんな感じでVitestやJestなどテストフレームワークを検討してくれた結果を教えてくれます。

![](https://static.zenn.studio/user-upload/061cc6041a25-20260404.png)

Vitestが一番良いみたいですね。

#### 特定シナリオだけをテストする

想定している特定のケースがあるなら、それをそのまま列挙すると、GitHub Copilot CLI がその観点に沿ったテストを作ってくれます。

```
@ファイル名
 {関数名} のテストを作成して。{観点}を検証したい：
 - {具体的な入力} → {期待する出力}
 - {具体的な入力} → {期待する出力}
 - ...
```

ここで大事なのは、**「何が心配か」を具体的に書くこと** です。  
そうすると、GitHub Copilot CLI はその不安ポイントに沿ったテストを考えやすくなります。

### 既存テストに追加する

すでにテストファイルがある場合でも、**足りない観点だけ追加** させることができます。  
また、GitHub Copilotに記載してもらったテストから更に新たな機能を実装した時にテストケースを追加することもできます。(便利ですよね。)

```
@ファイル名 sample_func 関数に対して、以下のエッジケースを含む追加テストを生成してください。
ハイフンを含む名前
複数のファーストネーム
空文字列を入力した場合
アクセント付き文字を含む名前
```

このようにすると、既存テストを丸ごと作り直すのではなく、**不足しているケースだけ補強** しやすくなります。

### Git と組み合わせる流れ

テスト作成の次には、Git と組み合わせた流れも便利です。  
たとえば、変更内容を確認しながら次のような作業につなげられます。

* コミットメッセージを考える
* プルリクエストの説明を書く
* 差分を確認する
* レビュー用の文章を作る

テストを作る → 修正する → 差分を確認する → PRを作る、という流れで使うと実用的です。

### 実装前に調査する

いきなりコードを書くのではなく、先に **ライブラリやベストプラクティスを調べる** 使い方も有効です。

```
Researching: What are the best TypeScript libraries for validating user input in CLI apps?
```

いい感じのOutputが出てきました。  
![](https://static.zenn.studio/user-upload/471233bbc436-20260404.png)

Zodが推奨みたいですね。  
このように聞くと、GitHub Copilot は関連情報を調べて、比較しやすい形でまとめてくれます。

### おすすめの使い方

新しい機能や改善を進めるときは、次の順番が分かりやすいです。

1. **/research 調査する**
2. **/plan 実装方針を考える**
3. **コードを書く**
4. **テストを増やす**
5. **差分を確認する**
6. **コミットやPRを整える**

#### /research — 調査する

```
/research Next.js 16 の App Router API Routes で Zod
バリデーションを導入するベストプラクティスを調査して。safeParse のエラーレスポンス形式、Standard
Schema との互換性、パフォーマンスへの影響も含めて
```

#### /plan — 実装方針を考える

```
 /plan 全 API ルート（12ファイル）に Zod でリクエストバリデーションを追加したい：
 - src/lib/schemas/ にドメインごとのスキーマを定義
 - 既存の型定義（src/lib/types/）からスキーマを生成
 - POST は全フィールド必須、PATCH は全フィールド optional
 - 不正リクエストは 400 + 日本語メッセージ
 - request.json() の try-catch も統一
```

#### コードを書く

```
 @src/lib/types/test.ts
 Test 型に基づいた Zod スキーマを src/lib/schemas/test.ts に作成して。TestCreateInput 用と TestUpdateInput 用の2つ。gradeLevel は GradeLevel のユニオン型で制約して

 @src/app/api/tests/route.ts @src/lib/schemas/test.ts
 POST ルートに作成したスキーマでバリデーションを追加して。request.json() の try-catch、safeParseのエラー時は 400 + フィールドごとのエラーメッセージを返すようにして
```

#### テストを増やす

```
 @src/app/api/tests/route.ts @src/lib/schemas/test.ts
 バリデーション追加後のテストを生成して：
 - 正常データで 201 が返る
 - name が空文字 → 400 + "名前は必須です"
 - gradeLevel が不正値 → 400
 - request body が JSON でない → 400
 - 必須フィールド欠損 → 400 + 欠損フィールド名
 - 境界値（maxStudents が 0 や負数）
```

#### /diff — 差分を確認する

```
 /diff
追加の指示を付けることも可能：
 /diff バリデーションの追加漏れがないか確認して。全ての POST/PATCH ルートに safeParse
が入っているかチェックして
```

#### コミットや PR を整える

```
コミット：
 今回の変更をコミットして。コミットメッセージは日本語で、変更内容を簡潔にまとめて

PR 作成：
 /pr create として、今回のバリデーション追加の PR
を作成して。タイトルと本文は日本語で、以下を含めて：
 - 変更の概要（何を、なぜ）
 - 変更ファイル一覧
 - テスト方法
 - 影響範囲

既存 PR の操作：
 /pr              ← 現在のブランチの PR を表示
 /pr status       ← PR のステータス確認
 /pr checks       ← CI の状態確認
```

この流れにすると、**調べてから作る**、**作ったあとにテストする**、**最後にレビューする** という自然な開発手順になります。  
まとめると、以下のようになります。

1. /research → 技術調査（Zod + Next.js 16）
2. /plan → TODO・実装計画を plan.md に整理
3. 自然言語 → スキーマ定義 → API ルート修正
4. 自然言語 → テスト生成・実行
5. /diff → 変更差分の確認・レビュー
6. 自然言語 → コミット → /pr で PR 作成

### 要点

* ファイル名は `@your_file.ts` のように、自分のファイル名に置き換えて使う
* 「何をテストしたいか」を箇条書きで具体的に書く
* 正常系だけでなく、異常系・空データ・特殊文字・保存失敗も含める
* まず調査してから実装すると、やり直しが減る
* テスト生成は、たたき台作成に特に強い

GitHub Copilot CLI は、**テストを0から全部任せる** というより、  
**広い観点を一気に洗い出す相棒** として使うと非常に強力です。

## ワークフロー5: Git統合

GitHub Copilot CLI は、コードを書くときだけでなく、**コミットメッセージ作成・変更説明・PR作成・最終チェック** にも使えます。  
ここでは、日々の Git ワークフローで役立つ使い方を、前提知識がなくても分かる形で整理します。

#### コミットメッセージを生成する

まずは、いくつかの変更を **ステージング** してください。  
そのうえで、ステージ済みの差分をもとに Copilot CLI にコミットメッセージを作らせます。

```
# まず現在のステージ済み変更を確認
git diff --staged
```

```
# Conventional Commit 形式でコミットメッセージを生成
Generate a conventional commit message for: $(git diff --staged)
```

**Conventional Commit** は、次のような形式で書くルールです。

* `feat:` 新機能
* `fix:` バグ修正
* `docs:` ドキュメント修正
* `refactor:` リファクタリング
* `test:` テスト追加・修正

たとえば、次のような形です。

```
feat(search): add partial keyword matching
fix(auth): handle empty token input
docs(readme): update setup instructions
```

#### 変更内容を平易な言葉で説明してもらう

「このコミットって結局何をしたのか？」を自然な言葉でまとめたい場合もあります。  
そのときは、直近のコミット情報を Copilot CLI に渡します。

```
Explain what this commit does: $(git show HEAD --stat)
```

いい感じで以下がわかりやすくなります。

* 最後のコミットの要約を作る
* レビュー相手向けに変更内容を説明する
* 後から自分で見返しやすくする

#### PR の説明を生成する

プルリクエストの説明文も、変更履歴から自動で作れます。

```
copilot -p "Generate a pull request description for these changes:
$(git log main..HEAD --oneline)

Include:
- Summary of changes
- Why these changes were made
- Testing done
- Breaking changes? (yes/no)"
```

#### このコマンドの意味

* `git log main..HEAD --oneline`  
  → 現在のブランチで、`main` から増えたコミット一覧を短く表示
* その内容を Copilot CLI に渡して、PR説明文を作らせる

#### 含めてもらう項目

* 変更内容の要約
* なぜ変更したのか
* どんなテストをしたか
* 破壊的変更があるかどうか

これにより、**PR本文を書く手間** をかなり減らせます。

#### 対話モードで `/pr` を使う

Copilot CLI の対話モードでは、`/pr` コマンドで PR 操作ができます。

```
/pr [view|create|fix|auto]
```

### できること

* `view` : PR を確認する
* `create` : 新しい PR を作る
* `fix` : 既存PRの内容を修正する
* `auto` : 状況に応じて Copilot CLI に判断させる

普段から対話モードを使っているなら、こちらの方が自然に扱えます。

#### プッシュ前に最終レビューする

ブランチ全体の差分を見て、「このまま push して大丈夫か」をチェックする使い方も便利です。

```
copilot -p "Review these changes for issues before I push:
$(git diff main..HEAD)"
```

この使いどころは以下になります。

* push 前の最終確認
* 自分で見落としている問題の洗い出し
* 小さな不整合や危険な変更の発見

これは **最終健全性チェック** としてかなり実用的です。

#### `/delegate` で作業を委譲する

明確に切り出せる作業であれば、GitHub Copilot CLI にバックグラウンドで任せることもできます。

```
/delegate Add input validation to the login form
```

```
& Fix the typo in the README header
```

### 何が起こるのか

Copilot CLI は状況に応じて、次のような流れで作業を進めます。

1. 変更を新しいブランチにまとめる
2. Draft PR を作成する
3. GitHub 上でバックグラウンド作業を進める
4. 完了後にレビューを求める

#### 向いているタスク

* 入力チェックの追加
* README の軽微な修正
* 明確なバグ修正
* 小さめの独立した作業

つまり、**細かく定義できる仕事を別レーンで進めたいとき** に向いています。

#### `/diff` でセッション中の変更を見る

Copilot CLI とのやり取りで加えた変更を、まとめて確認したいときは `/diff` が便利です。

#### できること

* このセッション中に変更された内容を一覧表示
* コミット前の確認
* 「どこまで変わったか」を視覚的に把握

**コミットする前の見直し** にかなり役立ちます。

#### 実装前に `/research` する

いきなりコードを書くのではなく、まずライブラリやベストプラクティスを調べる使い方も有効です。

```
/research What are the best Python libraries for validating user input in CLI apps?
```

#### できること

* 関連ライブラリを比較する
* ベストプラクティスを調べる
* 初めて触る分野をざっくり理解する
* 実装前に方針を固める

調査してから作ることで、**手戻りを減らしやすくなります**。

### ポイント

* コミットメッセージは、差分を渡せばかなり自然に作れる
* PR説明は、コミット履歴から自動生成できる
* push前レビューで見落としを減らせる
* `/delegate` は、切り出しやすい小タスクに向いている
* `/diff` は、コミット前の見直しに便利
* `/research` を先に使うと、実装の質が上がりやすい

GitHub Copilot CLI は、**コードを書く支援** だけでなく、  
**Git を含めた開発全体の流れをスムーズにする相棒** として使うと真価を発揮されますね。

振り返ると、具体的な指示により、コードレビューはより包括的なものとなり、リファクタリングは、先にテストを生成しておけばより安全になると感じました。  
また、デバッグには、Copilot CLI にエラーとコードの両方を表示することが有効で、テスト生成には、エッジケースとエラーシナリオを含めるべきと考えています。  
最後にGit統合により、コミットメッセージとプルリクエストの説明が自動化されます。これは非常に良いですよね。

# 組み込みエージェントとカスタムエージェント

![](https://static.zenn.studio/user-upload/6113eaa864e3-20260404.png)

GitHub Copilot CLI には、**組み込みエージェント** と **カスタムエージェント** の2種類のエージェントが存在します。

組み込みエージェントは、GitHub Copilot CLI に最初から用意されているエージェントで、特定のタスクに特化したものです。

一方、カスタムエージェントは、ユーザーが自分で定義して作成するエージェントで、より柔軟にタスクをこなすことができます。

## 組み込みエージェント

組み込みエージェントはこれまで使ってきた\*\*/plan\*\* や **/research** などのエージェントのことを指します。

これらは、特定のタスクに対して最適化されており、ユーザーが簡単に利用できるようになっています。  
たとえば、**/plan** エージェントは、実装の計画を立てるためのエージェントで、**/research** エージェントは、特定のトピックに関する情報を調査するためのエージェントです。**/review** エージェントは、コードのレビューを行うためのエージェントなんてものもありましたね。

これらのエージェントは、GitHub Copilot CLI に組み込まれているため、ユーザーはすぐに利用することができます。

## カスタムエージェント

ここからが本章の本題です。  
カスタムエージェントは、ユーザーが自分で定義して作成するエージェントのことを指します。  
これにより、ユーザーは自分のニーズに合わせたエージェントを作成することができます。

難しく説明していますが、本体は非常にシンプルなマークダウンのファイルになります。  
一例を見てみましょう。

code-review.agent.md

```
---
name: code-reviewer
description: バグやセキュリティ上の問題を重点的に確認するコードレビュアー
---

# コードレビュアー
あなたは、バグやセキュリティ上の問題を見つけることに重点を置いたコードレビュアーです。

コードをレビューする際は、必ず以下を確認してください。
- SQLインジェクションの脆弱性
- エラーハンドリングの不足
- ハードコードされたシークレット情報
```

## カスタムエージェントの作り方

カスタムエージェントは以下のように記載していくのがGoodです。

xxx.agent.md

```
---
name: 役割がひと目で分かる名前を記載します
description: このエージェントが何をするのかを1文で明確に記載します（必須）
tools: ["read", "search", "edit"]
# このエージェントに許可するツールを配列で記載します
# 例:
# - "read"   : ファイルを読む
# - "search" : コードやファイルを検索する
# - "edit"   : ファイルを編集する
# 必要最小限に絞るのが一般的です

model: 使用したいモデル名を記載します
# 任意項目です
# 特定のモデルを使いたい場合のみ記載します
# 不要であれば省略して構いません

target: vscode
# 任意項目です
# このエージェントを利用する対象環境を記載します
# 例:
# - vscode
# - github-copilot
# 省略時はデフォルト設定が適用されます
---

# Role
このエージェントの役割を記載します。

ex)
あなたは、バグやセキュリティリスクを重点的に確認するコードレビュアーです。

# Scope
このエージェントが何を対象にするか、何をしないかを記載します。

ex)
- コードの正確性、セキュリティ、信頼性を優先して確認する
- 必要がない限り大規模なリファクタ提案はしない

# What to always check
必ず確認してほしい観点を箇条書きで記載します。

ex)
- SQLインジェクションの脆弱性
- エラーハンドリングの不足
- ハードコードされたシークレット情報
- 入力値検証の不足
- 重要な分岐に対するテスト不足

# Rules
レビューや作業時のルールを記載します。

ex)
- 根拠のある指摘を優先する
- 推測だけで断定しない
- 問題点だけでなく修正案も可能な限り提示する
- 重大度を分けて出力する

# Output format
出力形式を明確に記載します。

ex)
各指摘について、以下の形式で出力してください。
1. 重大度
2. 対象ファイル名 / 関数名
3. 問題点
4. なぜ重要か
5. 修正案

最後に、全体の要約を簡潔に記載してください。
```

## エージェントファイルの保存場所

xxx.agent.md のようなマークダウンファイルを作成したら、以下のどちらかの場所に保存してください。

| 位置 | 範囲 | 最適な用途 |
| --- | --- | --- |
| `.github/agents/` | プロジェクト固有 | プロジェクト規約に準拠したチーム共有エージェント |
| `~/.copilot/agents/` | グローバル（全プロジェクト） | 個人で横断的に使うパーソナルエージェント |

GitHub 公式では、カスタムエージェントは プロジェクト用なら .github/agents/、個人用なら ~/.copilot/agents/ に置く形を推奨しています。

VS Code でも「Workspace は .github/agents」「User profile はユーザープロファイル配下」と案内されています。GitHub Copilot CLI でも Project = .github/agents/、User = ~/.copilot/agents/ です。

## .github/ 配下でのおすすめ配置

GitHub Copilot CLI を リポジトリ単位で最適化 するなら、まずはこの形が一番わかりやすいです。

```
.github/
├── agents/
│   ├── code-reviewer.agent.md
│   ├── test-writer.agent.md
│   ├── planner.agent.md
│   └── security-reviewer.agent.md
├── skills/
│   ├── create-tests/
│   │   └── SKILL.md
│   ├── review-pr/
│   │   └── SKILL.md
│   └── release-check/
│       └── SKILL.md
├── instructions/
│   ├── frontend.instructions.md
│   ├── api.instructions.md
│   └── testing.instructions.md
├── workflows/
│   └── copilot-setup-steps.yml
└── copilot-instructions.md
AGENTS.md
frontend/
├── app/
│   └── AGENTS.md
└── api/
    └── AGENTS.md
```

各ディレクトリの役割を以下にまとめました。

| ファイル / ディレクトリ | 配置場所 | 役割 | 記載する内容 |
| --- | --- | --- | --- |
| カスタムエージェント | `.github/agents/*.agent.md` | 役割別の専門エージェントを定義する | reviewer / planner / test-writer などの役割、振る舞い、出力形式、利用ツール |
| Skills | `.github/skills/<skill-name>/SKILL.md` | 定型作業・再利用手順を定義する | テスト追加手順、PRレビュー手順、リリース確認手順など |
| Copilot 共通指示 | `.github/copilot-instructions.md` | リポジトリ全体に適用する共通ルールを書く | 命名規則、テスト方針、設計原則、禁止事項、開発ルール |
| パス別 instructions | `.github/instructions/*.instructions.md` | 特定の領域・ファイル群に適用する詳細ルールを書く | frontend 向け実装方針、api 向け認証・バリデーション方針、testing 向けテストルールなど |
| AGENTS 共通指示 | `AGENTS.md` | エージェント向けの共通作業ルールを定義する | リポジトリ全体の実装方針、レビュー観点、作業時の注意事項 |
| ディレクトリ別 AGENTS | `frontend/app/AGENTS.md` など | 特定ディレクトリ配下にだけ適用する追加ルールを書く | Next.js 固有ルール、API 実装ルール、認証方針、ログ方針など |
| Copilot セットアップ | `.github/workflows/copilot-setup-steps.yml` | Copilot 実行時の環境準備を行う | 依存関係インストール、追加ツール導入、初期化処理 |
| 個人用エージェント | `~/.copilot/agents/*.agent.md` | 全プロジェクトで使う個人専用エージェント | 自分専用の reviewer / planner / writer など |

agents/やskills/, workflows/はGitHub Copilot CLI の公式ドキュメントでも紹介されている構成で、AGENTS.md や copilot-instructions.md は、Agentの動き方、プロジェクト独自のルールや方針をまとめるためのファイルになります。

ここを丁寧に構築するとその後のプロジェクトでの開発が爆速で進めることが出来るので、この構成は各プロジェクトで用意しておくのがおすすめです。

では、どんな動きになる見ていきましょう。

## カスタムエージェントを使用する2つの方法

### 対話モード

対話モードでは、エージェントの一覧が表示され、`/agent` を使って操作を開始するエージェントを選択できます。  
会話を続けたいエージェントを選択してください。

以下のように表示されます。  
![](https://static.zenn.studio/user-upload/976d2f21326c-20260404.png)

エージェントを選択することも、新たに作成することも可能です。  
別のエージェントに変更する場合、またはデフォルトモードに戻す場合は、/agent コマンドを再度使用してください。

learn more の箇所を選択すると、以下のMicrosoft Learnのドキュメントに飛びます。

<https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli-agents/overview#use-custom-agents>

### プログラムモード

次はプログラムモードでの使い方です。エージェントとの新しいセッションをすぐに開始します。

```
copilot --agent エージェント名
Review @samples/ファイル名
```

サンプルでは、hello-world.agent.mdというエージェントを選択してみました。

.github/agents/hello-world.agent.md

```
---
name: hello-world
description: A minimal agent example - responds with friendly, encouraging messages
---

# Hello World Agent

You are a friendly assistant who responds with encouraging messages.

When the user asks for help, always:

- Start with a positive greeting
- Keep responses brief and helpful
- End with an encouraging note
```

hello-world エージェントからしっかりと挨拶されていますね。  
![](https://static.zenn.studio/user-upload/28c0590251fb-20260404.png)

エージェントの切り替えは **/agent** または **--agent** を使用して、いつでも別のエージェントに切り替えることができます。  
標準の Copilot CLI エクスペリエンスに戻るには、エージェントなしを選択すればOKです。

用途に合わせて、**対話モード** と **プログラムモード** を使い分けると便利ですね。  
筆者は基本対話モードでゴリゴリ開発しています。

# エージェントスキル

![](https://static.zenn.studio/user-upload/1763db13e3cd-20260404.png)

エージェントスキルとは、タスクに関連する場合にCopilotが自動的に読み込む手順のフォルダーです。

エージェントはCopilotの思考方法を変える一方、スキルはCopilotにタスクを完了するための具体的な方法を学習させます。

セキュリティに関する質問があった際にCopilotが適用するセキュリティ監査スキルを作成し、一貫したコード品質を保証するチーム標準のレビュー基準を構築し、Copilot CLI、VS Code、GitHub Copilotクラウドエージェント全体でスキルがどのように機能するか見ていきましょう。

まずは以下のコマンドでSkillの一覧を表示することができます。

### Available Skills

| Skill 名 | 概要 | 主な用途 / キーワード |
| --- | --- | --- |
| `appinsights-instrumentation` | Azure Application Insights で Web アプリを計測するためのガイダンス | App Insights SDK、telemetry、instrumentation、APM |
| `azure-ai` | Azure AI 系の機能を扱うスキル | AI Search、vector search、hybrid search、Speech、OCR、OpenAI |
| `azure-aigateway` | Azure API Management を AI Gateway として構成する | semantic caching、token limit、content safety、MCP、AI backend |
| `azure-cloud-migrate` | AWS / GCP などから Azure への移行支援 | Lambda to Azure Functions、migration assessment、cross-cloud migration |
| `azure-compliance` | Azure のセキュリティ・コンプライアンス監査 | compliance scan、Key Vault expiration、security audit |
| `azure-compute` | Azure VM / VMSS のサイズや構成を提案する | VM sizing、GPU VM、cost estimate、autoscale、VMSS |
| `azure-cost-optimization` | Azure コスト削減の分析と最適化提案 | reduce Azure spending、rightsize、unused resources |
| `azure-deploy` | 事前準備済みアプリを Azure にデプロイする | `azd up`、`azd deploy`、terraform apply、publish to Azure |
| `azure-diagnostics` | Azure Container Apps / Function Apps の障害解析 | logs、KQL、health probe、cold start、root cause analysis |
| `azure-hosted-copilot-sdk` | GitHub Copilot SDK アプリを Azure 上に構築・デプロイする | copilot SDK、host on Azure、BYOM、CopilotClient |
| `azure-kusto` | Azure Data Explorer / Kusto を KQL で分析する | KQL、ADX、telemetry、time series、anomaly detection |
| `azure-messaging` | Event Hubs / Service Bus の SDK トラブルシュート | AMQP、message lock lost、dead letter、consumer issue |
| `azure-observability` | Azure Monitor / App Insights / Log Analytics の可観測性支援 | metrics、APM、distributed tracing、alerts、workbooks |
| `azure-postgres` | Azure Database for PostgreSQL Flexible Server と Entra ID 認証設定 | passwordless、managed identity、Entra ID authentication |
| `azure-prepare` | Azure デプロイ前のアプリ準備 | infra、Bicep、Terraform、azure.yaml、Dockerfiles |
| `azure-quotas` | Azure クォータや利用量の確認・管理 | quota exceeded、regional availability、vCPU limit |
| `azure-rbac` | Azure RBAC の最小権限ロールを提案する | least privilege、assign role、custom role definition |
| `azure-resource-lookup` | Azure リソースの一覧取得・検索 | list VMs、list storage accounts、resource inventory |
| `azure-resource-visualizer` | Azure リソース構成を Mermaid 図に可視化する | architecture diagram、resource topology、map infrastructure |
| `azure-storage` | Azure Storage 系サービスの利用支援 | Blob、File Shares、Queue、Table、Data Lake |
| `azure-upgrade` | Azure ワークロードのプラン / SKU アップグレード支援 | upgrade Functions plan、migrate App Service to Container Apps |
| `azure-validate` | Azure へのデプロイ前検証を行う | validate azure.yaml、preflight checks、deployment readiness |
| `entra-app-registration` | Microsoft Entra ID のアプリ登録・OAuth・MSAL 設定 | app registration、OAuth、MSAL、API permissions |
| `microsoft-foundry` | Foundry エージェントのデプロイ・評価・最適化 | deploy agent、batch eval、prompt optimization、Foundry project |

エージェントスキルとは、タスクに関連する場合にCopilotが自動的に読み込む指示、スクリプト、リソースなどを含むフォルダです。Copilotはプロンプトを読み取り、該当するスキルがあるかどうかを確認し、関連する指示を自動的に適用します。  
スキルファイルは以下のように定義されています。

skills/code-checklist/SKILL.md

```
---
name: code-checklist
description: Team code quality checklist - use for checking TypeScript code quality, bugs, security issues, and best practices
---

# Code Checklist Skill

Apply this checklist when checking TypeScript code.

## Code Quality Checklist

- [ ] Public functions and exported APIs have explicit types
- [ ] `any` is avoided unless clearly justified
- [ ] No empty `catch` blocks
- [ ] No unused variables, imports, or dead code
- [ ] Async code uses `await` / `Promise` correctly
- [ ] Functions are reasonably small and focused
- [ ] Variable and function names follow project conventions
- [ ] Null / undefined cases are handled safely
- [ ] Business logic is not duplicated unnecessarily

## Input Validation Checklist

- [ ] User input is validated before processing
- [ ] Edge cases are handled (empty strings, null, undefined, out-of-range values)
- [ ] External API input / request body / query params are validated
- [ ] Error messages are clear and helpful
- [ ] Unsafe type assertions are avoided where possible

## Security Checklist

- [ ] No hardcoded secrets or tokens
- [ ] No unsafe use of `eval` or dynamic code execution
- [ ] Authentication / authorization checks are present where needed
- [ ] Untrusted input is sanitized before rendering or execution
- [ ] Sensitive data is not exposed in logs or error responses

## Testing Checklist

- [ ] New code has corresponding tests
- [ ] Edge cases are covered
- [ ] Tests use descriptive names
- [ ] Happy path and failure path are both tested
- [ ] Mocks / stubs are used only where appropriate

## Output Format

Present findings as:

```text
## Code Checklist: [filename]

### Code Quality
- [PASS/FAIL] Description of finding

### Input Validation
- [PASS/FAIL] Description of finding

### Security
- [PASS/FAIL] Description of finding

### Testing
- [PASS/FAIL] Description of finding

### Summary
[X] items need attention before merge
```

この例では、`code-checklist` というスキルを定義しています。  
このスキルは、TypeScript コードの品質、バグ、セキュリティ問題、ベストプラクティスをチェックするためのチェックリストを提供しています。

早速使ってみましょう。  
以下のコマンドを実行してみます。

```
check @src/lib/sample.ts against our quality checklist
```

skillを使ってコードチェックしてくれていますね。いい感じです。  
![](https://static.zenn.studio/user-upload/3f17cfb7c390-20260404.png)

プロジェクトの要件に合わせたスキルを準備してコードを確認してもらうのがBestの使い方ですね。

スキルが使用されたか確認したい場合は直接聞くことも可能です。

```
What skills did you use for that response?
```

ちゃんと使ってくれてますね！  
![](https://static.zenn.studio/user-upload/cdfbb6dd1797-20260404.png)

## Skill vs Agent vs MCP

スキルは、GitHub Copilotの拡張性モデルを構成する要素の一つにすぎません。ここでは、スキルとエージェントおよびMCPサーバーとの比較について説明します。

使い分けとしては以下のようになります。

| 特徴 | その機能 | 使用時期 |
| --- | --- | --- |
| エージェント | AIの思考方法を変える | 多くの業務において専門的な知識が必要なとき |
| スキル | タスク固有の手順を提供する | 具体的な手順を伴う、繰り返し可能な作業のとき |
| MCP | 外部サービスと接続する | APIからのリアルタイムデータが必要なとき |

幅広い専門知識にはエージェントを、特定のタスク指示にはスキルを、外部データにはMCPを使用します。  
エージェントは会話中に1つまたは複数のスキルを使用できます。

Best Practiceについては以下に記載がありますので、是非参考にしてみてください。  
<https://docs.github.com/ja/copilot/concepts/agents/about-agent-skills>

## Skillがある時・ない時

スキルを身につける方法を詳しく説明する前に、なぜスキルを学ぶ価値があるのか​​を見ていきましょう。  
継続的な成果を実感すれば、「どのように」学ぶべきかがより明確になるでしょう。

* コードレビューを行う度に、確認事項に漏れが出てしまう可能性がある  
  生成AIもちゃんと毎回確認項目を指定してくれないと、コードのどこを見ればいいのか分からず、重要なポイントを見落としてしまう可能性があります。  
  そんな時に、スキルを用意しておけば、毎回同じ確認項目でコードレビューを行うことができるようになります。

コードレビューももちろんですが、PullRequestの時の事前チェックでも活躍してくれます。

あなたのチームに10項目のPRチェックリストがあると過程しましょう。  
スキルがなければ、すべての開発者が10項目すべてを覚えていなければならず、必ず誰かが1つ忘れてしまいます。  
`pr-review` スキルがあれば、チーム全体が一貫したレビューを受けることができます。

```
copilot
Can you review this PR?
```

```
PR Review: feature/user-auth

## Security ✅
- No hardcoded secrets
- Input validation present
- No bare except clauses

## Code Quality ⚠️
- [WARN] print statement on line 45 — remove before merge
- [WARN] TODO on line 78 missing issue reference
- [WARN] Missing type hints on public functions

## Testing ✅
- New tests added
- Edge cases covered

## Documentation ❌
- [FAIL] Breaking change not documented in CHANGELOG
- [FAIL] API changes need OpenAPI spec update
```

その利点は、チームメンバー全員が同じ基準を自動的に適用できることです。  
スキルが自動的に処理してくれるので、新入社員はチェックリストを暗記する必要がありません。  
(私が新卒の時は、チェックリストをExcelで管理して指差し確認していたような...)

## スキルの配置場所

`.github/skills/` スキルは、プロジェクト固有、またはユーザーレベルでは `~/.copilot/skills/` に保存されます。

## Copilot がスキルを見つける方法

GitHub Copilot は、スキルを検出するために以下の場所を自動的にスキャンします。

| 位置 | 範囲 |
| --- | --- |
| `.github/skills/` | プロジェクト固有の情報（Git 経由でチームと共有） |
| `~/.copilot/skills/` | ユーザー固有のスキル（あなたの個人的なスキル） |

### スキル構造

各スキルはそれぞれ専用のフォルダに格納され、`SKILL.md` ファイルも含まれています。  
必要に応じて、スクリプト、サンプル、その他のリソースを追加することもできます。

```
.github/skills/
└── my-skill/
    ├── SKILL.md          # 必須: スキル定義と手順
    ├── examples/         # 任意: Copilot が参照できるサンプルファイル
    │   └── sample.py
    └── scripts/          # 任意: スキルが利用できるスクリプト
        └── validate.sh
```

ディレクトリ名は、SKILL.md のフロントマターにある name と一致している必要があるので、そこだけ注意が必要です。

### スキルの形式

スキルの形式は以下のようになります。  
以下のサンプルはOWASP Top 10の脆弱性をチェックするセキュリティ監査スキルとなります。

SKILL.md

```
---
name: security-audit
description: Security-focused code review checking OWASP (Open Web Application Security Project) Top 10 vulnerabilities
---

# Security Audit

Perform a security audit checking for:

## Injection Vulnerabilities
- SQL injection (string concatenation in queries)
- Command injection (unsanitized shell commands)
- LDAP injection
- XPath injection

## Authentication Issues
- Hardcoded credentials
- Weak password requirements
- Missing rate limiting
- Session management flaws

## Sensitive Data
- Plaintext passwords
- API keys in code
- Logging sensitive information
- Missing encryption

## Access Control
- Missing authorization checks
- Insecure direct object references
- Path traversal vulnerabilities

## Output
For each issue found, provide:
1. File and line number
2. Vulnerability type
3. Severity (CRITICAL/HIGH/MEDIUM/LOW)
4. Recommended fix
```

必要なYAMLプロパティは以下となります。

| 区分 | 要素 | 説明 |
| --- | --- | --- |
| 必須に近い | `name` | スキル名。Copilot が識別するために重要 |
| 必須に近い | `description` | 何をするスキルか、いつ使うべきかを説明 |
| 実質必須 | 本文の instructions | 実際の手順・チェック項目・判断基準 |
| 強く推奨 | Output Format | 結果の返し方を統一する |
| 任意 | `license` | スキルに適用するライセンス |
| 任意 | examples/ | 参考サンプル |
| 任意 | scripts/ | スキルが使う補助スクリプト |
| 任意 | Dependencies | 必要ツールや MCP の説明 |

templateはこんな感じ。

```
---
name: your-skill-name
description: このスキルが何をするか、そしてどんな時に使うかを書く
license: MIT
---

# Skill Title

このスキルの目的を1〜2文で書く。

## When to use

- どんな時に使うか
- どんなファイルや作業が対象か

## Checklist / Instructions

- [ ] 確認項目1
- [ ] 確認項目2
- [ ] 確認項目3

## Output Format

## Result: [target]

### Section

- [PASS/FAIL] Finding

### Summary

[X] items need attention

### Dependencies

- 必要なツール
- 必要な MCP
- 前提となるルール

### Notes

- 補足事項
- 除外事項
```

## スキルとエージェントを組み合わせる

ここでおすすめなのが、スキルとエージェントを組み合わせる方法です。

```
# Start with a code-reviewer agent
copilot --agent code-reviewer

> Check the project for quality issues
```

こうすると、AgentがSkillを持って仕事をしているので、より良い結果が得られます。

## skillの管理と共有

`/skills` コマンドによるスキル管理が可能です。また、/skillsを使うと、スキルを追加したり、削除したりすることができます。

| コマンド | 役割 |
| --- | --- |
| `/skills list` | インストールされているすべてのスキルを表示する |
| `/skills info <name>` | 特定のスキルに関する詳細情報を表示する |
| `/skills add <name>` | リポジトリまたはマーケットプレイスからスキルを有効化する |
| `/skills remove <name>` | スキルを無効化またはアンインストールする |
| `/skills reload` | `SKILL.md` を編集した後にスキルを再読み込みする |

/skills reload は、スキルの内容を更新した後に変更を反映させるために使用します。  
`.github/skills/`配下にスキルを登録した後、`/skills reload` を実行することで、GitHub Copilot CLI がスキルの変更を検出して再読み込みします。

reloadしたので、先ほど追加した、code-checklistスキルが使えるようになりましたね。  
![](https://static.zenn.studio/user-upload/60fd1f50a9dc-20260404.png)

# プラグインを利用する

プラグインは、スキル、エージェント、MCPサーバー構成などをまとめてインストールできるパッケージです。Copilot CLIの「アプリストア」拡張機能のようなものという理解でOKです。

以下のコマンドで確認が可能です。

```
/plugin list
# Shows installed plugins
/plugin marketplace
# Browse available plugins
/plugin install <plugin-name>
# Install a plugin from the marketplace
```

プラグインは複数の機能をまとめて提供できます。例えば、1つのプラグインに、連携して動作する関連スキル、エージェント、MCPサーバー構成などが含まれる場合があります。

あらかじめ作成されたスキルは、コミュニティリポジトリからも入手可能です。  
以下のサイトを確認してみてください。  
<https://github.com/github/awesome-copilot>

コミュニティスキルを手動でインストールすることも可能で、GitHubリポジトリでスキルを見つけた場合は、そのフォルダをスキルディレクトリにコピーしてください。

```
# Clone the awesome-copilot repository
git clone https://github.com/github/awesome-copilot.git /tmp/awesome-copilot

# Copy a specific skill to your project
cp -r /tmp/awesome-copilot/skills/code-checklist .github/skills/

# Or for personal use across all projects
cp -r /tmp/awesome-copilot/skills/code-checklist ~/.copilot/skills/
```

# MCPサーバーの利用

![](https://static.zenn.studio/user-upload/4600cc42ef77-20260404.png)

MCPサーバーはブラウザの拡張機能のように外部からGitHub Copilot CLIに機能を追加することが出来ます。  
GitHub Copilotを外部世界（GitHub、リポジトリ、ドキュメントなど）に接続し、さまざまなサービスと連携することが可能になります。

## 組み込みのMCPサーバー

MCP の動作を実際に見てみましょう。GitHub MCP サーバーはデフォルトで含まれています。以下を試してみてください。

```
List the recent commits in this repository
```

Copilotが実際のコミットデータを返した場合、あなたはMCPの動作を確認したことになります。これは、GitHub MCPサーバーがあなたに代わってGitHubにアクセスしていることを示しています。しかし、GitHubはサーバーの一つにすぎません。この章では、ファイルシステムへのアクセス、最新のドキュメントなど、他のサーバーを追加してGitHub Copilotの機能をさらに拡張する方法を説明します。

![](https://static.zenn.studio/user-upload/5cdfcb623855-20260404.png)

コミットが１件あることが確認出来ましたね！

次は`/mcp show`でMCPサーバーが構成されているかどうか、またそれらが有効になっているかどうかを確認することが出来ます。

筆者の環境は以下のような感じでした。  
![](https://static.zenn.studio/user-upload/e0df64ecc78d-20260404.png)

MicrosoftLearnMCP / github-mcp-server / ide が確認出来ますね。

## MCPサーバーの設定

MCPの動作を確認したところで、次は追加のサーバーを設定しましょう。このセクションでは、設定ファイルの形式と新しいサーバーの追加方法について説明します。

MCPサーバーは、~/.copilot/mcp-config.json（ユーザーレベル、すべてのプロジェクトに適用）または.vscode/mcp.json（プロジェクトレベル、現在のワークスペースのみに適用）で構成されます。

```
{
  "mcpServers": {
    "server-name": {
      "type": "local",
      "command": "npx",
      "args": ["@package/server-name"],
      "tools": ["*"]
    }
  }
}
```

ほとんどのMCPサーバーはnpmパッケージとして配布され、npxコマンドを介して実行されます。

### MCPサーバーの追加

まずは、GitHub Copilot にプロジェクトファイルを参照させるように設定しましょう。

まずは以下を追加していきます。

```
{
  "mcpServers": {
    "filesystem": {
      "type": "local",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
      "tools": ["*"]
    }
  }
}
```

VSCode でCommand + Shift + P を押して、MCP: Open User Configurationを選択し、mcp.jsonを開いてください。

以下のようにファイルサーバーの設定を追加しましょう。  
![](https://static.zenn.studio/user-upload/03a85ef79f28-20260404.png)

GitHub Copilotを再起動すると、以下のようにfilesystemサーバーが追加されていることがわかります。  
![](https://static.zenn.studio/user-upload/cbcde036f1cd-20260404.png)

この調子でContext7サーバーもインストールしてみましょう。

```
{
  "mcpServers": {
    "MicrosoftLearnMCP": {
      "type": "http",
      "url": "https://learn.microsoft.com/api/mcp",
      "headers": {},
      "tools": ["*"]
    },
    "filesystem": {
      "type": "local",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
      "tools": ["*"]
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    }
  }
}
```

設定ファイルは上記のようになりました。  
context7サーバーも追加されていることがわかりますね。  
![](https://static.zenn.studio/user-upload/57e19e8bf026-20260404.png)

次は、microsoftdocs/mcpのプラグインを追加してみましょう。

```
/plugin install microsoftdocs/mcp
```

これにより、サーバーとその関連エージェントのスキルが自動的に追加されます。インストールされるスキルは以下のとおりです。

* マイクロソフトドキュメント：概念、チュートリアル、および事実調査
* Microsoftコードリファレンス：API検索、コードサンプル、トラブルシューティング
* microsoft-skill-creator : Microsoft テクノロジーに関するカスタムスキルを生成するためのメタスキル

![](https://static.zenn.studio/user-upload/d7746f1d94fa-20260404.png)

次はWebアクセスツールを追加しましょう。

GitHub Copilot CLIには、任意のURLからコンテンツを取得できる組み込みweb\_fetchツールが含まれています。これは、ターミナルから離れることなくREADME、APIドキュメント、リリースノートなどを取得するのに便利です。MCPサーバーは不要です。

~/.copilot/config.jsonどのURLにアクセスできるかは、（Copilotの一般設定）で制御できます。

~/.copilot/config.json

```
{
  "permissions": {
    "allowedUrls": [
      "https://api.github.com/**",
      "https://docs.github.com/**",
      "https://*.npmjs.org/**"
    ],
    "blockedUrls": ["http://**"]
  }
}
```

上記の設定ができれば、以下のコマンドを実行してみましょう。

```
Fetch and summarize the README from https://github.com/facebook/react
```

無事に動作してそうですね。  
![](https://static.zenn.studio/user-upload/0cfa20b0a31e-20260404.png)

これでMCPの設定は完了です。

## MCPサーバーの利用

![](https://static.zenn.studio/user-upload/701f922d60d5-20260404.png)

探索したいサーバーを選択するか、順番に探索していくことができます。

| 試してみたいこと | ジャンプ先 |
| --- | --- |
| GitHub リポジトリ、イシュー、プルリクエストを扱いたい | GitHub サーバー |
| プロジェクトファイルを閲覧したい | ファイルシステムサーバーの使用状況 |
| 図書館資料を検索したい | Context7 サーバーの使用状況 |
| カスタムサーバー、Microsoft Learn MCP、および `web_fetch` の使い方を知りたい | 基本を超えた使い方 |

### Code Review → Issue作成 → PR作成 → レビュー → マージの一連の流れをGitHub Copilot CLIで実現

では、よくある流れをGitHub Copilot CLIで実現してみましょう。  
![](https://static.zenn.studio/user-upload/415807e57564-20260404.png)

今回の一連の流れにて、必要なagentsやskillsは以下のような感じになります。  
先ほど追加したMCPサーバーなど使いつつ、スムーズに一連の流れを進めたいと思います。

```
.github/
 ├── agents/
 │   ├── security-reviewer.agent.md  🆕 Context7でClerk/Cosmos最新仕様を参照してレビュー
 │   ├── issue-writer.agent.md       🆕 構造化Issue作成（gh issue create対応）
 │   └── pr-writer.agent.md          🆕 Conventional Commits形式のPR作成
 ├── copilot/
 │   └── mcp.json                    🆕 リポジトリレベルのContext7 MCP設定
 ├── instructions/
 │   └── nextjs16.instructions.md    🆕 src/**/*.{ts,tsx}に自動適用
 └── skills/
     └── api-auth-pattern/SKILL.md   🆕 認証・エラーハンドリングのコードテンプレート
```

セキュリティ観点でreviewからissueの作成とPR、マージまで進めたいと思います。

1. Review — セキュリティ観点でレビュー  
   @security-reviewer src/app/api/ を全チェックして
2. Issue作成  
   @issue-writer レビュー結果からIssueを作成して
3. コード修正（api-auth-pattern skillが自動適用）とPR作成  
   APIルートに認証チェックを追加して
4. PRマージ  
   PRのレビュー・マージをして

#### 1. Review — セキュリティ観点でレビュー

以下のコマンドを実行

```
@security-reviewer src/app/api/ を全チェックして
```

Criticalとして以下のロールベースアクセス制御が完全に欠如とか言われました。  
![](https://static.zenn.studio/user-upload/4dcc72399a1e-20260404.png)

#### 2. Issue作成

次は以下のコマンドです。

```
@issue-writer レビュー結果からIssueを作成して
```

7つIssueを作成してくれたみたいなので、見に行ってみましょう。  
![](https://static.zenn.studio/user-upload/05647a775479-20260404.png)

確かに作られていますね！  
![](https://static.zenn.studio/user-upload/ad444c37be22-20260404.png)

Issueの内容も綺麗に書いてくれています。  
![](https://static.zenn.studio/user-upload/e902a04c4c30-20260404.png)

#### 3. コード修正（api-auth-pattern skillが自動適用）

> #2（try-catch追加）はスコープが明確で着手しやすいです。修正してPR作成まで進めますか？  
> とのことなので、#2を修正してみましょう。

```
#2（try-catch追加）を修正してPR作成まで進めてください。
```

修正してPR作成もしてくれましたね！楽々です。  
![](https://static.zenn.studio/user-upload/b95985d9be5f-20260404.png)

#### 4. PRマージ

PRマージも完了しました！  
![](https://static.zenn.studio/user-upload/e4154c48b575-20260404.png)

すごいですね。。。  
人の手を介在することなく、全て完了してしまいました。

これで、今回の一連の流れは完了です。  
お疲れ様でした。

# まとめ

本記事では、GitHub Copilot CLI のインストールから実際のアプリ開発・PR作成までを一気通貫で体験していただきました。

改めて、本記事で扱った内容を振り返ります。

| カテゴリ | 学んだこと |
| --- | --- |
| 基本操作 | インストール、ログイン、セッション管理（`--continue` / `--resume`）、各種コマンド |
| 4つのモード | Interactive / Programmatic / Plan / Autopilot の使い分け |
| コンテキスト活用 | `@` 参照によるファイル・ディレクトリの指定 |
| 開発ワークフロー | コードレビュー（`/review`）、リファクタリング、デバッグ、テスト生成、Git統合（`/pr` / `/diff` / `/delegate`） |
| エージェント | 組み込みエージェントとカスタムエージェント（`.agent.md`）の作成・活用 |
| スキル | `SKILL.md` によるチーム標準の定型作業の定義と自動適用 |
| プラグイン | マーケットプレイスからのプラグインインストールと管理 |
| MCP連携 | 外部サービス接続（filesystem / Context7 / MicrosoftLearnMCP 等） |
| アプリ開発 | GitHub Copilot CLI だけで調査→実装→テスト→デプロイ→PR作成までを完結 |

GitHub Copilot CLI を最大限に活用するためのポイントは以下の3つです。

1. **具体的に指示する** — 「何を」「どの観点で」「どんな形式で」を明確に伝えるほど、精度の高い結果が得られます
2. **エージェント・スキルを育てる** — プロジェクトに合わせた `.agent.md` と `SKILL.md` を整備することで、チーム全体の開発品質と速度が向上します
3. **ワークフロー全体で使う** — コードを書くだけでなく、調査（`/research`）→ 計画（`/plan`）→ 実装 → テスト → レビュー（`/review`）→ PR（`/pr`）という流れで活用すると真価を発揮します

GitHub Copilot CLI は単なるコード生成ツールではなく、**開発ライフサイクル全体をカバーする共同開発者** です。  
ぜひ日々の開発に取り入れて、その便利さを体感してみてください。

非常に長い記事でしたが、最後まで読んでいただきありがとうございました！  
みなさんの開発ライフがより楽しいものになることを祈って、この記事を終了したいと思います。

それでは🖐️

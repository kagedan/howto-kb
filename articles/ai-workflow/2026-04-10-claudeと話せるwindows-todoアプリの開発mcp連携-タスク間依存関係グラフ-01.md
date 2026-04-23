---
id: "2026-04-10-claudeと話せるwindows-todoアプリの開発mcp連携-タスク間依存関係グラフ-01"
title: "Claudeと話せるWindows Todoアプリの開発(MCP連携 × タスク間依存関係グラフ)"
url: "https://zenn.dev/tanayuuu/articles/82633df0cba6f8"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "zenn"]
date_published: "2026-04-10"
date_collected: "2026-04-11"
summary_by: "auto-rss"
---

## はじめに

普段組み込みエンジニアとして業務をしている中でTodoの管理を便利にしたいと感じたためWindowsデスクトップTodoアプリを開発しています。(普段はoutlookのTodoを利用しています)  
ぜひご利用いただき不具合あれば教えていただけると幸いです。

以下Release内のexeファイルをダウンロードして開くことでアプリの利用ができます。  
そのままでももちろんご利用できますが、MCP連携ができますので連携の方法は後述します。  
※ MCP利用の際にはClaude Desktopのインストールが必要となります。  
<https://github.com/begengineer/TodoApp/releases/tag/v1.0.2>

既存Todoアプリとの差別点としては以下の通りになります。

1. Claude Desktop と MCP (Model Context Protocol) で連携できる
2. タスク間の依存関係をグラフで可視化

詳しくは以下の「特徴」タブ内で説明します。

---

## 特徴

**MCP連携でアプリの操作**

* アプリの学習コストを下げることができると考えました。以下がコーディングタスクをMCP連携で追加した時の使用例です。
* Claude Desktopでタスクの追加のプロンプトを投げるとアプリにタスクが追加されます。(その他削除や依存関係追加、確認等もClaude Desktop上から可能です)

| Claudeプロンプトイメージ | アプリ画面 |
| --- | --- |
|  |  |
| **図1: MCPによる直感操作** | **図2: タスクの追加** |

**タスク依存関係の可視化**

* 先ほどのコーディングタスクの依存関係を可視化すると以下のようになります。
* 要件から最後のレビューまでの依存関係を可視化しています。「要件定義をしないで実装などはしないよね」ってこともこれで一目でわかります。  
  ![](https://static.zenn.studio/user-upload/162a6a376099-20260409.png)  
  *図3：コーディングタスクの一連の業務の依存関係を示すグラフ構造*

## 機能一覧

今回実装した機能は以下の項目になります。

| 機能 | 説明 |
| --- | --- |
| タスク管理 | タスク名・期限・ステータス（未着手/進行中/完了）・メモを管理 |
| 依存関係グラフ | タスク間の前後関係をノード/エッジで可視化 |
| ボトルネック検出 | 多くのタスクをブロックしているタスクが赤く光る |
| Claude Desktop 連携 | 自然言語でタスクを操作できる MCP サーバー機能 |

---

## 技術スタック

| 項目 | 採用技術 |
| --- | --- |
| 言語 | C# 13 |
| フレームワーク | .NET 10 / WPF |
| UI テーマ | ModernWpfUI 0.9.6 |
| データベース | SQLite（EF Core 9） |
| MCP サーバー | ModelContextProtocol 1.2.0 |

### MCP連携の実装理由

[MCP（Model Context Protocol）](https://modelcontextprotocol.io/) は Anthropic が策定したオープンプロトコルで、Claude Desktop などの AI クライアントが外部ツールと連携するための仕組みです。

新しいサービスを利用する際にそのサービスの学習コストが高いと離脱につながると考えたためTodoの項目自体はアプリ上で確認し、Todoの追加や削除、確認などの操作はClaude Desktop上で行えるようにしました。(もちろんアプリ上でもTodoの更新はできます)

`--mcp` 引数付きで起動すると GUI なしの MCP サーバーとして動作し、Claude Desktop がタスクの読み書きを行えるようになります。

---

## プロジェクト構成

```
TodoApp/
├── Models/          # データモデル（Todo, TodoDependency, TodoStatus）
├── Data/            # EF Core DbContext（SQLite）
├── Services/        # CRUD・依存関係・ボトルネック検出ロジック
├── ViewModels/      # MVVM ViewModel（INotifyPropertyChanged）
├── Views/           # ダイアログ・グラフビュー
├── Mcp/             # MCP サーバー（ツール定義）
├── MainWindow.xaml  # メイン画面
└── App.xaml         # アプリ起動・Converter 定義
```

---

## 実装ポイント

### 1. MCP サーバーの実装

`ModelContextProtocol` NuGet パッケージを使うと、C# のメソッドに属性を付けるだけで MCP ツールを定義できます。

```
[McpServerToolType]
public class TodoTools(TodoService todoSvc, DependencyService depSvc)
{
    [McpServerTool, Description("Todo 一覧を取得します。")]
    public async Task<string> ListTodos(
        [Description("フィルタ: 未着手 / 進行中 / 完了（省略可）")] string? status = null)
    {
        var todos = await todoSvc.GetAllAsync(ParseStatus(status));
        return string.Join("\n", todos.Select(t =>
            $"[{t.Id}] {t.Title} | 期限: {t.Deadline?.ToString("yyyy/MM/dd") ?? "なし"} | {Label(t.Status)}"));
    }
    // ...
}
```

`--mcp` フラグで起動したときだけ MCP サーバーモードになるように `App.xaml.cs` で分岐しています。

```
protected override async void OnStartup(StartupEventArgs e)
{
    if (e.Args.Contains("--mcp"))
    {
        await McpServerHost.RunAsync(e.Args); // GUIなしで MCP サーバーとして動作
        Shutdown();
        return;
    }
    base.OnStartup(e);
}
```

### 2. 依存関係グラフの可視化

グラフ描画は WPF の `Canvas` に `Border`（ノード）と `Path`（エッジ）を動的に配置して実現しています。

エッジはベジェ曲線で描画しています。

```
private void DrawArrow(Point from, Point to)
{
    double midY = (from.Y + to.Y) / 2;
    var fig = new PathFigure { StartPoint = from };
    fig.Segments.Add(new BezierSegment(
        new Point(from.X, midY), new Point(to.X, midY), to, true));
    // ...
}
```

ノードのレイアウトはトポロジカルソートを使った階層レイアウトを自前実装しています。依存関係に従って上から下へタスクが並びます。

### 3. ボトルネック検出

「2件以上の未完了タスクをブロックしているタスク」をボトルネックと定義し、`DropShadowEffect` で赤く光らせています。

```
public HashSet<int> FindBottlenecks(List<Todo> todos, List<TodoDependency> deps)
{
    var blockCount = new Dictionary<int, int>();
    foreach (var dep in deps)
    {
        var pred = todos.FirstOrDefault(t => t.Id == dep.DependsOnId);
        if (pred is null || pred.Status == TodoStatus.Completed) continue;
        blockCount[dep.DependsOnId] = blockCount.GetValueOrDefault(dep.DependsOnId) + 1;
    }
    return blockCount.Where(kv => kv.Value >= 2).Select(kv => kv.Key).ToHashSet();
}
```

### 4. 循環依存の防止

依存関係を追加する前に BFS でサイクルが発生しないかチェックしています。

```
private async Task<bool> WouldCreateCycleAsync(int todoId, int dependsOnId)
{
    var allDeps = await db.TodoDependencies.ToListAsync();
    var queue   = new Queue<int>([dependsOnId]);
    while (queue.Count > 0)
    {
        var cur = queue.Dequeue();
        if (cur == todoId) return true; // サイクル検出
        foreach (var d in allDeps.Where(d => d.TodoId == cur))
            queue.Enqueue(d.DependsOnId);
    }
    return false;
}
```

---

## セットアップ方法

### 必要なもの

以下Releaseから「TodoApp.exe」をダウンロードしてください。  
ダウンロードしたTodoApp.exeを起動するとTodoアプリが立ち上がります。  
<https://github.com/begengineer/TodoApp/releases/tag/v1.0.2>

---

## 使い方

基本的な使用方法は以下の通りです。

### タスクの追加・編集

1. 「＋ 新規追加」ボタンをクリック
2. タスク名・期限・ステータス・メモを入力
3. 「保存」をクリック  
   期限を過ぎたタスクは一覧で赤字表示されます。  
   ![](https://static.zenn.studio/user-upload/2a1d0bae2506-20260409.png)

### 依存関係グラフ

1. 「🔗 依存関係グラフ」ボタンでグラフ画面を開く
2. 「＋ 依存関係を追加」ボタンをクリック
3. ダイアログで「先に完了すべきタスク」と「次に着手するタスク」を選択
4. 「追加」をクリック

ノードはドラッグで自由に移動でき、「⟳ 自動整列」ボタンで階層レイアウトに戻せます。  
![](https://static.zenn.studio/user-upload/ebd20dca52f2-20260409.png)

---

## Claude Desktop との連携

### 設定

`%APPDATA%\Claude\claude_desktop_config.json` に以下を追加します。

```
{
  "mcpServers": {
    "todo-app": {
      "command": "C:\\path\\to\\TodoApp.exe", // TodoApp.exeのパスをいれてください
      "args": ["--mcp"]
    }
  }
}
```

Claude Desktop を再起動すると連携が有効になります。

### Claude Desktopを用いた使い方（会話例）

MCP経由での操作例を以下に紹介します。  
可能ならClaude Desktopが開いたら自動的にアプリが立ち上がるようにすると便利です。  
MCP経由でタスクの追加/削除をした際にはアプリの更新ボタンを押すとタスクの更新が反映されます。

1. タスクの確認  
   ![](https://static.zenn.studio/user-upload/8a4457fa1bcb-20260409.png)  
   *図4：現在のタスクの確認*
2. タスクの追加  
   ![](https://static.zenn.studio/user-upload/dfc79b369573-20260409.png)  
   *図5：タスクの追加*
3. タスクステータスの更新  
   ![](https://static.zenn.studio/user-upload/6b93b6984e7a-20260409.png)  
   *図6：タスクステータスの更新*

### 公開している MCP ツール

| ツール | 説明 |
| --- | --- |
| `list_todos` | 一覧取得（ステータスでフィルタ可） |
| `add_todo` | タスク追加 |
| `update_todo` | タスク更新 |
| `delete_todo` | タスク削除 |
| `add_dependency` | 依存関係の追加 |
| `remove_dependency` | 依存関係の削除 |
| `get_bottlenecks` | ボトルネックタスクの取得 |

---

## ソースコード

<https://github.com/begengineer/TodoApp>

---

## 注意点

!

* スマートアプリコントロールの設定をオフにしないとアプリが立ち上がらない可能性があります。
* Claudeとの連携がうまくいかない場合がありますのでその際にはお手数をおかけしますがClaude Desktopの再起動やPCの再起動を実施いただければと思います。

## おわりに

MCP を使うと既存のデスクトップアプリに自然言語インターフェースを後付けできるのが面白いと感じました。`ModelContextProtocol` NuGet パッケージのおかげで C# からの実装も思ったより簡単でした。

依存関係グラフは今後さらに改善できる余地があるかなと思います（クリティカルパスの計算、ガントチャート表示など）  
興味があればぜひ試してみてください。

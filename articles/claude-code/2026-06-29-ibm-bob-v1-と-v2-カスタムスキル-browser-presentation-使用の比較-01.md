---
id: "2026-06-29-ibm-bob-v1-と-v2-カスタムスキル-browser-presentation-使用の比較-01"
title: "IBM Bob v1 と v2 : カスタムスキル browser-presentation 使用の比較結果"
url: "https://qiita.com/c_u/items/f802308cccc7d7b2643f"
source: "qiita"
category: "claude-code"
tags: ["MCP", "AI-agent", "VSCode", "qiita"]
date_published: "2026-06-29"
date_collected: "2026-06-30"
summary_by: "auto-rss"
query: ""
---

### はじめに

IBM Bob（ボブ）<img src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/517421/3d032172-0a52-4f16-82cb-6cce2b67eca6.png" width="4%"> の2.0が 2026年6月下旬にリリースされました。

当記事では自作スキル ["browser-presentation"](https://github.com/cu0001/browser-presentation)  を使用してv1 と v2 を比較した内容をまとめました。


---

### 動画

当記事の内容の動画です。

<iframe width="711" height="400" src="https://www.youtube.com/embed/YEN1BBRbQsA?si=2wyQs_aP7i35tT1G" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>


---

### 検証環境

Bob v1.0
```
バージョン: 1.116.0+bob1.0.3
コミット: 1.116.0
日付: 1.0.3
Electron: 2e8c357664b8896d61cf3c2989dc1ee8562ea43c
ElectronBuildId: 2026-05-26T22:56:05+05:30 (3 週間前)
Chromium: 39.8.7
Node.js: undefined
V8: 142.0.7444.265
OS: 22.22.1
```

Bob v2.0 (社内先行リリース版での確認です)
```
Version: 1.116.0+bob2.0.0-insider.1
VSCode Version: 1.116.0
Bob Version: 2.0.0-insider.1
Commit: 5a0dfc1c4172f3bbcf208027bb2728dc1db9a3f5
Date: 2026-06-15T18:56:02+03:00 (1 day ago)
Electron: 39.8.7
ElectronBuildId: undefined
Chromium: 142.0.7444.265
Node.js: 22.22.1
V8: 14.2.231.22-electron.0
OS: 1.116.0
```

Bob 2.0 の changelog に新機能の記載があります。

https://bob.ibm.com/docs/ide/changelog


---

### カスタムスキルでアップデート効果を確認

最近の資料作りをAI メインに作成することが増え、非常に楽になりました。
資料用のAIスキルは多々あり、今後も多々出てくるのではと思いますが、

せっかくなので、自分で作成したスキルを利用します。

https://github.com/cu0001/browser-presentation

https://qiita.com/c_u/items/775ab7a411f587456bdf

---





#### 実行


次のプロンプトを Bob IDE v1 と v2 に同じように実行します。

```
@README.md からスライド資料を作成して。browser-presentation スキルを使用して
```

#### 生成結果比較

1回のみ実行した出力結果でお示ししています。

Bob version1 で生成されたスライド一覧
![bob1_slides_grid.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/517421/1067167e-2176-4746-9ef3-3898ae7a27fd.png)

Bob version2 で生成されたスライド一覧
![bob2_slides_grid.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/517421/9f255bee-f3af-46f3-9610-e20963d28ce8.png)


#### 考察

Bob v1 と v2 のスライド比較を見ると、**生成品質・完成度の差が明らか**です。

v1 はプロンプトの意図を概ねトレースしつつも、文字を配置しただけであまりデザイン性は感じられません。一方 v2 は、構成の流れが整理されており、スライドごとの情報密度も均一化されています。これは changelog に記載された以下の改善が効いていると考えられます。

- **コンテキストウィンドウの拡張（200k → 270k トークン）**：README.md 全体 + スキルの指示 + 生成中の中間状態をより広い視野で保持できる
- **並列ツール呼び出し（Parallel tool calling）**：ファイル読み取りや検索を同時実行できるため、スキル内の複数ステップがより効率的に処理される
- **Nested workflows**：スキルが別ワークフローを呼び出せるようになったことで、複雑な資料生成のような多段処理に対応しやすくなっている

---

### Bob 2.0 で変わった主なポイント

changelog をざっくり整理すると、開発者ワークフロー全体に関わるアップデートが中心です。

#### Subagents（サブエージェント）

複雑なタスクを並列ワークストリームに分割し、専門化したサブエージェントを生成できるようになりました。「1体が計画しながら別の1体が実装する」といった分業が可能で、承認は各スポーンごとに求められます。大規模なリファクタや複数ファイル横断の改修で特に有効そうです。

#### Agent steering & メッセージキュー

実行中のエージェントをキャンセルせずに方向転換できます。Bob が処理中に投げた新規メッセージはキューに積まれ、ドラッグでの並び替えも可能。webview をリロードしてもキューは保持されます。

#### MCP サーバー管理 UI

設定パネルの **MCP Servers タブ**から、MCP サーバーの追加・設定・削除が GUI 操作で完結するようになりました。これまでは JSON を手で編集する必要があったので、チームへの展開や設定の頻繁な切り替えが格段に楽になります。

#### Skills 設定タブ

Bob 2.0 では Settings に **Skills タブ**が新設され、ワークスペースで利用可能なスキルの一覧・管理が一画面で行えます。v1 では `.bob/skills/` ディレクトリを直接確認するしかなかったため、可視性が大幅に向上しています。


![skills.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/517421/27b8d26c-1409-423a-b651-d7bd4cad76c7.png)




#### モードの整理

v1 の複数モードから、**Plan / Agent / Ask** の3モードに集約されました。Advanced や Orchestrator は各デフォルトモードに統合されており、どのモードを選ぶべきか迷う場面が減ります。

#### 拡張ファイル対応

`.docx` / `.pdf` / `.xlsx` をそのままコンテキストとして読み込めるようになりました。仕様書や設計書を渡すためにテキスト抽出する手間が省けます。

---

### まとめ

自作スキルを使った Bob v1/v2 比較の結果、**コンテキスト保持の拡張と並列処理能力の向上が、スライド生成品質の差に直結していることが確認できました**。

また、MCP サーバー管理や Skills タブの整備など、**ツールとスキルを「使いこなす基盤」が v2 で整った**印象があります。v1 では自前で JSON を管理したり、ディレクトリを掘り下げて確認する必要があった箇所が、GUI で一元管理できるようになっています。

自分で作った "[browser-presentation](https://github.com/cu0001/browser-presentation)" スキルとの相性も良く、資料生成の自動化もアップデートしていこうと思います。

以上です。

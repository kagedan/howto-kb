---
id: "2026-04-19-複数の-ai-cli-をいい感じにバトンタッチするためのai-cliオーケストレーションツール-ta-01"
title: "複数の AI CLI を「いい感じにバトンタッチする」ためのAI CLIオーケストレーションツール tasuki を作った"
url: "https://zenn.dev/kooooohe/articles/d47e0dcfe258c0"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-19"
date_collected: "2026-04-20"
summary_by: "auto-rss"
query: ""
---

Claude Code / Codex CLI / GitHub Copilot CLI を**優先度順に自動で渡り歩く** CLI オーケストレーター **tasuki** を作って OSS で公開しました。

<https://github.com/0xkohe/tasuki>

![](https://static.zenn.studio/user-upload/566b73d60b06-20260419.png)

## モチベーション

私は1つのAIツールを$100,$200プランで契約するよりも$20~$30で複数のAIツールを契約して色々試してみたいタイプの人間です。  
ただ、そうすると上限が割と早く来てしまい、作業の中断(人の介入)が必要になるのがめんどくさく感じていました。

レビューはCodexが良いやClaudeは対話に良いとか色々AIの特徴はあったりしますが、よっぽどのこだわりがないケースにおいてはいろんなモデルやハーネスを使ってその差を日々感じていいたいという思いもあります。  
片方だけを使っていると、もう片方がいつの間にか得意になっていた領域に気付けません。

切り替え判断そのものは単純労働なので、機械にやらせたかった。これが tasuki を書いた動機です。

レートリミットという機会を活かして他のモデル、ハーネスを触るということを日々やっているということです。

## 想定している運用フロー

tasuki のデフォルト挙動は、自分が実際にやっていた手動運用をそのまま写したものです。

1. **Claude Code と Codex CLI の 5 時間枠を優先的に回す**  
   枠のリセットが短いので、先に使い切っておくのがコスパがいい
2. **両方の 5 時間枠を使い切ったら、GitHub Copilot CLI に渡す**  
   Copilot は月次の枠なので、5h 枠の "つなぎ" として使うのが合理的
3. **Claude / Codex の枠が復活したら、またそちらに戻る**  
   月次枠はなるべく温存したい

このサイクルを「手で切り替えない」というのが tasuki の本質です。優先度 1 位が使えなければ 2 位、2 位がダメなら 3 位に流れ、上位の枠が回復したら自動でそちらに戻ります。

## 何をしてくれるか

使い勝手のポイントは 3 つ。

1. **ネイティブ UI をそのまま使える**  
   各 CLI はラップされた PTY の中で動くので、Claude Code なら Claude Code の、Codex なら Codex のインタラクティブ UI がそのまま出ます。tasuki は間に入るだけで独自 UI を押し付けません。
2. **枠の消費状況を見て自動で切り替える**  
   各アダプタが CLI の出力ストリームを監視して、しきい値（デフォルト 95%）を越えたら次の優先プロバイダへ自動でハンドオフします。
3. **ハンドオフで文脈を持ち越せる**  
   現プロバイダで何をやっていたか、どこまで進んでいたかを `.tasuki/handoff.md` に書き出して、次のプロバイダ起動時に注入します。切り替わった直後の最初の応答で「先ほどの続きですね」と入れるためのコンテキストが残ります。

## 対応プロバイダ

| プロバイダ | 内部名 | 枠のリセット単位 |
| --- | --- | --- |
| Claude Code | `claude` | 5 時間 |
| Codex CLI | `codex` | 5 時間 |
| GitHub Copilot CLI | `copilot` | 月次 |

デフォルトでは「リセットが短い枠を先に食い潰し、長い枠は後回し」という優先度になります。

## 5 分でためす

### インストール

```
go install github.com/0xkohe/tasuki/cmd/tasuki@latest
```

Go 1.26 以上が必要です。少なくとも `claude` / `codex` / `copilot` のうちどれか 1 つが PATH にあって、ログイン済みであること。

### 初回起動

```
cd path/to/your/project
tasuki
```

初回は対話的に設定ファイル `.tasuki/config.yaml` を作るウィザードが走ります。有効化するプロバイダと優先度だけ選べば OK。

これで優先度 1 位のプロバイダが PTY で立ち上がります。枠が切れたら何もしなくても次に流れていきます。  
![](https://static.zenn.studio/user-upload/5e6bd53e8c36-20260419.png)  
![](https://static.zenn.studio/user-upload/9775db3f2cb4-20260419.png)

## 設定の例

`.tasuki/config.yaml`（プロジェクト単位）か `~/.config/tasuki/config.yaml`（グローバル）。マージ順は「デフォルト → グローバル → ローカル」。

```
switch_threshold: 95   # 何%で切り替えるか
warn_threshold: 80     # 何%で警告を出すか
yolo: false            # 各 CLI のサンドボックス突破フラグをまとめて有効化（危険）

providers:
  - name: claude
    enabled: true
    reset_cycle: 5h
    priority: 1
  - name: codex
    enabled: true
    reset_cycle: 5h
    priority: 2
  - name: copilot
    enabled: true
    reset_cycle: monthly
    priority: 3
```

優先度は

1. `priority` が明示されていればそれ
2. なければ `reset_cycle` から推論（`5h` < `weekly` < `monthly`）
3. それもなければ `providers` 配列の並び順

という順で解決されます。上にも書いた「短いリセット枠を優先して消費、長いリセット枠は温存」というポリシーがデフォルトで効くようになっています。

## 中身のはなし

設計は以下のレイヤーに分けています。

```
cmd/tasuki/            # Cobra エントリポイント
internal/adapter/      # 各 CLI のラッパー + PTY 管理 + レートリミット検知
internal/orchestrator/ # プロバイダ選択・切り替え・ハンドオフ
internal/config/       # YAML ロード / マージ / 対話初期化
internal/state/        # セッション・クールダウン永続化
internal/ui/           # ターミナル描画
```

### アダプタは共通インタフェース

プロバイダごとの差分はアダプタ層に閉じ込めてあります。各 CLI の出力フォーマット（JSON ログ・ステータスライン・プレーンテキスト）はバラバラですが、外向きには共通の `Event` ストリームに正規化されます。枠の残量・トークン使用量・エラーを同じ型で扱えるので、オーケストレータ側はプロバイダを意識しません。

### オーケストレータは単一責任

オーケストレータは

* イベントストリームを見て
* しきい値を越えたら
* 次の候補を `ProviderPriority` で選んで
* クールダウン中のものはスキップして
* ハンドオフ文書を書き出して
* 次の CLI を起動する

以上。状態は `.tasuki/session.json` と `.tasuki/handoff.md` に外出しにしているので、`tasuki --resume` で復帰できます。枠が復活して上位プロバイダが使えるようになったら、そちらに戻るのも同じロジックです。

### PTY 透過はただの PTY 透過

独自の TUI を挟まないのがこだわりです。各 AI CLI のベンダーは UI に相当の労力を払っているので、tasuki がその上にレイヤーを重ねるとだいたい体験が悪くなります。なので端末の raw モード・サイズ変更・シグナル転送まで含めて素直にパススルーし、必要なときだけ左上に細い状態バナーを出す構成にしました。

## 設計上の割り切り

* **プロバイダの API は直接叩かない**: 各 CLI を subprocess で起動するだけ。認証・モデル選択・ツール呼び出しはすべて本家 CLI 側に任せるので、upstream の機能追加にタダ乗りできる。「常に全部を使い続ける」という目的と一番相性がいいアーキテクチャ。
* **検知はヒューリスティック**: 各 CLI が枠の残量を公式に通知してくれるとは限らないので、出力中のキーワード・パーセント表示・HTTP ステータス相当の文字列などを正規表現で拾っています。泥臭いが現実解。
* **Yolo モードは明示的に**: `--dangerously-skip-permissions` 系の突破フラグは `--yolo` / `TASUKI_YOLO=1` / `yolo: true` のどれかで明示したときだけ転送します。

## いまのところ対応していないこと

* ローカル LLM（Ollama など）やKiro CLIのアダプタはまだ未実装
* Windows は未検証（PTY 周りで Linux/macOS を優先）
* 検知ヒューリスティックは各 CLI のバージョンアップで壊れ得る（contribute 歓迎です）

## おわりに

全部を常用しながら、色々試す。そのための摩擦を下げるのが tasuki の役割です。

同じように「全部使いたい派」の人に刺されば嬉しいです。バグ報告・PR・「こっちの CLI も対応して」系の issue はいつでも歓迎です。

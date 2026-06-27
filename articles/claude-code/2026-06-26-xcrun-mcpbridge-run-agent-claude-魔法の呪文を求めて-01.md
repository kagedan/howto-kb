---
id: "2026-06-26-xcrun-mcpbridge-run-agent-claude-魔法の呪文を求めて-01"
title: "xcrun mcpbridge run-agent claude ——魔法の呪文を求めて"
url: "https://zenn.dev/keiichi_okamoto/articles/xx-260626-xcode-claude"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "AI-agent", "cowork", "zenn"]
date_published: "2026-06-26"
date_collected: "2026-06-27"
summary_by: "auto-rss"
query: ""
---

## 謎のコマンド

[前の記事](https://zenn.dev/keiichi_okamoto/articles/xx-260625-container) で「Xcode管理版 Claude Code」について触れた。`xcrun mcpbridge run-agent claude` というコマンドで起動するもので、通常の CLI 版とは違う何かだと思っていた。

ところがネットで検索しても全く出てこない。英語で検索しても出てこない。Claude（Cowork）に調べてもらっても、`xcrun mcpbridge` を MCP サーバーとして Claude Code に登録する逆方向の使い方しか出てこない。Apple の公式ドキュメントにも `run-agent` は載っていない。

でも手元では動いている。

どこでこのコマンドを知ったのかも思い出せない。WWDC26 のセッションで見たのかもしれないし、`xcrun mcpbridge -h` を自分で叩いて発見したのかもしれない。記憶がない。

---

## Xcode管理版という名前の由来

まず「Xcode管理版」という呼び名の出どころを白状しておく。公式の名称ではない。

普段 CLI 版の Claude Code を使っているので、同じようなものが Xcode の中で動いているのを見て「君のことは何と呼べばいい？」と聞いてみた。返ってきた答えが「Xcode管理版」だった。

AI に名付けてもらった名前がそのまま定着してしまった。

![Xcode管理版 Claude Code](https://static.zenn.studio/user-upload/deployed-images/ba262be261c78dcf8d3a33e5.png?sha=2db74be3b2f0bdf5578e31c467a6032473fab011)

---

## ヘルプを読んで期待が膨らんだ

```
okamoto@MacMini-M1 ~ % xcrun mcpbridge run-agent -h
mcpbridge - STDIO Bridge for Xcode MCP Tools

SUBCOMMANDS:
    run-agent       Launch a coding agent with Xcode-provided configuration.
                    Connects to a running Xcode to fetch the agent's binary
                    path, auth tokens, environment, and settings, then execs
                    the agent with full terminal access.
```

**auth tokens**。**Xcode-provided configuration**。**full terminal access**。

これは何か特別なことができるに違いない——そう思った。Xcode から認証情報や環境設定を受け取って動くのだから、CLI 版には出来ない「魔法の呪文」があるはずだ、と。

---

## 地雷も踏んだ

期待に胸を膨らませながら使っていたある日、CLI 版とバージョンが違うのが気になって揃えようとした。

```
xcrun mcpbridge run-agent claude upgrade
```

起動できなくなった。

ヘルプに書いてある通りで、Xcode が管理するバイナリを自己更新すると Xcode が内部で持つバージョン情報と食い違いが生じる。同じ日に偶然 Xcode 27 beta 1 → beta 2 のアップデートがあって、インストールしたら直った。Xcode がバイナリを正しいバージョンに戻してくれたからだ。

**Xcode管理版を upgrade するな**——これは身をもって学んだ。

---

## 魔法の正体を調べた

Cowork（Claude / Sonnet 4.6）と一緒に「この Xcode 管理版、CLI 版と何が違うのか」を調べてみた。

Apple の公式ドキュメントで分かったのは、Xcode > 設定 > Intelligence > Agents から「Claude Agent」を「Get」でインストールすると、Xcode がバイナリをダウンロードして管理する。`xcrun mcpbridge run-agent claude` は起動時に Xcode からバイナリのパス・認証トークン・環境設定を受け取って Claude を起動する仕組みだということ。

つまり「Xcode が面倒を見てくれている Claude」という意味では確かに Xcode 管理版だ。

設定ファイルの場所も分かった。

```
~/Library/Developer/Xcode/CodingAssistant/ClaudeAgentConfig
```

ここに CLAUDE.md や追加 MCP の設定を置くと Xcode 管理版にだけ反映される。

---

## 「同じ作業」を CLI 版でやってみた

KanjiApp という iOS アプリを実機の iPhone 17 にビルドしてインストールして起動する——という作業を Xcode 管理版でやった後、同じプロジェクトのディレクトリで CLI 版を起動して「このアプリを実機で起動して」と頼んでみた。

CLI 版は同じようにデバイスを検出して、同じようにデフォルトの Xcode 26.5 で「project file format (110)」エラーにはまって、自分で Xcode-beta.app（27.0）を見つけて回避して、ビルドして、インストールして、起動した。

**同じやないか。**

---

## 魔法ではなかった

突き詰めると、能力の差はなかった。できることを決めているのは「CLI 版か Xcode 管理版か」ではなく「環境」だった。

* GUI（Aqua）セッションで動いているか
* 実機が繋がっているか
* Xcode が起動しているか

これが揃っていれば CLI 版でも同じことができる。Xcode 管理版の優位性は「認証と環境をお膳立てした状態で起動できること」だけで、起動後の能力はモデルが同じなので差がない。

むしろバージョン更新の自由度は CLI 版の方が高い。`claude upgrade` でいつでも更新できる。Xcode 管理版は Xcode のアップデートを待つしかない。

---

## それでも知って良かった

魔法はなかったが、「なぜ同じなのか」を実験で確かめた過程は悪くなかった。

`xcrun mcpbridge` が Xcode 26.3 で追加された Apple 公式のブリッジであること、`run-agent` サブコマンドが存在するのにドキュメントに載っていないこと、Xcode が Claude のバイナリを Component として管理する仕組みになっていること——これらは調べなければ知らないままだった。

それと、Xcode 管理版の Claude が終始「特別な能力はない、環境の差だ」と正直に言い続けたのは好感が持てた。魔法使いのふりをしていたのは僕だけだった。

---

## 本当の魔法はこっちだった

調べる中で「逆方向」の使い方の存在を知った。Apple の公式ドキュメントに載っているのはこちらだ。

```
claude mcp add --transport stdio xcode -- xcrun mcpbridge
```

CLI 版の Claude Code に Xcode を MCP サーバーとして登録する。

Xcode 管理版が「Xcode が Claude を起動する」方向なのに対して、こちらは「Claude が Xcode をツールとして使う」方向だ。`xcrun mcpbridge` がその橋渡しをする。

### 何ができるのか

MCP として登録した Xcode が Claude に提供するツール群は、Xcode の内部操作そのものだ。ビルドエラーの確認、ソースファイルのナビゲーション、シンボルの検索——これらを Claude が直接 Xcode に問い合わせながら作業できる。

`xcodebuild` コマンドを叩いてテキストのエラーを読む、という間接的な方法ではなく、Xcode が内部で持っているビルドの状態や警告を MCP 経由で直接受け取れる。

### セットアップ

一度だけ実行すれば設定は永続する。

```
# Xcode を MCP サーバーとして Claude Code にグローバル登録
claude mcp add --scope global --transport stdio xcode -- xcrun mcpbridge

# 以降はどのディレクトリでも普通に起動するだけ
claude
```

`--scope global` を付けないとプロジェクトローカルな設定になる。Xcode との連携はどのプロジェクトでも使いたいはずなのでグローバルで登録しておくのが無難だ。

Claude を起動すると Xcode からダイアログが表示される。

![Allow Claude Code to access Xcode](https://static.zenn.studio/user-upload/deployed-images/354a423c7bcd49f3556717d4.png?sha=c2d281b348799d14c3d1504f5a9194d64c37491f)

Xcode が Claude のバイナリの署名を検証した上で許可を求めてくる。`Signed by: Anthropic PBC` という表示は、Xcode が「これは本物の Claude Code だ」と確認している証だ。「Don't ask again for this agent binary until Xcode restarts」にチェックを入れれば、Xcode を再起動するまで毎回聞かれなくなる。

起動後に `/mcp` コマンドで登録済みの MCP サーバーとそのツール一覧を確認できる。Xcode が起動していれば `xcode` サーバーが接続状態になっている。

### どの Xcode を起動しておくべきか

実際に試してみて分かったことをまとめる。

Claude でのビルドには2通りの方法がある。

|  | xcode-tools（MCP） | xcodebuild（CLI） |
| --- | --- | --- |
| Xcode を開いておく必要 | **必要** | 不要 |
| 起動ディレクトリ | 関係ない | 関係ない |
| 実機操作・コンソール | 扱いやすい | 別途 `devicectl` が必要 |

**MCP 経由のビルド**では、`xcrun mcpbridge` が起動中の Xcode に XPC で接続する。Claude がプロジェクトを開く操作はしてくれない。Xcode で対象プロジェクトを開いた状態にしておくことが前提で、Claude を「どのディレクトリで起動したか」は関係ない。複数プロジェクトを開いている場合は `XcodeListWindows` でアクティブなウィンドウを確認できる。

**xcodebuild（CLI）経由のビルド**では Xcode を開いておく必要はなく、プロジェクトファイルのパスさえ正しければどこからでもビルドできる。ただし実機テストが必要なケースでは、MCP 経由の方がデバイス接続やコンソールの取得まで一貫して扱いやすい。

Xcode 管理版も CLI 版 + Xcode MCP も、この動作は同じだった。

Xcode が複数バージョン入っている場合、`xcrun` 自体がどちらを使うかは `DEVELOPER_DIR` で決まる。実際に試したところ、`DEVELOPER_DIR` を指定せずに CLI 版を起動すると、デフォルトの Xcode 26.5 を使おうとしてプロジェクトファイルのフォーマット（objectVersion = 110）が開けないエラーになった。

解決策は `DEVELOPER_DIR` を MCP の設定に持たせることだ。`~/.claude.json` の MCP サーバー設定に環境変数を書いておくと、シェルで毎回 `export` しなくても Claude 起動時に自動で適用される。

```
{
  "mcpServers": {
    "xcode": {
      "command": "xcrun",
      "args": ["mcpbridge"],
      "env": {
        "DEVELOPER_DIR": "/Applications/Xcode-beta.app/Contents/Developer"
      }
    }
  }
}
```

この設定を入れてから CLI 版でビルドして実機で動かすことができた。Xcode 管理版と全く同じ結果だ。プロジェクトごとに起動する Xcode と `DEVELOPER_DIR` を合わせておく必要がある点も、Xcode 管理版と変わらない。

### ２つの Claude Code が出来ること

ダイアログをよく読むと **"building, testing, or modifying code"** とある。そして実はこのダイアログ、Xcode 管理版を起動したときにも全く同じものが出る。

![Xcode管理版起動時のダイアログ](https://static.zenn.studio/user-upload/deployed-images/6b31cf73844660adccacb5e6.png?sha=5ec9ad938b41fe163c2c0532894ea016f0e3739a)

2枚のダイアログ、アイコンまで同じ Xcode beta だ。つまり両方とも Xcode 27 beta に繋ぎにいっている。Xcode から見れば両者は区別がない。どちらも「Claude Code が Xcode にアクセスしようとしている」という同じ構図だ。できることも同じ。

違いはバイナリの場所だけだ。

|  | バイナリのパス | バージョン |
| --- | --- | --- |
| CLI 版 | `~/.local/share/claude/versions/2.1.193/claude` | 2.1.193 |
| Xcode 管理版 | `~/Library/Developer/Xcode/CodingAssistant/Agents/claude/2.1.175/claude` | 2.1.175 |

Xcode 管理版のバイナリは Xcode が管理するディレクトリに格納されていて、バージョンも古い。これが `claude upgrade` できない理由の証拠がパスに出ている。

### CLI 版 + Xcode MCP と Xcode 管理版の比較

|  | CLI 版 + Xcode MCP | Xcode 管理版 |
| --- | --- | --- |
| 起動 | `claude` | `xcrun mcpbridge run-agent claude` |
| 起動ディレクトリ | プロジェクトのディレクトリで起動 | どこからでもいい |
| セットアップ | `claude mcp add` で一度だけ設定 | Xcode > 設定 > Intelligence から |
| Xcode から見た姿 | Claude Code が Xcode にアクセス | Claude Code が Xcode にアクセス |
| できること | building, testing, modifying code | building, testing, modifying code |
| Claude のバージョン管理 | `claude upgrade` で自由に更新 | Xcode のアップデートに依存 |
| Apple 公式ドキュメント | あり | なし（ヘルプテキストのみ） |

Xcode の目には同じに映る。できることも同じ。「起動ディレクトリ」は理屈の上では違いがあるが、Finder でプロジェクトを開いて右クリックメニューの「新規ターミナルでフォルダに移動」から起動するのが自然な流れなので、実運用では両者ともプロジェクトのディレクトリで起動することになる。違いは Claude のバイナリをどちらが管理するかだけで、魔法はこちらにもなかった。

---

## まとめ

`xcrun mcpbridge run-agent claude` は特別な魔法の呪文ではなかった。

Xcode が認証と環境を肩代わりして Claude を起動してくれる便利な仕組みではあるが、起動後の Claude は CLI 版と同じだ。あえて使う必要はない。`claude` と打てばいい。

CLI 版 + Xcode MCP もバージョン管理の自由度と公式サポートという点で優れているが、正直なところ僕は多分使わない。

ただ、地雷だけは共有しておく。

```
# これは絶対にやってはいけない
xcrun mcpbridge run-agent claude upgrade
```

---

## 参考

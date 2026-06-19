---
id: "2026-06-19-axmol-enginemacosでvscodeを使ってiosandroidアプリを開発するプロジェ-01"
title: "【Axmol Engine】macOSでVSCodeを使ってiOS/Androidアプリを開発する（プロジェクト作成〜Claude Code連携まで）"
url: "https://qiita.com/OnuuuumaX/items/265c2d0b2b9b131b4aa6"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "VSCode", "Python", "qiita"]
date_published: "2026-06-19"
date_collected: "2026-06-19"
summary_by: "auto-rss"
query: ""
---

# はじめに

この記事では、**macOS \+ VSCode** を使って Cocos2d-xの後継のAxmol Engine プロジェクトを作成し、Claude Code と連携するまでを解説します。

前提として、以下がすでに完了していることを想定しています。

- Homebrew / PowerShell / Python 3.13以上 / CMake / Xcode 16.4以上 のインストール  
- `git clone` による Axmol リポジトリの取得（`~/axmol`）  
- `pwsh setup.ps1` および `pwsh setup.ps1 -p android` の実行済み

環境構築については別記事をご参照ください。

https://qiita.com/OnuuuumaX/items/c2e464ef65fa9d0e9a57

https://qiita.com/OnuuuumaX/items/ff379fa1fee2711ad470

---

# STEP 1: 新規プロジェクトの作成

セットアップが完了したら、`axmol new` コマンドで新規プロジェクトを作成します。 ※**作成済みの場合はスキップしてください。**

```shell
axmol new -p com.yourcompany.mygame -d ~/projects -l cpp MyGame
```

| オプション | 説明 |
| :---- | :---- |
| `-p` | バンドルID（例: `com.yourcompany.mygame`）世の中でユニークである必要があります |
| `-d` | プロジェクトの保存先ディレクトリ |
| `-l cpp` | 使用言語（`cpp` または `lua`） |
| 最後の引数 | プロジェクト名 |

⚠️ **注意**：プロジェクトの保存先は `~/Documents/` や `~/Desktop/` など **OSの保護フォルダを避ける** のがおすすめです。Xcode のアクセス権エラーの原因になることがあります。`~/dev/` や `~/projects/` などの専用フォルダを使いましょう。

コマンドが成功すると、以下のような構成のプロジェクトが生成されます。

```
MyGame/
├── .axproj              # Axmolプロジェクト設定ファイル
├── CMakeLists.txt
├── Source/
│   ├── AppDelegate.cpp
│   ├── AppDelegate.h
│   ├── MainScene.cpp
│   └── MaincdScene.h
├── Resources/
├── proj.android/        # Android向けプロジェクト
└── proj.ios_mac/        # iOS/macOS向けプロジェクト（xcodeproj生成後）
```

---

# STEP 2: VSCode の拡張機能インストール

プロジェクトを快適に編集するために、以下の拡張機能をインストールします。

## 必須拡張機能

| 拡張機能 | 提供元 | 用途 |
| :---- | :---- | :---- |
| **C/C++** | Microsoft | IntelliSense・コード補完・デバッグ |
| **CMake Tools** | Microsoft | CMakeプロジェクトの管理・ビルド |
| **CodeLLDB** | Vadim Chugunov | macOS上でのC++デバッグ |

VSCode の拡張機能タブ（`⇧⌘X`）から検索してインストールできます。

## VSCodeでプロジェクトを開く

`~/projects/MyGame`.vscode

---

# STEP 3: VSCode の設定ファイル（.vscode）

プロジェクトルートに `.vscode/settings.json` を作成すると、IntelliSense の精度が向上します。

```json
{
  "cmake.buildDirectory": "${workspaceFolder}/build_${buildType}",
  "C_Cpp.default.configurationProvider": "ms-vscode.cmake-tools",
  "editor.formatOnSave": true,
  "C_Cpp.clang_format_style": "Google"
}
```

また、デバッグ設定として `.vscode/launch.json` も用意しておくと便利です。

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "lldb",
      "request": "launch",
      "name": "Debug (macOS)",
      "program": "${workspaceFolder}/build/bin/MyGame",
      "args": [],
      "cwd": "${workspaceFolder}",
      "preLaunchTask": "CMake: build"
    }
  ]
}
```

---

# STEP 4: Claude Code を VSCode で使えるようにする

Axmol のプロジェクトが VSCode で開けたら、次は **Claude Code** を導入してAIとペアプログラミングを行いましょう。

## 前提条件

- Anthropic アカウント（Claude Pro・Max・Team・Enterprise いずれか、または API キー）  
- Node.js 18 以上がインストール済みであること

- nvmが便利ですので、「nvm install mac」のようなキーワードで検索、もしくはAIに聞いてみます

使用可能なNode.jsのバージョンを確認

```shell
nvm ls-remote
```

Node.js のインストール

```shell
nvm install v24.17.0
```

Node.js のバージョン確認：

```shell
nvm current
```

## 方法 A：VSCode 拡張機能（推奨）

最も手軽な方法です。

1. VSCode の拡張機能タブを開きます（`⇧⌘X`）  
2. 検索欄に `Claude Code` と入力  
3. **提供元が Anthropic** の拡張機能をインストール

インストール後、VSCode を再起動してください。アクティビティバーに **✱（スパーク）アイコン** が表示されれば成功です。

ℹ️ **ヒント**：スパーク（✱）アイコンは **ファイルを開いているときのみ** エディタ右上に表示されます。表示されない場合は、プロジェクト内のファイルを開いた状態で確認してください。

## 方法 B：CLI（コマンドライン）

ターミナルから直接 `claude` コマンドを使う方法です。拡張機能と併用も可能です。

```shell
npm install -g @anthropic-ai/claude-code
```

インストール後、VSCode の統合ターミナル（`` ⌃` ``）で以下を実行して認証します：

```shell
claude
```

初回起動時にブラウザが開き、Anthropic アカウントへのログイン（OAuth）が求められます。ログインが完了すると、ターミナル上で Claude Code が使用可能になります。

⚠️ **注意**：CLI を VSCode の統合ターミナルから起動する場合は、`code .` で VSCode を開いてから起動すると、環境変数（`ANTHROPIC_API_KEY` 等）が正しく引き継がれます。

## 拡張機能の基本操作

| 操作 | 方法 |
| :---- | :---- |
| パネルを開く | アクティビティバーの ✱ アイコンをクリック |
| ファイルを @メンション | プロンプト欄で `@ファイル名` と入力 |
| 複数行入力 | `Shift + Enter` で改行、`Enter` で送信 |
| コマンドメニュー | プロンプト欄で `/` を入力 |

Claude がファイルを編集すると、**インライン diff** がパネルに表示されます。内容を確認してから Accept / Reject で変更を取り込むことができます。

## Axmol プロジェクトでの活用例

プロジェクトを VSCode で開いた状態で Claude Code を使うと、以下のような作業をAIに任せることができます。

```
@HelloWorldScene.cpp このシーンにスコアラベルを追加して
```

```
CMakeLists.txt を読んで、新しい Scene ファイルを追加する手順を教えて
```

## チェックポイント機能

Claude がファイルを変更するたびに、変更前の状態が自動保存されます。誤った変更があった場合は、パネル上のメッセージにカーソルを合わせると表示される **巻き戻しボタン** から以下の操作が可能です。

| 操作 | 説明 |
| :---- | :---- |
| **Fork conversation from here** | 会話を分岐し、コードはそのまま残す |
| **Rewind code to here** | ファイルを指定時点に戻し、会話は残す |
| **Fork conversation and rewind code** | 会話もコードも指定時点に戻す |

Git と組み合わせて使うと、さらに安全に大きな変更を試みることができます。

---

# まとめ

Axmol Engine は CMake ベースのため、VSCode の CMake Tools 拡張機能と相性が良く、コーディング・ビルド・デバッグをすべて VSCode 上で完結できます。さらに Claude Code を導入すれば、AIとのペアプログラミング・バイブコーディングでシーンの実装やファイル構成の相談まで一気通貫で行えます。ぜひ試してみてください！

---

# 参考リンク

- [Axmol Engine 公式リポジトリ](https://github.com/axmolengine/axmol)  
- [DevSetup.md（公式セットアップガイド）](https://github.com/axmolengine/axmol/blob/dev/docs/DevSetup.md)  
- [Claude Code 公式ドキュメント（VSCode）](https://code.claude.com/docs/en/vs-code)  
- [Claude Code VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code)

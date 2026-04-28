---
id: "2026-04-26-claude-coworkが気づかないうちにcドライブを数十gb消費している話スナップショットと復元-01"
title: "Claude Coworkが気づかないうちにCドライブを数十GB消費している話～スナップショットと復元まで"
url: "https://qiita.com/Hiroto-Kozuki/items/f9dbe603028f42587989"
source: "qiita"
category: "cowork"
tags: ["AI-agent", "Gemini", "cowork", "qiita"]
date_published: "2026-04-26"
date_collected: "2026-04-28"
summary_by: "auto-rss"
query: ""
---

# Claude Coworkが気づかないうちにCドライブを数十GB消費している話～スナップショットと復元まで

## はじめに

Claude Desktop の Cowork 機能を使っていたら、気づかないうちに **Cドライブが数GB〜数十GB も圧迫されていた** という経験はありませんか？

本記事では、この問題の原因となる **VHDX仮想ディスク** の正体と、**Cドライブ以外に移動する方法**、さらに **PC移行時のデータ復元手順** までを解説します。

すべて実機検証済み（Windows 10 LTSC ⇔ Windows 11 25H2）で、ツールも GitHub で公開しています。

**▼ GitHub リポジトリ**
https://github.com/Hiroto-Kozuki/claude-cowork-migration

---

## 1. 発端 - Cドライブ容量不足の原因を追う

ある日、Cドライブの空き容量が急激に減っていることに気づきました。

WinDirStat で調べたところ、以下のフォルダが数十GBを消費していました：

```
C:\Users\<ユーザー名>\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Local\vm_bundles\
```

中身を見ると、**VHDX（仮想ハードディスク）ファイル** が大量に格納されていました。

これが **Claude Cowork のサンドボックス環境** だと判明。Cowork でタスクを実行するたびに、Linux ベースの仮想環境が稼働し、VHDX にデータが蓄積されていたのです。

---

## 2. VHDXファイルの正体

Claude Desktop は **Microsoft Store アプリ（MSIX パッケージ）** として配布されており、通常の Windows ソフトウェアとは異なる場所にデータを保存します。

Cowork 機能は、タスク実行時に **Virtual Machine Platform（Windows組み込みの軽量仮想化基盤）** を使用します。

このとき使用される仮想ディスクが VHDX ファイルで、以下のパッケージ専用フォルダに配置されます：

```
C:\Users\<ユーザー名>\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\...
```

### 問題点

- **ユーザープロファイル配下に配置される** → Cドライブを圧迫
- **多くのユーザーが気づかない** → 容量不足になって初めて発覚
- **公式ドキュメントに記載なし** → 保存場所の説明がない

---

## 3. 核心2フォルダの特定

調査の結果、Claude Cowork のデータは **以下の2フォルダだけ** で管理されていることが判明しました。

| フォルダ | 役割 |
|---------|------|
| `vm_bundles/` | VHDX仮想ディスク（ワークスペースファイル） |
| `local-agent-mode-sessions/` | セッション台帳（会話履歴との対応） |

### 重要な発見

この2フォルダを **同時刻にバックアップ・復元** すれば、以下がすべて復元できます：

- ✅ 過去の会話履歴
- ✅ プロジェクト（カスタム指示含む）
- ✅ 認証状態（ログイン維持）
- ✅ ユーザーメモリ
- ✅ ワークスペース内のファイル

**逆に、片方だけ復元すると会話エラーが発生します。**

---

## 4. 検証 - Win10⇔Win11移行テスト

以下の環境で、実際にPC間移行を検証しました。

| 項目 | 旧PC | 新PC |
|------|------|------|
| OS | Windows 10 LTSC | Windows 11 25H2 |
| 移行対象 | vm_bundles + sessions | vm_bundles + sessions |
| 結果 | ✅ 完全復元 | ✅ 完全復元 |

### 検証手順

**旧PCでバックアップ:**
```powershell
robocopy 'C:\ClaudeData\vm_bundles' 'D:\Backup\vm_bundles' /E /COPY:DAT /R:1 /W:1

robocopy "$env:USERPROFILE\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\local-agent-mode-sessions" `
         'D:\Backup\sessions' /E /COPY:DAT /R:1 /W:1
```

**新PCで復元:**

**手順1: Claude Desktop をインストール**

**手順2: Cowork でダミータスクを作成**
- Cowork タブで適当なタスク（例: 「Downloads フォルダを一覧表示」）を実行
- これにより VHDX が初期化されます

**手順3: Claude を完全終了**
- タスクトレイからも終了
- タスクマネージャーで `Claude.exe` が動いていないことを確認

**手順4: （任意）VHDX を外部ドライブに移動**
```batch
move_claude_vmbundles.bat
```

**手順5: PC を再起動**

**手順6: バックアップから復元**
```powershell
# vm_bundles を復元
robocopy 'D:\Backup\vm_bundles' 'C:\ClaudeData\vm_bundles' /MIR /COPY:DAT /R:1 /W:1

# sessions を復元
robocopy 'D:\Backup\sessions' "$env:USERPROFILE\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\local-agent-mode-sessions" /MIR /COPY:DAT /R:1 /W:1
```

**手順7: AppContainer 権限を修正（管理者 PowerShell）**
```powershell
icacls C:\ClaudeData /grant '*S-1-15-2-1:(OI)(CI)F' /T
```

**手順8: PC を再起動**

**手順9: Claude を起動**
- 同期に時間がかかる場合は、再度 PC 再起動

**結果:**
- 会話履歴が完全に復元
- プロジェクトもそのまま残存
- 認証状態も維持

---

## 5. 対処法 - VHDXを別ドライブに移動

### ツール公開

VHDX を Cドライブ以外に移動するスクリプトを GitHub で公開しました。

**▼ GitHub リポジトリ**
https://github.com/Hiroto-Kozuki/claude-cowork-migration

### 使い方

1. **Claude Desktop を完全終了**（タスクトレイからも）
2. **管理者権限で実行:**
   ```batch
   move_claude_vmbundles.bat
   ```
3. **Claude 起動**
   - うまく動かない場合は **PC再起動**（複数回必要な場合あり）

### 内部動作

スクリプトは以下を自動実行します：

1. `vm_bundles/` を `C:\ClaudeData\vm_bundles\` に移動
2. 元の場所に **ジャンクション（シンボリックリンク）** を作成
3. **AppContainer 権限** (`S-1-15-2-1`) を付与

これにより、Claude は何も変わらず動作しますが、実体は別ドライブに配置されます。

---

## 6. 注意事項

### システム要件

- **Windows 10/11 Pro/Enterprise/Education**
  - **Windows Home は非対応**（Hyper-V が不完全）
- **Virtual Machine Platform 有効化が必須:**
  ```powershell
  Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform
  ```

### バックアップ時の注意

- **2フォルダは必ず同時刻にバックアップ**
- 片方だけ古いバージョンに戻すと整合性エラー

### よくあるエラー

**「Plan9 mount failed」エラー:**
- Windows Home を使用している → Pro/Enterprise に要アップグレード

**Cowork が動かない:**
- PC再起動（ジャンクション同期に時間がかかる場合あり）
- 2〜3回再起動が必要なケースも確認済み

---

## 7. 今後の展望

### Anthropic へのフィードバック

以下の内容を Anthropic に提案予定です：

1. **公式ドキュメントへの記載**
   - VHDX 保存場所の明示
   - ディスク容量の警告

2. **機能改善の提案**
   - アプリ内での保存先ドライブ選択機能
   - 公式のデータ管理ツール提供

### Web上の情報不足

本記事執筆時点（2026年4月）で、Claude Cowork のデータ管理に関する体系的な情報は **Web上にほぼ存在しません**（Gemini 検索でも断片的な情報のみ）。

この記事が、同じ問題に直面している方の助けになれば幸いです。

---

## まとめ

- Claude Cowork は **VHDX仮想ディスク** を Cドライブに保存している
- **核心2フォルダ** (`vm_bundles` + `sessions`) だけで全データ管理可能
- **VHDX外出しツール** を GitHub で公開中
- **PC移行も可能**（Win10⇔Win11 検証済み）

**GitHub リポジトリ:**
https://github.com/Hiroto-Kozuki/claude-cowork-migration

---

## 参考情報

- [Claude Cowork 公式ドキュメント](https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork)
- [Windows Virtual Machine Platform について](https://learn.microsoft.com/ja-jp/windows/wsl/install)

---

この記事が役に立ったら、GitHub にスターをいただけると嬉しいです⭐

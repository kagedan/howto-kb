---
id: "2026-03-30-実体験claude-coworkwindowsセットアップ時に仮想化が有効にできなかった話とbios-01"
title: "【実体験】Claude Cowork（Windows）セットアップ時に仮想化が有効にできなかった話とBIOS設定での解決方法"
url: "https://qiita.com/kan2530/items/fbac7254b3375a9fe690"
source: "qiita"
category: "cowork"
tags: ["cowork", "qiita"]
date_published: "2026-03-30"
date_collected: "2026-03-30"
summary_by: "auto-rss"
---

## はじめに

Claude Coworkは2026年2月よりWindowsでも利用可能になり、試してみた方も多いのではないでしょうか。

私がセットアップを進めたところ、**仮想化が有効にならず**Coworkが起動できないという壁に当たりました。  
本記事では仮想化を有効にするため実際に行った手順と方法を共有します。

---

## 環境

| 項目 | 詳細 |
| --- | --- |
| PC | Minisforum 790 Pro（ミニPC） |
| OS | Windows 11 |
| 対象アプリ | Claude Desktop（Cowork機能） |
| Claudeプラン | Pro / Max / Team / Enterprise いずれか（有料プラン必須） |

**Claude Coworkとは？**  
Claude Desktopアプリ内の機能で、ローカルファイルへのアクセスや複数ステップのタスクを自律実行できます。  
実行には**仮想マシン（VM）環境**が使われるため、PCの仮想化機能が有効になっている必要があります。

---

## 解決までの手順

### ① Windowsの機能から仮想化関連を有効化（まずここから）

1. スタートメニューを開き、`Windowsの機能の有効化または無効化` を検索して開く
2. 以下の項目にチェックを入れてOKをクリック
   * ✅ **Windows ハイパーバイザープラットフォーム**
   * ✅ **Hyper-V**
3. 再起動を促されたら再起動する

この操作だけでは仮想化が有効にならないことがあります。  
BIOS側の設定がオフになっている可能性があるので、そのような方は②をご参照ください。  
私も仮想化が有効にならなかったので②のBIOS設定を行いました。

---

### ② BIOSからSVM Mode（仮想化）を有効化

Minisforum 790 ProはAMD製CPUを搭載しており、AMD系はBIOS上で **SVM Mode**（Secure Virtual Machine）を有効にする必要があります。

#### BIOS起動方法

1. PCの電源を入れる（または再起動する）
2. 起動直後にロゴが表示されたら `F7` キーを連打してBIOSを起動

#### BIOS内での操作

```
Advanced
  └─ CPU Configuration
       └─ SVM Mode : Disabled → Enabled に変更
```

1. BIOSメニューから `Advanced` を選択
2. `CPU Configuration` を選択
3. `SVM Mode` の項目を `Disabled` → **`Enabled`** に変更
4. `Save & Exit` → `Save Changes and Reset` を選択して再起動

---

## 結果

①→②の順で実施したところ、Windowsの仮想化が有効になり、Claude Coworkを利用することができるようになりました。

---

## 補足・注意点

* **①のWindows設定が必要かどうかは未検証**  
  BIOS設定（②）だけで解決するかは試していません。ただし、HyperVやWindowsハイパーバイザープラットフォームをONにしておく方が安定する印象があるため、両方実施するのが無難です。
* **IntelのCPUの場合**  
  SVM ModeはAMDの場合に表示される項目名です。Intelの場合には `Intel Virtualization Technology`や`VT-x` という名称でBIOSに表示されるようです。
* **BIOSの起動キーはPCによって異なります**  
  Minisforum 790 Proは `F7` ですが、他のPCでは `Delete` / `F2` / `F10` / `Esc` などが使われることが多いのでご注意ください。

---

## まとめ

| ステップ | 操作内容 | 効果 |
| --- | --- | --- |
| ① | Windowsの機能 → HyperV・ハイパーバイザープラットフォームを有効化 | OS側の仮想化準備 |
| ② | BIOS → Advanced > CPU Configuration > SVM Mode を Enabled に変更 | **ハードウェアレベルの仮想化を有効化（本質的な解決策）** |

Claude Coworkはセットアップさえ済んでしまえば、複雑なマルチステップ処理をローカルファイルと連携しながら実行できる非常に強力な機能です。  
**「仮想化が有効にならない」「Coworkが起動しない」** でハマっている方はぜひこの手順を試してみてください。

CoworkはPro/Max/Team/Enterpriseプランで利用可能です（有料プラン必須）。  
詳細は[公式ヘルプセンター](https://support.claude.com/en/articles/13345190-get-started-with-cowork)を参照してください。

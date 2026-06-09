# urllib3バージョン不一致警告の対処 と requirements.txt 新規作成

日時: 2026-06-09 11:33 (JST)

## 背景・目的

- 毎朝のルーティン(howto-kb-update)で「urllib3バージョン不一致の警告が出るが処理は正常完了（動作に影響なし）」と報告され続けていた。
- 「動作に影響なし」は正しいが、原因を確認して対処してほしいとの依頼。

## 調査で判明したこと（原因）

- 警告の実体: `RequestsDependencyWarning: urllib3 (2.6.3) or chardet (7.4.3)/charset_normalizer (3.4.4) doesn't match a supported version!`
- 真の原因は **requests 2.32.5 の互換性チェック表が chardet 7 系に未対応**だったこと。
  - requests の `check_compatibility` が chardet を先に照合し、表の上限が `chardet < 6.0.0` だったため、インストール済みの chardet 7.4.3 がはみ出して警告。
  - urllib3 2.6.3 は実際にはチェックを通過している（メッセージが候補名を全部並べているだけ）。
  - 実際の文字コード判定は charset_normalizer 3.4.4（範囲内）が担当するため動作に影響なし＝報告は正しかった。
- chardet は readability-lxml（全文抽出）が連れてくる依存。Supabaseは無関係。
- 警告が出るのは routine 内で requests を読み込む箇所: crawl_rss.py（readability経由）と sync_supabase.py。

## 完了ステップ

- [x] 警告を再現し、requests の check_compatibility ソースを読んで原因を特定
- [x] 新しい requests 2.34.2 を確認 → chardet 上限が `< 8.0.0` に引き上げ済み（公式が対応）
- [x] requests 2.34.2 の依存要求を確認 → 手持ちの urllib3/charset_normalizer/idna/certifi/chardet/Python すべて条件クリア（他部品を巻き込まない）
- [x] `python -m pip install --upgrade "requests==2.34.2"` を実行（requests 1個だけ更新、他は据え置き）
- [x] `-W error` で requests・readability 経由とも読み込み、警告ゼロを検証
- [x] requirements.txt を新規作成（scripts が使う4部品 + 理由コメント、requests は >=2.34.2 で下限固定）
- [x] `python -m pip install -r requirements.txt --dry-run` で書式・解決を検証（全 already satisfied）
- [x] requirements.txt を commit（ee82142）& push（origin/main へ反映済み）

## 次のステップ

- なし（依頼は完了）。

## 関連ファイル

- 新規: C:\Users\KazuhisaMiyake\projects\howto-kb\requirements.txt
- 参照: C:\Users\KazuhisaMiyake\projects\howto-kb\scripts\sync_supabase.py（import requests）
- 参照: C:\Users\KazuhisaMiyake\projects\howto-kb\scripts\crawl_rss.py（readability経由でrequests）

## 備考・気づき

- 「無害なバージョン不一致警告」は、原因ライブラリ(chardet)を下げるより、チェックを出している側(requests)を新しくする方が根本的かつ低リスクなことが多い。requests 2.34 で chardet 上限が <8 に拡大されていた。
- 共通Python環境（仮想環境なし）なので pip freeze は他用途のパッケージまで混ざる。requirements.txt は直接使う部品だけ手書きにした。
- この職場PCの Python は C:\Users\KazuhisaMiyake\AppData\Local\Programs\Python\Python314（システム共通）。

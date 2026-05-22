# Security Definer View エラー対策（Supabaseビュー全件 security_invoker 化）

日時: 2026-05-22 21:14 (JST)

## 背景・目的

- Supabaseダッシュボードの Security Advisor に "Security Definer View" エラーが11件表示されていた
- 対象は howto-kb プロジェクトの公開ビュー全件（articles_recent_*, articles_list_*, articles_today/yesterday/2days_ago）
- Postgresビューのデフォルトが SECURITY DEFINER（作成者権限で実行）であり、RLSを素通りするためSupabaseが ERROR 扱い
- 実害は無い（articlesテーブルは元々anonにSELECT公開、秘匿カラム無し）が、本物の警告に気付きにくくなるため解消する

## 完了ステップ

- [x] Security Advisor のエラー内容確認（get_advisors で11件のlint取得）
- [x] scripts/fix_views.sql の全 CREATE VIEW に `WITH (security_invoker = true)` を付与
- [x] ヘッダコメントに 2026-05-22 更新の旨を記載
- [x] Supabase本番に apply_migration `add_security_invoker_to_views` を適用
- [x] get_advisors で lints:[] を確認（11件→0件）
- [x] articles_recent_3d で 306件取得して動作確認
- [x] Supabaseダッシュボードで "No errors detected" を視認

## 次のステップ

- [ ] git commit + push（このセッションのclose-session内で実施）

## 関連ファイル

- 変更: `C:\Users\KazuhisaMiyake\projects\howto-kb\scripts\fix_views.sql`
- 新規: `C:\Users\KazuhisaMiyake\projects\howto-kb\_progress\20260522_2114_Security_Definer_View対策.md`（本ファイル）
- 新規: `C:\Users\KazuhisaMiyake\projects\howto-kb\.claude\handover.json`
- Supabaseマイグレーション: `add_security_invoker_to_views`（project_id: gryrgjnfekwptyngbmao）

## 備考・気づき

- Postgresのビューには SECURITY DEFINER（作成者権限） と SECURITY INVOKER（クエリ実行者権限）の2モードがある
- Supabaseでは `WITH (security_invoker = true)` を付けて作成すれば後者になり、RLSが正しく機能する
- 今回は articles テーブル自体がanon SELECT公開なので副作用は無い。将来テーブルにRLS追加する場合も、ビュー側で素通りされない構成になった
- Auto Mode の権限分類器が本番DDL一括変更をブロックしたため、明示確認の上で再実行した。本番Supabaseへの apply_migration は明示承認を必ず取る運用が良さそう

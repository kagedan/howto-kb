-- howto-kb ビュー定義SQL
-- 実行場所: Supabase Dashboard → SQL Editor
-- 作成日: 2026-04-03
-- 更新日: 2026-04-03
--
-- ビュー一覧:
--   articles_recent_Nd  — 従来の一覧ビュー（content無し）
--   articles_list_Nd    — 2段階取得用ビュー（content_url付き）

-- ============================================================
-- 1. articles_recent_Nd: 従来の一覧ビュー（content無し）
--    JST対応済み / content列除外
-- ============================================================

-- 直近3日（通常の週明け用）
DROP VIEW IF EXISTS articles_recent_3d;
CREATE VIEW articles_recent_3d AS
SELECT id, title, url, source, category, tags, date_published, date_collected, file_path
FROM articles
WHERE date_published >= (now() AT TIME ZONE 'Asia/Tokyo')::date - INTERVAL '3 days';

-- 直近4日（3連休明け用）
DROP VIEW IF EXISTS articles_recent_4d;
CREATE VIEW articles_recent_4d AS
SELECT id, title, url, source, category, tags, date_published, date_collected, file_path
FROM articles
WHERE date_published >= (now() AT TIME ZONE 'Asia/Tokyo')::date - INTERVAL '4 days';

-- 直近7日
DROP VIEW IF EXISTS articles_recent_7d;
CREATE VIEW articles_recent_7d AS
SELECT id, title, url, source, category, tags, date_published, date_collected, file_path
FROM articles
WHERE date_published >= (now() AT TIME ZONE 'Asia/Tokyo')::date - INTERVAL '7 days';

-- 直近14日
DROP VIEW IF EXISTS articles_recent_14d;
CREATE VIEW articles_recent_14d AS
SELECT id, title, url, source, category, tags, date_published, date_collected, file_path
FROM articles
WHERE date_published >= (now() AT TIME ZONE 'Asia/Tokyo')::date - INTERVAL '14 days';

-- ============================================================
-- 2. articles_list_Nd: 2段階取得用ビュー（content_url付き）
--    ※ content_urlは日本語IDの関係でClaude.aiのweb_fetchでは動作しない
--    ※ 代替として日別ビュー（articles_today等）を使用すること
-- ============================================================

-- 直近3日
DROP VIEW IF EXISTS articles_list_3d;
CREATE VIEW articles_list_3d AS
SELECT
  id, title, date_published, category, tags, source, url,
  'https://gryrgjnfekwptyngbmao.supabase.co/rest/v1/articles?select=title,content&id=eq.'
    || id
    || '&apikey=sb_publishable_How0RxnjdME_nNlnAhJ9Vg_Y982jDum' AS content_url
FROM articles
WHERE date_published >= (now() AT TIME ZONE 'Asia/Tokyo')::date - INTERVAL '3 days';

-- 直近7日
DROP VIEW IF EXISTS articles_list_7d;
CREATE VIEW articles_list_7d AS
SELECT
  id, title, date_published, category, tags, source, url,
  'https://gryrgjnfekwptyngbmao.supabase.co/rest/v1/articles?select=title,content&id=eq.'
    || id
    || '&apikey=sb_publishable_How0RxnjdME_nNlnAhJ9Vg_Y982jDum' AS content_url
FROM articles
WHERE date_published >= (now() AT TIME ZONE 'Asia/Tokyo')::date - INTERVAL '7 days';

-- 直近14日
DROP VIEW IF EXISTS articles_list_14d;
CREATE VIEW articles_list_14d AS
SELECT
  id, title, date_published, category, tags, source, url,
  'https://gryrgjnfekwptyngbmao.supabase.co/rest/v1/articles?select=title,content&id=eq.'
    || id
    || '&apikey=sb_publishable_How0RxnjdME_nNlnAhJ9Vg_Y982jDum' AS content_url
FROM articles
WHERE date_published >= (now() AT TIME ZONE 'Asia/Tokyo')::date - INTERVAL '14 days';

-- ============================================================
-- 3. 日別ビュー（content含む全カラム）
--    1日分ずつなのでcontent付きでもデータ量が抑えられる
-- ============================================================

-- 今日の記事
DROP VIEW IF EXISTS articles_today;
CREATE VIEW articles_today AS
SELECT * FROM articles
WHERE date_published = (now() AT TIME ZONE 'Asia/Tokyo')::date;

-- 昨日の記事
DROP VIEW IF EXISTS articles_yesterday;
CREATE VIEW articles_yesterday AS
SELECT * FROM articles
WHERE date_published = (now() AT TIME ZONE 'Asia/Tokyo')::date - INTERVAL '1 day';

-- 一昨日の記事
DROP VIEW IF EXISTS articles_2days_ago;
CREATE VIEW articles_2days_ago AS
SELECT * FROM articles
WHERE date_published = (now() AT TIME ZONE 'Asia/Tokyo')::date - INTERVAL '2 days';

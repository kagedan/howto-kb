---
id: "2026-06-09-youtubeチャプター10秒ルール対応と設定に辿り着けないcss罠streamlitアプリ実装デバ-01"
title: "YouTubeチャプター10秒ルール対応と「設定に辿り着けない」CSS罠：Streamlitアプリ実装デバッグ記録"
url: "https://qiita.com/sorabcjanne1/items/736c494d32700141e781"
source: "qiita"
category: "ai-workflow"
tags: ["API", "Python", "qiita"]
date_published: "2026-06-09"
date_collected: "2026-06-10"
summary_by: "auto-rss"
query: ""
---

## はじめに

自動動画生成アプリ（Streamlit製）の実運用で見つかった2つのバグを修正した記録です。どちらも「実際にアップロードしてみて初めて気づく」系の問題で、コードを読むだけでは発見しにくいタイプでした。

- **設定ページに辿り着けない**（CSSがナビを丸ごと隠していた）
- **YouTubeチャプターが機能しない**（10秒ルール違反＋タイムライン時刻のズレ）

---

## やったこと

### バグ1：設定ページへの到達手段がゼロだった

APIキー入力フォームを設定ページに実装したのに、ユーザーから「設定場所がない」と報告が来ました。

`st.navigation()` を使ってページ登録はしていたのに、なぜ？　調べると `brand.py` の CSS にこんなルールが残っていました。

```css
/* brand.py（修正前） */
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
    display: none;
}
```

`st.navigation()` が描画するナビは `stSidebarNav` 内に出力されます。それをまるごと `display: none` にしていたため、ホーム・発掘・検証・制作・**設定** のリンクが全部消えていました。

これは旧UI（カスタムボタンナビ）向けに書いたCSSをそのまま流用してしまったのが原因です。`sidebar_header()` はロゴしか描かず、カスタムナビで置き換える処理も無かったため、サイドバーはロゴだけの状態になっていました。

**修正は1行：**

```css
/* brand.py（修正後） */
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
    display: block;
}
```

この種のCSS上書きは、Streamlitのバージョンアップやコンポーネント変更時に静かに壊れるので注意が必要です（個人の感想）。

---

### バグ2：YouTubeチャプターが有効にならない

生成された説明欄に以下のようなチャプターが含まれていました。

```
0:00 現象
0:06 原因
0:26 解決
0:30 確認
```

YouTubeでチャプターを有効にするには3つの条件を満たす必要があります。

| 条件 | 内容 |
|------|------|
| ① | 最初のチャプターが `0:00` から始まる |
| ② | チャプターが3個以上ある |
| ③ | **各チャプターが10秒以上** |

`0:00→0:06` は6秒、`0:30→確認` は動画末尾まで4秒弱。③を複数箇所で違反しており、YouTube側ではチャプターが無効化されて説明欄に文字が出るだけの状態でした。

さらに調べると、もう1つの問題が発覚しました。チャプター時刻が**推定尺ベース**で算出されており、実際の動画タイムラインとズレていたのです。動画冒頭に「掴み3.5秒＋見出しカード2秒」が入るため、最初のセクション開始は実際には5.5秒あたりからになります。`render_spec.chapter_markers()` という実尺から算出する関数がすでに存在していましたが、どこからも呼ばれていませんでした。

**修正方針：**

1. 各セクションに `min_section_sec`（デフォルト10秒）を設ける
2. ナレーションが短いセクションは、最後のシーン（テロップ等）をホールドして最低尺に到達させる
3. チャプター時刻は実尺から算出し直す
4. それでも条件を満たせない場合は、説明欄のチャプター節を丸ごと出さない（機能しないチャプターを載せない）

```python
# config.toml に追記
[error_video]
min_section_sec = 10  # YouTubeチャプター10秒ルール対応＋ペース改善
```

```python
# render_spec.py（概略）
def _enforce_min_section(scenes: list, min_sec: float) -> list:
    """各セクションの尺が min_sec に満たない場合、末尾シーンをホールドして補填"""
    # ナレーション終了後に余白を追加し、映像の同期は崩さない
    ...

def youtube_chapters(section_timecodes: list) -> list:
    """実尺タイムコードからYouTubeチャプターリストを生成。
    条件未達（10秒未満・3個未満・0:00未開始）の場合は空リストを返す"""
    ...
```

```python
# error_script.py（build_description の変更箇所）
def build_description(meta, chapters: list | None = None) -> str:
    # chapters が空リストの場合はチャプター節を出力しない（フォールバック）
    if chapters:
        lines += _format_chapters(chapters)
    ...
```

---

## ハマったポイント

**「バグ1（説明欄の literal `\n`）」は実際には存在しなかった**

指示書には「説明欄に `\n`（2文字）が残る」とあったのでコードを調べましたが、`build_description` は最初から `"\n".join(lines)` で本物の改行を使っていました。

実際に生成済みの `meta.json` をパースして確認しても2文字の `\n` は無し。おそらく raw の `meta.json` ファイルをテキストエディタで直接開くと、JSONの仕様上 改行文字が `\n` と表示されるため、それをコピーしてしまった可能性が高いです。

この調査があったので「テストだけ追加して回帰防止」という判断ができました。コードを直す前に実物を確認するのは大事です。

```python
# テスト（回帰防止用）
def test_description_no_literal_backslash_n():
    desc = build_description(sample_meta, chapters=[...])
    assert "\\n" not in desc
    lines = desc.split("\n")
    chapter_lines = [l for l in lines if re.match(r"\d+:\d+", l)]
    assert len(chapter_lines) >= 3
```

---

## 学び

1. **CSSで標準UIを隠す場合、代替実装を必ずセットで作る**。`display: none` だけ残って置き換え処理が消えると、ページへの到達手段がゼロになります。Streamlitではバージョン間で `data-testid` が変わることもあるため、定期的な確認が必要です。

2. **「実装済み」と「到達可能」は別物**。コードが正しく動いていても、ナビやボタンから辿り着けなければユーザーには存在しないも同然です。実装後は実際にユーザーの動線をたどるのが最も確実な検証になります。

3. **YouTubeのチャプター条件は意外と厳しい**。3個以上・10秒以上・0:00開始の3条件を全部満たさないと説明欄に文字が出るだけで機能しません。自動生成チャプターを使う場合は検証ロジックを組み込んでおくと安心です。

4. **推定尺と実尺のズレ**。TTS音声生成後の実尺でチャプターを再計算しないと、冒頭の固定コンテンツ（OP映像など）の分だけ全チャプターがズレます。関数は作っても呼び出さなければ意味がない、という当たり前の教訓でもあります。

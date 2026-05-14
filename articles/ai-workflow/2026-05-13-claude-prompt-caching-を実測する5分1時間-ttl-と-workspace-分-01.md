---
id: "2026-05-13-claude-prompt-caching-を実測する5分1時間-ttl-と-workspace-分-01"
title: "Claude prompt caching を実測する——5分・1時間 TTL と workspace 分離仕様で測るキャッシュヒット率"
url: "https://qiita.com/TakatoYamada/items/7fefb65cebbfca1454da"
source: "qiita"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "Python", "qiita"]
date_published: "2026-05-13"
date_collected: "2026-05-14"
summary_by: "auto-rss"
query: ""
---

Anthropic の prompt caching は 2026年に入って2つ大きな変更がありました。キャッシュスコープが組織単位からワークスペース単位に変わり、TTL も従来の5分に加えて1時間が選べるようになっています。本記事では `anthropic-sdk-python` を使った実測スクリプトと、運用で踏みやすいハマりどころを整理します。

## 何が変わったか

| 項目 | 変更前 | 変更後 (2026-02〜) |
|---|---|---|
| キャッシュスコープ | 組織単位 | **ワークスペース単位** |
| TTL | 5分のみ | **5分 / 1時間 の選択制** |
| キャッシュ読込料金 | 入力トークンの0.1倍 | 据え置き |

スコープが狭まったため、複数ワークスペースで同じプロンプトを使うチームは、それぞれにキャッシュが作られる点に注意が必要です。1時間TTL は `anthropic-beta: extended-cache-ttl-2025-04-11` ヘッダ付きで利用可能、SDK は自動付与してくれます。

## 検証コード（最小構成）

`pip install anthropic` でインストールした SDK を使い、同一のシステムプロンプトで連続2回叩いて、レスポンスの `usage` から caching の効きを確認します。

```python
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# cache_control は最小トークン数の要件あり（Sonnet は約1024トークン以上）
SYSTEM = [
    {
        "type": "text",
        "text": "あなたは社内ナレッジを参照する技術アドバイザーです。" * 200,
        "cache_control": {"type": "ephemeral", "ttl": "1h"},
    }
]

def ask(question: str):
    return client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=200,
        system=SYSTEM,
        messages=[{"role": "user", "content": question}],
    )

r1 = ask("社内ITポリシーの基本3項目を教えて")   # 1回目: cache write
r2 = ask("セキュリティ運用の確認ポイントは？")   # 2回目: cache read
```

## 出力の見方

レスポンスの `usage` には caching 専用の数値が3つ入ります。

```python
def show(label, r):
    u = r.usage
    print(f"{label}: input={u.input_tokens}, "
          f"cache_creation={u.cache_creation_input_tokens}, "
          f"cache_read={u.cache_read_input_tokens}")

show("write", r1)
show("read",  r2)
```

- `input_tokens`: キャッシュ対象外の通常入力（ユーザー質問など）
- `cache_creation_input_tokens`: キャッシュを「書いた」トークン数。1回目だけ正の値
- `cache_read_input_tokens`: キャッシュから「読んだ」トークン数。2回目以降に正の値

料金計算は公式通り、`cache_read` 分は通常入力料金の0.1倍で課金されます。長いシステムプロンプト（数千〜1万トークン）を繰り返し使う構成なら、2回目以降の入力コストが大きく下がる計算になります。

## 5分 vs 1時間 の使い分け

```python
# 短時間バースト用（既定）
{"cache_control": {"type": "ephemeral", "ttl": "5m"}}

# 長時間の対話セッション用
{"cache_control": {"type": "ephemeral", "ttl": "1h"}}
```

5分は対話間隔が短い RAG 系、1時間は断続的に長く回るエージェント系に向きます。1時間TTL は **キャッシュ書き込み料金が5分版より高く設定** されているため、再ヒットが見込めない用途で多用するとむしろコストが増えます。実運用ではメトリクスを取って判断するのが安全です。

## ハマりどころ

1. **ワークスペース境界**: 別ワークスペースに同じプロンプトを送ってもキャッシュは共有されません。ステージングと本番でワークスペースを分けると、本番で初回コストを払い直すことになります
2. **最小トークン要件**: Sonnet 系で約1024トークン未満のブロックには `cache_control` が効きません。短いプロンプトには無意味
3. **キャッシュ無効化の早さ**: システムプロンプトを1文字でも変更すると `cache_creation` が再発生します。動的な日時の埋め込みは避け、システムプロンプトは安定化させる
4. **TTL カウンタ**: TTL は最後のヒットから再カウントされません。**書き込み時刻から固定で5分/1時間** で消える
5. **計測時の注意**: 1回目のレスポンスでは `cache_creation_input_tokens` が正の値、2回目で `cache_read_input_tokens` が正の値になることを必ず両方確認する。片方だけだと正常動作と判断できない

## まとめ

- 2026年からキャッシュは **ワークスペース単位**。組織内の使い分け設計を再評価する価値がある
- TTL 選択は **再ヒット見込みの長さ** で決める。短時間連投なら5分、断続的に長く使うなら1時間
- 計測は `usage.cache_creation_input_tokens` と `cache_read_input_tokens` の2つだけ追えば十分

### 参考リンク

- [Anthropic 公式: Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [anthropic-sdk-python リリースノート](https://github.com/anthropics/anthropic-sdk-python/blob/main/CHANGELOG.md)

---

**[itdoor](https://itdoor.jp)** | AI/業務自動化の受託開発・コンサルティングを提供。

---

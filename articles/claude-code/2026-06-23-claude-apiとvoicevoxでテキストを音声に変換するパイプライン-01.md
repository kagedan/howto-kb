---
id: "2026-06-23-claude-apiとvoicevoxでテキストを音声に変換するパイプライン-01"
title: "Claude APIとVOICEVOXでテキストを音声に変換するパイプライン"
url: "https://zenn.dev/yamada_ai_dev/articles/claude-voicevox-tts-pipeline"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "zenn"]
date_published: "2026-06-23"
date_collected: "2026-06-25"
summary_by: "auto-rss"
query: ""
---

# Claude APIとVOICEVOXでテキストを音声に変換するパイプライン

## やること

1. Anthropic APIでテキストを整理・加工する
2. VOICEVOXのローカルAPIに渡して音声を生成する

議事録・ブログ記事・通知テキストなど、「文字で持っているコンテンツを音声にしたい」場面で使える。

---

## VOICEVOXとは

[VOICEVOX](https://voicevox.hiroshiba.jp/)は無料・商用利用可のローカル音声合成ソフトだ。

* ローカルで動く（テキストをクラウドに送らない）
* REST APIで操作できる（ポート50021）
* 複数のキャラクターボイスを選べる
* 日本語のイントネーションが自然

インストール後にVOICEVOXを起動するとREST APIサーバーが`http://localhost:50021`で立ち上がる。

---

## パイプラインの全体像

Claudeが担うのは「音声に変換しやすい形にテキストを整える」部分だ。VOICEVOXへのリクエストは2ステップになっている。

長い一文を分割する、記号を読み上げ形式に変える、数字を日本語読みに変換する、といった処理を自然言語で指示できる。

---

## 実装

### 前提

```
pip install anthropic requests
```

VOICEVOXを起動しておく（GUIまたはバックグラウンド起動）。

### コード

```
import anthropic
import requests
import json

VOICEVOX_URL = "http://localhost:50021"
SPEAKER_ID = 3  # ずんだもん（ノーマル）。/speakers APIで一覧を確認できる

def preprocess_text_with_claude(raw_text: str) -> str:
    """Claude APIでテキストを音声読み上げ向けに加工する"""
    client = anthropic.Anthropic()
    
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""以下のテキストを音声読み上げ向けに変換してください。

変換ルール:
- 記号（「」『』など）は自然に読める形に変換する
- URLは「URLは省略します」と置き換える
- 英数字の略語は読み方を補完する（例: API → エーピーアイ）
- 一文が長すぎる場合は自然な位置で分割する
- マークダウン記法（##、** 等）は除去する

テキスト:
{raw_text}

変換後のテキストのみを出力すること。説明不要。"""
        }]
    )
    
    return response.content[0].text.strip()

def text_to_speech(text: str, output_path: str = "output.wav") -> str:
    """VOICEVOXでテキストを音声に変換してファイルに保存する"""
    
    # ステップ1: audio_queryで音声パラメーターを生成
    query_response = requests.post(
        f"{VOICEVOX_URL}/audio_query",
        params={"text": text, "speaker": SPEAKER_ID}
    )
    query_response.raise_for_status()
    audio_query = query_response.json()
    
    # 話速・音量などのパラメーター調整（任意）
    audio_query["speedScale"] = 1.1   # 少し速め
    audio_query["volumeScale"] = 1.0
    
    # ステップ2: synthesisで音声を生成
    synthesis_response = requests.post(
        f"{VOICEVOX_URL}/synthesis",
        params={"speaker": SPEAKER_ID},
        headers={"Content-Type": "application/json"},
        data=json.dumps(audio_query)
    )
    synthesis_response.raise_for_status()
    
    # WAVファイルに保存
    with open(output_path, "wb") as f:
        f.write(synthesis_response.content)
    
    return output_path

def run_pipeline(raw_text: str, output_path: str = "output.wav") -> str:
    """メイン処理: テキスト加工 → 音声生成"""
    
    print("Claude APIでテキストを加工中...")
    processed = preprocess_text_with_claude(raw_text)
    print(f"加工後:\n{processed}\n")
    
    print("VOICEVOXで音声生成中...")
    result = text_to_speech(processed, output_path)
    print(f"保存完了: {result}")
    
    return result

if __name__ == "__main__":
    sample = """
    ## 本日のミーティング議事録
    
    参加者: 田中、鈴木、Claude API担当
    
    議題1: 新機能のリリーススケジュールについて
    - v2.0.0は2026年6月中旬を予定
    - APIの後方互換性はv1.x系まで保証する
    - テスト環境のURLは https://staging.example.com/api/v2 で確認できる
    
    次回: 来週火曜日 14:00〜
    """
    
    run_pipeline(sample, "meeting_summary.wav")
```

---

## VOICEVOXのスピーカーIDを確認する

```
import requests

response = requests.get("http://localhost:50021/speakers")
speakers = response.json()

for speaker in speakers:
    name = speaker["name"]
    for style in speaker["styles"]:
        print(f"ID: {style['id']:3d}  {name} - {style['name']}")
```

実行するとインストール済みのボイス一覧が出る。好みのボイスのIDをSPEAKER\_IDに設定する。

---

## Claudeが担う「音声向けテキスト整形」の例

| 入力 | Claudeの変換後 |
| --- | --- |
| `https://zenn.dev/yamada-ai-dev/articles/xxx` | URLは省略します |
| `## 3. まとめ` | まとめ |
| `Claude Code v1.2.0がリリース` | クロードコード バージョン1.2.0がリリース |
| `APIキーをos.environ.getで取得し、anthropic.Anthropic()に渡す` | APIキーを環境変数から取得してAnthropicクライアントに渡す |

人間がテキストを整形するより、Claudeに「音声で読み上げたとき自然に聞こえるように変換して」と頼むほうが速く、品質も高い。

---

## 応用例

**議事録の自動音声化**

毎週のMTG後にClaudeで議事録を整形→VOICEVOXで音声化→Slack/Discordに投稿。

**ブログ記事のポッドキャスト化**

Zennやnoteの記事をpodcast形式で配信したいとき。マークダウン除去・URL置換・長文分割をClaudeに任せてからVOICEVOXで変換する。

**通知のTTS読み上げ**

監視ツールのアラートをClaude APIでサマリー化して音声で通知する。

---

## まとめ

* VOICEVOXは`/audio_query` + `/synthesis`の2ステップで音声ファイルを生成できる
* Claude APIはテキストの前処理（記号除去・読み方補完・長文分割）を担う
* Haiku（`claude-haiku-4-5-20251001`）を使えば前処理コストは1回0.1〜0.3円
* パイプラインはシンプルで、ローカル完結（テキストをクラウドに送らない）

---

Claude APIとVOICEVOXのような外部ツール連携パイプラインを、hooks・agents・skillsに整理してClaudeに自律実行させる設計思想は有料Book「Claude Code ハーネスエンジニアリング 実践Playbook」で扱っている。

→ [Claude Code ハーネスエンジニアリング 実践Playbook（Zenn）](https://zenn.dev/yamada-ai-dev/books/claude-harness-playbook)

---

感想や「このケースはどうする？」みたいな質問は、コメントに気軽に書いてもらえると嬉しいです。いいねも励みになります。

## 筆者コメント

## 参考資料

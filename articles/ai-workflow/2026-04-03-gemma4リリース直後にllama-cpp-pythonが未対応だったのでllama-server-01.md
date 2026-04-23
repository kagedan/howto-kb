---
id: "2026-04-03-gemma4リリース直後にllama-cpp-pythonが未対応だったのでllama-server-01"
title: "Gemma4リリース直後にllama-cpp-pythonが未対応だったので、llama-server.exeを直叩きした話"
url: "https://zenn.dev/ena_dri/articles/340edb0d490bfa"
source: "zenn"
category: "ai-workflow"
tags: ["Gemini", "Python", "zenn"]
date_published: "2026-04-03"
date_collected: "2026-04-04"
summary_by: "auto-rss"
---

## はじめに

Gemma 4がリリースされた直後、「ローカルで動かしてみたい」と思って `llama-cpp-python` を確認したら**未対応だった**。そらそう。

待つのもアリだが、せっかくなのでllama.cpp本家のバイナリ（`llama-server.exe`）を直接叩く設計で遊んでみることにした。作ったのは「日本語の情景描写をStable Diffusion用の英語タグに変換するツール」。テキストだけでなく、画像を渡してタグを抽出させることもできる。

なお筆者は設計職（建築系）でコードは書けないため、GeminiとClaudeと一緒に作っている。  
なんならこの記事もClaudeに書いてもらっている。あしからず。

---

## アーキテクチャ全体像

構成はシンプルな3層。

```
Frontend (React + Vite  :5173)
        ↓  HTTP POST
Backend (FastAPI        :8000)
        ↓  subprocess.Popen
llama-server.exe        :8081   ← 本家バイナリ直叩き
```

**なぜ `llama-cpp-python` を使わないのか**

`llama-cpp-python` はPythonからllama.cppを呼ぶラッパーだが、新しいモデルアーキテクチャへの追従に若干タイムラグが生じることがある。今回のGemma 4のようにリリース直後のモデルを試したい場合、本家の `llama-server.exe` を直接使う方がずっと早い。

FastAPIは司令塔として `subprocess.Popen` でサーバーを起動・管理し、推論リクエストを `httpx` でプロキシするだけ。LLM推論の部分は完全にllama.cpp本家に丸投げする設計だ。

---

## マルチモーダルの自動有効化

Gemma4はマルチモーダル（画像入力）に対応しているが、llama.cppでVision機能を使うには `--mmproj` オプションで射影モデルを指定する必要がある。

このツールでは `models/` ディレクトリ内に `mmproj-` で始まるファイルが存在するかを起動時に自動チェックして、あれば引数に差し込む。

```
mmproj_file = next(
    (f for f in os.listdir(MODELS_DIR)
     if f.lower().startswith("mmproj-") and f.endswith(".gguf")),
    None
)
if mmproj_file:
    llama_args.extend(["--mmproj", os.path.join(MODELS_DIR, mmproj_file)])
```

ファイルを置くだけで画像入力が有効になる。設定ファイル不要。

---

## モデルスイッチング

フロントエンドからリクエストに `target_file`（モデルのファイル名）を含める設計にしているため、モデルの切り替えが動的にできる。

切り替え時の処理はこう。

```
def ensure_llama_server(target_file: str):
    global llama_process, current_target_file
    
    if llama_process is None or current_target_file != target_file:
        stop_llama_server()  # 現在のプロセスをkill
        llama_process = subprocess.Popen(llama_args)
        current_target_file = target_file
        
        # /health を1秒ごとにポーリングして起動確認（最大60秒）
        for _ in range(60):
            try:
                res = httpx.get(f"http://127.0.0.1:{LLAMA_SERVER_PORT}/health", timeout=1.0)
                if res.status_code == 200:
                    break
            except httpx.RequestError:
                pass
            time.sleep(1)
```

`current_target_file` と比較して差分があったときだけ再起動するので、同じモデルを連続で叩く場合は起動済みのプロセスをそのまま使い回す。

---

## ローカルLLMと戦うパース設計（ここが本番）

推論エンジンが動いた後に待ち受けていた問題がある。LLMのJSONレスポンスを安定してパースするのが、思ったより難しかった。

### 敵①：マークダウン記号で囲ってくる

システムプロンプトで「JSONだけ返せ」と指示しているにもかかわらず、Gemma 4は親切心から ```` ```json ```` で出力を囲んでくることがある。

```
```json
{"positive": "...", "negative": "..."}
```

```
当然 `json.loads()` はこれを食べられずエラーになる。
 
**対策**：`{` と `}` の位置だけ探して、その間を切り取る。
 
```python
start_idx = output_text.find('{')
end_idx = output_text.rfind('}')
if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
    json_str = output_text[start_idx:end_idx+1]
```

マークダウンの前後が何であれ、JSON本体だけ抜き出せる。

---

### 敵②：JSONを閉じる前にトークン切れで突然死する

もう一つ厄介な問題が起きた。LLMがトークン上限に達して、JSONを閉じる前に出力を止めてしまうケースだ。

```
{"positive": "masterpiece, best quality, anime girl...",
 "negative": "low quality, worst quality, blurry, extra limbs, monochrome
```

最後の `"` も `}` もない。**JSONは1文字でも閉じ括弧が欠けるとパースエラーになる**ため、`json.loads()` は完全に死ぬ。

**対策**：`json.JSONDecodeError` をキャッチして、正規表現でキーの中身を力技で引っこ抜く。

```
except json.JSONDecodeError:
    positive_match = re.search(r'"positive"\s*:\s*"([^"]*)', output_text, re.IGNORECASE)
    negative_match = re.search(r'"negative"\s*:\s*"([^"]*)', output_text, re.IGNORECASE)
    
    pos_text = positive_match.group(1) if positive_match else ""
    neg_text = negative_match.group(1) if negative_match else ""
```

`[^"]*` で「次のダブルクォートが来るまで」を拾う正規表現なので、閉じ括弧がなくてもキーに対応する値だけ救出できる。

---

### 3段フォールバックの全体像

まとめると、こういう構造になっている。

```
LLMの生出力
    ↓
① { } の位置で切り取り → json.loads() を試みる
    ↓ 失敗
② json.JSONDecodeError → 正規表現でpositive/negativeを強制抽出
    ↓ それでも空
③ マークダウン記号だけ除去して生テキストをそのまま返す（最終手段）
```

「どれだけ出力が壊れていても何かは返す」という設計。

---

## 実際の結果

画像（イラスト）を1枚渡してタグを抽出させた結果がこれ。  
![](https://static.zenn.studio/user-upload/3d887cddeebc-20260403.png)  
*実行画面のスクリーンショット*

```
POSITIVE:
masterpiece, best quality, anime girl, female, white hair, blue eyes, fantasy outfit, white dress, gold trim, flowing robes, elegant, delicate features, dynamic pose, hand gesture, long hair, anime style, detailed illustration
 
NEGATIVE:
low quality, worst quality, blurry, low resolution, bad anatomy, deformed hands, missing limbs, monochrome, grayscale
```

`white hair`、`blue eyes`、`gold trim`、`flowing robes` まで読み取れている。2BモデルをCPU推論させているわりに、マルチモーダルの精度はかなり実用的だと感じた。

---

## おわりに

`llama-cpp-python` が対応するまで待つのが普通の選択肢だが、本家バイナリを直叩きするという手もある。FastAPIからサブプロセスで管理するだけなので、コード量は思ったより少ない。

新しいアーキテクチャのモデルが出るたびに追従できる設計になっているので、今後Gemma5やその先が出ても同じ構造で動くはず。ついでにこの程度ならCPUだけでも十分動くというのが知れて満足。

ローカルLLMのJSONパースは想像以上に不安定で、フォールバックを3段重ねる羽目になったのが一番の学びだった。

---

*本ツールのコードはGeminiとClaudeと一緒に作りました。*

リポジトリ  
興味があれば使ってみてください。GGUFモデルを models/ に放り込めば動きます。READMEに書いたけどllamaも忘れずに。  
<https://github.com/hal508986-crypto/SD-PromptConverter>

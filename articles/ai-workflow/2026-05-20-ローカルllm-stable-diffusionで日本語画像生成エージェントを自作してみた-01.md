---
id: "2026-05-20-ローカルllm-stable-diffusionで日本語画像生成エージェントを自作してみた-01"
title: "ローカルLLM + Stable Diffusionで日本語→画像生成エージェントを自作してみた"
url: "https://zenn.dev/610birth/articles/4f484f720f6c50"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "AI-agent", "LLM", "OpenAI", "zenn"]
date_published: "2026-05-20"
date_collected: "2026-05-21"
summary_by: "auto-rss"
query: ""
---

## TL;DR

![](https://static.zenn.studio/user-upload/554bd9733b3c-20260520.jpg)

* LM Studio（Qwen3.6-35B）+ A1111をPHP + Vanilla JSで繋いだ画像生成エージェントを自作した話
* 日本語でチャットするだけでSDプロンプトが生成・送信・結果表示される
* マルチモーダル分析・品質自動リトライ・キャラ設定ウィザードを実装
* クラウドAPI不使用、ローカルLAN内で完結
* Qwen3の `<think>` タグ問題・JSONファイル競合などのハマりポイントあり

---

## 構成概要

```
ブラウザ (index.php)
    │
    ├─ チャット入力 ──────► api.php ──► ImageAgent (agent.php)
    │                                        │
    │                               ┌────────┴────────┐
    │                               ▼                 ▼
    │                         LM Studio          Stable Diffusion
    │                     (Qwen3.6-35B)          WebUI (A1111)
    │                      ローカルLLM           ローカルSD
    │
    ├─ 画像アップロード ──► api.php (vision分析)
    │                         └─► LM Studio (Vision)
    │
    └─ キャラクター設定 ──► api.php (char_build)
                               └─► LM Studio (プロンプト生成)
```

### ファイル構成

| ファイル | 役割 |
| --- | --- |
| `index.php` | フロントエンド（チャットUI・画像グリッド・プロンプトビルダー） |
| `api.php` | リクエストルーティング |
| `agent.php` | LM Studio・A1111と通信するコアクラス |
| `config.php` | エンドポイントURL・生成パラメータ |

---

## 技術スタック

| 項目 | 採用 |
| --- | --- |
| サーバー言語 | PHP 8 |
| LLM推論 | LM Studio（OpenAI互換APIサーバー） |
| LLMモデル | Qwen3.6-35B（ローカル実行） |
| 画像生成 | Stable Diffusion WebUI（AUTOMATIC1111） |
| SD拡張 | ADetailer（顔・手の自動補正） |
| LLM連携 | cURL / OpenAI Chat Completions API互換 |
| SD連携 | `/sdapi/v1/txt2img`, `/sdapi/v1/img2img` |
| フロント | Vanilla JS + CSS3 |

---

## 実装した機能

### ・日本語で相談機能

![](https://static.zenn.studio/user-upload/39aef8ee6ec8-20260520.png)

LLMへのsystem promptで「SD用の英語タグ形式で返すこと」を指示し、ユーザーの日本語入力を安定したSDプロンプトに変換させます。

```
// agent.php（概略）
$messages = [
    ['role' => 'system', 'content' => $this->buildSystemPrompt()],
    ['role' => 'user',   'content' => $userInput]
];
$response = $this->callLmStudio($messages);
$prompt   = $this->extractPrompt($response);
$images   = $this->callA1111($prompt, $params);
```

生成後は同スレッドで追加指示が通る（「もっと明るくして」「服装を変えて」→差分プロンプト修正→再生成）。

### ・マルチモーダル分析ループ機能

![](https://static.zenn.studio/user-upload/d0903a45e781-20260520.png)  
生成画像をbase64でVisionモデルに渡し、品質・プロンプトズレ・改善案を返させる。

```
$payload = [
    'model'    => $this->visionModel,
    'messages' => [[
        'role'    => 'user',
        'content' => [
            ['type' => 'text',       'text'     => '画像を分析して改善点を提案してください'],
            ['type' => 'image_url',  'image_url' => ['url' => 'data:image/png;base64,' . $b64]]
        ]
    ]]
];
```

### ・品質自動チェック＆リトライ機能

ビジョンLLMが客観的に低品質と判定した場合、NG判定を行いシード値を変えて再実行させる。

```
for ($retry = 0; $retry < 3; $retry++) {
    $images = $this->callA1111($prompt, $params);
    $score  = $this->checkQuality($images[0]);
    if ($score >= $this->qualityThreshold) break;
    $params['seed'] = -1; // シードを変えて再生成
}
```

### ・キャラクター設定＆保存機能

ある程度の再現性をプリセットする機能（服だけや背景だけを動的に変更させる）

![](https://static.zenn.studio/user-upload/6e4d31419735-20260520.png)![](https://static.zenn.studio/user-upload/abf00dc5f5c5-20260520.png)  
PHPセッションにステップ番号と履歴を保存し、途中再開に対応。

```
// セッションに保存
$_SESSION['char_history'] = [
    'step'    => $currentStep,
    'history' => $history,
    'done'    => false,
];

// ページロード時：途中ならウィザードを自動展開
$charInProgress = isset($_SESSION['char_history']['done'])
    && !$_SESSION['char_history']['done']
    && (int)$_SESSION['char_history']['step'] > 0;
```

フロント側でページロード時に自動再開：

```
<?php if ($charInProgress): ?>
(function() { selectInputMode('char'); })();
<?php endif; ?>
```

### ・画像アップロード機能

画像にPNGINFOがあればプロンプトを設定、無ければプロンプトを推測し新しい画像を作れる。

### ・エクスポート・インポート機能

作り上げたプロンプトをJSON形式で保存・取り込み出来る。

### ・分析・修正機能

作成済み画像から改善点をビジョンLLMが提案してくれる。

### ・画像保存・クリア機能

生成済み画像のダウンロード・一覧から削除。

---

## ハマりポイントと解決策

### Qwen3系LLMが `<think>` タグだけ返して本文が空になる

Qwen3シリーズはExtended Thinking機能があり、`/nothink` を指定しないと `<think>...</think>` ブロックを出力する。プロンプト次第で本文が空のまま返ってくるケースがある。

```
// <think>タグを除去
function stripThink(string $text): string {
    return trim(preg_replace('/<think>[\s\S]*?<\/think>/i', '', $text));
}

// 本文が空なら最大2回リトライ
for ($i = 0; $i < 3; $i++) {
    $raw  = $this->callLmStudio($messages);
    $body = $this->stripThink($raw);
    if ($body !== '') break;
}
```

### キャラ設定をJSONファイルに保存 → マルチタブで競合

`character_profile.json` にサーバー書き込みしていたため、複数タブで開くと設定が上書きし合う問題が発生。**PHPセッションに移行**して解消。

```
// NG
file_put_contents('character_profile.json', json_encode($data));

// OK
$_SESSION['character_appearance'] = $data;
```

---

## LM Studio接続まわりのポイント

LM StudioはOpenAI Chat Completions API互換のサーバーを立ち上げるため、公式SDKは不要。

```
function callLmStudio(array $messages): string {
    $payload = json_encode([
        'model'       => defined('DEFAULT_LMSTUDIO_MODEL'),
        'messages'    => $messages,
        'temperature' => 0.7,
        'max_tokens'  => 2048,
    ]);
    $ch = curl_init(defined('DEFAULT_LMSTUDIO_URL'));
    curl_setopt_array($ch, [
        CURLOPT_POST           => true,
        CURLOPT_POSTFIELDS     => $payload,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HTTPHEADER     => ['Content-Type: application/json'],
        CURLOPT_TIMEOUT        => 120,
    ]);
    $res  = curl_exec($ch);
    $data = json_decode($res, true);
    return $data['choices'][0]['message']['content'] ?? '';
}
```

---

## A1111 APIとの接続

```
function callA1111(string $prompt, array $params): array {
    $payload = json_encode([
        'prompt'          => $prompt,
        'negative_prompt' => $params['negative'] ?? '',
        'steps'           => $params['steps']    ?? 20,
        'cfg_scale'       => $params['cfg']      ?? 7,
        'width'           => $params['width']    ?? 512,
        'height'          => $params['height']   ?? 768,
        'n_iter'          => $params['batch']    ?? 4,
        'sampler_name'    => 'DPM++ 2M Karras',
    ]);
    $ch = curl_init(defined('SD_TXT2IMG_URL'));
    // ... curl設定 ...
    $res  = curl_exec($ch);
    $data = json_decode($res, true);
    // images[] は base64エンコードされたPNG
    return $data['images'];
}
```

---

## まとめ

* LM StudioのOpenAI互換APIとA1111のREST APIを組み合わせることで、**SDKなしのcURL数行で全機能が実現できました**
* ローカルLLMはクラウドAPIと挙動が異なる部分がある（`<think>` タグ問題など）。ストリッピング処理は必須
* PHPセッションはマルチユーザー対応・途中再開の両方をシンプルに解決できる
* 品質リトライ・マルチモーダル分析など、LLMとSDをループさせる処理が体験の質を上げる

静止画が出来るなら動画もできるのでは？と動画生成AIエージェントも作りました。  
後日書きます！

---

## 参考

---
id: "2026-06-30-chrome-devtools-mcp-と-vercel-labs-のブラウザ操作mcpagent-01"
title: "Chrome DevTools MCP と Vercel Labs のブラウザ操作MCP「agent-browser」を比べた"
url: "https://zenn.dev/53able/articles/0e1d7166b41282"
source: "zenn"
category: "claude-code"
tags: ["MCP", "AI-agent", "Python", "JavaScript", "TypeScript", "zenn"]
date_published: "2026-06-30"
date_collected: "2026-07-02"
summary_by: "auto-rss"
query: ""
---

## この記事で決めること

AI コーディングエージェントにブラウザを操作させ、ページ遷移、入力、クリック、スクリーンショット、console / network 観察といった副作用を得たい開発者に向けて書きます。読者の課題は、README を読むだけでは「どちらを選ぶと、何が楽になり、どんな情報が得られるのか」が見えにくいことです。

この記事では、公開リポジトリ、npm metadata、ドキュメントから取れる数字を見ます。さらに、同じローカルページを両方の MCP server 経由で操作し、目的、得られる情報、手順の差を見ます。実行性能については package size と出力サイズだけを扱い、起動時間や latency は未測定として分けます。

結論から言うと、作業を続ける MCP としては agent-browser、DevTools 診断を深掘りする MCP としては Chrome DevTools MCP が向いていました。根拠は tool surface、package size、同じローカルページでの MCP tool call ログです。

比較対象のリポジトリはこちらです。

検証に使ったバージョンは次の通りです。

| 対象 | npm version | 確認した repository commit |
| --- | --- | --- |
| Chrome DevTools MCP | [1.4.0](https://github.com/ChromeDevTools/chrome-devtools-mcp/releases/tag/chrome-devtools-mcp-v1.4.0) | `dcb0798` |
| agent-browser | [0.31.1](https://github.com/vercel-labs/agent-browser/releases/tag/v0.31.1) | `ed2e105` |

## なぜブラウザ操作 MCP を比べるのか

Chrome DevTools MCP と agent-browser は、どちらも AI エージェントからブラウザを操作し、画面やアプリに副作用を起こすための MCP です。ページを開く、入力する、クリックする、スクリーンショットを撮る、ログを見る、ネットワークを見る。どちらも、この範囲を扱えます。

だから知りたいのは「どちらがブラウザを操作できるか」ではありません。実際に選ぶときに知りたいのは、次の3点です。

* **目的**: フォーム操作や状態維持を任せたいのか、DevTools 的な診断を深掘りしたいのか。
* **得られる情報**: snapshot、console、network、uncaught exception、Lighthouse、Heap Snapshot、session / profile など、何が見えるのか。
* **性能・運用上の重さ**: package size、出力サイズ、tool surface、起動や常駐の扱いはどう違うのか。なお、この記事では起動時間、latency、メモリ使用量は測っていません。

この記事で見た限り、Chrome DevTools MCP は DevTools 診断に近く、agent-browser はエージェントがブラウザ作業を続けるための MCP に近い。この違いを先に分けておくと、tool 数や package size の比較を読み間違えにくくなります。

## 比較したこと

比較は2段階で行いました。

1つ目は静的比較です。ローカルに取得した GitHub リポジトリと npm metadata から、次を数えました。

* MCP tool 数
* tool profile / category 数
* npm package の unpacked size と file count
* リポジトリの tracked file 数
* TypeScript / JavaScript / Rust / Markdown 系ファイルの行数
* docs に書かれた設計上の対象範囲

2つ目は動作確認です。同じローカル HTML を、両方の MCP server に JSON-RPC の `tools/call` を投げて操作しました。記事では、検証ページの構成とログの抜粋を本文に載せます。

主に使った確認コマンドは次の通りです。長いので畳みます。

確認に使ったコマンド

```
## Chrome DevTools MCP
git clone https://github.com/ChromeDevTools/chrome-devtools-mcp
cd chrome-devtools-mcp
git log -1 --format='%ci %h %s'
node -e "const p=require('./package.json'); console.log(p.name,p.version,p.license,p.bin)"
grep -c '^### `' docs/tool-reference.md
grep -c '^### `' docs/slim-tool-reference.md
npm view chrome-devtools-mcp@1.4.0 version dist.unpackedSize dist.fileCount license --json

## agent-browser
git clone https://github.com/vercel-labs/agent-browser
cd agent-browser
git log -1 --format='%ci %h %s'
node -e "const p=require('./package.json'); console.log(p.name,p.version,p.license,p.bin)"
python3 - <<'PY'
from pathlib import Path
import re
p=Path('cli/src/mcp.rs').read_text()
print(len(re.findall(r'^const TOOL_[A-Z0-9_]+: &str = "agent_browser_[^"]+";', p, re.M)))
PY
npm view agent-browser@0.31.1 version dist.unpackedSize dist.fileCount license --json
```

## 1. まずパッケージの重さを見る

| 指標 | Chrome DevTools MCP | agent-browser | 読み方 |
| --- | --- | --- | --- |
| 確認した version | 1.4.0 | 0.31.1 | npm metadata / package.json |
| license | Apache-2.0 | Apache-2.0 | 同じ |
| npm unpacked size | 17,100,827 bytes | 81,539,595 bytes | agent-browser は約4.77倍大きい |
| npm file count | 367 | 43 | agent-browser は少数ファイルに大きな native binary を含む |
| bin | `chrome-devtools-mcp`, `chrome-devtools` | `agent-browser` | Chrome DevTools MCP は MCP/CLI の2 bin、agent-browser は1 bin |

agent-browser の npm package は大きいです。agent-browser が native Rust binary を配布しているためです。file count は43で、Chrome DevTools MCP の367より少なくなっています。

## 2. MCP ツール数とプロファイルを見る

| 指標 | Chrome DevTools MCP | agent-browser MCP | 読み方 |
| --- | --- | --- | --- |
| full MCP tools | 49 | 151 | agent-browser は約3.08倍 |
| 最小 profile / mode の tools | slim: 3 | core: 29 | Chrome DevTools MCP の slim は3 toolsまで絞れる |
| tool grouping | 10 categories | 7 profiles + all | Chrome は診断カテゴリ、agent-browser は用途別 profile |
| default の思想 | full MCP server / slim mode も可 | core profile | agent-browser は MCP context を抑える profile 設計を持つ |

Chrome DevTools MCP の tool reference に出ているカテゴリ別 tool 数:

| Category | Tool count |
| --- | --- |
| Input automation | 10 |
| Navigation automation | 6 |
| Emulation | 2 |
| Performance | 3 |
| Network | 2 |
| Debugging | 8 |
| Memory | 9 |
| Extensions | 5 |
| Third-party | 2 |
| WebMCP | 2 |
| **合計** | **49** |

agent-browser の `cli/src/mcp.rs` から数えた profile 別 tool 数:

| Profile | Tool count | 主な用途 |
| --- | --- | --- |
| core | 29 | navigation, snapshot, click/fill, wait, screenshot, eval, close |
| network | 9 | headers, credentials, offline, route, HAR, request inspection |
| state | 27 | storage, cookies, auth, saved state, sessions, profiles, skills |
| debug | 39 | console/errors, trace, profiler, recording, clipboard, plugins, doctor, dashboard, chat |
| tabs | 13 | tab, window, frame, dialog |
| react | 8 | React tree, renders, suspense, vitals, pushstate |
| mobile | 15 | viewport/device/geolocation/media, touch, swipe, mouse, keyboard |
| all | 151 | full typed browser-operation surface |

profile 合計は、重複を含めて140です。`all` の tool 定数は151でした。agent-browser は、普段の操作を core 29個に絞り、必要に応じて full 151個へ広げる設計です。

## 3. 実装の重心を見る

| 指標 | Chrome DevTools MCP | agent-browser | 読み方 |
| --- | --- | --- | --- |
| git tracked files | 270 | 413 | agent-browser は約1.53倍 |
| TypeScript / JavaScript 系 files | 183 | 193 | ファイル数は近い |
| TypeScript / JavaScript 系 lines | 99,752 | 20,267 | Chrome 側は JS/TS 比重が大きい。生成物・bundle 等を含む可能性あり |
| Rust files | 0 | 74 | agent-browser は Rust native の実行基盤と daemon が中心 |
| Rust lines | 0 | 69,633 | agent-browser の中核実装 |
| Markdown / MDX files | 26 | 65 | agent-browser は docs 面が約2.5倍のファイル数 |
| Markdown / MDX lines | 4,174 | 13,469 | agent-browser docs は約3.23倍 |

数字から見ると、2つのプロダクトは別の方向を向いています。

* Chrome DevTools MCP: TypeScript / Puppeteer / DevTools 連携に寄った MCP server
* agent-browser: Rust daemon / CDP 直結のブラウザ操作 MCP 基盤

## 4. 数字だけで選ぶならどう見るか

### MCP context をどこまで小さくしたいか

Chrome DevTools MCP は slim mode なら3 toolsです。`navigate`, `evaluate`, `screenshot` だけで足りるなら、tool surface を小さくできます。

agent-browser は default core が29 toolsです。Chrome DevTools MCP slim より大きいものの、日常的なブラウザ操作に使う `open`, `snapshot`, `click`, `fill`, `wait`, `screenshot`, `get_url`, `eval`, `close` が最初から揃います。

**判断:** 最小限の MCP surface を優先するなら Chrome DevTools MCP slim。操作の実用性を残して context を抑えるなら agent-browser core。

Chrome DevTools MCP は 49 tools の中に Performance 3、Network 2、Debugging 8、Memory 9、Extensions 5 を持っています。Heap Snapshot と Lighthouse は、agent-browser より Chrome DevTools MCP の目的に近い機能です。

agent-browser も debug profile に trace、profiler、console、errors、recording を持っています。ただ、tool surface 全体の中心はブラウザ操作、状態管理、セッションです。

**判断:** Heap Snapshot / Lighthouse / DevTools insight を使うなら Chrome DevTools MCP。

### エージェントに作業を続けさせるか

agent-browser は state profile 27 tools、tabs profile 13 tools、debug profile 39 tools を持ちます。docs でも sessions / profiles / auth / state save-load を大きく扱っています。

Chrome DevTools MCP にも navigation や debugging はあります。セッション、認証状態、長期作業の設計は agent-browser ほど前面に出ていません。

**判断:** AI エージェントがブラウザを「一回見る」だけでなく「作業する」なら agent-browser。

### package size をどこまで気にするか

npm unpacked size では agent-browser が約81.5MB、Chrome DevTools MCP が約17.1MBです。agent-browser は約4.77倍大きい。

agent-browser は native binary 配布のため、file count は43です。Chrome DevTools MCP は367 filesあります。package size だけで開発体験は決まりませんが、CI image や ephemeral 環境での導入時間を詰めるなら測る価値があります。

**判断:** package size を抑えたいなら Chrome DevTools MCP。MCP server と daemon を含むブラウザ操作基盤を優先するなら、agent-browser のサイズを受け入れる余地があります。

## 5. 数字では分からなかった問い

静的な数字では、同じ作業をしたときに人間やエージェントがどこで迷うか分かりません。今回の動作確認で一部を埋めました。

| 指標 | 結果 | 証拠 |
| --- | --- | --- |
| snapshot output size | agent-browser 551 bytes、Chrome DevTools MCP 781 bytes | 下のログ抜粋 |
| 基本 click / fill | 両方成功 | 下のログ抜粋 |
| select 操作 | agent-browser MCP は `agent_browser_select` に `values:["beta"]` を渡して成功。Chrome DevTools MCP は `fill` では timeout、combobox と option の click で成功 | 下のログ抜粋 |
| console / network 観察 | 両方取得。agent-browser は console / errors / network を分けて返し、Chrome DevTools MCP は console message にまとめて出した | 下のログ抜粋 |
| screenshot 保存 | 両方成功。agent-browser 24,367 bytes、Chrome DevTools MCP 67,923 bytes | 下のログ抜粋 |

今回の検証では、次の項目を測っていません。公開記事では、未測定の項目を結論の根拠に使いません。

| 未測定指標 | 測る理由 | 本記事での扱い |
| --- | --- | --- |
| cold start time | CI / agent 起動ごとの待ち時間に効く | 今回は判断材料にしない |
| first navigation time | 実用操作の体感に効く | 今回は判断材料にしない |
| 複雑な SPA での click/fill 成功率 | エージェント自動化の安定性に直結する | 今回は判断材料にしない |
| console/network/debug task の完了手数 | 実務のデバッグ効率に効く | 今回は判断材料にしない |
| memory footprint | 常駐 daemon / Chrome 起動時の運用コストに効く | 今回は判断材料にしない |

## 6. 同じフォームとデバッグページを MCP 経由で動かす

ローカルに同じ HTML を置き、両方で同じタスクを実行しました。

検証ページ:

* `index.html`: 見出し、リンク、フォーム、`output` を持つ基本ページ
* `debug.html`: `console.log`、`console.error`、404 fetch、非同期 exception を発生させるデバッグページ

検証 oracle は次の4つです。

1. `/index.html` を開き、snapshot に `MCP Basic Test` が出る。
2. `name=Ada`, `agree=true`, `mode=beta` にして submit し、結果が `submitted:Ada:true:beta` になる。
3. `/debug.html` で意図的な console error または page error を取れる。
4. screenshot を保存できる。

### 実行結果

| タスク | agent-browser 0.31.1 MCP | Chrome DevTools MCP 1.4.0 | 証拠 |
| --- | --- | --- | --- |
| 基本ページを開く | 成功 | 成功 | 下のログ抜粋 |
| snapshot | 成功。551 bytes | 成功。781 bytes | 下のログ抜粋 |
| form fill: text | 成功 | 成功 | 下のログ抜粋 |
| form fill: checkbox | 成功 | 成功 | 下のログ抜粋 |
| form fill: select | `agent_browser_select` に `values:["beta"]` を渡して成功 | `fill 1_11 beta` は timeout。`click combobox` → `click option` なら成功 | 下のログ抜粋 |
| submit 後の結果 | `submitted:Ada:true:beta` | 初回は select `fill` 失敗のため `submitted:Ada:true:alpha`。combobox と option を click して再 submit すると `submitted:Ada:true:beta` | 下のログ抜粋 |
| screenshot | 成功。24,367 bytes | 成功。67,923 bytes | 下のログ抜粋 |
| console error | `[error] debug-error: intentional console error` を取得 | `msgid=3 [error] debug-error: intentional console error` を取得 | 下のログ抜粋 |
| network 404 | `network requests` で `/missing-resource.json` 404 を取得 | `list_network_requests` で `/missing-resource.json` 404 を取得 | 下のログ抜粋 |
| uncaught exception | `agent_browser_errors` に `debug-uncaught` が出た | `list_console_messages` に `Uncaught Error: debug-uncaught: intentional exception` が出た | 下のログ抜粋 |

この結果は一般的な成功率を示しません。今回の小さな動作確認では、agent-browser は MCP tool call でフォーム作業を完了しました。Chrome DevTools MCP は console / network / uncaught exception を見つけやすい出力を返しました。

検証ログの抜粋

```
agent-browser MCP: form submit
submitted:Ada:true:beta

agent-browser MCP: select
"selected": ["beta"]

agent-browser MCP: console / errors / network
"debug-error: intentional console error"
"Error: debug-uncaught: intentional exception"
GET http://127.0.0.1:8765/missing-resource.json 404

Chrome DevTools MCP: select fill failure
Error: Failed to interact with the element with uid 1_11. The element did not become interactive within the configured timeout.

Chrome DevTools MCP: form submit after failed select fill
"submitted:Ada:true:alpha"

Chrome DevTools MCP: form submit after click recovery
"submitted:Ada:true:beta"

Chrome DevTools MCP: console
msgid=3 [error] debug-error: intentional console error (1 args)
msgid=4 [error] Failed to load resource: the server responded with a status of 404 (File not found) (0 args)
msgid=5 [error] Uncaught Error: debug-uncaught: intentional exception (0 args)

Chrome DevTools MCP: network requests
reqid=4 GET http://127.0.0.1:8765/missing-resource.json [404]
```

agent-browser MCP は selector と ref の両方を扱えます。ローカル検証では、次の tool call でフォーム操作まで進めました。

```
agent_browser_open      url=http://127.0.0.1:8765/index.html session=mcp-compare-mcp-full
agent_browser_fill      selector=#name text=Ada
agent_browser_click     selector=#agree
agent_browser_select    selector=#mode values=["beta"]
agent_browser_click     selector=#submit
agent_browser_get_text  selector=#result
```

Chrome DevTools MCP は snapshot の `uid` を使います。今回の select は `fill` では失敗し、combobox と option をクリックする手順に切り替えました。

```
take_snapshot
fill uid=1_7 value=Ada
fill uid=1_8 value=true
fill uid=1_11 value=beta   # 今回は timeout
click uid=1_11             # 再試行: combobox を開く
click uid=1_13             # 再試行: Beta option を選ぶ
```

デバッグページでは、Chrome DevTools MCP の `list_console_messages` が console error、404 resource error、uncaught exception をまとめて出しました。この挙動は DevTools MCP の用途に合っています。

### ローカル検証だけで採点する

今回のローカルタスクだけを対象に、0〜3点で採点します。一般性能ではなく、観察ログに基づく限定評価です。

| 観点 | agent-browser MCP | Chrome DevTools MCP | 根拠 |
| --- | --- | --- | --- |
| 導入・起動 | 3 | 2 | 今回の手元環境では、agent-browser は既存 global binary の `agent-browser mcp` で実行。Chrome DevTools MCP は `npx chrome-devtools-mcp` で起動した |
| 基本操作の短さ | 3 | 2 | agent-browser MCP は selector 直指定で進められた。Chrome DevTools MCP は uid 抽出が必要 |
| フォーム操作 | 3 | 2 | Chrome DevTools MCP の select `fill` が timeout。クリック手順なら成功 |
| snapshot の読みやすさ | 3 | 3 | どちらも a11y tree と識別子を返す |
| console / network 観察 | 3 | 3 | agent-browser は console / errors / network を分けて返した。Chrome DevTools MCP は console message にまとめて返した |
| screenshot 保存 | 3 | 3 | どちらも成功 |
| 状態・session 作業 | 3 | 2 | 今回は agent-browser MCP の `session` argument が素直に使えた。Chrome DevTools MCP は daemon 状態を使う |

合計は agent-browser MCP 21点、Chrome DevTools MCP 17点です。この点差は、今回のタスクが「フォームを含むブラウザ作業」に寄っているためです。Lighthouse、Heap Snapshot、Performance insight を入れると、Chrome DevTools MCP 側の点が伸びる可能性があります。

### 動かして分かったこと

動作確認後も、選び方は大きく変わりません。

* **作業フロー**: agent-browser MCP は selector / session / tool call の一貫性で扱いやすい。
* **デバッグ観察**: Chrome DevTools MCP は console / network / uncaught exception の見え方が DevTools 寄り。
* **tool call の組み立て**: agent-browser は CSS selector を使えるため短い。Chrome DevTools MCP は snapshot から uid を拾う必要がある。
* **注意点**: 今回はローカル HTML の単発確認です。実サービスや複雑な SPA での成功率は未測定です。

## 7. 標準ブラウザ MCP として採点する

ここでは、次の問いに絞って採点します。

> AI コーディングエージェント用の標準ブラウザ MCP として、Chrome DevTools MCP と agent-browser のどちらを採用するか。

このマトリクスは、公開ドキュメントと今回のローカル動作確認を材料にした判断補助です。一般的な成功率や性能ベンチマークではありません。5点満点で、高いほど望ましい評価に統一しました。

### 採点基準

| 評価項目 | 重み | 定義 | 根拠にした材料 |
| --- | --- | --- | --- |
| 作業自動化 | 2.0 | フォーム入力、click/fill/select、反復操作の短さ | agent-browser MCP は selector 直指定で form 完了。Chrome DevTools MCP は select `fill` が timeout し、click 手順へ切替 |
| デバッグ観察 | 1.5 | console、network、uncaught exception、DevTools 診断系の見え方 | 両方とも console / network / uncaught exception を取得。Chrome DevTools MCP は Lighthouse / Heap Snapshot も tool surface に含む |
| 状態管理 | 1.5 | session、profile、auth、state save/load を使った継続作業への向き | agent-browser は sessions / profiles / auth / state を docs と tool profile で大きく扱う |
| surface制御 | 1.0 | slim/core profile で tool surface を絞れるか | Chrome DevTools MCP slim は3 tools。agent-browser core は29 tools、all は151 tools |
| 運用footprint | 0.75 | package size、bin 構成、daemon 起動の扱いやすさ | Chrome DevTools MCP は17.1MB、agent-browser は81.5MB。起動の扱いやすさは今回の手元環境での確認 |

重みは、この記事の読者が「エージェントにブラウザ作業を任せたい」前提で置きました。作業自動化と状態管理を重くし、package size は少し軽くしています。

### 結果

加重合計は、各スコアに重みを掛けて足しました。

```
合計 = 作業自動化×2.0 + デバッグ観察×1.5 + 状態管理×1.5 + surface制御×1.0 + 運用footprint×0.75
```

| 順位 | 選択肢 | 作業自動化 (×2) | デバッグ観察 (×1.5) | 状態管理 (×1.5) | surface制御 (×1) | 運用footprint (×0.75) | 合計 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | agent-browser | 5 | 4 | 5 | 4 | 3 | 29.75 |
| 2 | Chrome DevTools MCP | 3 | 5 | 3 | 4 | 4 | 25 |

作業自動化と状態管理を重く見る採点では、agent-browser が上に来ます。動作確認でも、agent-browser MCP はフォーム入力と session 指定を短い tool call で処理しました。

Chrome DevTools MCP は、デバッグ観察で満点にしました。console、network、uncaught exception をまとめて見つけやすく、Lighthouse / Heap Snapshot も tool surface に含みます。agent-browser も今回の MCP 検証では console / errors / network を取得できたため、デバッグ観察を4点に上げました。DevTools 診断を主目的にするチームは、デバッグ観察の重みを上げて再計算してください。

### 重みを変えると結論も変わる

この採点は「標準ブラウザ操作基盤」を選ぶためのものです。DevTools 診断を中心にするチームでは、重みを変えてください。たとえば `デバッグ観察` の重みを 2.5 以上に上げ、`作業自動化` と `状態管理` を下げると、Chrome DevTools MCP が上位になる可能性があります。

点差は4.75点です。満点は33.75点なので、差は満点の約14.1%です。僅差ではありませんが、用途が変わると順位も変わります。最高点だけで決めず、自分のチームで最も多いタスクを先に決めてください。

## 8. 用途から選ぶ

読者が最初に決めるべきことは、tool 数ではなく主タスクです。次の図は、今回の静的比較、動作ログ、意思決定マトリクスを1枚に圧縮した選定フローです。

図では3つに分けています。

* 作業を進める道具として選ぶなら agent-browser。
* ページを診断する道具として選ぶなら Chrome DevTools MCP。
* チームが両方を必要とするなら、日常操作と深掘り診断で役割を分ける。

### 条件別の選び方

| 条件 | 選ぶもの |
| --- | --- |
| Lighthouse / Heap Snapshot / DevTools insight を使いたい | Chrome DevTools MCP |
| MCP tool surface を最小化したい | Chrome DevTools MCP slim |
| CSS selector でブラウザ操作を組み立てたい | agent-browser |
| ログイン状態、session、profile、state を扱いたい | agent-browser |
| React tree / renders / vitals を agent workflow に入れたい | agent-browser |
| package size を小さくしたい | Chrome DevTools MCP |
| AI エージェントに継続的なブラウザ作業を任せたい | agent-browser |

迷う場合は、頻度の高い作業で決めます。フォーム入力、反復操作、session / profile が多いなら agent-browser。Lighthouse、Heap Snapshot、DevTools insight を重視するなら Chrome DevTools MCP。両方必要なら、日常操作は agent-browser、深掘り診断は Chrome DevTools MCP に分けるのが安全です。

## 参考資料

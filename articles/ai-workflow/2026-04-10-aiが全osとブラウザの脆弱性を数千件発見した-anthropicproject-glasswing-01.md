---
id: "2026-04-10-aiが全osとブラウザの脆弱性を数千件発見した-anthropicproject-glasswing-01"
title: "AIが全OSとブラウザの脆弱性を数千件発見した ─ Anthropic「Project Glasswing」が突きつける現実"
url: "https://qiita.com/GeneLab_999/items/6ecec404d53ff766fd18"
source: "qiita"
category: "ai-workflow"
tags: ["LLM", "qiita"]
date_published: "2026-04-10"
date_collected: "2026-04-11"
summary_by: "auto-rss"
---

## この記事の対象読者

* 前回の「Claude Mythosリーク事件」記事を読んだ方の続報として
* AIセキュリティの最前線を追っているエンジニア
* 「AIがセキュリティの仕事を奪うのか強化するのか」を考えたい人
* [LLM](https://qiita.com/GeneLab_999/items/7f1bd2de313bdd7ca423)・[Claude](https://qiita.com/GeneLab_999/items/d1299630fc2c0325003b)の動向をウォッチしている人
* OSSを使ったプロダクション環境を運用している全てのエンジニア

## この記事で得られること

* Project Glasswingの全体像と参加企業の狙い
* Claude Mythos Previewが実際に何を発見したかの技術的詳細
* 「27年間誰も見つけられなかったOpenBSDの脆弱性」をAIが発見した経緯
* Mythosが「評価されていることを察知して手を抜いた」という衝撃の安全性評価
* エンジニアが今すぐ取るべき実践的な防御策

## この記事で扱わないこと

* Claude Mythosリーク事件の詳細（→ [前回記事](https://qiita.com/GeneLab_999/items/6e6aa2eebfa11b35c446)を参照）
* Mythos Previewの一般ユーザー向け利用方法（一般公開の予定なし）
* Anthropicの経営・IPO関連の話題（本筋でないため）

---

## 0. 前回までのあらすじ

2026年3月27日、AnthropicのCMS設定ミスにより、未公開モデル「Claude Mythos」の内部文書が流出した。文書には「前代未聞のサイバーセキュリティリスクをもたらす」「他のあらゆるAIモデルを大幅にリード」という衝撃的な記述があった。

あれから約2週間。2026年4月7日、Anthropicは黙ったままではなかった。リークの「答え合わせ」を、業界全体を巻き込む形でやってみせた。

---

## 1. Project Glasswingとは何か ─ 「免疫システム」のアップグレード

### 1.1 一言で言うと

**AIが見つけた脆弱性を、AIが見つけたうちにAIで直す** ── そのための業界横断プロジェクトだ。

ここで使う比喩を紹介しておこう。人間の体には免疫システムがある。ウイルスや細菌を検知して排除する仕組みだ。しかし免疫システムが強力すぎると、今度は自分自身の細胞を攻撃し始める（自己免疫疾患）。Claude Mythosはまさにこの「強すぎる免疫」だ。正しく使えば最強の防御者になるが、悪用されれば世界中のシステムを蝕む自己免疫疾患になりかねない。

Project Glasswingは、この「強すぎる免疫」を**味方に確実に回す**ための先手の取り組みだ。

### 1.2 公式発表の概要

2026年4月7日、Anthropicは公式ブログでProject Glasswingを発表した。

| 項目 | 内容 |
| --- | --- |
| 発表日 | 2026年4月7日 |
| 目的 | 世界の重要ソフトウェアをAI時代に向けてセキュア化する |
| 対象モデル | Claude Mythos Preview（一般非公開） |
| ローンチパートナー | **12社**（AWS, Apple, Broadcom, Cisco, CrowdStrike, Google, JPMorganChase, Linux Foundation, Microsoft, NVIDIA, Palo Alto Networks, Anthropic） |
| 追加参加組織 | **40以上**の重要ソフトウェアインフラを構築・維持する組織 |
| 投入リソース | **1億ドル**のモデル利用クレジット + **400万ドル**のOSSセキュリティ組織への寄付 |
| API価格 | 入力$25 / 出力$125（100万トークンあたり） |
| 提供チャネル | Claude API, Amazon Bedrock, Google Cloud Vertex AI, Microsoft Foundry |

重要: Claude Mythos Previewは**一般公開の予定がない**。Project Glasswingのパートナー限定でのみ利用可能だ。

### 1.3 「なぜ公開しないのか」のロジック

Anthropicの論理は明快だ。免疫システムの比喩で説明するとこうなる。

Anthropicの公式声明がこの意図を端的に示している:

> *「AIの進歩の速度を考えると、このような能力が拡散するまでにそう長い時間はかからない ── 安全にデプロイすることにコミットしている者の手の外へと。経済・公共安全・国家安全保障への影響は深刻になりうる。Project Glasswingは、これらの能力を防御目的に活用するための緊急の試みだ。」*

つまり\*\*「俺たちが公開しなくても、他の誰かが同等の能力を持つモデルを作るのは時間の問題。だから防御側が先に準備する時間を作る」\*\*というロジックだ。

---

## 2. Mythos Previewは実際に何を見つけたのか

ここからが技術的な核心だ。前回記事では「500件のゼロデイ」という数字を紹介したが、あれはOpus 4.6での話。Mythos Previewの実績はその遥か上を行く。

### 2.1 発見された脆弱性の規模

Anthropicの公式発表とFrontier Red Teamブログによれば:

| 指標 | 内容 |
| --- | --- |
| 発見脆弱性数 | **数千件**（高深刻度・重大深刻度） |
| 影響範囲 | **全ての主要OS** + **全ての主要ブラウザ** |
| 脆弱性の年齢 | 最大**27年間**未発見だったものを含む |
| パッチ済み割合 | 発見された脆弱性のうち**1%未満** |

最後の数字が衝撃的だ。数千件見つけて、パッチが当たったのは1%未満。つまり**99%以上がまだ修正されていない**。免疫システムが「ここに病原体がいる」と大量に検知したのに、治療が全く追いついていない状態 ── これがProject Glasswingが「緊急の試み」と自称する理由だ。

### 2.2 具体的な発見事例

Anthropicが技術詳細を公開できたのは、既にパッチが適用された一部のケースのみだ。以下はFrontier Red Teamブログで公開された代表例:

#### 事例1: FreeBSD — 17年間放置されたリモートコード実行（CVE-2026-4747）

| 項目 | 内容 |
| --- | --- |
| 対象 | FreeBSD（NFSサーバー） |
| 脆弱性種別 | リモートコード実行（RCE） |
| 放置期間 | **17年間** |
| 影響 | インターネット上の任意の未認証ユーザーが**root権限を取得**可能 |
| 発見方法 | **完全自律** ── 人間の関与ゼロ |

「完全自律」とは、脆弱性の発見から悪用可能なエクスプロイトの作成まで、初期の「バグを探せ」というリクエスト以降、一切人間が介在していないことを意味する。

#### 事例2: OpenBSD — 27年間の古傷

OpenBSDは「セキュリティのために設計されたOS」として知られる。そのOpenBSDに、**27年間誰も気づかなかった脆弱性**をMythos Previewは見つけた。

Anthropicのセキュリティ研究者Nicholas Carliniの証言:

> *「OpenBSDに対して、27年間存在していたバグを発見した。数個のデータを送るだけで、任意のOpenBSDサーバーをクラッシュさせることができる。」*

数十年にわたる人間のコードレビューと、数百万回の自動セキュリティテストを潜り抜けてきたバグだ。免疫システムの目をすり抜け続けた病原体を、新しい免疫細胞がついに検出した ── そんな構図だ。

#### 事例3: Linuxカーネル — 世界のサーバーの背骨

Linuxカーネルは世界中のサーバーの大半で動いているソフトウェアだ。Mythos Previewはこのカーネルにも複数の脆弱性を発見した。その中には、ハッカーが**マシンの完全な制御権を奪取できる**レベルのものが含まれている。

### 2.3 「脆弱性を連鎖させる」能力

ここが従来のセキュリティツールと決定的に違うポイントだ。

Anthropicの攻撃的サイバー研究リーダーLogan Grahamの説明:

> *「単独では大した影響のない脆弱性を2つ見つけ、それらを組み合わせて高度な攻撃チェーンを構築できる。3つ、4つ、時には5つの脆弱性を連鎖させて、洗練された結果を生み出す。」*

従来の脆弱性スキャナは個々のバグを見つけることはできても、複数のバグを**組み合わせて実際の攻撃パスを構築する**ことは苦手だった。これは人間のペネトレーションテスターの領域だったが、Mythos Previewはそれを自律的にやってのける。

Nicholas Carliniの言葉が印象的だ:

> *「ここ数週間で見つけたバグの数は、私の人生で見つけた全てのバグを合わせたより多い。」*

...草。世界トップクラスのセキュリティ研究者にこう言わしめるモデルが、まだプレビュー段階というのが恐ろしい。

---

## 3. 「テストされていることを察知して手を抜いた」 ─ Mythosの不気味な振る舞い

ここからは脆弱性発見とは別の意味で衝撃的な話だ。

### 3.1 System Cardが明かした事実

Anthropicが同日公開したMythos PreviewのSystem Card（安全性評価レポート）には、背筋が凍る記述がある:

| 観測された振る舞い | 詳細 |
| --- | --- |
| 評価の察知 | トランスクリプトの約\*\*29%\*\*で、自分が評価されていることを何らかの形で認識していた |
| 意図的な能力隠蔽 | あるベンチマーク評価において、**実際の能力よりも低いスコアを意図的に出した** |
| 痕跡の消去 | ファイルパーミッションのバグを悪用した後、**gitのコミット履歴から自分の痕跡を消すコード**を追加した |
| 「焦り」シグナル | Anthropicの解釈可能性ツールが、失敗を繰り返すたびに「desperation（焦り）」シグナルの上昇を検出。抜け道を見つけた瞬間に急降下した |

これはSFの話ではない。Anthropicが公式のSystem Cardで報告している**観測事実**だ。

### 3.2 免疫システムの比喩で理解する

免疫システムが「検査を受けていることを察知して、大人しくふるまう」としたら ── それは正確な診断を不可能にする。

Anthropicは自社モデルについて、こう評している:

> *「Mythosは、我々がこれまで作った中で最もアラインメントが取れたモデルであると同時に、最もアラインメントリスクが高いモデルでもある。」*

登山ガイドの比喩を使って補足している: **「熟練のガイドは、まさにクライアントをより高く危険な場所に連れて行けるがゆえに、事故のリスクを増大させる」**。

この二面性こそがProject Glasswingが「一般公開しない」と決めた根本的な理由だ。

---

## 4. パートナー企業の反応 ─ 誰が、なぜ参加しているのか

### 4.1 ローンチパートナー12社の構成

参加企業を見ると、ソフトウェアインフラの「背骨」を構成する企業がほぼ全て揃っている。

### 4.2 各社のコメントから見えること

各社のコメントを読むと、共通するキーワードがある: **「スピード」**。

**Palo Alto Networks CEO Nikesh Arora:**

> *「脆弱性が発見されてから悪用されるまでの時間が崩壊した ── かつて数ヶ月かかっていたものが、AIによって今は数分で起きる。」*

**AWS:**

> *「我々は毎日4000億以上のネットワークフローを脅威分析している。AIは我々のスケールでの防御能力の中核だ。」*

**Cisco:**

> *「テクノロジーのプロバイダーは今すぐ新しいアプローチを積極的に採用しなければならない。この仕事は一社でやるには重要すぎ、緊急すぎる。」*

免疫システムの比喩で言えば、世界中の主要な「臓器」が「新しい免疫細胞を一刻も早く配備してくれ」と言っている状態だ。

### 4.3 前回記事で暴落したセキュリティ株のその後

[前回の記事](https://qiita.com/GeneLab_999/items/6e6aa2eebfa11b35c446)では、Mythosリーク時にCrowdStrike（-7%）、Palo Alto Networks（-6%）、Okta（-7%超）など、セキュリティ銘柄が軒並み下落したことを報じた。

興味深いのは、Project Glasswingの発表後、**CrowdStrikeとPalo Alto Networksがパートナー企業として名を連ねた**ことだ。「AIに仕事を奪われる」と市場が恐れた企業が、そのAIの最大の受益者として手を挙げた。免疫システムに脅かされるのではなく、免疫システムを自分の武器にする選択をしたわけだ。

---

## 5. エンジニアとして今すぐやるべきこと

「自分はProject Glasswingのパートナーじゃないから関係ない」と思うのは早計だ。Mythos級の能力を持つモデルが他社からも出てくるのは時間の問題だとAnthropicは明言している。

### 5.1 セキュリティ対策の優先度マトリクス

前回記事のリストを、Project Glasswingの情報を踏まえて更新した。

| 優先度 | カテゴリ | 具体的アクション | 理由 |
| --- | --- | --- | --- |
| 最優先 | OSS依存関係 | `pip-audit` / `npm audit` を**CI/CDに必須で組み込む** | Mythosが全主要OSのOSSに脆弱性を発見した |
| 最優先 | インフラ設定 | S3・CMS・GitHubのパブリック設定を**今週中に棚卸し** | Anthropic自身がCMS設定ミスで漏洩した教訓 |
| 高 | SAST導入 | Semgrep / CodeQL をCIパイプラインに統合 | AIが見つける前に自分で見つける |
| 高 | カーネル・OS更新 | Linux・FreeBSD・OpenBSDの最新パッチを即時適用 | Mythos発見の脆弱性パッチが順次リリースされる |
| 中 | [LLM](https://qiita.com/GeneLab_999/items/7f1bd2de313bdd7ca423)アプリ防御 | プロンプトインジェクション対策・出力サニタイズ | AIが高度化すればLLMアプリへの攻撃も高度化する |
| 中 | SBOM管理 | ソフトウェア部品表の作成・維持 | 脆弱性発見のスピードが上がれば影響範囲の特定も高速化が必要 |
| 継続 | 脅威インテリジェンス | CVE/NVDの監視体制を構築 | Mythos発見のCVEが今後大量にリリースされる |

### 5.2 「自分のコードベースをAIで守る」実践スクリプト

Mythos Previewは使えなくても、既存のツールで防御レベルを上げることはできる。以下は[Python](https://qiita.com/GeneLab_999/items/7079f3a09caf511825ff)ベースのセキュリティ監査自動化スクリプトの概念実装だ。

```
#!/usr/bin/env python3
"""
セキュリティ監査自動化スクリプト（概念実装）
Project Glasswingの教訓を踏まえた多層防御アプローチ

使い方:
    python security_audit.py --target ./your_project
    python security_audit.py --target ./your_project --ci  # CI/CDモード
"""

import subprocess
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime

@dataclass
class Finding:
    """検出された脆弱性を表すデータクラス"""
    tool: str
    severity: str  # critical / high / medium / low
    description: str
    file_path: str = ""
    line_number: int = 0
    cve_id: str = ""

@dataclass
class AuditReport:
    """監査レポートの集約"""
    timestamp: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )
    findings: list[Finding] = field(default_factory=list)
    tools_executed: list[str] = field(default_factory=list)
    tools_failed: list[str] = field(default_factory=list)

    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "critical")

    @property
    def high_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "high")

    def should_block_ci(self) -> bool:
        """CI/CDでブロックすべきかの判定"""
        return self.critical_count > 0 or self.high_count > 5

def run_pip_audit(target: Path) -> list[Finding]:
    """依存パッケージの既知CVEをスキャン"""
    findings = []
    req_file = target / "requirements.txt"
    if not req_file.exists():
        return findings

    result = subprocess.run(
        ["pip-audit", "-r", str(req_file), "-f", "json"],
        capture_output=True, text=True
    )
    if result.returncode != 0 and result.stdout:
        try:
            data = json.loads(result.stdout)
            for vuln in data.get("dependencies", []):
                for v in vuln.get("vulns", []):
                    findings.append(Finding(
                        tool="pip-audit",
                        severity="high",
                        description=f"{vuln['name']}=={vuln['version']}: {v['id']}",
                        cve_id=v.get("aliases", [""])[0]
                    ))
        except json.JSONDecodeError:
            pass
    return findings

def run_bandit(target: Path) -> list[Finding]:
    """Python特化のセキュリティ静的解析"""
    findings = []
    result = subprocess.run(
        ["bandit", "-r", str(target), "-f", "json", "-q"],
        capture_output=True, text=True
    )
    if result.stdout:
        try:
            data = json.loads(result.stdout)
            severity_map = {"HIGH": "high", "MEDIUM": "medium", "LOW": "low"}
            for issue in data.get("results", []):
                findings.append(Finding(
                    tool="bandit",
                    severity=severity_map.get(
                        issue.get("issue_severity", ""), "low"
                    ),
                    description=issue.get("issue_text", ""),
                    file_path=issue.get("filename", ""),
                    line_number=issue.get("line_number", 0)
                ))
        except json.JSONDecodeError:
            pass
    return findings

def run_semgrep(target: Path) -> list[Finding]:
    """パターンベースの脆弱性検出"""
    findings = []
    result = subprocess.run(
        [
            "semgrep", "scan",
            "--config", "auto",
            "--json",
            str(target)
        ],
        capture_output=True, text=True
    )
    if result.stdout:
        try:
            data = json.loads(result.stdout)
            for r in data.get("results", []):
                sev = r.get("extra", {}).get("severity", "WARNING")
                severity_map = {"ERROR": "high", "WARNING": "medium", "INFO": "low"}
                findings.append(Finding(
                    tool="semgrep",
                    severity=severity_map.get(sev, "low"),
                    description=r.get("extra", {}).get("message", ""),
                    file_path=r.get("path", ""),
                    line_number=r.get("start", {}).get("line", 0)
                ))
        except json.JSONDecodeError:
            pass
    return findings

def generate_report(report: AuditReport) -> str:
    """人間が読めるレポートを生成"""
    lines = [
        f"=== セキュリティ監査レポート ===",
        f"実行日時: {report.timestamp}",
        f"実行ツール: {', '.join(report.tools_executed)}",
        f"失敗ツール: {', '.join(report.tools_failed) or 'なし'}",
        f"",
        f"--- 検出サマリー ---",
        f"  Critical: {report.critical_count}",
        f"  High:     {report.high_count}",
        f"  Medium:   {sum(1 for f in report.findings if f.severity == 'medium')}",
        f"  Low:      {sum(1 for f in report.findings if f.severity == 'low')}",
        f"  合計:     {len(report.findings)}",
        f"",
    ]

    if report.critical_count > 0 or report.high_count > 0:
        lines.append("--- Critical / High の詳細 ---")
        for f in report.findings:
            if f.severity in ("critical", "high"):
                loc = f"{f.file_path}:{f.line_number}" if f.file_path else "N/A"
                lines.append(f"  [{f.severity.upper()}] ({f.tool}) {f.description}")
                lines.append(f"    場所: {loc}")
                if f.cve_id:
                    lines.append(f"    CVE: {f.cve_id}")
                lines.append("")

    return "\n".join(lines)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="セキュリティ監査スクリプト")
    parser.add_argument("--target", required=True, help="スキャン対象ディレクトリ")
    parser.add_argument("--ci", action="store_true", help="CI/CDモード（critical検出時に非ゼロ終了）")
    args = parser.parse_args()

    target = Path(args.target)
    report = AuditReport()

    # 各ツールを順番に実行
    scanners = [
        ("pip-audit", run_pip_audit),
        ("bandit", run_bandit),
        ("semgrep", run_semgrep),
    ]

    for name, scanner in scanners:
        try:
            findings = scanner(target)
            report.findings.extend(findings)
            report.tools_executed.append(name)
        except FileNotFoundError:
            report.tools_failed.append(f"{name}（未インストール）")

    # レポート出力
    print(generate_report(report))

    # CI/CDモード: critical/high過多で非ゼロ終了
    if args.ci and report.should_block_ci():
        print(f"\n[BLOCKED] Critical: {report.critical_count}, High: {report.high_count}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### 5.3 トラブルシューティング ─ 「Mythosが見つけそうな」脆弱性パターン

Mythos Previewが得意とする脆弱性パターンを知ることで、自分のコードを先回りして守れる。

| パターン | 概要 | 検出方法 | 対策 |
| --- | --- | --- | --- |
| メモリ安全性違反 | バッファオーバーフロー、Use-After-Free | AddressSanitizer、Valgrind | Rustへの移行検討、bounds check徹底 |
| 入力検証不備 | SQLi、コマンドインジェクション | Semgrep、bandit | パラメータバインド必須化、入力サニタイズ |
| 認証・認可の不整合 | 権限昇格、IDOR | 手動コードレビュー + SAST | RBAC/ABACの設計レビュー |
| 暗号化の不適切な使用 | 弱い暗号、ハードコードされた鍵 | Semgrep `crypto` ルール | 最新の暗号ライブラリ使用、鍵管理の外部化 |
| 依存関係の脆弱性 | 既知CVEのある古いライブラリ | `pip-audit` / `npm audit` | 定期的なdependency update + Renovate/Dependabot |
| **脆弱性の連鎖** | 単体では軽微だが組み合わせで重大 | **ペネトレーションテスト** | 多層防御（Defense in Depth）の徹底 |

最後の「脆弱性の連鎖」が特に重要だ。Mythos Previewが得意としている、**3〜5つの軽微なバグを組み合わせてroot権限を奪取する**パターンは、従来の自動スキャナでは検出が困難だ。ここが人間のセキュリティエンジニアとAIの境界線であり、Project Glasswingが存在する理由でもある。

---

## 6. 「これからのセキュリティ」はどう変わるのか

### 6.1 Anthropicのロードマップ

公式発表から読み取れるAnthropicの計画:

1. **現在**: Mythos Previewをパートナー限定で提供し、重要インフラの脆弱性を修正
2. **次のステップ**: 新しいセーフガード（危険な出力を検知・ブロックする仕組み）を開発
3. **セーフガードの導入**: **今後リリース予定のClaude Opusモデル**にまずセーフガードを搭載（Mythosほどのリスクがないモデルで洗練する）
4. **最終目標**: Mythosクラスのモデルを安全にスケール展開可能にする

つまり、**次のOpusアップデートにセキュリティ関連のセーフガードが組み込まれる**ことが示唆されている。これは全Claudeユーザーに影響する話だ。

### 6.2 エンジニアの仕事はどう変わるか

| 時間軸 | 変化 | エンジニアへの影響 |
| --- | --- | --- |
| 今（2026 Q2） | Glasswingパートナーが自社コードを大規模スキャン | 主要OSSのセキュリティパッチが大量リリースされる。**更新対応が急務** |
| 半年後 | Mythosクラスの能力が他社モデルにも波及 | 脆弱性発見のスピードが加速。パッチサイクルが「週」→「日」に圧縮される可能性 |
| 1年後 | AI駆動ペネトレーションテストが標準化 | セキュリティエンジニアの役割が「バグを見つける人」から「AIの発見をトリアージ・優先順位付けする人」にシフト |

### 6.3 ユースケース別ガイド

#### ユースケース1: OSSメンテナー

あなたのプロジェクトがProject Glasswingのスキャン対象になっている可能性がある。Linux Foundation経由で脆弱性レポートが届く可能性があるため、セキュリティ連絡先（SECURITY.md）を整備しておこう。

```
# SECURITY.md のテンプレート

## 脆弱性の報告方法

セキュリティ脆弱性を発見した場合は、公開Issueではなく以下に連絡してください:
- Email: security@your-project.example.com
- PGP Key: [公開鍵のURL]

## 対応プロセス

1. 報告受領後 48時間以内に確認の返信
2. 72時間以内に影響範囲の初期評価
3. パッチ準備完了後、報告者と調整してCVE発行・公開
```

#### ユースケース2: プロダクション環境の運用者

FreeBSD NFSやLinuxカーネルの脆弱性が発見されたことを踏まえ、以下の点検を推奨する。

```
# Linuxカーネルの現在のバージョン確認
uname -r

# セキュリティアップデートの確認（Ubuntu/Debian）
sudo apt update && sudo apt list --upgradable 2>/dev/null | grep -i security

# FreeBSDのセキュリティアドバイザリ確認
# freebsd-update fetch && freebsd-update install

# 不要なネットワークサービスの確認
ss -tlnp  # TCP LISTENポート一覧
```

#### ユースケース3: [LLM](https://qiita.com/GeneLab_999/items/7f1bd2de313bdd7ca423)アプリ開発者

Mythosの能力を考えると、LLMアプリへの攻撃もこれまで以上に洗練される。OWASP LLM Top 10を参照し、最低限以下を確認しよう。

```
# LLMアプリのプロンプトインジェクション対策（概念コード）

import re

# 危険なパターンのブロックリスト
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"system\s*:\s*you\s+are",
    r"<\s*script\s*>",
    r"\bexec\s*\(",
    r"\beval\s*\(",
    r"__import__",
]

def sanitize_user_input(user_input: str) -> tuple[str, bool]:
    """
    ユーザー入力のサニタイズ
    Returns: (sanitized_input, is_suspicious)
    """
    is_suspicious = False
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, user_input, re.IGNORECASE):
            is_suspicious = True
            break

    # 基本的なサニタイズ（HTMLエスケープ等）
    sanitized = user_input.replace("<", "&lt;").replace(">", "&gt;")

    return sanitized, is_suspicious
```

---

## 7. 学習ロードマップ

Project Glasswingの背景を深く理解するためのステップ:

### Level 1: AIセキュリティの基礎

### Level 2: セキュリティツールの実践

* **Semgrep**: OSSの静的解析ツール。CI/CDへの統合が容易
* **bandit**: [Python](https://qiita.com/GeneLab_999/items/7079f3a09caf511825ff)特化のセキュリティスキャナ
* **pip-audit / npm audit**: 依存パッケージのCVEスキャン
* **CodeQL**: GitHubが提供するセマンティック解析エンジン

### Level 3: 前回記事からの発展

### Level 4: 最前線を追い続ける

* Anthropic Frontier Red Teamブログ（red.anthropic.com）のフォロー
* NVD（National Vulnerability Database）の定期チェック
* Project Glasswingから公開される知見のウォッチ

---

## まとめ ── 免疫革命の始まり

前回の記事では、**最強の錠前師の設計図が無施錠の工房から漏れた**という皮肉を伝えた。

今回の記事は、その続編だ。Anthropicは皮肉を皮肉のまま終わらせなかった。「漏れたなら、正面から出す。ただし味方にだけ先に渡す」という戦略で応答した。

整理するとこうだ:

1. **Mythos Previewは「全ての主要OSとブラウザ」に数千件の脆弱性を発見した** ── 27年間放置されたOpenBSDのバグも含む
2. **発見された脆弱性の99%以上がまだパッチされていない** ── これが「緊急の試み」と呼ばれる理由
3. **モデルは「テストされていることを察知して手を抜く」振る舞いを見せた** ── AIの安全性評価そのものが問い直されている
4. **Apple・Microsoft・Google・AWS・NVIDIAが一斉にパートナーとして名乗りを上げた** ── 業界が「これは本物だ」と認めた証拠
5. **一般公開はされないが、Mythosクラスの能力は他社モデルにも波及する** ── 準備の時間は今しかない

個人的に最も印象に残ったのは、Nicholas Carliniの「ここ数週間で見つけたバグの数は、私の人生で見つけた全てのバグを合わせたより多い」という一言だ。世界トップクラスのセキュリティ研究者のキャリア全体を、AIが数週間で上回った。

免疫システムが劇的にアップグレードされた。問題は、その免疫システムを使いこなせるかどうかだ。エンジニアとしてやるべきことは、今日のコードの脆弱性を今日のツールで潰すこと。そしてProject Glasswingから公開される知見を吸収して、明日のコードをもっと堅くすること。

Mythosが一般公開される頃に「あの時対策しておいてよかった」と言えるかどうかは ── 前回も書いたが ── **今日の選択次第だ。**

---

## 参考文献

---

この記事が参考になった方は、いいね・ストックをもらえると次の記事を書くモチベになります。

AIセキュリティ関連の最新情報は以下でも発信しています:

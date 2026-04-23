---
id: "2026-03-29-今日の深掘りclaudeのcomputer-use研究プレビュー-01"
title: "今日の深掘り：Claudeの「Computer Use研究プレビュー」"
url: "https://note.com/nekopy222/n/n626a490f5cec"
source: "note"
category: "ai-workflow"
tags: ["note"]
date_published: "2026-03-29"
date_collected: "2026-03-29"
summary_by: "auto-rss"
---

## 今日の深掘りテーマ

## ① 今回何が変わったか

Anthropicは2026年3月23日に、Claude CoworkとClaude Codeで\*\*Claudeがユーザーのコンピュータを直接操作できる「Computer Use」\*\*を研究プレビューとして公開した。Claudeはコネクタがない場面でも、画面上を見てクリック、入力、ブラウザ操作、ファイルを開く、開発ツールを走らせる、といった動作を実行できるようになった。[1](https://support.claude.com/en/articles/14128542-let-claude-use-your-computer-in-cowork)

今回の更新の中心は、単に「画面を見られる」ことではなく、**CoworkとClaude Codeに実務レベルの代理操作を持ち込んだこと**にある。公式説明では、まずSlackやGoogle Calendarのようなコネクタを優先し、使える専用接続がないときにブラウザ操作や画面操作へ切り替える設計だ。つまりComputer Useは、最初から全部を画面操作で片付ける機能ではなく、既存のツール接続を補完する最後の手段として位置づけられている。[2](https://support.claude.com/en/articles/13947068-assign-tasks-to-claude-from-anywhere-in-cowork)

公開範囲はかなり明確で、**ProとMax限定の研究プレビュー**だ。Claude Desktop上で有効化して使う方式で、公式ヘルプでは**macOS対応、Windows対応は近日予定**と案内されている。一方で、Dispatch自体は要件として**Claude DesktopのmacOSまたはWindows x64**を挙げており、スマホからデスクトップ上のClaudeへ仕事を投げる流れも同時に強化された。[2](https://support.claude.com/en/articles/12138966-release-notes) ここはやや混同しやすいが、DispatchとComputer Useは関連機能でありつつ、提供条件は同一ではない。

注目点は、Anthropicがこの機能を\*\*「早いが未完成」ではなく「便利だが危険を伴う初期段階」\*\*として前面に出しているところだ。公式は、Claudeが明示的な許可を求めること、アプリ単位の権限管理があること、プロンプトインジェクション対策を入れていることを説明しつつも、複雑なタスクではやり直しが必要で、画面経由は直接統合より遅いと認めている。[2](https://support.claude.com/en/articles/13364135-use-cowork-safely)

## ② 以前と何が違うか

これまでのClaudeでも、CoworkやClaude Codeによってファイル操作やエージェント的な作業委譲は進んでいたが、基本は**仮想環境・接続済みツール・端末内ファイルへのアクセス**が中心だった。2026年1月時点のCoworkは、ローカルで動く隔離VMを使いながらファイルやMCP連携を扱う設計として案内されていた。[6](https://support.claude.com/en/articles/10065433-installing-claude-desktop)

今回の更新で変わったのは、その外側に出て**実際のデスクトップやアプリを直接触れる段階に進んだこと**だ。公式安全ガイドでも、Computer Useは通常のCoworkが使う仮想マシンの外で動き、実際のデスクトップとアプリに触れるため、追加のリスクがあると明記している。[5](https://support.claude.com/en/articles/13364135-use-cowork-safely) ここが以前との最大差で、便利さの源泉でもあり、同時に導入判断が難しくなる理由でもある。

また、3月17日に追加されたDispatchとの組み合わせで、スマホから「朝のメール整理」「指標の取りまとめ」「レポート作成」「PR準備」などを投げ、デスクトップ側でClaudeに走らせる流れが現実的になった。単体の画面操作より、**継続スレッド＋デスクトップ代理実行**という運用全体の変化が大きい。[3](https://support.claude.com/en/articles/12138966-release-notes)

外部報道でも焦点はそこにある。The Vergeは、今回の更新を「不在時でもユーザーのコンピュータを使ってタスクを進める機能」と整理し、TechCrunchは自律度を高めつつも安全レイヤーを残した実装だと評価している。[7](https://techcrunch.com/2026/03/24/anthropic-hands-claude-code-more-control-but-keeps-it-on-a-leash/) つまり以前より賢くなったというより、**Claudeが作業対象へ近づいた**更新と見るのが正確だ。

## ③ 無料でどこまで使えるか

無料プランでは、このテーマの中心であるComputer Useは使えない。公式ヘルプは**Pro / Maxのみ**と明記しており、現在の制限事項として**Team / Enterpriseにも未提供**と書いている。[2](https://support.claude.com/en/articles/14128542-let-claude-use-your-computer-in-cowork) そのため、無料ユーザーが今回の話題から直接得られるものは多くない。

料金面では、Claude公式価格ページで**Proは年払い換算で月17ドル、月払いで20ドル、Maxは月100ドルから**となっている。ProにはCoworkとClaude Codeが含まれ、MaxはPro比で5倍または20倍の利用枠、高い出力上限、高トラフィック時の優先アクセス、先行機能アクセスが付く。[9](https://claude.com/pricing/max)

ここで注意したいのは、**Coworkそのものは有料全般に広がっていても、Computer Useはその中の限定機能**だという点だ。Claude Desktopの案内では、Cowork自体はPro / Max / Team / Enterpriseの有料プランで使える研究プレビューとなっているが、Computer Useは別枠でPro / Max限定である。[2](https://support.claude.com/en/articles/10065433-installing-claude-desktop) したがって「CoworkがあるからTeamでも同じ」とは言えない。

導入コストの感覚としては、Proは個人が試す入口、Maxは本格的にデスクトップ委譲を回す人向けだ。今回の更新価値は「高性能な会話」より「作業の肩代わり」なので、無料からの比較対象は通常チャット機能ではなく、**どこまで反復作業を渡せるか**になる。[2](https://claude.com/pricing)

## ④ 副業・マネタイズでの活かし方

今回の更新は、副業で複数アプリをまたぐ単純だが手間の大きい作業に向いている。たとえば、ローカルの原稿フォルダを確認し、Slackやメールの情報を集め、表計算に転記し、下書きを整えてレポート化する、といった**橋渡し作業**はこれまで人が細かく触る必要があった。Computer Useはそこを埋める。[2](https://support.claude.com/en/articles/13947068-assign-tasks-to-claude-from-anywhere-in-cowork)

情報発信では、ネタ整理や週次レポート作成との相性が良い。Dispatchの説明では、スマホから依頼し、完了時に結果を受け取る形が想定されているため、移動中に依頼して作業席に戻ったときに素材が整っている運用が作りやすい。[3](https://support.claude.com/en/articles/12138966-release-notes) 価値が出るのは「文章生成そのもの」より、**生成前後の収集・整形・移送**だ。

開発寄りの副業ではさらに分かりやすい。公式ブログは、IDEの変更、テスト実行、PR作成のような使い方を例示している。[1](https://claude.com/blog/dispatch-and-computer-use) 既存のClaude Codeはターミナル中心だったが、画面やアプリも含めて触れることで、CLIだけでは閉じない作業までClaude側へ渡しやすくなった。これは小規模受託や保守案件で、地味に時間を食う確認・転記・補助操作の短縮に直結する。

一方で、金銭や契約や医療データに関わる運用は、収益化目的でも避けるべきだ。公式は金融、法務、医療、他人の個人情報を含むアプリへの利用を強く非推奨としており、スクリーンショット取得や画面横断の副作用も認めている。[2](https://support.claude.com/en/articles/13364135-use-cowork-safely) 収益に直結するからこそ、**安全に渡せる低リスク工程へ限定する**のが現実的な使い方になる。

## ⑤ 向いている人・向いていない人

### 向いている人

向いているのは、毎日同じ種類の“つなぎ作業”を繰り返している人だ。具体的には、複数ツールを横断するリサーチ、日次レポート、簡単な資料化、開発の補助操作、ローカルファイル整理のような作業がある人に合う。[1](https://support.claude.com/en/articles/14128542-let-claude-use-your-computer-in-cowork)[3](https://support.claude.com/en/articles/13947068-assign-tasks-to-claude-from-anywhere-in-cowork)

また、スマホから仕事を投げて、デスクトップ側で片づけたい人にも向く。Dispatchは永続スレッドで文脈を保持するため、1回ごとの使い捨てではなく、継続タスクとの相性がある。[3](https://support.claude.com/en/articles/12138966-release-notes) この点は単発のチャットAIでは代替しにくい。

### 向いていない人

向いていないのは、AIに金融・法務・医療・個人情報処理を触らせたい人だ。Anthropic自身が、Computer Useはスクリーンショットを撮って画面を理解し、仮想マシン外で実デスクトップに触るため、機密性の高い用途は避けるべきだとしている。[2](https://support.claude.com/en/articles/13364135-use-cowork-safely)

また、無料プラン前提の人にも現時点では向かない。今回の目玉は有料限定で、しかも研究プレビューなので、完成度より先行体験を買う側面が強い。[2](https://claude.com/pricing) さらに、速さと確実性を最優先する人も慎重に見るべきだ。公式は、複雑なタスクは再試行が必要で、画面操作はコネクタより遅いと説明している。[2](https://support.claude.com/en/articles/14128542-let-claude-use-your-computer-in-cowork)

## ⑥ 今後どう使い分けるべきか

使い分けの基本は明快で、**コネクタで済む仕事はコネクタ、CLIで済む仕事はClaude Code、画面に閉じた仕事だけComputer Use**が自然だ。公式も、最初にコネクタ、次にブラウザ、最後に画面操作という順序を示している。[2](https://support.claude.com/en/articles/14128542-let-claude-use-your-computer-in-cowork) つまりComputer Useを主役にするより、穴埋め役として使う方が失敗しにくい。

個人用途では、まずProで試して、定着したらMaxを考える順番が妥当だ。Maxの価値は上位機能そのものより、**高トラフィック時の優先枠と大きい利用枠**にある。[9](https://claude.com/pricing/max) 日々の定型業務を実際に投げる段階で、Proの上限や待ち時間が気になるかが分岐点になる。

競合比較で見ると、今回のClaudeは「回答精度」より**代理実行の実務性**で勝負している。TechCrunchはClaude Codeのauto modeもあわせて、自律性を高めつつ安全層を残す方向を指摘している。[8](https://techcrunch.com/2026/03/24/anthropic-hands-claude-code-more-control-but-keeps-it-on-a-leash/) そのため、他AIを調査・要約用途で使い、Claudeを“最後の操作担当”として置く組み合わせも十分あり得る。

今後の実務では、AIを「聞く道具」から「操作を引き受ける道具」へ分けて考える必要がある。今回の更新はその境目をはっきりさせた。Claudeに向くのは、文章品質の比較だけではなく、**どこまで自分の代わりに触らせたいか**で選ぶ場面だ。[1](https://support.claude.com/en/articles/14128542-let-claude-use-your-computer-in-cowork)[7](https://www.theverge.com/ai-artificial-intelligence/899430/anthropic-claude-code-cowork-ai-control-computer)

## ⑦ 導入判断まとめ（意思決定用）

今すぐ試す価値が高いのは、2026年3月23日時点の研究プレビューでも、**低リスクな反復作業を毎日持っている個人ユーザー**だ。Proで試し、スマホからデスクトップへ投げるDispatchも併用すると、今回の更新価値が一番見えやすい。[1](https://support.claude.com/en/articles/13947068-assign-tasks-to-claude-from-anywhere-in-cowork)[4](https://claude.com/pricing)

様子見が妥当なのは、チーム全体導入を考えている人や、監査・ログ・規制対応が必要な人だ。公式安全ガイドでは、Cowork活動は監査ログやデータエクスポートに載らず、規制業務には使うべきでないとしている。[5](https://support.claude.com/en/articles/13364135-use-cowork-safely) 加えてComputer Use自体はTeam / Enterprise未提供なので、組織導入前提ではまだ早い。[2](https://support.claude.com/en/articles/14128542-let-claude-use-your-computer-in-cowork)

見送りでよいのは、無料プラン前提、または機密データや金融・契約・医療情報を触らせたいケースだ。今回の更新は話題性が高いが、導入効果より事故コストが上回る領域がはっきりしている。[2](https://support.claude.com/en/articles/13364135-use-cowork-safely) 判断基準は単純で、**任せたい作業が可逆で低リスクかどうか**で切るのがよい。

## ⑧ 総合所感

2026年3月23日のAnthropic公式発表は、単なる新機能追加ではなく、Claudeの立ち位置を**会話AIからデスクトップ作業エージェントへ一段進めた更新**として見る価値がある。[1](https://support.claude.com/en/articles/14128542-let-claude-use-your-computer-in-cowork) しかも3月17日のDispatch強化と連続しており、同じ週の流れとして読むと意味が大きい。[3](https://support.claude.com/en/articles/12138966-release-notes)

今これを扱う価値がある理由は、2026年3月24日から29日にかけて外部メディアも連続して取り上げ、TechCrunchは購読増の要因としてまで言及しているからだ。[7](https://techcrunch.com/2026/03/24/anthropic-hands-claude-code-more-control-but-keeps-it-on-a-leash/)[12](https://techcrunch.com/2026/03/28/anthropics-claude-popularity-with-paying-consumers-is-skyrocketing/) つまり今回の話題性は、派手なデモ映えだけではなく、**有料ユーザーが実際にお金を払う理由になり始めている**ところにある。

総じて、今回のComputer Useは「万能AI」ではない。速さも確実性もまだ専用統合に劣るし、扱ってよい領域も狭い。[2](https://support.claude.com/en/articles/13364135-use-cowork-safely) それでも、反復的な低リスク作業をデスクトップごと渡せる世界観は、2026年3月23日の更新として十分に重い。今後のAI比較は、回答の上手さだけでなく、**どこまで安全に肩代わりできるか**へ軸が移っていく。

---

## 関連書籍

AIエージェントや実装寄りの流れをまとめて掴みたい人向けです。  
※アフィリエイトリンクを含みます。

---

## ⑨ 公式情報・参照先

---

※アフィリエイトリンクを含みます

---

[#Claude](https://note.com/hashtag/Claude) [#ClaudeComputerUse](https://note.com/hashtag/ClaudeComputerUse) [#ClaudeCowork](https://note.com/hashtag/ClaudeCowork) [#ClaudeCode](https://note.com/hashtag/ClaudeCode) [#AIアップデート](https://note.com/hashtag/AI%E3%82%A2%E3%83%83%E3%83%97%E3%83%87%E3%83%BC%E3%83%88) [#AIエージェント](https://note.com/hashtag/AI%E3%82%A8%E3%83%BC%E3%82%B8%E3%82%A7%E3%83%B3%E3%83%88) [#AI活用](https://note.com/hashtag/AI%E6%B4%BB%E7%94%A8) [#副業活用](https://note.com/hashtag/%E5%89%AF%E6%A5%AD%E6%B4%BB%E7%94%A8) [#今日の深掘り](https://note.com/hashtag/%E4%BB%8A%E6%97%A5%E3%81%AE%E6%B7%B1%E6%8E%98%E3%82%8A) [#ClaudeのComputerUse研究プレビュー](https://note.com/hashtag/Claude%E3%81%AEComputerUse%E7%A0%94%E7%A9%B6%E3%83%97%E3%83%AC%E3%83%93%E3%83%A5%E3%83%BC)

---
id: "2026-07-13-claude-codeでapexのテストクラスを自動生成使える場面と落とし穴-01"
title: "Claude CodeでApexのテストクラスを自動生成──使える場面と落とし穴"
url: "https://zenn.dev/muranyanta/articles/sf-20260713-c3cc9f"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-07-13"
date_collected: "2026-07-14"
summary_by: "auto-rss"
query: ""
---

## Claude CodeでApexテストを自動生成──期待と現実のギャップ

結論から言うと、Claude CodeはApexのテストクラス生成に「使える」。ただし全面的にではなく、対象を選べば、という条件付きです。単純なメソッドの骨組みなら確かに速い。一方で、外部連携やガバナ制限を意識した複雑なテストになると、生成物のレビューに時間を取られて、結局自分で書いた方が早かった、という場面もそれなりにありました。

私はApex/LWC開発を10年ほどやっていて、今はClaude Code含むAIツールを日常の開発パイプラインに組み込んで運用しています。その中で、テスト生成は「効果が出る領域」と「逆に工数が増える領域」の差が特に激しいと感じる。この差はAI自動化一般の話ではなく、Apexテスト固有の複雑さ──ガバナ制限、Mock戦略、アサーション粒度──に起因しています。今回はそこを軸に書きます。

まず前提として、Claude CodeはApexの構文もSalesforceのテストパターンもかなり理解しています。`@isTest`、`Test.startTest()`/`Test.stopTest()`、`System.assertEquals` あたりは何も言わなくても出してくる。問題はそこではなく、「このメソッドが本当に検証すべきことは何か」「どこにガバナの罠があるか」という判断のほう。ここはAIが最も苦手とするところです。

自動生成に無警戒に頼ると何が起きるか。カバレッジは通るけど中身がスカスカのテストが量産されます。75%の壁は越えるけど、いざリファクタしたときに何も検知してくれないテスト。これはレビュー負荷が逆に上がるパターンで、「生成→レビューで全書き直し」という一番損なワークフローに陥る。

なので実務では、AIを「テストを完成させる道具」ではなく「骨組みとデータ構築の下書きを出す道具」として使うのが現実的、というのが今の私の運用です。

## Claude Codeが得意な場面：単純CRUD・バリデーションのテスト

得意な領域ははっきりしています。外部依存がなく、入力と出力の関係が閉じているメソッド。たとえば入力値のバリデーションや、Standard Objectへの単純なInsert/Update、ユーティリティ的な変換ロジックあたり。

例として、金額に応じて割引率を返すだけのシンプルなロジックを渡してみます。生成されたテストがこれ。骨組みとして十分使えるレベルでした。

```
// 対象メソッド: DiscountCalculator.getRate(Decimal amount)
// 生成されたテスト。境界値を自分で拾ってくるのが地味に助かる点。
@isTest
private class DiscountCalculatorTest {
    @isTest
    static void getRate_belowThreshold_returnsZero() {
        Test.startTest();
        Decimal rate = DiscountCalculator.getRate(9999);
        Test.stopTest();
        System.assertEquals(0, rate, '閾値未満は割引なし');
    }

    @isTest
    static void getRate_atThreshold_returnsTenPercent() {
        Decimal rate = DiscountCalculator.getRate(10000);
        System.assertEquals(0.1, rate, '閾値ちょうどは10%');
    }
}
```

`Test.startTest()` の位置や境界値（9999と10000）を自分で拾ってくるのは評価できる。閾値ちょうどのケースを忘れがちな人間より、むしろ抜けが少ないくらいです。この手の純粋関数に近いメソッドなら、8割方そのまま使えました。

工数削減の実感としては、こういう単純メソッドで2〜3割くらい。劇的ではないけど、`@isTest`アノテーションや命名規則をタイプする手間がなくなる分、地味に効く。手元の環境での感覚値なので、コードの性質によって上下します。

## Claude Codeが失敗する場面：Mock戦略・依存関係・ガバナ考慮

問題はここから。外部連携が絡んだ瞬間に精度が落ちます。

HttpCalloutを含むメソッドのテストを頼むと、`HttpCalloutMock` の実装は出してくるものの、`CalloutException` 系の異常系や、レスポンスのステータスコード別の分岐までは踏み込んでくれないことが多い。「正常系のモックは作ったけど、タイムアウトや500エラーのテストがない」という状態になりがちです。

もっと厄介なのが複数オブジェクトの依存関係。たとえばOpportunityを作るにはAccountが要る、AccountにはRecordTypeやカスタム必須項目がある、という前提をAIは平気で読み落とします。生成されたテストをそのまま実行すると`REQUIRED_FIELD_MISSING`や`FIELD_CUSTOM_VALIDATION_EXCEPTION`で落ちる。この前提条件の複雑さは組織のカスタマイズ状況に依存するので、AIには知りようがないんですよね。

そしてガバナ制限。これが一番危ない。AIはバルクテスト用のデータを作るとき、深く考えず200件ループでInsertするようなコードを出すことがあります。それ自体は正しいんだけど、対象メソッドの中にSOQLがループで入っていると、テストデータの作り方次第でテスト側がガバナに引っかかる。「本番コードのガバナ超過を検知したいのに、テストの組み方が甘くて素通りする」あるいは逆に「テストのデータ準備自体が制限超過で落ちる」。この見極めはAIには任せられません。

決定的なのはアサーションの粒度です。AIは「何を検証すべきか」を本質的には理解していない。カバレッジを上げるアサーションは書けても、「このビジネスロジックで絶対に守られるべき不変条件は何か」までは分からない。だからアサーションが `System.assertNotEquals(null, result)` みたいな、通ればいいだけの薄いものになりがち。ここは人間が書くしかない部分です。

## 実務ではどこで線を引くか

じゃあどこで線を引くか。私が実際に使っている判断基準を挙げます。

まず、外部連携を含むか。Callout、Platform Event、`@future`や非同期処理が絡むなら、自動生成の恩恵はかなり薄いと考えて、最初から自分で設計する。骨組みだけAIに出させて残りは全部手動、くらいの割り切りが要ります。

次に、新規か既存か。新規メソッドで、その仕様を自分がちゃんと理解している状態なら、AIに投げても添削しやすい。逆に他人が書いた既存の複雑なメソッドにテストを後付けする場合、AIは表面的な入出力しか見ないので、隠れた副作用を見逃す。この場合はまず自分がコードを読む方が先です。

最後に、テスト行数の見積もり。ざっくり100行以下で収まりそうならAI支援がハマる。200行を超えそう、つまり複数シナリオ・複数Mock・バルクテストが必要なものは、設計から人間がやった方が結局速い。AIに出させて添削する工数が自分で書く工数を上回る分岐点が、私の感覚だとこのあたりです。

要は「添削工数が削減にならないケースを見極める」こと。生成物のレビューに30分かかるなら、20分で自分で書けるテストをAIに頼む意味はない。

## Claude Codeで現実的に運用する

実際のワークフローはステップを分けます。全部一発でやらせない。

まず骨組みとデータ構築だけ生成させて、依存関係とMockは人間が追記する。先ほどのCallout例を、手動で異常系とアサーションを強化するとこうなります。

```
// AIが出した正常系モックに、異常系とアサーション粒度を人間が追加。
// StatusCode別に分けるのは、本番の分岐を検証する目的があるから。
@isTest
private class ExternalSyncServiceTest {
    private class MockFactory implements HttpCalloutMock {
        Integer statusCode;
        String body;
        MockFactory(Integer code, String b) { statusCode = code; body = b; }
        public HTTPResponse respond(HTTPRequest req) {
            HttpResponse res = new HttpResponse();
            res.setStatusCode(statusCode);
            res.setBody(body);
            return res;
        }
    }

    @isTest
    static void sync_serverError_marksRecordFailed() {
        Account a = new Account(Name = 'Test');
        insert a;
        // 500を返して、レコードのステータスが Failed に落ちることまで検証する
        Test.setMock(HttpCalloutMock.class, new MockFactory(500, '{}'));
        Test.startTest();
        ExternalSyncService.sync(a.Id);
        Test.stopTest();

        Account updated = [SELECT Sync_Status__c FROM Account WHERE Id = :a.Id];
        System.assertEquals('Failed', updated.Sync_Status__c,
            'サーバエラー時はステータスをFailedにする契約');
    }
}
```

`System.assertEquals('Failed', ...)` のように「何が守られるべきか」を明記する。ここがAI任せにできない核心で、コメントにビジネス上の意図（契約）を書いておくと、後任がテストの目的を理解できます。

ガバナを意識したデータ量調整も、意図を持って書く。

```
// バルク検証。Limits で SOQL の消費を実測し、
// 「対象メソッドがループ内SOQLになっていない」ことを保証する。
@isTest
static void process_bulkRecords_staysWithinGovernorLimits() {
    List<Account> accts = new List<Account>();
    for (Integer i = 0; i < 200; i++) {
        accts.add(new Account(Name = 'Bulk ' + i));
    }
    insert accts;

    Test.startTest();
    Integer before = Limits.getQueries();
    AccountProcessor.process(accts);
    Integer used = Limits.getQueries() - before;
    Test.stopTest();

    System.assert(used <= 5, 'クエリ数が件数比例していないこと: ' + used);
}
```

`Limits.getQueries()` で実測してアサーションを張ると、将来ループ内SOQLを埋め込む変更が入ったときに落ちてくれる。カバレッジだけでは検知できない回帰を防ぐ狙いです。これはAIが自発的には書かない発想でした。

チーム運用では、テストコンベンションをプロンプトに固定しておくと生成物のブレが減ります。私が使っているテンプレートの骨子はこんな感じ。

```
# Apexテスト生成ルール
- テストメソッド名は method_condition_expected の形式
- テストデータは TestDataFactory クラスのメソッドを使う（直接insertしない）
- 各アサーションには第3引数で日本語の検証意図を必ず書く
- Test.startTest/stopTest はテスト対象の呼び出しだけを囲む
- 異常系（例外・空リスト・null）を最低1ケース含める
- @isTest(SeeAllData=true) は使わない
```

「異常系を最低1ケース」を明文化しておくだけで、正常系だけ出してくる問題がかなり減ります。TestDataFactory経由を強制するのも、依存項目の抜けを防ぐため。

長期運用で気をつけているのは、AIに頼りすぎると例外ハンドリングの甘いテストが静かに増えること。カバレッジは維持されるので気づきにくい。定期的に「異常系アサーションが薄いテスト」を人間の目で棚卸しする運用は、今のところ外せません。

## 次の一手──Claude Codeの先

AI補助テストと人間設計テストは、どちらか一方ではなく両方要る、というのが現時点の私の立場です。単純メソッドは骨組みをAIに任せて浮いた時間を、複雑な連携テストの設計に回す。この配分が一番効率がいい。

保守コストを本気で下げたいなら、AIより先にやることがあります。`TestDataFactory` のようなテストデータ構築の共通ライブラリを整備すること。依存関係の複雑さは組織固有なので、そこを人間が一度きれいに部品化しておけば、AIが出すコードもそのライブラリを呼ぶだけになって精度が上がる。AI活用の前提としての土台づくり、という順番です。

将来、Apexとメタデータの依存構造を学習した専用モデルが出てくれば、ガバナや依存関係の読み落としも減って話は変わるかもしれません。ただ執筆時点（2026年7月、Salesforceは Summer '26 の時期）のClaude Codeは、あくまで賢い下書き係。判断の主体は人間側に置く前提で使うのが、いちばん裏切られない使い方だと思っています。

---
id: "2026-07-11-claude-fable-5-が教えてくれた-fastenum-の高速化テクニック-1-文字列のハッ-01"
title: "Claude Fable 5 が教えてくれた FastEnum の高速化テクニック (1) - 文字列のハッシュ値生成"
url: "https://zenn.dev/xin9le/articles/6fb2045805996c"
source: "zenn"
category: "ai-workflow"
tags: ["API", "zenn"]
date_published: "2026-07-11"
date_collected: "2026-07-12"
summary_by: "auto-rss"
query: ""
---

数日前、[@neuecc](https://github.com/neuecc) 先生が Claude Fable 5 を利用したパフォーマンスチューニング手法を投稿してました。それを読んで「できるところから真似してみよう！」と思い立ち、早速やってみました。

<https://neue.cc/2026/07/06_highperformancecode_with_ai.html>

で、実際に上記の記事が投稿された日から 2 日ほど Fable をぶん回してみたら出るわ出るわw 「.NET 界最速の enum ユーティリティ」を狙ってここまでやってきたけれど、まだまだやれることがあったんですね...(ぴえん。ということで (？) ひとつの記事で解説するにはだいぶ長くなってしまうので、記事を分離してちょっとずつ書いていこうと思います。

初回は**文字列のハッシュ値生成の独自実装**について解説していきます。FastEnum では、`.TryParse()` や `.IsDefined(string)` の内部実装のために文字列から値を Lookup するための辞書を自作しています。.NET 標準の辞書だとだいぶ遅いので自作もやむなし。このとき辞書内で文字列のハッシュ値を取得する必要がありますが、ここに独自のハッシュ関数を実装することで高速化したというお話です。

<https://github.com/xin9le/FastEnum/pull/94>

# 大文字/小文字の区別あり

## 改善前

まずは Case Sensitive な文字列に対する実装について。これは非常にシンプルで `string.GetHashCode()` を呼び出しているだけでした。

CaseSensitive.GetHashCode() : 改善前

```
public static class CaseSensitive
{
    [MethodImpl(MethodImplOptions.AggressiveInlining)]
    public static int GetHashCode(ReadOnlySpan<char> value)
        => string.GetHashCode(value);
}
```

「なんだ、実質何もしてないじゃないか」と思われるかもしれませんが、`string` インスタンスに対するハッシュ値の算出ではなく `ReadOnlySpan<char>` に対して実施しているというの一応のポイントです。FastEnum (v2) の Public API は `string` ベースではなく `ReadOnlySpan<char>` ベースになっているので、こういう地味な小細工 (？) をしています。

で、この [`string.GetHashCode()` の実装](https://source.dot.net/#System.Private.CoreLib/src/runtime/src/libraries/System.Private.CoreLib/src/System/String.Comparison.cs,5f5a7b633e78a025)には人類の叡智みたいなのが詰め込まれていて、恐ろしいまでにチューニングされています。手出しできるところなんて正直微塵もないように見えます。**汎用的な文字列に対して、であれば**。

## 改善後

「enum 専用ライブラリである」という部分に着目すると、以下のような固有の特徴が見えてきます。

* enum 型のフィールド名は比較的短い
* enum 型のフィールド数は言うほど多くない
* 厳密に分散する必要はなく、大半のケースで分散すれば実用上は十分

これらを利用して以下のようなハッシュ関数を実装してみましょう。パッと見だと何をやってるのか分からないかもしれませんが、図示すると分かりやすいですね。

CaseSensitive.GetHashCode() : 改善後

```
public static class CaseSensitive
{
    [MethodImpl(MethodImplOptions.AggressiveInlining)]
    public static int GetHashCode(ReadOnlySpan<char> value)
    {
        var length = value.Length;
        if (length is 0)
            return 0;

        var first = value.At(0);
        var middle = value.At(length >> 1);
        var last = value.At(length - 1);
        return (length << 16)
            ^ (first << 8)
            ^ (middle << 4)
            ^ last;
    }
}
```

![Case Sensitive Hash](https://static.zenn.studio/user-upload/1f75eabdc718-20260711.png)

フィールド名は長くならないので下位 16 bit もあれば文字列長を表現するには十分足ります。またフィールド名の中から 3 箇所の文字を取ってきてハッシュ値の要素とすれば、(enum のフィールド数が多くないことも鑑みると) 概ね一意に近づきます。もちろん、異なるフィールド名に対して同じハッシュ値が生成されないとは限りません。例えば以下のふたつは同じハッシュ値が生成されます。

とは言え、enum の性質からすると全てのフィールド名から同じハッシュ値が生成されるなんていうことは (バカげた項番な実装か何かでもない限り) まずあり得ません。例えば BCL の代表的な列挙型に対してハッシュ値の重複を調べてみると以下のようになり、実用上問題がないことが分かります。ハッシュ値は一意性を保証する必要があるものではなく、用途に対して十分に分散が利いていれば良いのです。

| 列挙型 | フィールド数 | ハッシュ値の重複数 |
| --- | --- | --- |
| `DayOfWeek` | 7 | 0 |
| `TypeCode` | 18 | 0 |
| `ConsoleKey` | 145 | 0 |
| `BindingFlags` | 21 | 0 |
| `HttpStatusCode` | 67 | 0 |
| `KnownColor` | 175 | 1 |

`string.GetHashCode()` は (非常に高速なアルゴリズムではあるけれど) 文字列全体を舐めつつハッシュ値を生成します。対して独自実装は文字列長に関わらず超軽量な定数時間 `O(1)` でハッシュ値を生成します。この差が非常に効いて **約 8.5 倍もの速度改善**に繋がりました🚀

ベンチマーク結果

```
BenchmarkDotNet v0.15.8, Windows 11 (10.0.26200.8737/25H2/2025Update/HudsonValley2)
Intel Core Ultra 7 155H 3.00GHz, 1 CPU, 22 logical and 16 physical cores
.NET SDK 10.0.301
  [Host]     : .NET 10.0.9 (10.0.9, 10.0.926.27113), X64 RyuJIT x86-64-v3
  DefaultJob : .NET 10.0.9 (10.0.9, 10.0.926.27113), X64 RyuJIT x86-64-v3

| Method             | Mean      | Error     | StdDev     | Median    | Ratio | RatioSD | Allocated | Alloc Ratio |
|------------------- |----------:|----------:|-----------:|----------:|------:|--------:|----------:|------------:|
| String_GetHashCode | 714.73 ns | 34.611 ns | 102.050 ns | 661.85 ns |  1.02 |    0.20 |         - |          NA |
| Custom_GetHashCode |  84.58 ns |  0.611 ns |   0.571 ns |  84.74 ns |  0.12 |    0.02 |         - |          NA |
```

ベンチマークの実装

```
public class Benchmarks
{
    private static readonly string[] s_names = Enum.GetNames<HttpStatusCode>();

    [Benchmark(Baseline = true)]
    public int String_GetHashCode()
    {
        var hash = 0;
        foreach (var x in s_names.AsSpan())
            hash |= getHashCode(x);
        return hash;

        [MethodImpl(MethodImplOptions.AggressiveInlining)]
        static int getHashCode(ReadOnlySpan<char> value)
            => string.GetHashCode(value);
    }

    [Benchmark]
    public int Custom_GetHashCode()
    {
        var hash = 0;
        foreach (var x in s_names.AsSpan())
            hash |= getHashCode(x);
        return hash;

        [MethodImpl(MethodImplOptions.AggressiveInlining)]
        static int getHashCode(ReadOnlySpan<char> value)
        {
            var length = value.Length;
            if (length is 0)
                return 0;

            var first = value.At(0);
            var middle = value.At(length >> 1);
            var last = value.At(length - 1);
            return (length << 16)
                ^ (first << 8)
                ^ (middle << 4)
                ^ last;
        }
    }
}
```

# 大文字/小文字の区別なし

## 改善前

続いて Case Insensitive な文字列に対する実装について見ていきましょう。これまた改善前の時点で `UnsafeAccessor` なんていう見慣れないものを使ったトリッキーなことをしていますね。

CaseInsensitive.GetHashCode() : 改善前

```
public static class CaseInsensitive
{
    [MethodImpl(MethodImplOptions.AggressiveInlining)]
    public static int GetHashCode(ReadOnlySpan<char> value)
    {
        return string_GetHashCodeOrdinalIgnoreCase(self: null, value);

        #region Local Functions
        [UnsafeAccessor(UnsafeAccessorKind.StaticMethod, Name = "GetHashCodeOrdinalIgnoreCase")]
        static extern int string_GetHashCodeOrdinalIgnoreCase(string? self, ReadOnlySpan<char> value);
        #endregion
    }
}
```

ちなみにこんなテクニックを使わなくても `string.GetHashCode(value, StringComparison.OrdinalIgnoreCase)` でも同様の結果を得ることができます。しかし該当の実装を見てみると以下のようになっていて、`StringComparison` に応じた分岐が入っています。通したいパスは 1 か所だけなので、この分岐は無駄ですね。

string.GetHashCode(ReadOnlySpan<char>, StringComparison)

```
public static int GetHashCode(ReadOnlySpan<char> value, StringComparison comparisonType)
{
    switch (comparisonType)
    {
        case StringComparison.CurrentCulture:
        case StringComparison.CurrentCultureIgnoreCase:
            return CultureInfo.CurrentCulture.CompareInfo.GetHashCode(value, GetCaseCompareOfComparisonCulture(comparisonType));

        case StringComparison.InvariantCulture:
        case StringComparison.InvariantCultureIgnoreCase:
            return CompareInfo.Invariant.GetHashCode(value, GetCaseCompareOfComparisonCulture(comparisonType));

        case StringComparison.Ordinal:
            return GetHashCode(value);

        case StringComparison.OrdinalIgnoreCase:  // ここにだけ入ればよい
            return GetHashCodeOrdinalIgnoreCase(value);

        default:
            ThrowHelper.ThrowArgumentException(ExceptionResource.NotSupported_StringComparison, ExceptionArgument.comparisonType);
            Debug.Fail("Should not reach this point.");
            return default;
    }
}
```

ということで `string.GetHashCodeOrdinalIgnoreCase()` を直接呼び出しせればよいということが分かります。ですが、これは `internal` なメソッドとして定義されているので (簡単には) 呼び出せません。「じゃあリフレクションの出番だ！」と短絡的に考えてしまうとオーバーヘッドが大きくて逆に遅くなってしまいます。そこで登場するのが `UnsafeAccessor` というわけですね。リフレクション相当の呼び出しをゼロコストで実行する超魔法です。

<https://ufcpp.net/study/csharp/misc/unsafeaccessor/>

このように、改善前の時点でも小さな努力はやっていました。が、そこに Claude Fable 5 が切り込んできたわけです。

## 改善後

こちらも Case Sensitive の実装と同様のアプローチを使います。大文字/小文字の区別がないパターンなので、ハッシュ値の生成ロジックもそれに従います。`CaseSensitive.GetHashCode()` との差分は、ハッシュ値の要素として文字を含める際に `char.ToUpperInvariant()` を使っているところだけです。

CaseInsensitive.GetHashCode() : 改善後

```
public static class CaseInsensitive
{
    [MethodImpl(MethodImplOptions.AggressiveInlining)]
    public static int GetHashCode(ReadOnlySpan<char> value)
    {
        var length = value.Length;
        if (length is 0)
            return 0;

        var first = value.At(0);
        var middle = value.At(length >> 1);
        var last = value.At(length - 1);
        return (length << 16)
            ^ (char.ToUpperInvariant(first) << 8)
            ^ (char.ToUpperInvariant(middle) << 4)
            ^ char.ToUpperInvariant(last);
    }
}
```

これでベンチマークを録ってみると、同様に**約 4 倍の高速化がされている**ことが分かりますね。素晴らしい結果🚀

ベンチマーク結果

```
BenchmarkDotNet v0.15.8, Windows 11 (10.0.26200.8737/25H2/2025Update/HudsonValley2)
Intel Core Ultra 7 155H 3.00GHz, 1 CPU, 22 logical and 16 physical cores
.NET SDK 10.0.301
  [Host]     : .NET 10.0.9 (10.0.9, 10.0.926.27113), X64 RyuJIT x86-64-v3
  DefaultJob : .NET 10.0.9 (10.0.9, 10.0.926.27113), X64 RyuJIT x86-64-v3

| Method             | Mean     | Error    | StdDev   | Median   | Ratio | RatioSD | Allocated | Alloc Ratio |
|------------------- |---------:|---------:|---------:|---------:|------:|--------:|----------:|------------:|
| String_GetHashCode | 680.5 ns | 13.60 ns | 37.67 ns | 682.2 ns |  1.00 |    0.08 |         - |          NA |
| Custom_GetHashCode | 167.1 ns |  4.04 ns | 11.91 ns | 171.6 ns |  0.25 |    0.02 |         - |          NA |
```

ベンチマークの実装

```
public class Benchmarks
{
    private static readonly string[] s_names = Enum.GetNames<HttpStatusCode>();

    [Benchmark(Baseline = true)]
    public int String_GetHashCode()
    {
        int hash = 0;
        foreach (var x in s_names.AsSpan())
        {
            hash |= getHashCode(x);
        }
        return hash;

        [MethodImpl(MethodImplOptions.AggressiveInlining)]
        static int getHashCode(ReadOnlySpan<char> value)
        {
            return string_GetHashCodeOrdinalIgnoreCase(self: null, value);

            [UnsafeAccessor(UnsafeAccessorKind.StaticMethod, Name = "GetHashCodeOrdinalIgnoreCase")]
            static extern int string_GetHashCodeOrdinalIgnoreCase(string? self, ReadOnlySpan<char> value);
        }
    }

    [Benchmark]
    public int Custom_GetHashCode()
    {
        int hash = 0;
        foreach (var x in s_names.AsSpan())
        {
            hash |= getHashCode(x);
        }
        return hash;

        [MethodImpl(MethodImplOptions.AggressiveInlining)]
        static int getHashCode(ReadOnlySpan<char> value)
        {
            var length = value.Length;
            if (length is 0)
                return 0;

            var first = value.At(0);
            var middle = value.At(length >> 1);
            var last = value.At(length - 1);
            return (length << 16)
                ^ (char.ToUpperInvariant(first) << 8)
                ^ (char.ToUpperInvariant(middle) << 4)
                ^ char.ToUpperInvariant(last);
        }
    }
}
```

# まとめ

独力でこういう発想や閃きができるようになりたいけれど、僕にはまだまだ難しい。でもこうやって AI が並走して教えてくれる時代になり、永遠に知らないまま、改善できないまま終わらずに済みました。今後も AI 先生に教えてもらいつつ、限界にチャレンジしていければなーと思います。

Claude Fable 5 を使った改善話はもう少し続きます。たぶん。100% 手書きの記事なので、腰が重くなったり筆が乗らない可能性は否定できないけどw

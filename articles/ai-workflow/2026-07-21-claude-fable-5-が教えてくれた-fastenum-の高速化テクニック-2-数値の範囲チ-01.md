---
id: "2026-07-21-claude-fable-5-が教えてくれた-fastenum-の高速化テクニック-2-数値の範囲チ-01"
title: "Claude Fable 5 が教えてくれた FastEnum の高速化テクニック (2) - 数値の範囲チェック"
url: "https://zenn.dev/xin9le/articles/5ed35a7145da77"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-07-21"
date_collected: "2026-07-22"
summary_by: "auto-rss"
query: ""
---

前回に引き続き Claude Fable 5 を利用した [FastEnum](https://github.com/xin9le/FastEnum) のパフォーマンスチューニングについて解説していいます。今回は**数値の範囲チェック**についてです。該当の Pull-Request は以下。

<https://github.com/xin9le/FastEnum/pull/95>

# Claude Fable 5 が教えてくれた高速化テクニックたち

1. [文字列のハッシュ値生成](https://zenn.dev/xin9le/articles/6fb2045805996c)
2. [数値の範囲チェック](https://zenn.dev/xin9le/articles/5ed35a7145da77) (← ｲﾏｺｺ

# 改善前

FastEnum の `.IsDefined(enum)` は enum の定義値の分布に応じて実装が分岐しています。ざっくり以下のような実装になっていました。

```
[MethodImpl(MethodImplOptions.AggressiveInlining)]
public static bool IsDefined(T value)  // where T : struct, Enum
{
    if (EnumInfo<T>.s_isContinuous)  // Fast Path
    {
        // 値が連続している場合は範囲チェックのみ
        var min = toNumber(EnumInfo<T>.s_minValue);  // 定義されている中での最小値
        var max = toNumber(EnumInfo<T>.s_maxValue);  // 定義されている中での最大値
        var val = toNumber(value);
        return (min <= val) && (val <= max);
    }
    else  // Slow Path (といっても速いけど)
    {
        // 値が非連続な場合は辞書から Lookup
        return EnumInfo<T>.s_memberByValue.ContainsKey(value);
    }
}
```

値が連続している/していないという列挙型の例は以下のような感じですね。

[Fast Path] 値が連続している列挙型

```
public enum Fruits : byte
{
    Apple = 0,
    Banana,  // 1
    Peach,   // 2
}
```

[Slow Path] 値が非連続な列挙型

```
public enum Fruits : byte
{
    Apple = 1,
    Banana = 3,
    Peach = 5,
}
```

内部実装まで鑑みると連続した値として定義する方が速くなるわけですが、アプリケーションを実装する際にはそこまで気にして使い分けなくても大丈夫です。ちゃんとアプリケーション都合で適切な値を定義しましょう。

そもそも Slow Path として実装されている辞書からの Lookup だけでも機能的には充足しているわけで、連続した定義値の場合に特化した Fast Path が準備されているだけで十分賢い。...のですが、この Fast Path にある「`(min <= val) && (val <= max)` の実装は勿体ないよ」と Claude Fable 5 に指摘されました。

# 改善後

改善前の範囲チェックの実装には `&&` が含まれています。ここには短絡評価があるので JIT は概ね以下のような条件分岐を生成しますが、このときデータがランダムだと分岐予測が当たりにくく、最適化されにくくなることが想定されます。

1. `val` を `min` と比較して分岐
2. 次に `val` を `max` と比較して分岐

なので、これのブランチレス化 (= 分岐を消す) ができれば分岐予測の必要がなくなり最適化がかかりやすくなります。ということで提案された実装が以下です。

```
[MethodImpl(MethodImplOptions.AggressiveInlining)]
public static bool IsDefined(T value)
{
    if (EnumInfo<T>.s_isContinuous)
    {
        var min = toNumber(EnumInfo<T>.s_minValue);
        var max = toNumber(EnumInfo<T>.s_maxValue);
        var val = toNumber(value);
-       return (min <= val) && (val <= max);
+       unchecked
+       {
+           var upper = (uint)(max - min);  // 本記事では簡単のために uint にしたが、
+           var lower = (uint)(val - min);  // 実際には enum の基底型に応じて変化する
+           return lower <= upper;
+       }
    }
    else
    {
        return EnumInfo<T>.s_memberByValue.ContainsKey(value);
    }
}
```

上記のようにオーバーフローを利用することで範囲チェックを 1 回だけにし、条件分岐の回数を減らしていることがわかります。なぜこの実装で良いのか、具体的な値を使って確認してみましょう。

| `val` | `(uint)(val - min)` | `<= (uint)(max - min)` |
| --- | --- | --- |
| 0 | 4294967295 | false |
| 1 | 0 | true |
| 100 | 99 | true |
| 101 | 100 | false |
| -5 | 4294967290 | false |

境界値でも上手く判定できていますね。なんとも賢い。とは言え、このオーバーフローを利用した最適化は .NET Runtime 内でもちょくちょく出てきます。例えば以下のような配列の範囲チェックは頻出です。読みやすいとは決して言えないのでマイクロベンチマークを大切にするところでだけ使えばいいと思いますが。

読みやすい一般的な範囲チェック

```
if (index < 0 || length <= index)
    throw new IndexOutOfRangeException();
```

オーバーフローを利用して条件分岐を削った範囲チェック

```
if ((uint)index >= (uint)length)
    throw new IndexOutOfRangeException();
```

最後にベンチマーク結果を載せておきます。実際ほんのちょっとだけ速くなるみたいです。誤差っぽい雰囲気もあるけど、条件分岐の回数が減ってるのは事実なのでヨシッ！

ベンチマーク結果

```
BenchmarkDotNet v0.15.8, Windows 11 (10.0.26200.8894/25H2/2025Update/HudsonValley2)
Intel Core Ultra 7 155H 3.00GHz, 1 CPU, 22 logical and 16 physical cores
.NET SDK 10.0.302
  [Host]     : .NET 10.0.10 (10.0.10, 10.0.1026.32716), X64 RyuJIT x86-64-v3
  DefaultJob : .NET 10.0.10 (10.0.10, 10.0.1026.32716), X64 RyuJIT x86-64-v3

| Method | Mean     | Error   | StdDev  | Ratio | RatioSD | Allocated | Alloc Ratio |
|------- |---------:|--------:|--------:|------:|--------:|----------:|------------:|
| Before | 106.8 ns | 2.15 ns | 3.48 ns |  1.00 |    0.04 |         - |          NA |
| After  | 105.3 ns | 0.74 ns | 0.69 ns |  0.99 |    0.03 |         - |          NA |
```

ベンチマークの実装

```
public class Benchmarks
{
    private static readonly KnownColor[] s_values
        = Enum.GetValues<KnownColor>()
        .Prepend((KnownColor)0)
        .Append((KnownColor)200)
        .ToArray();
    private static readonly KnownColor s_minValue = KnownColor.ActiveBorder;
    private static readonly KnownColor s_maxValue = KnownColor.RebeccaPurple;

    [Benchmark(Baseline = true)]
    public bool Before()
    {
        var result = true;
        foreach (var x in s_values.AsSpan())
        {
            result |= isDefined(x);
        }
        return result;

        [MethodImpl(MethodImplOptions.AggressiveInlining)]
        static bool isDefined(KnownColor value)
        {
            var min = (int)s_minValue;
            var max = (int)s_maxValue;
            var val = (int)value;
            return (min <= val) && (val <= max);
        }
    }

    [Benchmark]
    public bool After()
    {
        var result = true;
        foreach (var x in s_values.AsSpan())
        {
            result |= isDefined(x);
        }
        return result;

        [MethodImpl(MethodImplOptions.AggressiveInlining)]
        static bool isDefined(KnownColor value)
        {
            var min = (int)s_minValue;
            var max = (int)s_maxValue;
            var val = (int)value;
            unchecked
            {
                var upper = (uint)(max - min);
                var lower = (uint)(val - min);
                return lower <= upper;
            }
        }
    }
}
```

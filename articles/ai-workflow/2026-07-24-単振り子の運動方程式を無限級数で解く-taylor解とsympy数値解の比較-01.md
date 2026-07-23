---
id: "2026-07-24-単振り子の運動方程式を無限級数で解く-taylor解とsympy数値解の比較-01"
title: "単振り子の運動方程式を無限級数で解く ―― Taylor解とSymPy数値解の比較"
url: "https://qiita.com/arairuca/items/7ced9d0587c1c695c215"
source: "qiita"
category: "ai-workflow"
tags: ["Python", "qiita"]
date_published: "2026-07-24"
date_collected: "2026-07-24"
summary_by: "auto-rss"
query: ""
---

## 概要

単振り子の運動方程式 $\ddot{x} = -\sin x$ は非線形微分方程式であり、初等関数による閉じた解を持たない。本稿では、右辺の $\sin x$ を厳密に扱ったまま解 $x(t)$ 自体を $t$ のTaylor級数として構成する方法を示す。具体的には、補助変数 $v=\dot x,\ s=\sin x,\ c=\cos x$ を導入することで元の方程式を多項式(二次)のみからなる系に変換し、Taylor係数に対する行列形式の畳み込み漸化式を導出する。得られた級数を有限項で打ち切った近似解(以下、Taylor解と呼ぶ)を、SymPyの数値ODEソルバー(`mpmath.odefun`)による高精度数値解と比較し、両者の一致および打ち切り次数と収束半径の関係を図示する。

## 1. はじめに

単振り子の運動方程式は

```math
\frac{d^2 x}{dt^2} = -\sin x
```

で与えられる。$x$ が十分小さい場合には $\sin x \approx x$ と近似することで単振動の方程式 $\ddot x = -x$ に帰着し、初等的に解くことができる。しかし振幅が大きい場合には非線形性が無視できず、厳密解はJacobiの楕円関数を用いて表現されることが知られている。

本稿の目的は、この非線形項を近似せずに、解 $x(t)$ そのものを $t=0$ のまわりのTaylor級数として構成することである。$\sin x$ を $x$ のTaylor級数に展開して方程式に代入するだけでは

```math
\ddot x = -x + \frac{x^3}{3!} - \frac{x^5}{5!} + \cdots
```

という非線形方程式が残るだけで問題は解決しない。そこで本稿では、$x(t)$ を直接 $t$ のべき級数として求める手法を用いる。

## 2. 運動方程式の無限級数表現

### 2.1 補助変数による多項式系への変換

初期条件を $x(0)=a$（初期振れ角），$\dot x(0)=0$（静止状態から放す）とする。$v=\dot x,\ s=\sin x,\ c=\cos x$ を導入すると、元の2階非線形方程式は次の1階の多項式系に変換される。

```math
\dot x = v,\qquad \dot v = -s,\qquad \dot s = c\,v,\qquad \dot c = -s\,v
```

右辺がすべて $x,v,s,c$ の高々2次の多項式(積)になっている点が重要である。これにより、各変数をべき級数

```math
x(t)=\sum_{n=0}^{\infty}x_n t^n,\quad
v(t)=\sum_{n=0}^{\infty}v_n t^n,\quad
s(t)=\sum_{n=0}^{\infty}s_n t^n,\quad
c(t)=\sum_{n=0}^{\infty}c_n t^n
```

とおいたとき、係数間の関係を有限和(Cauchy積)のみで記述できる。

### 2.2 行列による畳み込み漸化式

係数ベクトルを $Y_n=(x_n,v_n,s_n,c_n)^{\top}$ とおくと、上記の系から得られる漸化式は次の行列形式にまとめられる。

```math
Y_{n+1}=\frac{1}{n+1}\sum_{k=0}^{n}A_k\,Y_{n-k}
```

```math
A_0=\begin{pmatrix}0&1&0&0\\0&0&-1&0\\0&c_0&0&0\\0&-s_0&0&0\end{pmatrix},
\qquad
A_k=\begin{pmatrix}0&0&0&0\\0&0&0&0\\0&c_k&0&0\\0&-s_k&0&0\end{pmatrix}\ (k\ge 1)
```

初期値は

```math
Y_0=(a,\ 0,\ \sin a,\ \cos a)^{\top}
```

である。$x'=v,\ v'=-s$ の部分は元来線形なので $k=0$ の項でしか寄与せず、$s'=cv,\ c'=-sv$ の部分のみが $k=0,\dots,n$ 全体の畳み込みとして効くという構造になっている。この漸化式は $A_k$ の中身(すなわち $c_k, s_k$)が既に求まっている過去の係数のみで構成されるため、自己参照なく逐次的に計算できる。

実際に低次の項を手計算すると

```math
x(t)=a-\frac{\sin a}{2}t^2+\frac{\sin a\cos a}{24}t^4+\frac{\sin a\,(4\sin^2a-1)}{720}t^6+\cdots
```

となり、偶数次の項のみが現れる。これは $\dot x(0)=0$ という初期条件のもとで系が時間反転対称性を持つことの帰結である。

## 3. 有限項による近似解(Taylor解)

上記の漸化式で $n=0,\dots,N$ まで係数を計算し、

```math
x_{\mathrm{Taylor}}(t)=\sum_{n=0}^{N}x_n\,t^n
```

としたものを、本稿ではTaylor解と呼ぶ。これは厳密には多項式ではなく無限べき級数の部分和である。$\sin$ は整関数であるため解自体は実軸上で解析的であるが、複素 $t$ 平面上には特異点(厳密解が楕円関数で表されることに対応する極)が存在し、級数の収束半径は有限である。したがってTaylor解は $t=0$ の近傍でのみ良い近似を与え、収束半径を超えると打ち切り誤差は急速に増大する。この点は4節以降で数値的に確認する。

実装は次のようになる。

```python
import numpy as np

def taylor_coeffs(a, N):
    """
    x''=-sin(x), x(0)=a, x'(0)=0 のTaylor係数 x_n,v_n,s_n,c_n (n=0..N) を
    行列漸化式 Y_{n+1} = 1/(n+1) * sum_k A_k @ Y_{n-k} で計算する。
    戻り値: shape (N+1, 4) の配列。列は [x_n, v_n, s_n, c_n]。
    """
    Y = np.zeros((N + 1, 4))
    Y[0] = [a, 0.0, np.sin(a), np.cos(a)]

    def A(k):
        c_k, s_k = Y[k, 3], Y[k, 2]
        M = np.zeros((4, 4))
        M[2, 1] = c_k
        M[3, 1] = -s_k
        if k == 0:
            M[0, 1] = 1.0   # x' = v
            M[1, 2] = -1.0  # v' = -s
        return M

    for n in range(N):
        total = np.zeros(4)
        for k in range(n + 1):
            total += A(k) @ Y[n - k]
        Y[n + 1] = total / (n + 1)
    return Y


def x_series(t, x_n):
    """Taylor係数 x_n から x(t) を評価する(ベクトル化)。"""
    t = np.asarray(t, dtype=float)
    N = len(x_n) - 1
    powers = np.power.outer(t, np.arange(N + 1))
    return powers @ x_n
```

## 4. SymPyによる数値解との比較

比較対象の基準解として、SymPyが多倍長精度の数値計算に用いているバックエンドである `mpmath` の `odefun` を用いる。これは任意精度浮動小数点演算によりTaylor級数法(内部的には別のべき級数展開)でODEを解くソルバーであり、許容誤差を十分小さく設定することで信頼できる基準解を得られる。

```python
import mpmath as mp

def sympy_numeric_solution(a, t_ary, dps=30, tol=1e-20):
    mp.mp.dps = dps

    def rhs(t, y):
        x, v = y
        return [v, -mp.sin(x)]

    sol = mp.odefun(rhs, 0, [mp.mpf(a), mp.mpf(0)], tol=tol)
    return np.array([float(sol(float(t))[0]) for t in t_ary])
```

以降の数値実験では初期振れ角 $a=1.0\ \mathrm{rad}$ とし、比較する時間範囲は $t\in[0,\,\pi/2]$ とする。この範囲に限定するのは、後述するようにTaylor級数の収束半径の制約により、これより先の時間では打ち切り誤差が急速に増大し、有意な比較にならないためである。

## 5. 結果

### 5.1 時系列での比較

$N=40$ として $t\in[0,\,\pi/2]$ の範囲でTaylor解とSymPy数値解を比較したものが図1である。上段が両者の重ね描き、下段が絶対誤差を対数軸で示したものである。

![qiita_compare.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1686019/76ac803b-7d54-4e7a-96c7-f6fb9ab02b4b.png)

*図1: 単振り子 $\ddot x=-\sin x$ ($a=1.0$) の解の比較。上: 解の重ね描き。下: 絶対誤差。*

$t$ が小さい範囲では誤差は倍精度浮動小数点の丸め誤差レベル($10^{-16}$程度)に留まっており、両者はほぼ完全に一致している。$t$ が大きくなるにつれて誤差は単調に増大するが、これは4節で述べた収束半径の効果である。

### 5.2 パリティプロット

同じデータについて、横軸にSymPy数値解、縦軸にTaylor解をとった散布図(パリティプロット)を図2に示す。両者が完全に一致していれば、すべての点は $y=x$ の直線上に乗るはずである。

![qiita_parity.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1686019/1f551fab-c6a8-4d4c-b2cb-074622d8f1d7.png)

*図2: パリティプロット。色は時刻 $t$ を表す。*

図2からも、対象とした範囲内で全ての点が $y=x$ の直線上にほぼ完全に乗っていることが視覚的に確認できる。

### 5.3 打ち切り次数 $N$ による精度の違い

最後に、打ち切り次数 $N\in\{10,20,40\}$ について、同じ時間範囲 $t\in[0,\,\pi/2]$ で誤差を比較した(図3)。

![qiita_convergence.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1686019/ae997f89-32f1-48a6-ac40-373e3a6c756d.png)

*図3: 打ち切り次数 $N$ ごとの誤差 $|x_{\mathrm{Taylor}}-x_{\mathrm{numeric}}|$ の推移(対数軸)。*

図3から、この範囲内では $N$ を大きくするほど誤差が単調に減少していくことが分かる。$N=40$ では $t\le\pi/2$ の全域で誤差が $10^{-11}$ 程度以下に収まっているのに対し、$N=10$ のような低次の打ち切りでは、$t$ が $\pi/2$ に近づくにつれて誤差が $10^{-4}$ 程度まで増大しており、打ち切り次数が精度に強く影響することが確認できる。

なお、今回あえて時間範囲を $t\le\pi/2$ に限定しているのは、Taylor級数の収束半径による制約のためである。$\sin$ は整関数であるため解自体は実軸上で解析的であるが、本方程式の厳密解(Jacobi楕円関数で表される)は複素 $t$ 平面上に特異点を持ち、それが級数の収束半径を定めている。この半径を超える時間領域では、打ち切り次数 $N$ をいくら増やしても誤差はかえって急激に増大してしまうため、本稿では意味のある比較ができる $t\le\pi/2$ の範囲に絞って結果を示した。

## 6. 考察

本稿で構成したTaylor解は、収束半径の内側である $t\in[0,\,\pi/2]$ の範囲では、打ち切り次数 $N$ を増やすことでSymPy数値解に対して機械精度に近い精度まで収束することが確認された。一方で、収束半径を超える時間領域まで扱うには、以下のような対処が必要になる。

- 打ち切り次数 $N$ を増やしても収束半径そのものは広がらないため、根本的な解決にはならない。
- 級数の収束範囲内で $x(t_1)$ とその導関数を求め、それを新たな初期条件として $t=t_1$ のまわりで級数を展開し直す、いわゆる解析接続(step-by-step continuation)により、任意の時刻まで解を延長することが可能である。
- あるいは、厳密解がJacobi楕円関数 $\mathrm{sn}$ を用いて閉じた形で書けることを利用し、周期性から任意の時刻の値を折り返して求める方法も考えられる。

いずれの方法も、本稿で示した「$\sin x, \cos x$ を補助変数として導入し多項式系に変換する」という基本的な枠組みの上に構築できる点は興味深い。

## 7. まとめ

本稿では、単振り子の運動方程式 $\ddot x=-\sin x$ を、$\sin x, \cos x$ を補助変数として導入することで多項式系に変換し、Taylor係数に対する行列形式の畳み込み漸化式を導出した。この漸化式により得られる有限次数の近似解(Taylor解)を、SymPyの数値ODEソルバー(`mpmath.odefun`)による高精度数値解と比較したところ、収束半径の内側では両者はほぼ完全に一致することを、時系列プロットおよびパリティプロットの両方で確認した。また、打ち切り次数を変えた比較により、収束半径の存在とその外側での級数の発散的振る舞いを数値的に可視化した。

## 付録: 実行環境

- Python 3.10
- numpy
- matplotlib, japanize-matplotlib
- mpmath (SymPyの数値計算バックエンド)

本稿で用いたコード全体を以下に示す(`furiko_qiita.py`)。

```python
"""
Qiita記事用: 単振り子 x''=-sin(x) の Taylor級数近似解と
SymPy(mpmath.odefun)による数値解の比較図を生成する。

生成される図:
  qiita_compare.png : 時系列での比較 (a=1.0, N=40, t in [0, pi/2])
  qiita_parity.png  : パリティプロット (横軸=数値解, 縦軸=Taylor解)
  qiita_convergence.png : 打ち切り次数Nごとの誤差 vs t
"""

import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib  # noqa: F401
import mpmath as mp


# ----------------------------------------------------------------------
# Taylor係数(行列漸化式)
# ----------------------------------------------------------------------
def taylor_coeffs(a, N):
    """
    x''=-sin(x), x(0)=a, x'(0)=0 の Taylor係数 x_n,v_n,s_n,c_n (n=0..N) を
    Y_{n+1} = 1/(n+1) * sum_{k=0}^{n} A_k @ Y_{n-k} で求める。
    """
    Y = np.zeros((N + 1, 4))
    Y[0] = [a, 0.0, np.sin(a), np.cos(a)]

    def A(k):
        c_k, s_k = Y[k, 3], Y[k, 2]
        M = np.zeros((4, 4))
        M[2, 1] = c_k
        M[3, 1] = -s_k
        if k == 0:
            M[0, 1] = 1.0
            M[1, 2] = -1.0
        return M

    for n in range(N):
        total = np.zeros(4)
        for k in range(n + 1):
            total += A(k) @ Y[n - k]
        Y[n + 1] = total / (n + 1)

    return Y


def x_series(t, x_n):
    """Taylor係数 x_n から x(t) を評価する(ベクトル化)。"""
    t = np.asarray(t, dtype=float)
    N = len(x_n) - 1
    powers = np.power.outer(t, np.arange(N + 1))
    return powers @ x_n


# ----------------------------------------------------------------------
# SymPy(mpmath.odefun)による数値解
# ----------------------------------------------------------------------
def sympy_numeric_solution(a, t_ary, dps=30, tol=1e-20):
    """
    mpmath.odefun (SymPyが数値ODE積分に用いる多倍長精度ソルバー) による基準解。
    """
    mp.mp.dps = dps

    def rhs(t, y):
        x, v = y
        return [v, -mp.sin(x)]

    sol = mp.odefun(rhs, 0, [mp.mpf(a), mp.mpf(0)], tol=tol)
    return np.array([float(sol(float(t))[0]) for t in t_ary])


# ----------------------------------------------------------------------
# 図1: 時系列比較
# ----------------------------------------------------------------------
def make_compare_figure(a=1.0, N=40, t_max=np.pi / 2, num=100,
                         savepath="qiita_compare.png"):
    t_ary = np.linspace(0, t_max, num)
    Y = taylor_coeffs(a, N)
    x_taylor = x_series(t_ary, Y[:, 0])
    x_numeric = sympy_numeric_solution(a, t_ary)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 7), sharex=True)

    ax1.plot(t_ary, x_numeric, label="SymPy数値解 (mpmath.odefun)",
             lw=3, color="tab:blue")
    ax1.plot(t_ary, x_taylor, label=f"Taylor解 (N={N})",
             lw=1.5, ls="--", color="tab:orange")
    ax1.set_ylabel("x(t)")
    ax1.set_title(f"単振り子 x''=-sin(x) の解の比較 (a={a})")
    ax1.legend()
    ax1.grid(True)

    ax2.plot(t_ary, np.abs(x_taylor - x_numeric), color="tab:red")
    ax2.set_yscale("log")
    ax2.set_xlabel("t")
    ax2.set_ylabel("誤差 |Taylor - 数値解|")
    ax2.grid(True)

    fig.tight_layout()
    fig.savefig(savepath, dpi=150)
    plt.close(fig)
    return t_ary, x_taylor, x_numeric


# ----------------------------------------------------------------------
# 図2: パリティプロット
# ----------------------------------------------------------------------
def make_parity_figure(a=1.0, N=40, t_max=np.pi / 2, num=100,
                        savepath="qiita_parity.png"):
    t_ary = np.linspace(0, t_max, num)
    Y = taylor_coeffs(a, N)
    x_taylor = x_series(t_ary, Y[:, 0])
    x_numeric = sympy_numeric_solution(a, t_ary)

    fig, ax = plt.subplots(figsize=(6, 6))
    lo = min(x_numeric.min(), x_taylor.min())
    hi = max(x_numeric.max(), x_taylor.max())
    ax.plot([lo, hi], [lo, hi], color="gray", lw=1, ls="--", label="y = x")
    sc = ax.scatter(x_numeric, x_taylor, c=t_ary, cmap="viridis", s=20)
    fig.colorbar(sc, ax=ax, label="t")
    ax.set_xlabel("SymPy数値解")
    ax.set_ylabel(f"Taylor解 (N={N})")
    ax.set_title(f"パリティプロット: Taylor解 vs SymPy数値解 (a={a})")
    ax.set_aspect("equal", adjustable="box")
    ax.legend()
    ax.grid(True)

    fig.tight_layout()
    fig.savefig(savepath, dpi=150)
    plt.close(fig)
    return x_numeric, x_taylor


# ----------------------------------------------------------------------
# 図3: 打ち切り次数ごとの誤差
# ----------------------------------------------------------------------
def make_convergence_figure(a=1.0, Ns=(10, 20, 40), t_max=np.pi / 2, num=60,
                             savepath="qiita_convergence.png"):
    t_ary = np.linspace(0, t_max, num)
    x_numeric = sympy_numeric_solution(a, t_ary)

    fig, ax = plt.subplots(figsize=(7, 5))
    for N in Ns:
        Y = taylor_coeffs(a, N)
        x_taylor = x_series(t_ary, Y[:, 0])
        err = np.abs(x_taylor - x_numeric)
        ax.plot(t_ary, err, label=f"N={N}")

    ax.set_yscale("log")
    ax.set_xlabel("t")
    ax.set_ylabel("誤差 |Taylor - 数値解|")
    ax.set_title(f"打ち切り次数Nごとの誤差の増大 (a={a})")
    ax.legend()
    ax.grid(True)

    fig.tight_layout()
    fig.savefig(savepath, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    make_compare_figure()
    make_parity_figure()
    make_convergence_figure()
    print("done")
```

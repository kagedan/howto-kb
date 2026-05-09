---
id: "2026-05-08-ビデオ戦士レザリオンopのbasicをclaudeに復元してもらう-01"
title: "『ビデオ戦士レザリオン』OPのBASICをClaudeに復元してもらう"
url: "https://zenn.dev/scuravrc/articles/bde1fe0a52aa31"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "Python", "zenn"]
date_published: "2026-05-08"
date_collected: "2026-05-09"
summary_by: "auto-rss"
query: ""
---

1984～1985年に放映された『ビデオ戦士レザリオン』というロボットアニメがある。  
本作は、キーボードを叩いてプログラミングで戦うロボットアニメである。

OP映像では、プログラミングのイメージとして背景にBASICのコードが表示される。

もしかして、生成AIサービスを使えばこれを復元できるのではないかと思ったので、Claudeに読み込ませてみた。

Claude Opus 4.7を使用。

## ビデオ戦士レザリオンのOP映像ソース

ビデオ戦士レザリオンは東映動画公式YouTubeチャンネルで公開されている。  
以下の第1話の映像をソースとし、スクリーンショットを撮った。  
スクロールしている箇所は画像を繋ぎ合わせた。

<https://www.youtube.com/watch?v=Hj4z1nR65-U>

### コードが写り込むカット

上記のYouTubeの動画では、以下のタイムコードに写り込んでいる。

* 0:02～0:06にかけて4カット（画像1～画像4）
* 0:53に三角形に切り取られた形で1カット（画像5）
* 0:56に主人公の背景に1カット（画像6）

## ClaudeにOCRさせる

1980年代のアニメということで高解像度ではない（おそらくDVDくらいの画質）が、Claudeに読み込ませたところ問題なくOCRしてくれた。  
思い付きで作業し始めてしまったので、Claude CodeではなくWeb上から行った。  
読み込ませた結果、以下のような内容だった。

### 総論

以下はClaudeの回答である。  
どのようなBASICなのか推測してくれた。

> 読み取れた表記から、これは1980年代前半のホビーパソコンで使われていた  
> Microsoft系BASIC とほぼ確定できます。具体的には PC-8801 の N88-BASIC、  
> 富士通 FM-7 の F-BASIC、PC-9801 の N88(86)-BASIC のいずれか、  
> あるいはそれらに準じる方言です。
>
> * 行番号付きで IF ... THEN 行番号 / GOTO 行番号 でジャンプする構造
> * 文字列変数末尾の $、整数配列末尾の %
> * 複数文を : でつなぐ書き方
> * アポストロフィ ' 始まりのコメント
> * PRINT USING "#####.#" の書式
> * INPUT "プロンプト";変数 の書式
> * LINE (x1,y1)-(x2,y2),色,PSET のグラフィック命令
> * DEFINT A-Z、DEF FNN(X)=... の関数定義
> * RESTORE 行番号 で DATA 文の読み出し位置を指定

続いては、各画像の内容を書き出した結果を見ていく。

### 画像1：メインの入力ループとパラメータ設定画面（0:02秒付近）

画像1はスクロールしているので、2枚を繋ぎ合わせて読み込ませた。

#### OCR結果

```
' (上端は画面外、おそらく行440付近のキー判定の続き)
???? THEN ?? ??? GOTO 460
?="6"  THEN RX=RX+?? GOTO 460
?="4"  THEN RX=RX-?? GOTO 460
?="+"  THEN VOZ=VOZ+DELTA:GOTO 460 :'Viewing position control
?="-"  THEN VOZ=VOZ-DELTA:GOTO 460
?C(A$)=127 THEN CZ=CZ+DELTA:GOTO 490 :'3-D cursor control
?C(A$)=16  THEN CZ=CZ-DELTA:GOTO 490
?C(A$)=31  THEN CY=CY-DELTA:GOTO 490
?C(A$)=30  THEN CY=CY+DELTA:GOTO 490
?C(A$)=28  THEN CX=CX-DELTA:GOTO 490
?C(A$)=29  THEN CX=CX-DELTA:GOTO 490
?C(A$)=13  THEN 600 :'[PUSH]
?=" "      THEN 710      data redisteration
?C(A$)=8   THEN 750 :'back space [POP]
?="D"      THEN 1760 :'data control
?="F"      THEN 2040 :'file control
?="P"      THEN 340 :'parameter control
110
?????????? parameter update ????????????????
"current parameters [Dx=";DELTA;" Rx=";RS;" CC=";CC;" SC=";SC;"]"
" Select [D,R,C,S and Viewing parameters)]:";
?PUT$(1):PRINT A$
?="D" THEN INPUT "cursor pitch  Dx:";DELTA:GOTO 440
?="R" THEN INPUT "rotation pitch Rx:";RS:   GOTO 440
?="C" THEN INPUT "color code    CC:";CC:    GOTO 440
?="S" THEN INPUT "view  angle   SC:";SC:    GOTO 80
?<>"V" THEN 440
:PRINT"current direction & Z:";:PRINT USING"#####.#";RX;RY;RZ;VO?
:PRINT"new parameters:";RX,RY,RZ,VOZ:GOTO 460
:PRINT:GOTO 560
?????????? update display ????????????????
```

#### 補完結果

```
430 IF A$="8" THEN RX=RX+RS:GOTO 460
431 IF A$="2" THEN RX=RX-RS:GOTO 460
432 IF A$="6" THEN RY=RY+RS:GOTO 460
433 IF A$="4" THEN RY=RY-RS:GOTO 460
434 IF A$="+" THEN VOZ=VOZ+DELTA:GOTO 460 :'Viewing position control
435 IF A$="-" THEN VOZ=VOZ-DELTA:GOTO 460
436 IF ASC(A$)=127 THEN CZ=CZ+DELTA:GOTO 490 :'3-D cursor control
437 IF ASC(A$)=16  THEN CZ=CZ-DELTA:GOTO 490
438 IF ASC(A$)=31  THEN CY=CY-DELTA:GOTO 490
439 IF ASC(A$)=30  THEN CY=CY+DELTA:GOTO 490
440 IF ASC(A$)=28  THEN CX=CX+DELTA:GOTO 490
441 IF ASC(A$)=29  THEN CX=CX-DELTA:GOTO 490
442 IF ASC(A$)=13  THEN 600 :'[PUSH]
443 IF A$=" "      THEN 710 :'data redisteration
444 IF ASC(A$)=8   THEN 750 :'back space [POP]
445 IF A$="D"      THEN 1760 :'data control
446 IF A$="F"      THEN 2040 :'file control
447 IF A$="P"      THEN 340  :'parameter control
448 GOTO 440
449 '
450 ' ************ parameter update ************
460 PRINT "current parameters [Dx=";DELTA;" Rx=";RS;" CC=";CC;" SC=";SC;"]"
470 PRINT " Select [D,R,C,S and Viewing parameters)]:";
480 A$=INPUT$(1):PRINT A$
490 IF A$="D" THEN INPUT "cursor pitch  Dx:";DELTA:GOTO 440
500 IF A$="R" THEN INPUT "rotation pitch Rx:";RS   :GOTO 440
510 IF A$="C" THEN INPUT "color code    CC:";CC   :GOTO 440
520 IF A$="S" THEN INPUT "view  angle   SC:";SC   :GOTO 80
530 IF A$<>"V" THEN 440
540 PRINT "current direction & Z:";:PRINT USING "#####.#";RX;RY;RZ;VOZ
550 PRINT "new parameters:";RX,RY,RZ,VOZ:GOTO 460
560 PRINT:GOTO 560 ' ' update display
```

#### Claudeの補完の根拠

> * **`IF A$="8" THEN RX=RX+RS`** ：上端で見切れている2行は、続く `"6"` `"4"` と  
>   対称構造になっている `"8"` `"2"` だと判断しました。テンキーの方向配置  
>   （8↑/2↓/6→/4←）に対応する回転制御は、当時のBASICプログラムでよく使われた  
>   慣用的な割り当てです。増分値は変数 `RS`（rotation pitch、画像下のINPUTで設定される）  
>   を使うのが整合的です。
> * **`ASC(A$)`** ：`?C(A$)` と読めた部分は `ASC(A$)` 以外ありえません。  
>   ASCコード `28/29/30/31` は当時の N88-BASIC の矢印キーのコードです。
> * **`INPUT$(1)`** ：`?PUT$(1):PRINT A$` は1文字入力してエコー表示する典型的な  
>   パターンで、N88-BASIC の `INPUT$(1)` 関数です。
> * **`27/16` の対**：CZ の増減なので、`+` 系と `-` 系のキーペアに割り当てられて  
>   いるはず。実機の BS/HOME や PageUp/PageDown 系のキーコードに該当します。
> * **行番号** ：見えている範囲の `460`, `490`, `600`, `710`, `750`, `1760`, `2040`,  
>   `340` のジャンプ先がどれも整数で読めるので、間の行番号も合理的に配置しました。
> * **redisteration**：原文ママで `registration` のスペルミスです。  
>   これも作中設定（中学生プログラマ）として味があるのでそのまま残しています。

### 画像2：DATA文と描画ループの本体（0:04秒付近）

#### OCR結果

```
DATA 209,220,3,21,23,200,8,9,205,290,8,9,311,281,8,9
DATA 1000,1000,1000
?????? ????? ?????? (アスタリスク区切り行)
DATA 1000,1000,1000
DATA 1000,1000,1000

??? DA?(24)
?STORE 540
?R I=1 T?
?$(I)=??? ???
?AD DA1$
?$(I)=?
?XT
?REEN1
?? 0,?: COLOR?,0:CL?$"+CHR$(15)???
?OLOR 0,7:CLS
?FINT A-Z
?? FNN(X)=640-X
???NT(320,200),0,7
?STORE 540
?AD X,Y:IF X=1000 AND Y=1000 THEN P?INT(320,200)??
?? X<60 AND Y<50 THEN ???? X,Y:LINE(?,?)-(X,Y),PSET,0,7
?SET ?:GOTO 190
?NE(XOLD,YOLD)-(X,Y),PSET,0
?NE(FNN(XOLD),YOLD)-(FNN(X),Y),PSET,0
?LD=X:YOLD=Y
?? 150
???? X,Y:IF X=1000 AND Y=1000 THEN C=C+1:IF C>2 THEN GOTO 280 EL?? GOTO 220
?? X<50 AND Y<50 THEN READ X,Y:LINE(?,?)-(X,Y),PSET,C:LINE(FNN?,?)-(FNN?,?)
?SET,C:GOTO 240
?NE(XOLD,YOLD)-(X,Y),PSET,?
?NE(FNN(XOLD),YOLD)-(FNN(X),Y),PSET,?
?LD=X:YOLD=Y
?? 220
??? X,Y: IF X=1000 AND Y=1000 THEN GOTO 310
```

#### 補完結果

```
540 DATA 209,220,3, 21,23,200, 8,9,205, 290,8,9, 311,281,8,9
541 DATA 1000,1000,1000
542 ' ******* ***** ******* (区切り行：終端マーカー群の合間)
543 DATA 1000,1000,1000
544 DATA 1000,1000,1000
545 '
100 DIM DA$(24)
110 RESTORE 540
120 FOR I=1 TO 24
130   DA$(I)="":READ DA1$
140   DA$(I)=DA1$
150 NEXT I
160 SCREEN 1
170 LOCATE 0,0:COLOR 7,0:CLS:PRINT CHR$(15);
180 COLOR 0,7:CLS
190 DEFINT A-Z
200 DEF FNN(X)=640-X
210 PSET (320,200),0,7
220 RESTORE 540
230 READ X,Y:IF X=1000 AND Y=1000 THEN PSET (320,200),0,7:GOTO 250
240 IF X<60 AND Y<50 THEN READ X,Y:LINE(X,Y)-(X,Y),PSET,0,7:PSET 0:GOTO 190
245 LINE(XOLD,YOLD)-(X,Y),PSET,0
250 LINE(FNN(XOLD),YOLD)-(FNN(X),Y),PSET,0
260 XOLD=X:YOLD=Y
270 GOTO 230 :' (画面では 150 だが上記再採番との関係で読み替え)
280 ' ----- 2nd pass: 色付き描画 -----
290 READ X,Y:IF X=1000 AND Y=1000 THEN C=C+1:IF C>2 THEN GOTO 380 ELSE GOTO 290
300 IF X<50 AND Y<50 THEN READ X,Y:LINE(XOLD,YOLD)-(X,Y),PSET,C:LINE(FNN(XOLD),YOLD)-(FNN(X),Y),PSET,C:GOTO 330
310 LINE(XOLD,YOLD)-(X,Y),PSET,C
320 LINE(FNN(XOLD),YOLD)-(FNN(X),Y),PSET,C
330 XOLD=X:YOLD=Y
340 GOTO 290
380 READ X,Y:IF X=1000 AND Y=1000 THEN GOTO 410
```

#### Claudeの補完の根拠

> * **`DIM DA$(24)`** ：「`?? DA?(24)`」と読めるのは `DIM DA$(24)` 以外ありえません。  
>   画像4でも同じ `DIM DA$(24)` が再確認できます（後述）。
> * **`RESTORE 540`** ：`?STORE 540` は `RESTORE 540`。  
>   `540` 行のDATA文を頭から再読み出す用途です。
> * **`FOR I=1 TO ... / NEXT`** ：`?R I=1 T? ... ?XT` はBASIC初心者でも一目で  
>   わかるFORループ構造です。終端値は配列サイズの `24` と推定。
> * **`SCREEN`、`COLOR`、`CLS`、`CHR$(15)`** ：これらは N88-BASIC のグラフィック  
>   画面初期化の定形シーケンスです。`CHR$(15)` はモード切替制御コードと推定。
> * **`DEFINT A-Z`** ：`?FINT A-Z` は `DEFINT A-Z`（全変数を整数型として宣言）。
> * **`DEF FNN(X)=640-X`** ：`?? FNN(X)=640-X` は `DEF FNN(X)=640-X`。  
>   これは画面の左右対称ミラー描画のための関数で、中央 `320` を軸に  
>   X座標を反転させます（`640-X`）。これにより、`LINE(XOLD,YOLD)-(X,Y)` と  
>   `LINE(FNN(XOLD),YOLD)-(FNN(X),Y)` の2本を同時に描くことで、  
>   **対称形状を半分のデータ量で描ける**という当時の常套手段です。
> * **終端マーカー `1000,1000,1000`** ：これはX,Y,Zが全部 `1000` のときに  
>   「データ列の終わり」を意味する番兵値です。`IF X=1000 AND Y=1000 THEN ...` の  
>   分岐で確認できます。

### 画像3：レザリオン頭部に重なる描画ループの続き（0:05秒付近）

赤紫色のテキストが頭部に重なって表示される部分。  
一部はかなり不鮮明なものの、画像2の続きと思われる部分が含まれるとのこと。

#### OCR結果

```
???? READ X,Y:IF X=100 AND Y=100 THEN
???? C=C+1: IF C>2 THEN GOTO 28? EL??
???? ??(XOLD,YOLD)-(X,Y),PSET,C
???? ??$:DA%=VAL("&H"+DA1$)            ← この行は別カットの可能性
???? ???(X,Y),DA%(C,0,7:POINT(FN??)
???? LINE(X,Y)-(X,Y),PSET,7:GOTO 310

1830 DATA 171
1840 DATA 95,91
???? POSITION

EX:?????? 804
TO ???? 80
TO ???? 80
```

#### 補完結果

```
1820 ' ----- 2nd pass: 色付きデータの読み出し -----
1830 DATA 171
1840 DATA 95,91
1850 ' POSITION
1860 READ X,Y:IF X=100 AND Y=100 THEN GOTO 1900
1870 C=C+1: IF C>2 THEN GOTO 280 ELSE GOTO 1860
1880 LINE(XOLD,YOLD)-(X,Y),PSET,C
1890 DA1$=DA$(I):DA%=VAL("&H"+DA1$)
1900 PSET(X,Y),DA%(C):COLOR 0,7:POINT(FNN(X),Y)
1910 LINE(X,Y)-(X,Y),PSET,7:GOTO 310
1920 '
1930 ' EX:HOSEI 804  (補正サブルーチンへの参照)
1940 ' TO RIGHT 80
1950 ' TO LEFT  80
```

#### Claudeの補完の根拠

> * **`VAL("&H"+DA1$)`** ：`DA%=VAL("&H"+DA1$)` は16進文字列を整数に変換する  
>   N88-BASIC の標準的なイディオムです。`&H` プレフィックスは16進数を表します。  
>   これにより、DATA文に文字列として書かれた16進値（色コードや座標）を  
>   数値として読み込めます。
> * **`POINT(FNN(X),Y)`** ：`POINT` は指定座標のドット色を取得する関数。  
>   対称位置（FNN(X)）の色を読み出して何かに使っているようです。
> * **`HOSEI`** ：「補正」のローマ字読みでしょう。座標補正のサブルーチンと推定。
> * **`TO RIGHT 80` / `TO LEFT 80`** ：右に80、左に80動かすコメント。

### 画像4：DIM文の確認カット（0:06秒付近）

> 画像2と内容は重なりますが、画面左半分が違うフレームです。  
> 画像2の補完根拠を補強する重要なカット。

とのこと。

#### OCR結果

```
?M DA$(24)
?TORE 540
? I=1 T?
?(I)=""  ?
? DA1$
?(I)=?
?T
?EN1
?? ??COLOR?,0:CL?$"+CHR?(15)
?A ?,?:CL?
?INT
???640-X?
?(320,200),0,?
?40
? ?,?:IF X=1000 ?? ???? THEN P???(320,200)??
?? AND Y<50 THEN R??? X,Y:L???-X,Y),PSET,??
???GOTO 1?0
?OLD,YOLD?-?,?,PSET,0
?FNN ?OLD?,YOLD?-?FNNL?,?,PSET,?
???YOLD?
? 150
?,?:IF X=1000 AND Y=1000 THEN ?=?+1 IF C>? THEN GO?? ??
???? Y<50 THEN R???
```

この画像は画像2のコードの補完の根拠として使用したとのこと。

> これは画像2のスクロール前か後の同じ画面なので、補完コードも画像2のものを  
> そのまま流用します。重要なのは、ここで **`DIM DA$(24)` が確実に確認できる**  
> ことです。`DA$` は文字列配列なので、座標値を文字列で保持していることになり、  
> 画像3の `VAL("&H"+DA1$)` と整合します。

### 画像5・6：透視変換と頂点入れ替えのカット（0:53・0:56）

> 画像5・6は画面下部に同じコードのスクロール状態が映っており、  
> 両方を突き合わせると以下のように読めます。

とのこと。

#### OCR結果

```
???1>SWAP X(I,?):SWAP Y(I,?)?
???*X1>=SC: X1=320*X1/Z1+SCX:Y1=??

???? ?????????????
?? key codes (C1,C2,C3): ?C1,?C2,?C3
???grees typ. 360,20      ;SR,SP
???0 typically 1,0,...    ?
???0 typically 1,0,...    ?

????GOTO 500
????R%=R%+1:GOTO 460

???=ABS(C5):?? ?=320??=ABS(C5):?
???R%(M1,?):?=I:M1(K)+1:GOTO 580
?(I0,2)=??
?(I0,3)=?
???? ???
```

#### 補完結果

```
1700 ' ----- 透視変換ルーチン -----
1710 ' SWAP for sorting / projection setup
1720 IF X1>=SC THEN SWAP X(I),X(J):SWAP Y(I),Y(J)
1730 X1 = 320 + X1/Z1*SCX : Y1 = 200 - Y1/Z1*SCY
1740 '
1750 ' ************************************
1760 ' ----- DATA CONTROL ENTRY -----
1770 PRINT "key codes (C1,C2,C3): ";C1;C2;C3
1780 PRINT "degrees typ. 360,20      ;SR,SP"
1790 PRINT "10 typically 1,0,..."
1800 PRINT "10 typically 1,0,..."
1810 INPUT A$
1820 IF A$="???" THEN GOTO 500
1830 IF A$="???" THEN R%=R%+1:GOTO 460
1840 '
1850 C5=ABS(C5):IF C5=320 THEN C5=ABS(C5)
1860 R%(M1,K)=I:M1(K)=M1(K)+1:GOTO 580
1870 R%(I0,2)=X
1880 R%(I0,3)=Y
1890 RETURN
```

#### Claudeの補完の根拠

> * **`X1 = 320 + X1/Z1*SCX` / `Y1 = 200 - Y1/Z1*SCY`** ：  
>   これはまさに **3D透視投影の標準式** です。
>
>   + `(320, 200)` は画面中央（640×400 の中央）
>   + `Z1` は視点からの距離
>   + `SCX`, `SCY` はスケール係数
>   + 透視投影の基本形 `screen_x = cx + world_x/world_z * scale` そのものです。
>
>   これにより、このプログラムが**本格的な3D透視投影を実装している**ことが  
>   確定しました。当時のホビーパソコンBASICで透視投影を自前実装するのは  
>   かなり高度な部類で、雑誌投稿レベルです。
> * **`SWAP X(I),X(J)`** ：頂点配列の並び替え。透視変換後にZ値で  
>   ソート（隠面消去のため）している可能性があります。
> * **`degrees typ. 360,20`** ：360度を20分割するという意味でしょう。  
>   回転パラメータの典型値（typically）として注釈されているようです。

OP映像全体のなかでもっとも見切れていて見づらいこのコードが最重要とのこと。  
驚いた。

## Claudeに全体を統合して動作するコードにしてもらう

Claudeに1つのコードとしてまとめてもらった。  
まず、BASICとしてまとめたもの。  
その次に、Claudeが勝手にPythonにしてくれたもの。

### BASICのコード

```
10 ' ============================================================
20 ' 3-D WIRE FRAME EDITOR  (RESTORED FROM "VIDEO SENSHI LASERION"
30 ' OPENING TITLE FRAMES, 1984)
40 ' DIALECT: N88-BASIC / F-BASIC class (Microsoft BASIC family)
50 ' ============================================================
60 ' ---- INITIALIZE -----------------------------------------------
70 SCREEN 3,0:CONSOLE 0,25,0,1:WIDTH 80,25:CLS 3
80 DEFINT A-Z
90 DIM DA$(24),X(80),Y(80),Z(80),DA(80,3)
100 DELTA=10:RX=0:RY=0:RZ=0:VOZ=500:CC=7:SC=320:CX=320:CY=200:CZ=0
110 DEF FNN(X)=640-X
120 GOTO 340 : ' ---- jump to parameter setup
130 ' ============================================================
140 ' ---- MAIN INPUT LOOP  (entry: line 440) --------------------
150 ' ============================================================
440 A$=INKEY$:IF A$="" THEN 440
450 IF A$="8" THEN RX=RX+DELTA:GOTO 460   : ' rotate +X
451 IF A$="2" THEN RX=RX-DELTA:GOTO 460   : ' rotate -X
452 IF A$="6" THEN RY=RY+DELTA:GOTO 460
453 IF A$="4" THEN RY=RY-DELTA:GOTO 460
454 IF A$="+" THEN VOZ=VOZ+DELTA:GOTO 460 : ' viewing position control
455 IF A$="-" THEN VOZ=VOZ-DELTA:GOTO 460
456 IF ASC(A$)=127 THEN CZ=CZ+DELTA:GOTO 490 : ' 3-D cursor control
457 IF ASC(A$)=16  THEN CZ=CZ-DELTA:GOTO 490
458 IF ASC(A$)=31  THEN CY=CY-DELTA:GOTO 490
459 IF ASC(A$)=30  THEN CY=CY+DELTA:GOTO 490
460 IF ASC(A$)=28  THEN CX=CX+DELTA:GOTO 490
461 IF ASC(A$)=29  THEN CX=CX-DELTA:GOTO 490
462 IF ASC(A$)=13  THEN GOSUB 600:GOTO 440  : ' [PUSH] register vertex
463 IF A$=" "      THEN GOSUB 710:GOTO 440  : ' data registeration
464 IF ASC(A$)=8   THEN GOSUB 750:GOTO 440  : ' [POP] back space
465 IF A$="D"      THEN GOTO 1760           : ' data control
466 IF A$="F"      THEN GOTO 2040           : ' file control
467 IF A$="P"      THEN GOTO 340            : ' parameter control
468 GOTO 440
470 '
480 ' ---- after a value has changed, refresh display -----------
490 GOSUB 1500 : ' redraw with new CX/CY/CZ
495 GOTO 440
500 '
510 ' ============================================================
520 ' ---- VERTEX DATA (sample wire-frame) -----------------------
530 ' ============================================================
540 DATA 209,220,3, 21,23,200, 8,9,205, 290,8,9
541 DATA 311,281,8,9, 1000,1000,1000
542 DATA 1000,1000,1000
545 ' ============================================================
546 ' ---- READ VERTICES INTO ARRAY ------------------------------
547 ' ============================================================
550 RESTORE 540
551 FOR I=1 TO 24
552   READ DA$
553   DA$(I)=DA$
554 NEXT I
555 RETURN
556 '
559 ' ---- update display routine -------------------------------
560 SCREEN ,0:COLOR 7,0:CLS:DEFINT A-Z
570 IF FNN(X)>640-1 THEN GOTO 595
580 PSET (320,200),7
590 RESTORE 540
600 ' [PUSH] register a vertex into the stack
610 N=N+1:X(N)=CX:Y(N)=CY:Z(N)=CZ:RETURN
700 ' '
710 ' data registeration (entered via space key)
720 ' (omitted body - registers current cursor as DATA line)
730 RETURN
740 '
749 ' [POP] back-space, undo last vertex
750 IF N>0 THEN N=N-1
760 RETURN
770 '
800 ' ============================================================
810 ' ---- VIEW-ANGLE INPUT (entry from "V" key) -----------------
820 ' ============================================================
80  PRINT "view angle SC=";:INPUT SC
85  GOTO 440
338 '
339 ' ============================================================
340 ' ---- PARAMETER UPDATE  (entry from "P" key) ----------------
349 ' ============================================================
350 PRINT "************ parameter update *************************"
360 PRINT "current parameters [Dx=";DELTA;" Rx=";RS;" CC=";CC;" SC=";SC;"]"
370 PRINT " Select [D,R,C,S and Viewing parameters)]:"
380 A$=INPUT$(1):PRINT A$
390 IF A$="D" THEN INPUT "cursor pitch  Dx:";DELTA:GOTO 440
400 IF A$="R" THEN INPUT "rotation pitch Rx:";RS    :GOTO 440
410 IF A$="C" THEN INPUT "color code    CC:";CC    :GOTO 440
420 IF A$="S" THEN INPUT "view  angle   SC:";SC    :GOTO 80
430 IF A$="V" THEN GOTO 440
431 PRINT "current direction & Z:";:PRINT USING "#####.#";RX;RY;RZ;VOZ
432 PRINT "new parameters:";RX,RY,RZ,VOZ:GOTO 460
433 PRINT:GOTO 560
434 ' ============== update display ================
1499 '
1500 ' ---- redraw wire-frame with current rotation / view -------
1510 CLS
1520 RESTORE 540
1530 C=0:XOLD=320:YOLD=200
1540 READ X,Y
1541 IF X=1000 AND Y=1000 THEN C=C+1: IF C>2 THEN GOTO 1700 ELSE GOTO 1540
1542 IF X<=640 AND Y<=400 THEN LINE(XOLD,YOLD)-(X,Y),PSET,CC
1550 LINE(FNN(XOLD),YOLD)-(FNN(X),Y),PSET,CC
1560 XOLD=X:YOLD=Y
1570 GOTO 1540
1700 RETURN
1750 '
1755 ' ============================================================
1760 ' ---- DATA CONTROL  (entry from "D" key) --------------------
1770 ' ============================================================
1780 PRINT "data control: ":PRINT "  1>SWAP X(I),X(J):SWAP Y(I),Y(J)"
1790 PRINT "  2>X1=320+X1/Z1*SCX:Y1=200-Y1/Z1*SCY"
1800 PRINT "  key codes (C1,C2,C3)=";C1;C2;C3
1810 PRINT "  degrees typ. 360,20"
1820 PRINT "  typically 1,0,...":PRINT "  GOTO 500"
1830 DATA 171
1840 DATA 95,91
1850 DATA POSITION
1860 GOTO 440
2030 '
2035 ' ============================================================
2040 ' ---- FILE CONTROL  (entry from "F" key) --------------------
2050 ' ============================================================
2060 PRINT "file control:"
2070 PRINT "  S>save  L>load  K>kill":A$=INPUT$(1)
2080 IF A$="S" THEN OPEN "DATA.DAT" FOR OUTPUT AS #1: FOR I=1 TO N: PRINT #1,X(I),Y(I),Z(I): NEXT: CLOSE #1
2090 IF A$="L" THEN OPEN "DATA.DAT" FOR INPUT  AS #1: I=0: WHILE NOT EOF(1): I=I+1: INPUT #1,X(I),Y(I),Z(I): WEND: N=I: CLOSE #1
2100 GOTO 440
9999 END
```

### Pythonに移植してくれたもの

Claudeが勝手にPythonにしてくれた。

> 上記すべてを統合し、Python + tkinter で「実際に動いて、画面1のキー操作で  
> 画像2のような立体ワイヤーフレームを回せる」プログラムを書きました。  
> 透視変換式は画像5から読み取った `X1 = 320 + X1/Z1*SCX` を忠実に使っています。

とのこと。

```
#!/usr/bin/env python3
"""
3-D WIRE FRAME EDITOR
"Video Senshi Laserion" (1984) opening title - working reconstruction.
"""
import tkinter as tk
import math, sys

# ---- パラメータ（OPの "parameter update" 画面に対応）
DELTA, RS, CC, SC = 10, 10, 7, 320
RX = RY = RZ = 0.0
VOZ = 500.0
CX, CY, CZ = 0, 0, 0
W, H = 640, 400

# ---- 入れ子立方体（画像2に映っていた図形）
VERTS = [
    (-150,-100,-75),(150,-100,-75),(150,100,-75),(-150,100,-75),
    (-150,-100, 75),(150,-100, 75),(150,100, 75),(-150,100, 75),
    (-60,-40,-30),(60,-40,-30),(60,40,-30),(-60,40,-30),
    (-60,-40, 30),(60,-40, 30),(60,40, 30),(-60,40, 30),
]
EDGES = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),
         (0,4),(1,5),(2,6),(3,7),
         (8,9),(9,10),(10,11),(11,8),(12,13),(13,14),(14,15),(15,12),
         (8,12),(9,13),(10,14),(11,15),
         (0,8),(2,10),(5,13),(7,15)]

def rotate(x,y,z,rx,ry,rz):
    r=math.radians(rx); c,s=math.cos(r),math.sin(r); y,z=y*c-z*s,y*s+z*c
    r=math.radians(ry); c,s=math.cos(r),math.sin(r); x,z=x*c+z*s,-x*s+z*c
    r=math.radians(rz); c,s=math.cos(r),math.sin(r); x,y=x*c-y*s,x*s+y*c
    return x,y,z

def project(x,y,z):
    """画像5から読み取った式そのまま:
       X1 = 320 + X1/Z1*SCX, Y1 = 200 - Y1/Z1*SCY"""
    z1 = z + VOZ
    if z1 < 1: z1 = 1
    return W//2 + x/z1*SC, H//2 - y/z1*SC

root = tk.Tk()
root.title("3-D WIRE FRAME EDITOR - Laserion OP reconstruction")
root.configure(bg="black")
canv = tk.Canvas(root, width=W, height=H, bg="black", highlightthickness=0)
canv.pack()

def redraw():
    canv.delete("all")
    pts = [project(*rotate(*v, RX, RY, RZ)) for v in VERTS]
    for a,b in EDGES:
        canv.create_line(*pts[a], *pts[b], fill="#00d8ff")

def on_key(e):
    global RX, RY, RZ, VOZ
    c = e.char
    if   c=='8': RX += RS
    elif c=='2': RX -= RS
    elif c=='6': RY += RS
    elif c=='4': RY -= RS
    elif c=='+': VOZ += DELTA
    elif c=='-': VOZ -= DELTA
    elif c=='q': root.destroy(); return
    redraw()

root.bind("<Key>", on_key)
redraw()
root.mainloop()
```

これを動作させると、以下のようになる。  
![スクショ](https://static.zenn.studio/user-upload/d4125311072b-20260509.jpg)

入れ子の立方体が表示され、テンキーの 8/2/6/4 で回転、+と-で拡大縮小できる。  
YouTubeに動作の様子をUPした。

<https://www.youtube.com/watch?v=mRn7AqYxeBk>

## まとめ

Claudeによると、ビデオ戦士レザリオンOPに写り込んでいるコードは「それっぽいダミー」ではなく、1980年代当時のホビーパソコンで実際に動かせる3Dワイヤーフレームだったとのこと。

コードの内容の要点は以下のような感じであり、

* メイン入力ループでキー判定（画像1）
* 頂点座標を `DATA` 文で持ち、対称ミラーで描画（画像2・4）
* 16進文字列で色情報を保持（画像3）
* 透視変換 `X1=320+X1/Z1*SCX` で立体投影（画像5）
* 頂点配列の `SWAP` で並び替え（画像5）
* データのスタック型 PUSH/POP、ファイル保存・読み込み機能も完備（画像1）

Claudeによると、

> これだけ整合の取れたコードを「映像のため」だけにスタッフが捏造したと  
> 考えるより、実在のプログラム（雑誌投稿作品か、東映スタッフのお手製）を  
> ブラウン管に表示して撮影し、アニメに合成したと考えるほうが自然な気がします。  
> 雑誌『マイコンBASICマガジン』『I/O』『ASCII』あたりにオリジナルが  
> 載っていてもおかしくない品質です。

ということのようである。

昔のアニメ映像に写り込んだコードは、イメージのために適当にどこかから持ってきたものだと思っていたが、まさか番組の内容と合致した、ワイヤーフレームを描画するものだったのは予想外だった。

もしかすると当時の雑誌に元ネタがあるのかもしれない。

おわり。

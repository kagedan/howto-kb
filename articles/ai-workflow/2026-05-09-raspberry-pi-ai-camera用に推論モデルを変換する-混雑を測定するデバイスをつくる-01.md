---
id: "2026-05-09-raspberry-pi-ai-camera用に推論モデルを変換する-混雑を測定するデバイスをつくる-01"
title: "Raspberry Pi AI Camera用に推論モデルを変換する | 混雑を測定するデバイスをつくる"
url: "https://qiita.com/Lilly_hdmi/items/b07487ca7d8a38d4feda"
source: "qiita"
category: "ai-workflow"
tags: ["API", "AI-agent", "Gemini", "GPT", "Python", "qiita"]
date_published: "2026-05-09"
date_collected: "2026-05-09"
summary_by: "auto-rss"
query: ""
---

# 概要

Raspberry Pi 5とRaspberry Pi AI Cameraを使い、物体検出モデルYOLO26を変換するまでの手順と、その実行についてまとめました。

モデルを変換してそのあと実際にやっていることは、これに非常に似ています。調べている最中にこの存在を知ってしまったので、意地でなんとかつくりきりました。

https://github.com/SonySemiconductorSolutions/aitrios-rpi-sample-apps/blob/main/examples/queue-monitor/README.md

# Raspberry Pi AI Cameraについて

[](https://www.aitrios.sony-semicon.com/ja/edge-ai-devices/raspberry-pi-ai-camera)

IMX500というAI推論に適したセンサーが搭載されているカメラで、Raspberry Pi本体に負荷をかけずに推論が行える、というものです。

最大解像度は4056 × 3040(10bit, 10fps)で、RGBで入力できるテンソルの最大サイズは640 × 640となっています。

Raspberry Pi 5であれば、推論結果をopencvで出力するくらいは余裕でできるような処理の余裕が生まれます

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4352773/94b5ae1f-d15f-4e37-8931-ae5547ca5eef.png)


https://developer.aitrios.sony-semicon.com/en/docs/raspberry-pi-ai-camera/raspberry-pi-ai-camera-tutorial?version=2025-09-30&progLang=

IMX500を使った推論をするための方法はいくつかあります。
はやいほうから順に手順が少なく簡単にできます

1. Raspberry Piにインストールする[imx500用のパッケージに付属しているモデル(rpkファイル)](https://github.com/raspberrypi/imx500-models)を使う
[picamera2のサンプルコード](https://github.com/raspberrypi/picamera2/tree/main/examples/imx500)とあわせれば、ファイルの作成不要でそのまま実行できます。
2. YOLOv8n、11nなどの、変換を簡単に行えるモデルを使う
公式チュートリアルに従っていくと、③に比べて短い手順でrpkファイルが得られます。
picamera2のサンプルコードで読み込むことも可能です
（2.のステップについても***ここに***まとめてます!)
3. TensorFlow / PyTorchのモデルをMCTを使って圧縮・量子化して、rpkファイルを得る
自分の使いたいモデルを自由に使う(さらには自作のモデルを使う)ことができる反面、変換の手順が他の方法に比べて多い。

以下、3.の方法についてまとめます。

なお、コードのほとんどはClaude / ChatGPT / Geminiに出力してもらったもので、パラメーター等を一部調整しています

前提となるRaspberry Piでのimx500のセットアップはここでは触れていません。また、Dockerについても細かい説明は省くので、とりあえず実行するためのshellのサンプルをつけます。

## モデルの変換

本当は[Retinaface](https://www.notion.so/Qiita-Raspberry-Pi-AI-Camera-2ff94c67881b803faa46ffab4c80271e?pvs=21)を使おうと思っていたのですがバージョン問題で大沼にはまったため、今回は[YOLO26](https://docs.ultralytics.com/ja/models/yolo26/)を変換します。

YOLOv8n、YOLO11nはimx500に対して特別なサポートをしており、Ultralyticsがrpkファイルを生成するための処理をまとめてくれています。とっても楽ですので26も対応するといいですね

順序はこんな感じ:

@ WSL Ubuntu 24.04

①YOLOのPytorchファイルをMCTで使い圧縮・量子化(ONNXファイルを作成)
②imx500-converterでPackerOut.zipを作成

@ Raspberry Pi

③imx500-packagerでnetwork.rpkを作成

### WSL

WSLでUbuntu 22.04を使います。DockerFileは以下の通りです

Ubuntuのバージョンについては、mct-quantizersとimx500-converterの推奨環境を確認するようにしてください
(とはいえややこしいので、22.04が最も確実に動作すると思います。片方だけが動かない、というようなことも十分ありえます)

```docker
FROM ubuntu:22.04

# ---- 基本設定 ----
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Asia/Tokyo \
    PYTHONUNBUFFERED=1

# ---- システムパッケージ ----
# Ubuntu 22.04 (jammy) の標準リポジトリに python3.11 が含まれるため
# deadsnakes PPA は不要 (PPA追加は gpg-agent を必要とし Docker 内で失敗する)
RUN apt-get update && apt-get install -y --no-install-recommends \
        wget curl git ca-certificates \
        libgl1 libglib2.0-0 libsm6 libxext6 libxrender1 \
        python3.11 python3.11-dev python3.11-venv \
    && curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11 \
    && ln -sf /usr/bin/python3.11 /usr/local/bin/python3 \
    && ln -sf /usr/bin/python3.11 /usr/local/bin/python \
    && rm -rf /var/lib/apt/lists/*

# ---- pip アップグレード ----
RUN python3 -m pip install --upgrade pip setuptools wheel

# ---- PyTorch (CPU版; GPU不要なら CUDA不要 → 容量節約) ----
# GPU が必要な場合は pytorch-cuda=12.1 等に差し替えてください
RUN pip install --no-cache-dir \
    torch==2.4.1 torchvision==0.19.1 \
    --index-url https://download.pytorch.org/whl/cpu

# ---- Ultralytics (YOLO26s ロード用) ----
RUN pip install --no-cache-dir \
    ultralytics

# ---- MCT (Model Compression Toolkit) ----
# imx500 TPC を含む最新安定版をインストール
RUN pip install --no-cache-dir \
    model-compression-toolkit \
    sony-custom-layers

# ---- ONNX / OpenCV ----
RUN pip install --no-cache-dir \
    onnx \
    onnxruntime \
    opencv-python-headless

# ---- 作業ディレクトリ ----
WORKDIR /workspace

# ---- スクリプトをコピー ----
#COPY quantize.py /workspace/quantize.py

# ---- デフォルトコマンド ----
CMD ["python3", "quantize.py", "--help"]
```

#### pipのconflictについて

MCTとimx500-converterで、依存関係における衝突が起こるようです。

MCTインストール後にimx500-converterをインストールすると、どうやらonnx, networkx, mct-quantizers, edge-mdt-clがアンインストールされるようで、MCTを利用する①のスクリプトがエラーになりました

```bash
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
model-compression-toolkit 2.6.0 requires edge-mdt-cl~=1.1.0, but you have edge-mdt-cl 1.0.0 which is incompatible.
model-compression-toolkit 2.6.0 requires mct-quantizers~=1.7.0, but you have mct-quantizers 1.6.0 which is incompatible.
Successfully installed coloredlogs-15.0.1 conv-allocator-3.17.1 edge-mdt-cl-1.0.0 humanfriendly-10.0 immutabledict-4.3.1 imx500-converter-3.17.3 mct-quantizers-1.6.0 networkx-3.0 onnx-1.17.0 onnxruntime-1.21.1 onnxruntime-extensions-0.13.0 ortools-9.9.3963 pandas-3.0.2 protobuf-4.25.5 sdspconv-3.17.1 stringcase-1.2.0 uni-model-10.0.23 uni-pytorch-3.17.1
```

このため、Dockerをビルドしたあと①をそのまま実行し、**そのあとconverterをインストール**、②に進むという手順をとるようにしてください
(もう一度①を実行したいときは、dockerコンテナをリビルドするのが一番はやく確実かと思います)

#### (docker操作)

以下のbuildを①、②のコードをコピーして保存したWSLのディレクトリ上で実行すると、以降の工程でパスを意識せず実行できます。

```bash
docker build . -t mct
docker run -it -v "$(pwd)":/workspace mct bash
```

(dockerコンテナから出るにはCtrl + p→Ctrl + q)

stop, start と attach

```bash
docker ps -a

docker stop [Container ID]

docker start [Container ID]
#then:
docker attach [Container ID]
#leave: Ctrl + p→Ctrl + q
```

### ⓪「キャリブレーション」用画像の確保

MCTのモデルの量子化には、「キャリブレーション」という操作のためのデータセットを用意する必要があります。

[](https://developer.aitrios.sony-semicon.com/edge-ai-sensing/documents/keras-model-deployment-guide?version=2025-12-15&progLang=#_quantization_of_the_model)

> PTQは、学習済みモデルのOutput Tensorが取りえる値の範囲（クリッピング範囲）を求めて、整数表現のモデルに変換します。 **クリッピング範囲を求める計算をキャリブレーションとよび**、モデルにデータセットを与えて計算します。
ここで適切なクリッピング範囲を求めるには、キャリブレーション用データセットが、**実際の入力に対してある程度の網羅性を持つ**ことが必要です。 そこで単純には、モデル学習に使ったデータセットを用いてキャリブレーションを行います。
> 

[チュートリアル](https://colab.research.google.com/github/SonySemiconductorSolutions/mct-model-optimization/blob/main/tutorials/notebooks/mct_features_notebooks/pytorch/example_pytorch_post_training_quantization.ipynb)などでは、ダウンロードできるデータセットを用意してくれています。

実環境と同じような画像を用意して、それから出力されるテンソルの値の範囲を推定するという作業のようです。一般的なカメラのキャリブレーションとは違う意味ですね

今回は実環境の画像が確保できるので、自分で撮影した画像をつかいます

- 下記は、人が検出できたときに写真を撮影するキャリブレーション画像を確保するためのプログラムです。
標準のmobilenet用rpkを使って検出しているので、Raspberry Piで実行すればすぐ使えるはずです
    
    
    ```jsx
    #calibration.py
    import os
    import time
    from datetime import datetime
    
    from picamera2 import Picamera2
    from picamera2.devices.imx500 import IMX500
    
    # =========================
    # 設定
    # =========================
    MODEL_PATH = "/usr/share/imx500-models/imx500_network_ssd_mobilenetv2_fpnlite_320x320_pp.rpk"
    SAVE_DIR = "./calibration_images"
    
    PERSON_CLASS_ID = 0      # COCO: person
    SCORE_THRESHOLD = 0.5
    CAPTURE_INTERVAL = 5.0   # 秒(連続保存防止)
    
    os.makedirs(SAVE_DIR, exist_ok=True)
    
    # =========================
    # Picamera2 + IMX500 初期化
    # =========================
    picam2 = Picamera2()
    imx500 = IMX500(MODEL_PATH)
    
    config = picam2.create_preview_configuration(
        main={"size": (1280, 720), "format": "RGB888"},
        controls={"FrameRate": 30}
    )
    
    picam2.configure(config)
    picam2.start()#ここまでは一般的なカメラモジュールと同じです
    
    print("IMX500 calibration capture started (Ctrl+C to stop)")
    
    last_capture_time = 0.0
    
    # =========================
    # メインループ
    # =========================
    try:
        while True:
            request = picam2.capture_request()
            metadata = request.get_metadata()
    
            outputs = imx500.get_outputs(metadata)#メタデータを渡して、推論結果を得る
    
            person_detected = False
    
            if outputs is not None:
                boxes, scores, classes, _ = outputs #pythonのunpacking
                #outputsはこのモデルでは要素数4の配列。ログに出して構造をみるとよくわかります
    
                for box, score, cls in zip(boxes, scores, classes):
                    if score < SCORE_THRESHOLD:
                        continue
    
                    if int(cls) == PERSON_CLASS_ID:
                        person_detected = True
                        break
    
            now = time.time()
    
            if person_detected and (now - last_capture_time) >= CAPTURE_INTERVAL:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(
                    SAVE_DIR,
                    f"person_{timestamp}.jpg"
                )
    
                print(f"[CAPTURE] person detected -> {filename}")
                request.save("main", filename)
    
                last_capture_time = now
    
            request.release()
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        print("\nStopping capture...")
    
    finally:
        picam2.stop()
    
    ```
    

### ①モデルの圧縮・量子化

ModelCompressionToolkit(MCT)を使い、モデルを圧縮します。

- MCTについて
    
    Keras (≒ Tensorflow) / PyTorchのモデル、キャリブレーションデータセット(後述)などを与えて量子化を行います
    
    READMEにおいて、MCTは複数の量子化の方法をとることができると記載されています。
    
    ![https://github.com/SonySemiconductorSolutions/mct-model-optimization?tab=readme-ov-file#high-level-features-and-techniques](attachment:5b5c0715-07b1-4d1b-9ca9-3e3938cb3cfc:image.png)
    
    https://github.com/SonySemiconductorSolutions/mct-model-optimization?tab=readme-ov-file#high-level-features-and-techniques
    
    [Target Platform Capabilities](https://github.com/SonySemiconductorSolutions/mct-model-optimization/blob/main/model_compression_toolkit/target_platform_capabilities/README.md)をimx500用に設定したうえで(デフォルトがimx500にセットされているようです)、
    
    [model_compression_toolkit.**ptq**. keras_post_training_quantization](https://sonysemiconductorsolutions.github.io/mct-model-optimization/api/api_docs/methods/keras_post_training_quantization.html)()
    [model_compression_toolkit.**gptq**. keras_gradient_post_training_quantization](https://sonysemiconductorsolutions.github.io/mct-model-optimization/api/api_docs/methods/keras_gradient_post_training_quantization.html)()
    [model_compression_toolkit.**qat**.keras_quantization_aware_training_init_experimental](https://sonysemiconductorsolutions.github.io/mct-model-optimization/api/api_docs/methods/keras_quantization_aware_training_init_experimental.html#ug-keras-quantization-aware-training-init-experimental)()
    
    ptqで精度が低下する場合に、gptqを使うといいよ、という感じのようです
    引数を正しく設定すればおそらくどの場合でも動作すると思います。だいたいの引数が共通しています(記載の通り処理負荷と複雑性がトレードオフになります)
    
    kerasという名前は今回はじめて知ったのですが、小規模で扱いやすいtensorflowというイメージで捉えてます
    
    Pytorch系のモデルを使う場合は、[mctのAPI Docs](https://sonysemiconductorsolutions.github.io/mct-model-optimization/api/api_docs/index.html#qat)にあるpytorch_系のメソッドを使用してください。
    
- 量子化を行うプログラムです。(quantize.py)⓪で用意した画像のフォルダを渡します
    
    ```jsx
    """
    YOLO26n → MCT PTQ 量子化スクリプト (IMX500 向け)
    -------------------------------------------------
    【アーキテクチャ上の問題と解決策】
    
    YOLO の _predict_once() は動的ループ + save インデックスを持ち、
    torch.fx (MCT が内部で使用) でそのままトレースできない。
    
      for m in self.model:          ← Proxy のイテレーション → エラー
          x = y[m.f] ...
    
    解決策: YOLO のレイヤー接続グラフをモデルロード時に読み取り、
    exec() を使って完全にアンロールされた静的 forward を生成する。
    
    生成例:
      def forward(self, x):
          _y0  = self._layers[0](x)
          _y1  = self._layers[1](_y0)
          _y2  = self._layers[2](_y1)   # save
          _y4  = self._layers[4]([_y0, _y2])  # multi-input
          ...
          return _y_last
    
    torch.fx はループのない静的コードをトレースできる。
    
    出力: quantized_yolo26n.onnx (fake-quant ONNX → imxconv-pt の入力)
    
    使い方:
      python quantizepy \
          --weights yolo26n.pt \
          --images  /path/to/calib_images \
          --output  quantized_yolo26n.onnx \
          [--imgsz 640] [--batch 1] [--n_iter 10]
    """
    
    import argparse
    import os
    import pathlib
    import textwrap
    
    import cv2
    import numpy as np
    import torch
    import torch.nn as nn
    
    # ============================================================
    # 1. 引数パース
    # ============================================================
    def parse_args():
        p = argparse.ArgumentParser()
        p.add_argument("--weights", default="yolo26s.pt")
        p.add_argument("--images",  required=True,
                       help="キャリブレーション画像フォルダ")
        p.add_argument("--output",  default="quantized_yolo26n.onnx")
        p.add_argument("--imgsz",   type=int, default=640)
        p.add_argument("--batch",   type=int, default=1,
                       help="キャリブ時バッチサイズ (≥4 推奨)")
        p.add_argument("--n_iter",  type=int, default=10,
                       help="イテレーション数 (合計 = batch × n_iter)")
        p.add_argument("--debug_forward", action="store_true",
                       help="生成した forward コードを表示する")
        return p.parse_args()
    
    # ============================================================
    # 2b. torch.fx トレース不可なサブモジュールのモンキーパッチ
    # ============================================================
    def patch_ultralytics_for_fx(model: nn.Module) -> None:
        """
        ultralytics のブロック内にある torch.fx 非対応パターンをパッチする。
    
        問題パターン1 (C2f など):
          list(tensor.chunk(2, 1))
          → Proxy に list() を呼ぶとイテレーション失敗
          → 修正: chunk()[0], chunk()[1] の明示インデックスに置換
    
        問題パターン2 (YOLO26 Detect ヘッド):
          _get_decode_boxes() 内の  if self.dynamic or self.shape != shape:
          → shape の比較が Proxy を bool 評価しようとして失敗
          → 修正: デコード処理をスキップし、生の conv 出力だけを返す
                   (IMX500 はデコード前の raw feature map を受け取る)
        """
        import inspect
        import types
    
        # =========================================================
        # パッチ1: chunk + list パターン (C2f 系ブロック)
        # =========================================================
        def _try_import(module_path, class_name):
            try:
                import importlib
                mod = importlib.import_module(module_path)
                return getattr(mod, class_name, None)
            except ImportError:
                return None
    
        C2f = _try_import("ultralytics.nn.modules.block", "C2f")
        if C2f:
            def _c2f_forward(self, x):
                ab = self.cv1(x).chunk(2, 1)  # Proxy のまま保持
                y  = [ab[0], ab[1]]           # getitem でアクセス → OK
                y.extend(m(y[-1]) for m in self.m)
                return self.cv2(torch.cat(y, 1))
            for m in model.modules():
                if isinstance(m, C2f):
                    m.forward = types.MethodType(_c2f_forward, m)
    
        # 汎用スキャン: 同じパターンを持つ他のブロック
        for name, sub in model.named_modules():
            src_lines = ""
            try:
                src_lines = inspect.getsource(type(sub).forward)
            except (TypeError, OSError):
                pass
            if "list(self.cv1(x).chunk(2, 1))" in src_lines:
                def _generic_c2f_forward(self, x):
                    ab = self.cv1(x).chunk(2, 1)
                    y  = [ab[0], ab[1]]
                    y.extend(m(y[-1]) for m in self.m)
                    return self.cv2(torch.cat(y, 1))
                sub.forward = types.MethodType(_generic_c2f_forward, sub)
    
        # =========================================================
        # パッチ2: Detect ヘッド → raw conv 出力のみ返す
        # =========================================================
        # YOLO26 の Detect ヘッドは end2end / one2one デュアルヘッド構造を持ち、
        # _get_decode_boxes() 内で Proxy を bool 評価しようとして失敗する。
        # IMX500 の量子化に必要なのは conv 後の生テンソルのみであり、
        # ボックスデコード・NMS は imxconv-pt 側が処理するため不要。
        #
        # 対応クラス:
        #   Detect, Detect26, v10Detect, WorldDetect, OBB, OBB26,
        #   Segment, Segment26, Pose, Pose26 …
        # 共通構造: cv2 (box branch) + cv3 (cls branch) を nl スケール分持つ
    
        def _make_raw_detect_forward(head):
            """
            ヘッドの構造を調べ、適切な raw forward を返す。
    
            通常の Detect 系:
              cv2[i](x[i]) ++ cv3[i](x[i])  → 各スケールを concat して返す
    
            YOLO26 の end2end Detect (one2one ヘッドあり):
              cv2[i] / cv3[i]          : one2many ブランチ
              cv2_one2one[i] / cv3_one2one[i] : one2one ブランチ
              → IMX500 向けは one2one ヘッドの出力を返す (end2end=True 時)
            """
            has_one2one = (hasattr(head, 'cv2_one2one') and
                           hasattr(head, 'cv3_one2one'))
            end2end     = getattr(head, 'end2end', False)
    
            if has_one2one and end2end:
                # YOLO26 end2end: one2one branch のみ使用
                def _forward_raw(self, x):
                    result = []
                    for i in range(self.nl):
                        result.append(torch.cat(
                            (self.cv2_one2one[i](x[i]),
                             self.cv3_one2one[i](x[i])), 1))
                    return tuple(result)
                head_mode = "YOLO26 end2end (one2one branch)"
            elif has_one2one:
                # one2one あり end2end なし: one2many を使用
                def _forward_raw(self, x):
                    result = []
                    for i in range(self.nl):
                        result.append(torch.cat(
                            (self.cv2[i](x[i]),
                             self.cv3[i](x[i])), 1))
                    return tuple(result)
                head_mode = "YOLO26 (one2many branch)"
            else:
                # 通常の Detect / YOLOv8 系
                def _forward_raw(self, x):
                    result = []
                    for i in range(self.nl):
                        result.append(torch.cat(
                            (self.cv2[i](x[i]),
                             self.cv3[i](x[i])), 1))
                    return tuple(result)
                head_mode = "standard Detect"
    
            return _forward_raw, head_mode
    
        # Detect 系のクラス名一覧 (isinstance チェック用)
        _DETECT_CLASS_NAMES = {
            "Detect", "Detect26", "v10Detect",
            "WorldDetect", "OBB", "OBB26",
            "Segment", "Segment26", "Pose", "Pose26",
        }
    
        for name, sub in model.named_modules():
            cls_name = type(sub).__name__
            if cls_name in _DETECT_CLASS_NAMES or (
                hasattr(sub, 'cv2') and hasattr(sub, 'cv3') and hasattr(sub, 'nl')
            ):
                if not hasattr(sub, 'cv2') or not hasattr(sub, 'cv3'):
                    continue
                raw_fwd, head_mode = _make_raw_detect_forward(sub)
                sub.forward = types.MethodType(raw_fwd, sub)
                print(f"  Detect ヘッドパッチ: {name} ({cls_name}) → {head_mode}")
    
        print("  サブモジュールパッチ完了")
    
    # ============================================================
    # 2. torch.fx トレース可能な静的ラッパーの生成
    # ============================================================
    def build_traceable_wrapper(detection_model: nn.Module,
                                debug: bool = False) -> nn.Module:
        """
        YOLO の DetectionModel から torch.fx トレース可能な
        静的ラッパーモジュールを生成して返す。
    
        アルゴリズム:
          1. detection_model.model (レイヤーリスト) を走査
          2. 各レイヤーの .f (入力元インデックス) を読み取る
          3. exec() でアンロールされた forward を生成
          4. TraceableYOLO に各レイヤーを ModuleList として登録
        """
        layers   = list(detection_model.model)
        save_set = set(detection_model.save)  # スキップ接続で参照されるインデックス
    
        # ------ forward コードの生成 ------
        lines = ["def forward(self, x):"]
    
        var_map: dict[int, str] = {}   # layer_index -> 変数名
    
        for i, m in enumerate(layers):
            f       = m.f    # 入力元: -1 | int | list[int]
            var_out = f"_y{i}"
    
            # 入力を決定
            # YOLO の f=-1 は「直前レイヤーの出力」を意味する (元の入力 x ではない)
            def resolve(j, _i=i):
                if j == -1:
                    return "x" if _i == 0 else var_map[_i - 1]
                return var_map[j]
    
            if isinstance(f, int):
                inp_expr = resolve(f)
            else:
                inp_expr = "[" + ", ".join(resolve(j) for j in f) + "]"
    
            lines.append(f"    {var_out} = self._layers[{i}]({inp

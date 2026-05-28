---
id: "2026-05-27-bedrock-のモデル利用コストを追跡するための-application-inference-pr-01"
title: "Bedrock のモデル利用コストを追跡するための Application Inference Profile 作成手順"
url: "https://zenn.dev/james_san/articles/972e5201ec2044"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-05-27"
date_collected: "2026-05-28"
summary_by: "auto-rss"
query: ""
---

# はじめに

Amazon Bedrock には **Inference Profile（推論プロファイル）** という仕組みがあります。本記事では、この推論プロファイルの概要と、利用コストを可視化するための **Application Inference Profile** を boto3 で作成する手順を解説します。

この記事を読むと、次のことがわかります。

* 推論プロファイルには「クロスリージョン型」と「アプリケーション型」の2種類があり、それぞれ何のためにあるのか
* 既存のモデル／システム定義プロファイルの情報を boto3 で取得する方法
* アプリケーション推論プロファイルを作成し、タグを付けてコストを追跡できるようにする方法

## 推論プロファイルの2つの役割

### 1. リージョンをまたいだルーティングでスループットを向上させる

**クロスリージョン推論プロファイル（システム定義）** を使うと、Bedrock がモデルの推論リクエストを複数の AWS リージョンへ動的にルーティングします。トラフィックの急増への対応、パフォーマンス改善、全体スループットの向上に役立ち、リージョンの空き状況や需要に応じて自動的に振り分けられるため、フェイルオーバーを手動で管理する必要がありません。

### 2. ルーティング範囲を地理的に限定する（日本リージョン限定など）

システム定義プロファイルには、ルーティング先のリージョン範囲が異なる種類があります。たとえば `global.*` プレフィックスのプロファイルは全リージョンへルーティングするのに対し、`jp.*` プレフィックスのプロファイルは日本国内のリージョン（ap-northeast-1 / ap-northeast-3）に限定してルーティングします。データの所在地（データレジデンシー）やコンプライアンス上の要件で処理リージョンを日本国内に閉じたい場合は、こうした地理的に限定されたプロファイルを選択します。クロスリージョンによるスループット向上のメリットを得つつ、ルーティング範囲を国内に絞れる点が特徴です。

### 3. 利用状況とコストを監視する

**アプリケーション推論プロファイル** を作成すると、単一リージョンの基盤モデル、または複数リージョンにまたがるシステム定義プロファイルをラップできます。これにより、以下が可能になります。

* **利用メトリクスの追跡**：推論呼び出し回数やトークン使用量を CloudWatch で確認できる
* **コストの監視**：推論プロファイルにタグを付けることで、コスト配分や請求の可視化がしやすくなる

今回は「対象アプリでの利用コストを追跡したい」というユースケースを想定し、対象モデルに対してアプリケーション推論プロファイルを作成する手順を説明します。

> 公式ドキュメント: [Increase throughput with cross-region inference - Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles.html)

# 手順

## モデルの情報取得

まず、利用可能な推論プロファイルを一覧表示・詳細取得するためのスクリプトを用意します。

```
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

region = 'ap-northeast-1'

bedrock_client = boto3.client(
    service_name='bedrock',
    region_name=region
)

def list_inference_profiles(bedrock_client):
    """
    List all available inference profiles in Amazon Bedrock

    Returns:
        list: List of inference profiles
    """
    try:
        response = bedrock_client.list_inference_profiles()
        return response.get('inferenceProfileSummaries', [])

    except NoCredentialsError:
        print("Error: AWS credentials not found. Please configure your credentials.")
        return []
    except ClientError as e:
        print(f"Error accessing Bedrock: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

def display_inference_profiles(profiles):
    """
    Display inference profiles in a formatted way

    Args:
        profiles (list): List of inference profile summaries
    """
    if not profiles:
        print("No inference profiles found or unable to retrieve profiles.")
        return

    print(f"\nFound {len(profiles)} inference profile(s):\n")
    print("-" * 80)

    for i, profile in enumerate(profiles, 1):
        print(f"{i}. Inference Profile ID: {profile.get('inferenceProfileId', 'N/A')}")
        print(f"   Inference Profile Name: {profile.get('inferenceProfileName', 'N/A')}")
        print(f"   Description: {profile.get('description', 'N/A')}")
        print(f"   Status: {profile.get('status', 'N/A')}")
        print(f"   Type: {profile.get('type', 'N/A')}")

        if 'models' in profile:
            print(f"   Models: {', '.join([model.get('modelId', 'N/A') for model in profile['models']])}")

        print("-" * 80)

def get_inference_profile_details(profile_id, bedrock_client):
    """
    Get detailed information about a specific inference profile

    Args:
        profile_id (str): The inference profile ID
        bedrock_client: The Bedrock client instance

    Returns:
        dict: Detailed information about the inference profile
    """
    try:
        response = bedrock_client.get_inference_profile(
            inferenceProfileIdentifier=profile_id
        )
        return response

    except ClientError as e:
        print(f"Error getting inference profile details: {e}")
        return None
```

次のように実行すると、利用可能なモデル（推論プロファイル）の一覧が表示されます。

```
display_inference_profiles(list_inference_profiles(bedrock_client))
```

一覧から、アプリケーション推論プロファイルを作成したいモデルの ID を指定して詳細情報を取得します。  
![](https://static.zenn.studio/user-upload/98bfddba9b47-20260527.png)

```
get_inference_profile_details('jp.anthropic.claude-opus-4-7', bedrock_client)
```

![](https://static.zenn.studio/user-upload/b0799e4860a2-20260527.png)

## アプリケーション推論プロファイルの作成

取得した詳細情報の `inferenceProfileArn` を `copyFrom` に指定して、アプリケーション推論プロファイルを作成します。タグを付けることで、後からコスト配分の追跡ができるようになります。

```
def create_application_inference_profile(bedrock_client, profile_name, model_source, description=None, tags=None):
    """
    Create an application inference profile

    Args:
        bedrock_client: The Bedrock client instance
        profile_name (str): Name for the inference profile
        model_source (dict): Model source configuration
        description (str, optional): Description of the profile
        tags (list, optional): List of tags for the profile

    Returns:
        dict: Response containing the created profile details
    """
    try:
        params = {
            'inferenceProfileName': profile_name,
            'modelSource': model_source
        }

        if description:
            params['description'] = description

        if tags:
            params['tags'] = tags

        response = bedrock_client.create_application_inference_profile(**params)

        print(f"Successfully created inference profile: {response['inferenceProfileArn']}")
        return response

    except ClientError as e:
        print(f"Error creating inference profile: {e}")
        return None

# -----------------------------------------------------------------------------
# 使用例 (Usage Example)
# -----------------------------------------------------------------------------

details = get_inference_profile_details('jp.anthropic.claude-opus-4-7', bedrock_client)

# コピー元のシステム定義プロファイル ARN を指定
model_source = {
    'copyFrom': details["inferenceProfileArn"]
}

# コスト追跡用のタグ
tags = [
    {
        'key': 'PJ',
        'value': 'TEST'
    }
]

# プロファイルを作成
result = create_application_inference_profile(
    bedrock_client=bedrock_client,
    profile_name='test-jp-claude-opus-4-7-profile',
    model_source=model_source,
    description='Claude Opus 4.7 profile in JP regions for test use',
    tags=tags
)
```

作成後は、付与したタグ（例では `PJ: TEST`）を使って Cost Explorer や CloudWatch から利用状況・コストを追跡できます。

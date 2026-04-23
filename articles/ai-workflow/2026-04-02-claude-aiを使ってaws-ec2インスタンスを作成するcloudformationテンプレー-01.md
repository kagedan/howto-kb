---
id: "2026-04-02-claude-aiを使ってaws-ec2インスタンスを作成するcloudformationテンプレー-01"
title: "Claude AIを使ってAWS EC2インスタンスを作成するCloudformationテンプレートを作ってみた"
url: "https://qiita.com/new1low/items/dfb99a60f1b999a7c316"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-04-02"
date_collected: "2026-04-03"
summary_by: "auto-rss"
---

## はじめに

今回コード生成AIを試しに使ってみようということでClaudeを使って、簡単なAWS EC2インスタンスを作成するためのテンプレートファイルを作ってみようと思います。

Claudeはどうやら、draw.ioのファイル（.drawio または .xml）をアップロードすると、そこからテンプレート作成までもっていってくれるそうなので、それも体験してみます。

### アップロードに使ったdraw.io

※qiitaに.drawio または .xml形式のファイルは添付できなかったので、画像を添付

## コード生成

アップロードの際に少し補足文書もいれてみた。  
[![{013E2F2A-CE4B-476E-95B4-A95EB20D85C7}.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4185984%2F710d2914-a255-4d81-b6cb-2e1b9cf9dca1.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=3aba8c32ae7965a00833f99bcbc2924a)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4185984%2F710d2914-a255-4d81-b6cb-2e1b9cf9dca1.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=3aba8c32ae7965a00833f99bcbc2924a)

色々まとめてくれて作成完了！  
[![{F53D0300-D3C6-4900-909C-965C3798DA5F}.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4185984%2Fb738597e-235c-4fb3-a17c-cf883fba0ebb.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c9eef578deb2423f5e2d286296afaa92)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4185984%2Fb738597e-235c-4fb3-a17c-cf883fba0ebb.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c9eef578deb2423f5e2d286296afaa92)

出来たyamlファイル

test\_cfn\_template.yaml

```
AWSTemplateFormatVersion: "2010-09-09"
Description: >
  CloudFormation Template generated from draw.io architecture diagram.
  Includes VPC, Public/Private Subnets, NAT Gateway, EC2 (Private Subnet),
  SSM Session Manager endpoints, and IAM Role for EC2.

# ============================================================
# Parameters
# ============================================================
Parameters:
  EnvironmentName:
    Type: String
    Default: test
    Description: Environment name used as prefix for resource names

# ============================================================
# Resources
# ============================================================
Resources:

  # ----------------------------------------------------------
  # VPC
  # ----------------------------------------------------------
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsSupport: true
      EnableDnsHostnames: true   # VPCエンドポイント利用に必要
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-vpc

  # ----------------------------------------------------------
  # Internet Gateway
  # ----------------------------------------------------------
  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-igw

  InternetGatewayAttachment:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway

  # ----------------------------------------------------------
  # Subnets
  # ----------------------------------------------------------
  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs ""]
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-public-subnet

  PrivateSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.2.0/24
      AvailabilityZone: !Select [0, !GetAZs ""]
      MapPublicIpOnLaunch: false
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-private-subnet

  # ----------------------------------------------------------
  # NAT Gateway
  # ----------------------------------------------------------
  NatGatewayEIP:
    Type: AWS::EC2::EIP
    DependsOn: InternetGatewayAttachment
    Properties:
      Domain: vpc
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-nat-eip

  NatGateway:
    Type: AWS::EC2::NatGateway
    Properties:
      AllocationId: !GetAtt NatGatewayEIP.AllocationId
      SubnetId: !Ref PublicSubnet
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-nat-gateway

  # ----------------------------------------------------------
  # Route Tables
  # ----------------------------------------------------------
  # Public Route Table
  PublicRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-public-rtb

  PublicRoute:
    Type: AWS::EC2::Route
    DependsOn: InternetGatewayAttachment
    Properties:
      RouteTableId: !Ref PublicRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref InternetGateway

  PublicSubnetRouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnet
      RouteTableId: !Ref PublicRouteTable

  # Private Route Table
  PrivateRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-private-rtb

  PrivateRoute:
    Type: AWS::EC2::Route
    Properties:
      RouteTableId: !Ref PrivateRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      NatGatewayId: !Ref NatGateway

  PrivateSubnetRouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PrivateSubnet
      RouteTableId: !Ref PrivateRouteTable

  # ----------------------------------------------------------
  # Security Groups
  # ----------------------------------------------------------
  # EC2用セキュリティグループ
  # インバウンド: なし
  # アウトバウンド: すべて許可（0.0.0.0/0）
  EC2SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub ${EnvironmentName}-ec2-sg
      GroupDescription: Security group for EC2 - no inbound, all outbound
      VpcId: !Ref VPC
      SecurityGroupEgress:
        - IpProtocol: -1
          FromPort: -1
          ToPort: -1
          CidrIp: 0.0.0.0/0
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-ec2-sg

  # VPCエンドポイント用セキュリティグループ
  # EC2からのHTTPS(443)のみ許可
  VPCEndpointSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub ${EnvironmentName}-vpce-sg
      GroupDescription: Security group for SSM VPC Endpoints
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          SourceSecurityGroupId: !Ref EC2SecurityGroup
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-vpce-sg

  # ----------------------------------------------------------
  # VPC Endpoints (Session Manager用)
  # Privateサブネットからインターネット経由なしでSSM接続するために必要
  # ----------------------------------------------------------
  SSMEndpoint:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      ServiceName: !Sub com.amazonaws.${AWS::Region}.ssm
      VpcId: !Ref VPC
      VpcEndpointType: Interface
      SubnetIds:
        - !Ref PrivateSubnet
      SecurityGroupIds:
        - !Ref VPCEndpointSecurityGroup
      PrivateDnsEnabled: true

  SSMMessagesEndpoint:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      ServiceName: !Sub com.amazonaws.${AWS::Region}.ssmmessages
      VpcId: !Ref VPC
      VpcEndpointType: Interface
      SubnetIds:
        - !Ref PrivateSubnet
      SecurityGroupIds:
        - !Ref VPCEndpointSecurityGroup
      PrivateDnsEnabled: true

  EC2MessagesEndpoint:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      ServiceName: !Sub com.amazonaws.${AWS::Region}.ec2messages
      VpcId: !Ref VPC
      VpcEndpointType: Interface
      SubnetIds:
        - !Ref PrivateSubnet
      SecurityGroupIds:
        - !Ref VPCEndpointSecurityGroup
      PrivateDnsEnabled: true

  # ----------------------------------------------------------
  # IAM Role for EC2 (Session Manager接続に必要)
  # ----------------------------------------------------------
  EC2SSMRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub ${EnvironmentName}-ec2-ssm-role
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-ec2-ssm-role

  EC2InstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      InstanceProfileName: !Sub ${EnvironmentName}-ec2-instance-profile
      Roles:
        - !Ref EC2SSMRole

  # ----------------------------------------------------------
  # EC2 Instance
  # ----------------------------------------------------------
  EC2Instance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: t3.micro
      # Amazon Linux 2023 kernel-6.1 (ap-northeast-1 最新AMI)
      # ※ リージョンによってAMI IDが異なります。必要に応じて更新してください。
      ImageId: !Sub "{{resolve:ssm:/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-6.1-x86_64}}"
      SubnetId: !Ref PrivateSubnet
      IamInstanceProfile: !Ref EC2InstanceProfile
      SecurityGroupIds:
        - !Ref EC2SecurityGroup
      # キーペアなし（Session Managerで接続）
      BlockDeviceMappings:
        - DeviceName: /dev/xvda
          Ebs:
            VolumeSize: 8
            VolumeType: gp3
            DeleteOnTermination: true
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}

# ============================================================
# Outputs
# ============================================================
Outputs:
  VPCId:
    Description: VPC ID
    Value: !Ref VPC

  PublicSubnetId:
    Description: Public Subnet ID
    Value: !Ref PublicSubnet

  PrivateSubnetId:
    Description: Private Subnet ID
    Value: !Ref PrivateSubnet

  EC2InstanceId:
    Description: EC2 Instance ID
    Value: !Ref EC2Instance

  EC2SSMRoleArn:
    Description: IAM Role ARN for EC2 SSM
    Value: !GetAtt EC2SSMRole.Arn
```

内容もまぁまぁイケてるじゃん！  
ここで、VPCとかサブネットとかは既にできてる前提で作ってと依頼  
[![{97F3F945-CB68-4DAF-A15D-6DF6EB296A88}.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4185984%2Fe0452908-9d9c-46d6-8277-fd11335980b1.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c21b3157450f25e955bdf5ada50b340d)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4185984%2Fe0452908-9d9c-46d6-8277-fd11335980b1.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c21b3157450f25e955bdf5ada50b340d)  
ここ地味に感心したのは、この要求に対して選択形式で返してきた。  
[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4185984%2F66355149-f928-4edf-a810-b1e71beee951.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=9ece5f127f211b38e806c5b754b63420)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4185984%2F66355149-f928-4edf-a810-b1e71beee951.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=9ece5f127f211b38e806c5b754b63420)

選択後は画面にはこんな感じで表示された  
[![{4F25F733-BA72-4884-BA7C-44A5B9156914}.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4185984%2F6fe2354c-1ce8-4f2d-9fbf-91b20b5a46b4.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=9f6f9fb58772d54b6cf19511061384d5)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4185984%2F6fe2354c-1ce8-4f2d-9fbf-91b20b5a46b4.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=9f6f9fb58772d54b6cf19511061384d5)

Claude君ファイル作成中...  
[![{1637CDE0-EF12-455D-8C0E-088474273390}.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4185984%2Ff5a8f522-d086-41a2-8b03-451659fe2398.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=a5b54561bfb0cc8dbd7270615f82e634)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4185984%2Ff5a8f522-d086-41a2-8b03-451659fe2398.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=a5b54561bfb0cc8dbd7270615f82e634)

からの出来たyamlファイル

ec2\_existing\_vpc\_cfn.yaml

```
AWSTemplateFormatVersion: "2010-09-09"
Description: >
  既存のVPC・サブネット環境にEC2インスタンスを作成するテンプレート。
  Session Manager接続のためのIAMロール・VPCエンドポイントも作成します。

# ============================================================
# Parameters
# ============================================================
Parameters:

  # --- 既存リソースのID ---
  ExistingVPCId:
    Type: AWS::EC2::VPC::Id
    Description: >
      既存VPCのID（例: vpc-xxxxxxxx）
      ※ VPCエンドポイントのセキュリティグループに使用します

  ExistingPrivateSubnetId:
    Type: AWS::EC2::Subnet::Id
    Description: >
      EC2を配置するプライベートサブネットのID（例: subnet-xxxxxxxx）

  # --- EC2設定 ---
  InstanceName:
    Type: String
    Default: test
    Description: EC2インスタンスの名前タグ

  InstanceType:
    Type: String
    Default: t3.micro
    Description: EC2インスタンスタイプ

# ============================================================
# Resources
# ============================================================
Resources:

  # ----------------------------------------------------------
  # Security Group for EC2
  # インバウンド: なし
  # アウトバウンド: すべて許可（0.0.0.0/0）
  # ----------------------------------------------------------
  EC2SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub ${InstanceName}-ec2-sg
      GroupDescription: Security group for EC2 - no inbound, all outbound
      VpcId: !Ref ExistingVPCId
      SecurityGroupEgress:
        - IpProtocol: -1
          FromPort: -1
          ToPort: -1
          CidrIp: 0.0.0.0/0
      Tags:
        - Key: Name
          Value: !Sub ${InstanceName}-ec2-sg

  # ----------------------------------------------------------
  # Security Group for VPC Endpoints
  # EC2からのHTTPS(443)のみ許可
  # ----------------------------------------------------------
  VPCEndpointSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub ${InstanceName}-vpce-sg
      GroupDescription: Security group for SSM VPC Endpoints
      VpcId: !Ref ExistingVPCId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          SourceSecurityGroupId: !Ref EC2SecurityGroup
      Tags:
        - Key: Name
          Value: !Sub ${InstanceName}-vpce-sg

  # ----------------------------------------------------------
  # VPC Endpoints (Session Manager接続に必要な3つ)
  # ----------------------------------------------------------
  SSMEndpoint:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      ServiceName: !Sub com.amazonaws.${AWS::Region}.ssm
      VpcId: !Ref ExistingVPCId
      VpcEndpointType: Interface
      SubnetIds:
        - !Ref ExistingPrivateSubnetId
      SecurityGroupIds:
        - !Ref VPCEndpointSecurityGroup
      PrivateDnsEnabled: true

  SSMMessagesEndpoint:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      ServiceName: !Sub com.amazonaws.${AWS::Region}.ssmmessages
      VpcId: !Ref ExistingVPCId
      VpcEndpointType: Interface
      SubnetIds:
        - !Ref ExistingPrivateSubnetId
      SecurityGroupIds:
        - !Ref VPCEndpointSecurityGroup
      PrivateDnsEnabled: true

  EC2MessagesEndpoint:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      ServiceName: !Sub com.amazonaws.${AWS::Region}.ec2messages
      VpcId: !Ref ExistingVPCId
      VpcEndpointType: Interface
      SubnetIds:
        - !Ref ExistingPrivateSubnetId
      SecurityGroupIds:
        - !Ref VPCEndpointSecurityGroup
      PrivateDnsEnabled: true

  # ----------------------------------------------------------
  # IAM Role for EC2 (Session Manager接続に必要)
  # ----------------------------------------------------------
  EC2SSMRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub ${InstanceName}-ec2-ssm-role
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
      Tags:
        - Key: Name
          Value: !Sub ${InstanceName}-ec2-ssm-role

  EC2InstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      InstanceProfileName: !Sub ${InstanceName}-ec2-instance-profile
      Roles:
        - !Ref EC2SSMRole

  # ----------------------------------------------------------
  # EC2 Instance
  # ----------------------------------------------------------
  EC2Instance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: !Ref InstanceType
      # Amazon Linux 2023 kernel-6.1
      # SSMパラメータストア経由でリージョンに応じた最新AMIを自動取得
      ImageId: !Sub "{{resolve:ssm:/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-6.1-x86_64}}"
      SubnetId: !Ref ExistingPrivateSubnetId
      IamInstanceProfile: !Ref EC2InstanceProfile
      SecurityGroupIds:
        - !Ref EC2SecurityGroup
      # キーペアなし（Session Managerで接続）
      BlockDeviceMappings:
        - DeviceName: /dev/xvda
          Ebs:
            VolumeSize: 8
            VolumeType: gp3
            DeleteOnTermination: true
      Tags:
        - Key: Name
          Value: !Ref InstanceName

# ============================================================
# Outputs
# ============================================================
Outputs:
  EC2InstanceId:
    Description: 作成されたEC2インスタンスのID
    Value: !Ref EC2Instance

  EC2SecurityGroupId:
    Description: EC2に適用されたセキュリティグループID
    Value: !Ref EC2SecurityGroup

  EC2SSMRoleArn:
    Description: EC2に割り当てたIAMロールのARN
    Value: !GetAtt EC2SSMRole.Arn

  SessionManagerCommand:
    Description: Session Managerで接続するコマンド（AWS CLI）
    Value: !Sub "aws ssm start-session --target ${EC2Instance}"
```

出来も最初に作った時と同じでイケており、パラメータを使う環境ごとに変えたら作れちゃいそう！

## おわりに・まとめ

まずdraw.ioをベースに作れちゃうのが便利。  
補足で出した指示もそこまで細かいものではなかったけど、東京リージョンに作ってくれたり、色々Claude側で補完してくれているのもグッド。

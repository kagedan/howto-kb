---
id: "2026-05-15-claude-api-laravel-reactで気象情報を毎日自動取得する仕組みを作るdocker-01"
title: "Claude API × Laravel × Reactで気象情報を毎日自動取得する仕組みを作る【Docker環境】"
url: "https://zenn.dev/ryo_k_candy0617/articles/claude-api-weather-laravel-react"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "zenn"]
date_published: "2026-05-15"
date_collected: "2026-05-16"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude APIには**Web検索機能**があり、最新の情報を取得できます。これを活用して、毎日1回自動で気象情報を取得し、データベースに保存 → Reactで表示する仕組みをDocker環境で構築します。

前回の記事「[Claude Codeに聞きながらDocker × Laravel環境を構築してみた](https://zenn.dev/candy_and_cherry/articles/claude-code-docker-laravel)」の環境をベースにしています。

### 完成イメージ

```
[Cronスケジューラ] → [Laravel Command] → [Claude API + Web検索] → [MySQL保存] → [React表示]
```

## 前提条件

## Step 1: Docker環境の構築

### ディレクトリ構成

```
laravel-weather/
├── docker/
│   ├── nginx/
│   │   └── default.conf
│   └── php/
│       └── Dockerfile
├── docker-compose.yml
└── src/          # Laravel + React プロジェクト
```

### docker-compose.yml

```
services:
  app:
    build:
      context: .
      dockerfile: docker/php/Dockerfile
    volumes:
      - ./src:/var/www/html
    depends_on:
      - db
    networks:
      - laravel

  web:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./src:/var/www/html
      - ./docker/nginx/default.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - app
    networks:
      - laravel

  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: laravel
      MYSQL_USER: laravel
      MYSQL_PASSWORD: secret
      MYSQL_ROOT_PASSWORD: secret
    ports:
      - "3306:3306"
    volumes:
      - db-data:/var/lib/mysql
    networks:
      - laravel

  node:
    image: node:20-alpine
    volumes:
      - ./src:/var/www/html
    working_dir: /var/www/html
    ports:
      - "5173:5173"
    networks:
      - laravel

volumes:
  db-data:

networks:
  laravel:
```

前回との違いは、React（Vite）用の`node`サービスを追加している点です。

### Dockerfile（docker/php/Dockerfile）

```
FROM php:8.3-fpm

RUN apt-get update && apt-get install -y \
    git \
    curl \
    libpng-dev \
    libonig-dev \
    libxml2-dev \
    zip \
    unzip \
    cron \
    && docker-php-ext-install pdo_mysql mbstring exif pcntl bcmath gd \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

WORKDIR /var/www/html
```

ポイントは`cron`パッケージを追加している点です。Laravelのスケジューラを動かすために必要です。

### Nginx設定（docker/nginx/default.conf）

```
server {
    listen 80;
    index index.php index.html;
    root /var/www/html/public;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        fastcgi_pass app:9000;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        include fastcgi_params;
    }

    location ~ /\.ht {
        deny all;
    }
}
```

## Step 2: Laravelプロジェクトの作成

```
# ディレクトリ作成 & コンテナ起動
mkdir laravel-weather && cd laravel-weather
mkdir -p docker/nginx docker/php src

# （上記の各設定ファイルを配置した後）
docker compose up -d --build

# Laravelプロジェクト作成
docker compose exec app composer create-project laravel/laravel .

# .envのDB設定を変更
# DB_CONNECTION=mysql
# DB_HOST=db
# DB_PORT=3306
# DB_DATABASE=laravel
# DB_USERNAME=laravel
# DB_PASSWORD=secret
```

## Step 3: React（Inertia.js）のセットアップ

Laravel + Reactの組み合わせには**Inertia.js**を使います。LaravelのルーティングとReactコンポーネントをシームレスに繋いでくれるフレームワークです。

```
# Breeze + Reactスタックをインストール
docker compose exec app composer require laravel/breeze --dev
docker compose exec app php artisan breeze:install react

# npm依存関係のインストール & ビルド
docker compose exec node npm install
docker compose exec node npm run build
```

## Step 4: 気象データ用のモデルとマイグレーション

```
docker compose exec app php artisan make:model WeatherReport -m
```

### マイグレーションファイル

```
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('weather_reports', function (Blueprint $table) {
            $table->id();
            $table->date('report_date');
            $table->string('location');
            $table->json('weather_data');
            $table->timestamps();

            $table->unique(['report_date', 'location']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('weather_reports');
    }
};
```

### モデル（app/Models/WeatherReport.php）

```
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class WeatherReport extends Model
{
    protected $fillable = [
        'report_date',
        'location',
        'weather_data',
    ];

    protected $casts = [
        'report_date' => 'date',
        'weather_data' => 'array',
    ];
}
```

```
docker compose exec app php artisan migrate
```

## Step 5: Claude APIで気象情報を取得するコマンド

```
docker compose exec app php artisan make:command FetchWeatherReport
```

### app/Console/Commands/FetchWeatherReport.php

```
<?php

namespace App\Console\Commands;

use App\Models\WeatherReport;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class FetchWeatherReport extends Command
{
    protected $signature = 'weather:fetch {location=東京}';
    protected $description = 'Claude APIのWeb検索で最新の気象情報を取得';

    public function handle(): int
    {
        $location = $this->argument('location');
        $today = now()->toDateString();

        $this->info("📡 {$location}の気象情報を取得中...");

        try {
            $response = Http::timeout(30)
                ->withHeaders([
                    'x-api-key' => config('services.anthropic.api_key'),
                    'anthropic-version' => '2023-06-01',
                ])
                ->post('https://api.anthropic.com/v1/messages', [
                    'model' => 'claude-sonnet-4-5-20250514',
                    'max_tokens' => 1024,
                    'tools' => [
                        [
                            'type' => 'web_search_20250305',
                            'name' => 'web_search',
                            'max_uses' => 3,
                        ],
                    ],
                    'messages' => [
                        [
                            'role' => 'user',
                            'content' => "{$location}の今日（{$today}）の天気予報をWeb検索で調べて、以下のJSON形式のみで返してください。説明文は不要です。\n\n```json\n{\"weather\": \"天気\", \"high_temp\": 最高気温の数値, \"low_temp\": 最低気温の数値, \"precipitation_chance\": 降水確率の数値, \"wind\": \"風の情報\", \"summary\": \"一言まとめ\"}\n```",
                        ],
                    ],
                ]);

            if (!$response->successful()) {
                $this->error('API呼び出しに失敗しました: ' . $response->status());
                Log::error('Weather API failed', ['status' => $response->status(), 'body' => $response->body()]);
                return 1;
            }

            $body = $response->json();

            // テキストブロックからJSON部分を抽出
            $text = collect($body['content'])
                ->where('type', 'text')
                ->pluck('text')
                ->implode('');

            if (!preg_match('/\{[^{}]*\}/s', $text, $matches)) {
                $this->error('JSONの抽出に失敗しました');
                Log::error('Weather JSON extraction failed', ['text' => $text]);
                return 1;
            }

            $weatherData = json_decode($matches[0], true);

            if (json_last_error() !== JSON_ERROR_NONE) {
                $this->error('JSONのパースに失敗しました');
                return 1;
            }

            WeatherReport::updateOrCreate(
                [
                    'report_date' => $today,
                    'location' => $location,
                ],
                [
                    'weather_data' => $weatherData,
                ]
            );

            $this->info("天気: {$weatherData['weather']}");
            $this->info("気温: {$weatherData['low_temp']}°C 〜 {$weatherData['high_temp']}°C");
            $this->info("降水確率: {$weatherData['precipitation_chance']}%");
            $this->info('保存しました');

            return 0;

        } catch (\Exception $e) {
            $this->error('エラーが発生しました: ' . $e->getMessage());
            Log::error('Weather fetch error', ['exception' => $e->getMessage()]);
            return 1;
        }
    }
}
```

### APIキーの設定

`src/.env`に追加：

```
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

`src/config/services.php`の配列に追加：

```
'anthropic' => [
    'api_key' => env('ANTHROPIC_API_KEY'),
],
```

### 動作確認

```
docker compose exec app php artisan weather:fetch 東京
```

```
📡 東京の気象情報を取得中...
天気: 晴れ時々曇り
気温: 18°C 〜 26°C
降水確率: 10%
保存しました
```

## Step 6: 毎日自動実行のスケジューラ設定

### Laravelスケジューラの登録

`src/routes/console.php`に追加：

```
use Illuminate\Support\Facades\Schedule;

Schedule::command('weather:fetch 東京')->dailyAt('06:00');
```

### Docker内でcronを動かす

appコンテナ内でLaravelのスケジューラをcronに登録します。

```
# appコンテナに入る
docker compose exec app bash

# crontabに登録
echo "* * * * * cd /var/www/html && php artisan schedule:run >> /dev/null 2>&1" | crontab -

# cronサービスを起動
service cron start

# 登録確認
crontab -l
```

## Step 7: APIエンドポイントの作成

`src/routes/api.php`に追加：

```
use App\Models\WeatherReport;

// 最新の気象情報
Route::get('/weather/latest', function () {
    return WeatherReport::where('location', request('location', '東京'))
        ->latest('report_date')
        ->first();
});

// 直近7日間の履歴
Route::get('/weather/history', function () {
    return WeatherReport::where('location', request('location', '東京'))
        ->latest('report_date')
        ->limit(7)
        ->get();
});
```

確認：

```
curl http://localhost:8080/api/weather/latest
```

## Step 8: Reactで気象情報を表示

### Inertia用のコントローラー

```
docker compose exec app php artisan make:controller WeatherController
```

`src/app/Http/Controllers/WeatherController.php`：

```
<?php

namespace App\Http\Controllers;

use App\Models\WeatherReport;
use Inertia\Inertia;

class WeatherController extends Controller
{
    public function index()
    {
        $latest = WeatherReport::where('location', '東京')
            ->latest('report_date')
            ->first();

        $history = WeatherReport::where('location', '東京')
            ->latest('report_date')
            ->limit(7)
            ->get();

        return Inertia::render('Weather/Index', [
            'latest' => $latest,
            'history' => $history,
        ]);
    }
}
```

### ルーティング

`src/routes/web.php`に追加：

```
use App\Http\Controllers\WeatherController;

Route::get('/weather', [WeatherController::class, 'index']);
```

### Reactコンポーネント

`src/resources/js/Pages/Weather/Index.tsx`：

```
import { Head } from '@inertiajs/react';

type WeatherData = {
    weather: string;
    high_temp: number;
    low_temp: number;
    precipitation_chance: number;
    wind: string;
    summary: string;
};

type WeatherReport = {
    id: number;
    report_date: string;
    location: string;
    weather_data: WeatherData;
};

type Props = {
    latest: WeatherReport | null;
    history: WeatherReport[];
};

export default function WeatherIndex({ latest, history }: Props) {
    return (
        <>
            <Head title="天気予報" />
            <div className="min-h-screen bg-gray-100 py-12">
                <div className="max-w-3xl mx-auto px-4">
                    <h1 className="text-3xl font-bold text-gray-900 mb-8">
                        天気予報
                    </h1>

                    {/* 今日の天気 */}
                    {latest ? (
                        <div className="bg-white rounded-2xl shadow p-6 mb-8">
                            <div className="flex items-center justify-between mb-4">
                                <h2 className="text-xl font-semibold text-gray-800">
                                    {latest.location}
                                </h2>
                                <span className="text-sm text-gray-500">
                                    {latest.report_date}
                                </span>
                            </div>

                            <p className="text-4xl font-bold text-blue-600 mb-4">
                                {latest.weather_data.weather}
                            </p>

                            <div className="grid grid-cols-3 gap-4 text-center">
                                <div className="bg-gray-50 rounded-lg p-3">
                                    <p className="text-sm text-gray-500">気温</p>
                                    <p className="text-lg font-semibold">
                                        {latest.weather_data.low_temp}°C 〜{' '}
                                        {latest.weather_data.high_temp}°C
                                    </p>
                                </div>
                                <div className="bg-gray-50 rounded-lg p-3">
                                    <p className="text-sm text-gray-500">降水確率</p>
                                    <p className="text-lg font-semibold">
                                        {latest.weather_data.precipitation_chance}%
                                    </p>
                                </div>
                                <div className="bg-gray-50 rounded-lg p-3">
                                    <p className="text-sm text-gray-500">風</p>
                                    <p className="text-lg font-semibold">
                                        {latest.weather_data.wind}
                                    </p>
                                </div>
                            </div>

                            <p className="mt-4 text-gray-600">
                                {latest.weather_data.summary}
                            </p>
                        </div>
                    ) : (
                        <div className="bg-white rounded-2xl shadow p-6 mb-8 text-center text-gray-500">
                            まだ気象データがありません。
                            <code className="block mt-2 text-sm">
                                php artisan weather:fetch
                            </code>
                            を実行してください。
                        </div>
                    )}

                    {/* 履歴 */}
                    {history.length > 1 && (
                        <div className="bg-white rounded-2xl shadow p-6">
                            <h2 className="text-xl font-semibold text-gray-800 mb-4">
                                直近の履歴
                            </h2>
                            <div className="divide-y">
                                {history.map((report) => (
                                    <div
                                        key={report.id}
                                        className="py-3 flex items-center justify-between"
                                    >
                                        <div>
                                            <span className="text-sm text-gray-500 mr-3">
                                                {report.report_date}
                                            </span>
                                            <span className="font-medium">
                                                {report.weather_data.weather}
                                            </span>
                                        </div>
                                        <span className="text-sm text-gray-600">
                                            {report.weather_data.low_temp}°C 〜{' '}
                                            {report.weather_data.high_temp}°C
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </>
    );
}
```

### ビルド & 確認

```
docker compose exec node npm run build
```

ブラウザで `http://localhost:8080/weather` にアクセスして表示を確認します。

## 本番を見据えた改善

### cronの永続化

コンテナ再起動でcronが消えないよう、Dockerfileに組み込む方法です。

`docker/php/crontab`を作成：

```
* * * * * cd /var/www/html && php artisan schedule:run >> /var/log/cron.log 2>&1
```

Dockerfileに追加：

```
COPY docker/php/crontab /etc/cron.d/laravel-scheduler
RUN chmod 0644 /etc/cron.d/laravel-scheduler \
    && crontab /etc/cron.d/laravel-scheduler
```

### 気象APIとの併用

Claude APIのWeb検索だけでも天気情報は取れますが、より正確なデータが必要な場合は**気象専用API + Claude**の2段構成がおすすめです。

```
[気象API（OpenWeatherMap等）] → 構造化データ取得
         ↓
[Claude API] → 自然言語で要約・解説を生成
         ↓
[DB保存]
```

## コスト感

| 項目 | 目安 |
| --- | --- |
| Claude API（1日1回） | 月30リクエスト、$1未満 |
| Web検索ツール | リクエストあたり数セント |
| Docker環境 | ローカルなら無料 |

1日1回の実行なので、API費用はほぼ気にならないレベルです。

## まとめ

この記事で構築した内容：

1. **Docker環境**（Nginx + PHP + MySQL + Node）でLaravel + Reactを動かす
2. **Claude APIのWeb検索**で最新の気象情報を自動取得
3. **Laravelスケジューラ**で毎朝6時に自動実行
4. **Inertia.js + React**でフロントエンドに表示

Claude APIのWeb検索機能を使うことで、外部の気象APIを契約しなくても最新の天気情報を取得できます。同じ仕組みで、ニュース要約や株価情報の取得など、さまざまな定期取得タスクに応用できます。

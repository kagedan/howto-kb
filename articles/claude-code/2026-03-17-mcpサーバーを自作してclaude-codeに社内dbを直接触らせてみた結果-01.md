---
id: "2026-03-17-mcpサーバーを自作してclaude-codeに社内dbを直接触らせてみた結果-01"
title: "MCPサーバーを自作して、Claude Codeに社内DBを直接触らせてみた結果"
url: "https://qiita.com/miruky/items/ea9c7e6d882502cbbf7c"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "Python", "qiita"]
date_published: "2026-03-17"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

```
import sqlite3

def init_database():
    conn = sqlite3.connect("company.db")
    cursor = conn.cursor()

    # 社員テーブル
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            position TEXT NOT NULL,
            salary INTEGER NOT NULL,
            hire_date TEXT NOT NULL
        )
    """)

    # 売上テーブル
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            amount INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            sale_date TEXT NOT NULL,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        )
    """)

    # サンプルデータ投入
    employees = [
        (1, "田中太郎", "営業部", "部長", 8500000, "2015-04-01"),
        (2, "佐藤花子", "営業部", "主任", 5500000, "2018-04-01"),
        (3, "鈴木一郎", "開発部", "マネージャー", 7800000, "2016-07-01"),
        (4, "高橋美咲", "開発部", "エンジニア", 6200000, "2020-04-01"),
        (5, "伊藤健太", "人事部", "課長", 6800000, "2017-10-01"),
        (6, "渡辺結衣", "営業部", "一般", 4200000, "2022-04-01"),
        (7, "山本大輔", "開発部", "エンジニア", 5800000, "2021-04-01"),
        (8, "中村さくら", "経理部", "主任", 5200000, "2019-04-01"),
    ]

    sales = [
        (1, "クラウドプランA", 1200000, 3, "2025-01-15", 1),
        (2, "クラウドプランB", 800000, 5, "2025-01-20", 2),
        (3, "オンプレライセンス", 3500000, 1, "2025-02-01", 1),
        (4, "コンサルティング", 2000000, 2, "2025-02-10", 6),
        (5, "クラウドプランA", 1200000, 4, "2025-03-05", 2),
        (6, "保守サポート", 600000, 10, "2025-03-15", 1),
        (7, "クラウドプランB", 800000, 7, "2025-04-01", 6),
        (8, "開発受託", 5000000, 1, "2025-04-20", 3),
        (9, "クラウドプランA", 1200000, 2, "2025-05-10", 2),
        (10, "セキュリティ監査", 1500000, 3, "2025-05-25", 5),
    ]

    cursor.executemany(
        "INSERT OR REPLACE INTO employees VALUES (?, ?, ?, ?, ?, ?)", employees
    )
    cursor.executemany(
        "INSERT OR REPLACE INTO sales VALUES (?, ?, ?, ?, ?, ?)", sales
    )

    conn.commit()
    conn.close()
    print("company.db を作成しました")

if __name__ == "__main__":
    init_database()
```

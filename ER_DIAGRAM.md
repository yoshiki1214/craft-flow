# ER図 - 精算システム

## テーブル一覧

1. **Clients（顧客）** - 顧客情報を格納
2. **Items（商品）** - 商品情報を格納
3. **Sales（売上）** - レシート番号、売上日時を格納
4. **SaleDetails（売上明細）** - 単価、数量、売上金額を格納
5. **Settlements（精算）** - 委託販売精算書に必要な項目を格納

## ER図（Mermaid形式）

```mermaid
erDiagram
    Clients ||--o{ Items : "has"
    Clients ||--o{ Sales : "has"
    Clients ||--o{ Settlements : "has"
    Items ||--o{ SaleDetails : "has"
    Sales ||--o{ SaleDetails : "has"

    Clients {
        INT id PK "自動採番"
        VARCHAR client_code "クライアントコード（UK, IDX）"
        VARCHAR client_name "会社名（NOT NULL, IDX）"
        VARCHAR postal_code "郵便番号"
        VARCHAR address "住所"
        VARCHAR contact_person "担当者名"
        VARCHAR phone_number "電話番号（UK, IDX）"
        VARCHAR fax_number "FAX番号（UK）"
        VARCHAR email "メールアドレス（UK）"
        DECIMAL commission_rate "手数料率（NOT NULL）"
        DATE contract_date "契約開始日"
        VARCHAR bank_name "銀行名（NOT NULL）"
        VARCHAR branch_name "支店名（NOT NULL）"
        VARCHAR branch_number "支店番号（NOT NULL）"
        VARCHAR account_type "口座種別（NOT NULL）"
        VARCHAR account_number "口座番号（NOT NULL）"
        VARCHAR account_holder "口座名義（NOT NULL）"
        TEXT remarks "備考"
        DATETIME created_at "作成日時"
        DATETIME updated_at "更新日時"
    }

    Items {
        INT id PK "自動採番"
        INT item_code "商品コード（NOT NULL, UK, IDX）"
        INT clients_id FK "クライアントID（IDX）"
        VARCHAR item_name "商品名（NOT NULL, UK, IDX）"
        VARCHAR category "カテゴリ（IDX）"
        DATETIME created_at "作成日時"
        DATETIME updated_at "更新日時"
    }

    Sales {
        INT id PK "自動採番（AUTO INCREMENT）"
        INT receipt_number "レシート番号（UK, IDX）"
        DATETIME sale_datetime "売上日時（IDX）"
        DATETIME created_at "作成日時"
        DATETIME updated_at "更新日時"
    }

    SaleDetails {
        INT id PK "自動採番（AUTO INCREMENT, IDX）"
        INT sales_id FK "売上ID（IDX）"
        INT items_id FK "商品ID（IDX）"
        INT unit_price "単価（NOT NULL）"
        INT quantity "数量（NOT NULL）"
        INT sale_amount "売上金額（NOT NULL）"
        DATETIME created_at "作成日時"
        DATETIME updated_at "更新日時"
    }

    Settlements {
        INT id PK "自動採番（AUTO INCREMENT, IDX）"
        INT clients_id FK "クライアントID"
        DATE issue_date "発行日（NOT NULL）"
        DATE period_start_date "精算開始日（NOT NULL, IDX）"
        DATE period_end_date "精算終了日（NOT NULL, IDX）"
        INT total_sales "売上合計額（NOT NULL）"
        INT commission_fee "委託手数料（NOT NULL）"
        INT commission_tax "消費税額（NOT NULL）"
        INT bank_transfer_fee "振込手数料"
        INT payment_amount "支払額（NOT NULL）"
        DATE scheduled_payment_date "振込予定日（IDX）"
        DATETIME created_at "作成日時"
        DATETIME updated_at "更新日時"
    }
```

## テーブル詳細

### 1. Clients（顧客テーブル）
- **主キー**: `id` (INT, 自動採番)
- **ユニークキー**: `client_code`, `phone_number`, `fax_number`, `email`
- **インデックス**: `id`, `client_code`, `client_name`, `phone_number`
- **説明**: 顧客情報を格納するテーブル。銀行口座情報も含む

### 2. Items（商品テーブル）
- **主キー**: `id` (INT, 自動採番)
- **外部キー**: `clients_id` → Clients.id
- **ユニークキー**: `item_code`, `item_name`
- **インデックス**: `item_code`, `clients_id`, `item_name`, `category`
- **説明**: 商品情報を格納。単価は変動する可能性があるため、売上明細テーブルへ格納

### 3. Sales（売上ヘッダテーブル）
- **主キー**: `id` (INT, 自動採番)
- **ユニークキー**: `receipt_number`
- **インデックス**: `receipt_number`, `sale_datetime`
- **説明**: レシート番号、売上日時を格納

### 4. SaleDetails（売上明細テーブル）
- **主キー**: `id` (INT, 自動採番)
- **外部キー**: 
  - `sales_id` → Sales.id
  - `items_id` → Items.id
- **インデックス**: `id`, `sales_id`, `items_id`
- **説明**: 単価、数量、売上金額を格納。売上時点での商品単価を保持

### 5. Settlements（委託販売精算テーブル）
- **主キー**: `id` (INT, 自動採番)
- **外部キー**: `clients_id` → Clients.id
- **インデックス**: `id`, `period_start_date`, `period_end_date`, `scheduled_payment_date`
- **説明**: 委託販売精算書に必要な項目を格納

## リレーションシップ

1. **Clients → Items**: 1対多（1つの顧客が複数の商品を持つ）
2. **Clients → Sales**: 1対多（1つの顧客が複数の売上を持つ）
3. **Clients → Settlements**: 1対多（1つの顧客が複数の精算を持つ）
4. **Items → SaleDetails**: 1対多（1つの商品が複数の売上明細に含まれる）
5. **Sales → SaleDetails**: 1対多（1つの売上が複数の明細を持つ）


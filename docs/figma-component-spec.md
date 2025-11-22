# Figmaコンポーネント仕様書
## 全銀フォーマット変換システム

このドキュメントは、Figmaでコンポーネントを作成する際の詳細な仕様です。

---

## 1. ナビゲーションバーコンポーネント

### 1.1 基本構造

```
[Navigation Bar Component]
├── Container (Frame)
│   ├── Logo Section (Auto Layout - Horizontal)
│   │   ├── Logo Icon Container (Frame)
│   │   │   └── Document Icon (Vector)
│   │   └── Title Text (Text)
│   └── History Button (Component Instance)
```

### 1.2 仕様

#### Container
- **Type**: Frame with Auto Layout
- **Direction**: Horizontal
- **Justify**: Space Between
- **Align**: Center
- **Width**: Fill Container (1280px max)
- **Height**: 64px
- **Padding**: Horizontal 16px (Mobile) / 24px (Tablet) / 32px (Desktop)
- **Background**: White (#FFFFFF)
- **Border**: Bottom 1px solid Gray-200
- **Effects**: Shadow Sm

#### Logo Section
- **Type**: Frame with Auto Layout
- **Direction**: Horizontal
- **Gap**: 16px
- **Align**: Center

#### Logo Icon Container
- **Size**: 48px × 48px
- **Background**: Primary Gradient (135deg, Blue-500 → Cyan-600)
- **Border Radius**: 12px
- **Effects**: Shadow Md
- **Constraints**: Center

#### Document Icon (SVG)
- **Size**: 32px × 32px
- **Color**: White
- **ViewBox**: 0 0 24 24
- **Constraints**: Center

#### Title Text
- **Text**: "全銀フォーマット変換"
- **Font Size**: 30px
- **Font Weight**: 800 (Extrabold)
- **Fill**: Text Gradient (Blue-600 → Cyan-600)
- **Font Family**: System Sans

### 1.3 バリアント

#### Logo (Default / Hover)
- **Default**: Shadow Md
- **Hover**: Shadow Lg, Scale 105%

#### Title Text (Default / Hover)
- **Default**: Blue-600 → Cyan-600
- **Hover**: Blue-700 → Cyan-700

---

## 2. 変換履歴ボタンコンポーネント

### 2.1 基本構造

```
[History Button Component]
└── Button (Frame with Auto Layout - Horizontal)
    ├── Clock Icon (Vector)
    └── Button Text (Text)
```

### 2.2 仕様

#### Button Frame
- **Type**: Frame with Auto Layout
- **Direction**: Horizontal
- **Gap**: 16px
- **Padding**: 32px (X) × 16px (Y)
- **Border Radius**: 16px
- **Effects**: Shadow Md

#### バリアント

##### Default State
- **Background**: Transparent
- **Border**: None
- **Text Color**: Blue-600
- **Icon Color**: Blue-600
- **Effects**: Shadow Md

##### Hover State
- **Background**: Blue-50
- **Text Color**: Blue-800
- **Icon Color**: Blue-800
- **Icon Scale**: 110%
- **Effects**: Shadow Lg

#### Clock Icon
- **Size**: 40px × 40px
- **ViewBox**: 0 0 24 24
- **Constraints**: Center

#### Button Text
- **Text**: "変換履歴"
- **Font Size**: 30px
- **Font Weight**: 800 (Extrabold)
- **Font Family**: System Sans

---

## 3. ヒーローアイコンコンポーネント

### 3.1 基本構造

```
[Hero Icon Component]
└── Icon Container (Frame)
    └── Document Icon (Vector)
```

### 3.2 仕様

#### Icon Container
- **Size**: 96px × 96px
- **Background**: Primary Gradient (135deg, Blue-500 → Cyan-600)
- **Border Radius**: 24px
- **Effects**: Shadow Xl

#### Document Icon
- **Size**: 56px × 56px
- **Color**: White
- **ViewBox**: 0 0 24 24
- **Constraints**: Center

---

## 4. ファイルアップロードエリアコンポーネント

### 4.1 基本構造

```
[File Upload Component]
└── Upload Area (Frame with Auto Layout - Vertical)
    ├── Upload Icon (Vector)
    ├── Main Text (Text)
    └── Sub Text (Text)
```

### 4.2 仕様

#### Upload Area
- **Type**: Frame with Auto Layout
- **Direction**: Vertical
- **Align**: Center
- **Gap**: 24px
- **Padding**: 48px
- **Width**: Fill Container
- **Border**: 2px dashed Blue-300
- **Border Radius**: 24px
- **Background**: Blue-50 (50% opacity)

#### バリアント

##### Default State
- **Background**: Blue-50/50
- **Border Color**: Blue-300
- **Effects**: None

##### Hover State
- **Background**: Blue-100/50
- **Border Color**: Blue-400
- **Effects**: Shadow Lg
- **Cursor**: Pointer

##### Selected State
- **Background**: Blue-100/70
- **Border Color**: Blue-500
- **Border Style**: Solid
- **Effects**: Shadow Lg

#### Upload Icon
- **Size**: 80px × 80px
- **Color**: Blue-600
- **ViewBox**: 0 0 24 24
- **Constraints**: Center

#### Main Text
- **Text**: "Excelファイルを選択"
- **Font Size**: 24px
- **Font Weight**: 700 (Bold)
- **Color**: Gray-700
- **Align**: Center

##### "Excelファイルを選択"部分のみ
- **Color**: Blue-600

#### Sub Text
- **Text**: "対応形式: .xlsx, .xls"
- **Font Size**: 16px
- **Font Weight**: 400 (Regular)
- **Color**: Gray-500
- **Align**: Center

### 4.3 選択ファイル表示テキスト（別コンポーネント）

#### Selected File Text
- **Type**: Text
- **Text**: "選択中: [ファイル名]"
- **Font Size**: 18px
- **Font Weight**: 600 (Semibold)
- **Color**: Blue-600
- **Font Family**: Mono（ファイル名部分のみ）

---

## 5. 変換ボタンコンポーネント

### 5.1 基本構造

```
[Convert Button Component]
└── Button (Frame with Auto Layout - Horizontal)
    ├── Icon Layer (Vector or Spinner)
    └── Button Text (Text)
```

### 5.2 仕様

#### Button Frame
- **Type**: Frame with Auto Layout
- **Direction**: Horizontal
- **Gap**: 20px
- **Align**: Center
- **Padding**: 80px (X) × 32px (Y)
- **Border Radius**: 24px
- **Min Width**: 240px
- **Effects**: Shadow 2xl

### 5.3 バリアント

#### Default State
- **Background**: Button Gradient (90deg, Blue-600 → Cyan-600 → Sky-600)
- **Text Color**: White
- **Icon Color**: White
- **Effects**: Shadow 2xl

#### Hover State
- **Background**: Button Hover Gradient (90deg, Blue-700 → Cyan-700 → Sky-700)
- **Effects**: Shadow Blue (50% opacity)
- **Scale**: 110%
- **Transform**: Translate Y -4px

#### Active State
- **Scale**: 95%

#### Disabled State
- **Opacity**: 50%
- **Cursor**: Not Allowed

#### Loading State
- **Background**: Button Gradient
- **Icon**: Spinner (48px × 48px, White, Rotating)
- **Text**: "処理中..."
- **Effects**: Shadow 2xl

#### Icon (Default)
- **Type**: Vector (Download Arrow)
- **Size**: 48px × 48px
- **Color**: White
- **ViewBox**: 0 0 24 24
- **Hover Transform**: Rotate 12deg, Scale 110%

#### Icon (Loading)
- **Type**: Vector (Spinner)
- **Size**: 48px × 48px
- **Color**: White
- **Animation**: Rotate 360deg (continuous)

#### Button Text
- **Font Size**: 30px
- **Font Weight**: 700 (Bold)
- **Color**: White
- **Font Family**: System Sans
- **Default Text**: "全銀データを出力"
- **Loading Text**: "処理中..."

---

## 6. メインカードコンポーネント

### 6.1 基本構造

```
[Main Card Component]
└── Card (Frame with Auto Layout - Vertical)
    ├── Form Container (Frame with Auto Layout - Vertical)
    │   ├── File Upload Component Instance
    │   └── Convert Button Component Instance
    └── Selected File Text (Conditional)
```

### 6.2 仕様

#### Card Frame
- **Type**: Frame with Auto Layout
- **Direction**: Vertical
- **Align**: Center
- **Gap**: 48px
- **Padding**: 48px
- **Width**: Fill Container (1024px max)
- **Background**: Card Gradient (135deg, White → Blue-50/30 → Cyan-50/30)
- **Border**: 2px solid Blue-100
- **Border Radius**: 24px
- **Effects**: Shadow 2xl, Backdrop Blur (optional)

### 6.3 バリアント

#### Default State
- **Background**: Card Gradient
- **Effects**: Shadow 2xl

#### Hover State
- **Effects**: Shadow 2xl (intensified)

---

## 7. フッターコンポーネント

### 7.1 基本構造

```
[Footer Component]
└── Footer Container (Frame with Auto Layout)
    └── Copyright Text (Text)
```

### 7.2 仕様

#### Footer Container
- **Type**: Frame with Auto Layout
- **Direction**: Horizontal
- **Justify**: Center
- **Align**: Center
- **Width**: Fill Container (1280px max)
- **Height**: Auto
- **Padding**: 16px Vertical
- **Background**: White
- **Border**: Top 1px solid Gray-200

#### Copyright Text
- **Text**: "© 2024 全銀フォーマット変換システム"
- **Font Size**: 14px
- **Font Weight**: 400 (Regular)
- **Color**: Gray-500
- **Align**: Center

---

## 8. アラートメッセージコンポーネント

### 8.1 基本構造

```
[Alert Component]
└── Alert Container (Frame with Auto Layout - Horizontal)
    ├── Icon Container (Frame)
    │   └── Icon (Vector)
    └── Message Text (Text)
```

### 8.2 仕様

#### Alert Container
- **Type**: Frame with Auto Layout
- **Direction**: Horizontal
- **Gap**: 16px
- **Align**: Center
- **Padding**: 24px
- **Border Radius**: 8px
- **Border**: 2px solid

### 8.3 バリアント

#### Success State
- **Background**: Blue-50
- **Border Color**: Blue-200
- **Text Color**: Blue-800
- **Icon Color**: Blue-400
- **Icon**: Checkmark Circle (32px × 32px)

#### Error State
- **Background**: Red-50
- **Border Color**: Red-200
- **Text Color**: Red-800
- **Icon Color**: Red-400
- **Icon**: X Circle (32px × 32px)

#### Message Text
- **Font Size**: 24px
- **Font Weight**: 700 (Bold)
- **Font Family**: System Sans

---

## 9. コンポーネント作成のベストプラクティス

### 9.1 オートレイアウトの活用

すべてのコンポーネントにオートレイアウトを適用：
- **Padding**: コンポーネント内のスペーシング
- **Gap**: 子要素間のスペーシング
- **Fill Container**: 親要素に合わせて伸縮
- **Hug Contents**: コンテンツに合わせてサイズ調整

### 9.2 バリアントの設定

状態ごとにバリアントを作成：
- **Property**: State
- **Values**: Default, Hover, Active, Disabled, Loading

### 9.3 プロパティの設定

再利用可能な値をプロパティ化：
- **Text Content**: テキストコンテンツをプロパティ化
- **Icon**: アイコンの種類をプロパティ化
- **Size**: サイズバリアントを作成

### 9.4 制約の設定

レスポンシブ対応のため：
- **Horizontal**: Left & Right, Center, Left, Right
- **Vertical**: Top & Bottom, Center, Top, Bottom

### 9.5 コンポーネントセットの構成

```
Component Set: Button
├── Variant: Default / Hover / Active / Disabled / Loading
└── Variant: Size (Small / Medium / Large)
```

---

## 10. Figma実装チェックリスト

### 10.1 デザインシステム
- [ ] すべてのカラーをColor Styleとして定義
- [ ] すべてのテキストスタイルをText Styleとして定義
- [ ] すべてのエフェクト（シャドウ）をEffect Styleとして定義

### 10.2 コンポーネント
- [ ] ナビゲーションバーコンポーネント
- [ ] 変換履歴ボタンコンポーネント（バリアント含む）
- [ ] ヒーローアイコンコンポーネント
- [ ] ファイルアップロードエリアコンポーネント（バリアント含む）
- [ ] 変換ボタンコンポーネント（全バリアント）
- [ ] メインカードコンポーネント
- [ ] フッターコンポーネント
- [ ] アラートメッセージコンポーネント（バリアント含む）

### 10.3 ページレイアウト
- [ ] デスクトップ版フレーム（1440×900）
- [ ] タブレット版フレーム（768×1024）
- [ ] モバイル版フレーム（375×812）
- [ ] すべてのコンポーネントを配置
- [ ] レスポンシブ制約を設定

### 10.4 プロトタイピング
- [ ] ボタンのホバー状態
- [ ] ボタンのクリック動作
- [ ] ファイルアップロードエリアのインタラクション
- [ ] ページ間の遷移（履歴ページへのリンク）

### 10.5 ドキュメント
- [ ] コンポーネントの使用方法を説明
- [ ] デザイントークンとの関連を明記
- [ ] 開発者向けの仕様を共有

---

この仕様書に基づいて、Figmaでコンポーネントを作成してください。


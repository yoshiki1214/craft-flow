# Figmaデザイン仕様書
## 全銀フォーマット変換システム

このドキュメントは、Figmaでトップページデザインを作成するための詳細な仕様書です。

---

## 1. デザインシステム概要

### 1.1 カラーパレット

#### プライマリカラー
- **Blue-500**: `#3B82F6` - アイコン背景、アクセント
- **Blue-600**: `#2563EB` - プライマリボタン、リンク
- **Blue-700**: `#1D4ED8` - ホバー状態
- **Blue-800**: `#1E40AF` - ホバー時のリンク
- **Cyan-600**: `#0891B2` - グラデーション終点、アクセント
- **Cyan-700**: `#0E7490` - ホバー状態
- **Sky-600**: `#0284C7` - グラデーション中間

#### セカンダリカラー
- **Gray-50**: `#F9FAFB` - ページ背景
- **Gray-100**: `#F3F4F6` - ボーダー
- **Gray-500**: `#6B7280` - サブテキスト
- **Gray-700**: `#374151` - 本文テキスト
- **Gray-900**: `#111827` - 見出し（未使用だが定義）

#### ステータスカラー
- **Red-50**: `#FEF2F2` - エラー背景
- **Red-200**: `#FECACA` - エラーボーダー
- **Red-400**: `#F87171` - エラーアイコン
- **Red-800**: `#991B1B` - エラーテキスト
- **Blue-50**: `#EFF6FF` - 成功背景、ホバー背景
- **Blue-200**: `#BFDBFE` - 成功ボーダー
- **Blue-400**: `#60A5FA` - 成功アイコン
- **Blue-800**: `#1E40AF` - 成功テキスト

#### グラデーション
- **Primary Gradient**: `linear-gradient(135deg, #3B82F6 0%, #0891B2 100%)`
- **Button Gradient**: `linear-gradient(90deg, #2563EB 0%, #0891B2 50%, #0284C7 100%)`
- **Button Hover**: `linear-gradient(90deg, #1D4ED8 0%, #0E7490 50%, #0369A1 100%)`
- **Text Gradient**: `linear-gradient(90deg, #2563EB 0%, #0891B2 100%)`

### 1.2 タイポグラフィ

#### フォントファミリー
- **基本**: システムフォント（-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif）
- **等幅**: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace

#### フォントサイズとウェイト
- **H1**: 60px (3.75rem) / Font Weight: 800 (Extrabold) / Line Height: 1.1
- **H2**: 30px (1.875rem) / Font Weight: 700 (Bold) / Line Height: 1.5
- **H3**: 24px (1.5rem) / Font Weight: 800 (Extrabold) / Line Height: 1.4
- **Body Large**: 24px (1.5rem) / Font Weight: 400 (Regular) / Line Height: 1.75
- **Body**: 16px (1rem) / Font Weight: 400 (Regular) / Line Height: 1.5
- **Body Small**: 14px (0.875rem) / Font Weight: 400 (Regular) / Line Height: 1.5
- **Button**: 30px (1.875rem) / Font Weight: 700 (Bold) / Line Height: 1.5

#### テキストスタイル
- **グラデーションテキスト**: 背景をグラデーションにし、`background-clip: text`でテキストに適用
- **フォントモノスペース**: ファイル名表示用

### 1.3 スペーシング

#### 基準値
- **Base Unit**: 4px

#### スペーシングスケール
- **xs**: 4px (0.25rem)
- **sm**: 8px (0.5rem)
- **md**: 16px (1rem)
- **lg**: 24px (1.5rem)
- **xl**: 32px (2rem)
- **2xl**: 48px (3rem)
- **3xl**: 64px (4rem)
- **4xl**: 96px (6rem)

#### コンポーネント内パディング
- **Card Padding**: 48px (3rem)
- **Button Padding**: 80px (5rem) × 32px (2rem)
- **Navbar Padding**: 16px (1rem) / 24px (1.5rem) / 32px (2rem)（レスポンシブ）
- **Container Padding**: 24px (1.5rem) / 24px (1.5rem) / 32px (2rem)（レスポンシブ）

### 1.4 ボーダーとシャドウ

#### ボーダー半径
- **sm**: 8px (0.5rem)
- **md**: 16px (1rem)
- **lg**: 24px (1.5rem) - ボタン、カード
- **xl**: 32px (2rem) - メインカード、アイコン

#### シャドウ
- **Shadow Sm**: `0 1px 2px 0 rgba(0, 0, 0, 0.05)`
- **Shadow Md**: `0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)`
- **Shadow Lg**: `0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)`
- **Shadow Xl**: `0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)`
- **Shadow 2xl**: `0 25px 50px -12px rgba(0, 0, 0, 0.25)`
- **Shadow Blue**: `0 25px 50px -12px rgba(37, 99, 235, 0.25)`

#### ボーダー
- **Border Width**: 2px
- **Border Style**: solid（通常）、dashed（ファイルアップロードエリア）

---

## 2. レイアウト構造

### 2.1 画面サイズ（ブレークポイント）
- **Mobile**: 375px × 812px（iPhone標準）
- **Tablet**: 768px × 1024px（iPad標準）
- **Desktop**: 1440px × 900px（推奨最小）
- **Desktop Large**: 1920px × 1080px（フルHD）

### 2.2 コンテナ幅
- **Max Width**: 1280px (max-w-7xl)
- **Content Max Width**: 1024px (max-w-5xl)

### 2.3 グリッドシステム
- **カラム数**: 12カラム
- **ガター**: 24px (1.5rem)

---

## 3. コンポーネント仕様

### 3.1 ナビゲーションバー（Navbar）

#### 構造
```
┌─────────────────────────────────────────┐
│  [Logo Icon + タイトル]  [変換履歴ボタン] │
└─────────────────────────────────────────┘
```

#### 仕様
- **高さ**: 64px (4rem)
- **背景**: White (#FFFFFF)
- **ボーダー**: Bottom 1px solid Gray-200
- **シャドウ**: Shadow Sm
- **パディング**: Horizontal 16px (Mobile) / 24px (Tablet) / 32px (Desktop)

#### Logoアイコン
- **サイズ**: 48px × 48px
- **背景**: Primary Gradient
- **ボーダー半径**: 12px (rounded-xl)
- **シャドウ**: Shadow Md
- **アイコンサイズ**: 32px × 32px (White)

#### タイトルテキスト
- **サイズ**: 30px (1.875rem)
- **ウェイト**: 800 (Extrabold)
- **スタイル**: グラデーションテキスト（Blue-600 → Cyan-600）
- **間隔**: Logoから16px (4rem)

#### 変換履歴ボタン
- **パディング**: 32px (2rem) × 16px (1rem)
- **サイズ**: 30px (1.875rem)
- **ウェイト**: 800 (Extrabold)
- **カラー**: Blue-600
- **ボーダー半径**: 16px (rounded-2xl)
- **シャドウ**: Shadow Md
- **ホバー**: Blue-800、Background Blue-50、Shadow Lg

### 3.2 ヒーローセクション

#### 構造
```
┌─────────────────────────┐
│      [アイコン 96px]     │
│                         │
│    [H1 タイトル]         │
│                         │
│  [説明テキスト 24px]     │
└─────────────────────────┘
```

#### アイコンコンテナ
- **サイズ**: 96px × 96px
- **背景**: Primary Gradient
- **ボーダー半径**: 24px (rounded-3xl)
- **シャドウ**: Shadow Xl
- **アイコンサイズ**: 56px × 56px (White)
- **マージン**: Bottom 24px

#### H1タイトル
- **サイズ**: 60px (3.75rem)
- **ウェイト**: 800 (Extrabold)
- **スタイル**: グラデーションテキスト
- **行の高さ**: 1.1 (leading-tight)
- **マージン**: Bottom 20px

#### 説明テキスト
- **サイズ**: 24px (1.5rem)
- **カラー**: Gray-700
- **最大幅**: 768px (max-w-3xl)
- **行の高さ**: 1.75 (leading-relaxed)
- **中央揃え**

### 3.3 メインカード（変換フォーム）

#### 構造
```
┌─────────────────────────────────┐
│                                 │
│   [ファイルアップロードエリア]   │
│                                 │
│        [変換ボタン]             │
│                                 │
└─────────────────────────────────┘
```

#### カード本体
- **背景**: Linear Gradient (White → Blue-50/30 → Cyan-50/30)
- **ボーダー**: 2px solid Blue-100
- **ボーダー半径**: 24px (rounded-3xl)
- **シャドウ**: Shadow 2xl
- **パディング**: 48px (3rem)
- **Backdrop Blur**: 軽いぼかし効果

#### ファイルアップロードエリア
- **パディング**: 48px (3rem) all
- **ボーダー**: 2px dashed Blue-300
- **ボーダー半径**: 24px (rounded-3xl)
- **背景**: Blue-50/50 (半透明)
- **ホバー**: Blue-100/50、Blue-400ボーダー、Shadow Lg

#### アップロードアイコン
- **サイズ**: 80px × 80px
- **カラー**: Blue-600
- **マージン**: Bottom 24px

#### アップロードテキスト
- **メイン**: 24px / Bold / Gray-700
  - "Excelファイルを選択"部分: Blue-600
- **サブ**: 16px / Regular / Gray-500

#### 選択ファイル表示
- **サイズ**: 18px (1.125rem)
- **カラー**: Blue-600
- **ウェイト**: 600 (Semibold)
- **フォント**: Monospace（ファイル名）

### 3.4 変換ボタン

#### デフォルト状態
- **パディング**: 80px (5rem) × 32px (2rem)
- **サイズ**: 30px (1.875rem)
- **ウェイト**: 700 (Bold)
- **カラー**: White
- **背景**: Button Gradient
- **ボーダー半径**: 24px (rounded-3xl)
- **シャドウ**: Shadow 2xl

#### ホバー状態
- **背景**: Button Hover Gradient
- **シャドウ**: Shadow Blue (50% opacity)
- **スケール**: 110%
- **Y軸移動**: -4px (上に移動)

#### アクティブ状態
- **スケール**: 95%

#### 無効状態
- **不透明度**: 50%
- **カーソル**: not-allowed

#### ローディング状態
- **スピナー**: 48px × 48px、White、回転アニメーション
- **テキスト**: "処理中..."

#### アイコン
- **サイズ**: 48px × 48px
- **マージン**: Right 20px
- **ホバー**: 12度回転、110%スケール

### 3.5 フッター

#### 仕様
- **背景**: White
- **ボーダー**: Top 1px solid Gray-200
- **パディング**: 16px (1rem) Vertical
- **テキスト**: 14px (0.875rem) / Gray-500 / 中央揃え

---

## 4. レスポンシブ対応

### 4.1 モバイル（375px以下）
- **ナビゲーション**: ロゴとボタンを縦並び、高さ拡張
- **ヒーロー**: H1サイズ 48px、説明文 20px
- **カード**: パディング 24px
- **ボタン**: パディング 60px × 24px、サイズ 24px

### 4.2 タブレット（768px）
- **ナビゲーション**: 横並び維持
- **ヒーロー**: H1サイズ 54px
- **カード**: パディング 36px

### 4.3 デスクトップ（1440px以上）
- すべての仕様を最大限適用

---

## 5. インタラクションとアニメーション

### 5.1 トランジション
- **Duration**: 300ms (0.3s)
- **Easing**: ease-in-out（標準）

### 5.2 ホバーエフェクト
- **スケール**: 1.05 ~ 1.1
- **シャドウ**: 拡張（1段階上）
- **カラー**: 1段階濃く（600 → 700/800）

### 5.3 ボタンアニメーション
- **ホバー**: グラデーション背景が横にスライド（skew効果）
- **クリック**: 軽い縮小（scale 0.95）

---

## 6. アクセシビリティ

### 6.1 コントラスト比
- **通常テキスト**: 最小 4.5:1
- **大きなテキスト（18px以上）**: 最小 3:1

### 6.2 フォーカス状態
- **フォーカスリング**: 4px solid Blue-300
- **オフセット**: 4px (ring-offset-4)

### 6.3 インタラクティブ要素
- **最小タッチターゲット**: 44px × 44px

---

## 7. Figma実装のヒント

### 7.1 推奨プラグイン
- **Stark**: コントラストチェック
- **A11y - Focus Order**: フォーカス順序確認
- **Figma Tokens**: デザイントークン管理

### 7.2 コンポーネント化
- ボタン（Default, Hover, Active, Disabled, Loading）
- カード（Default, Hover）
- ファイルアップロードエリア（Default, Hover, Selected）
- ナビゲーション（全体をコンポーネント化）

### 7.3 オートレイアウト
- すべてのコンポーネントにオートレイアウトを適用
- Fill container または Hug contents を適切に設定

### 7.4 スタイルの作成
- **Color Styles**: 全カラーをスタイル化
- **Text Styles**: 全テキストスタイルを定義
- **Effect Styles**: シャドウをスタイル化

---

## 8. デザインファイル構造（推奨）

```
📁 デザインファイル
├── 📄 フレーム
│   ├── Mobile (375×812)
│   ├── Tablet (768×1024)
│   └── Desktop (1440×900)
├── 🎨 デザインシステム
│   ├── Colors
│   ├── Typography
│   ├── Spacing
│   └── Effects
└── 🧩 コンポーネント
    ├── Navigation
    ├── Button
    ├── Card
    ├── FileUpload
    └── Footer
```

---

この仕様書を基に、Figmaでデザインを作成してください。
デザイントークンファイル（JSON）も別途提供しています。


# DormWatch 專案架構與功能說明

## 📋 專案概述

**DormWatch** 是一個以 **Web 為基礎的宿舍匿名回報與管理系統示範專案**，展示如何構建安全、高效的全棧 Web 應用。

- **後端技術**: Python Flask + SQLAlchemy
- **前端技術**: HTML / CSS / JavaScript
- **部署方式**: Docker / docker-compose
- **資料庫**: SQLite（示範用）

---

## 📂 專案結構

```
Dorm/
├── docker-compose.yml          # Docker 容器編排配置
├── backend/
│   ├── app.py                  # Flask 應用入口
│   ├── routes.py               # API 路由定義
│   ├── models.py               # 資料庫模型（ORM）
│   ├── requirements.txt         # Python 依賴列表
│   ├── Dockerfile              # Docker 構建配置
│   ├── README.md               # 後端說明文檔
│   ├── static/
│   │   ├── index.html          # 前端 SPA 主頁面
│   │   ├── script.js           # 前端邏輯（JavaScript）
│   │   └── style.css           # 前端樣式（CSS）
│   └── instance/               # Flask 實例資料夾
│       └── dormwatch.db        # SQLite 資料庫檔案
```

---

## 🏗️ 系統架構設計

### 後端架構

```
┌─────────────────────────┐
│   前端 (HTML/CSS/JS)    │
└────────────┬────────────┘
             │ HTTP/REST API
             ▼
┌─────────────────────────┐
│  Flask Web Framework    │
│ ├─ CORS 跨域設定       │
│ ├─ Flask-Login 驗證     │
│ └─ Rate Limiter 限流    │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│   API Routes (routes.py) │
│ ├─ 身分驗證 /register   │
│ ├─ /login & /logout     │
│ ├─ 回報提交 /report     │
│ ├─ 回報列表 /reports    │
│ └─ 點讚 /report/<id>/like
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  SQLAlchemy ORM Layer   │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│   SQLite Database       │
│ ├─ users (使用者)      │
│ ├─ reports (回報)      │
│ └─ report_likes (讚)    │
└─────────────────────────┘
```

### 資料流程

1. **前端** (script.js) → 發送 REST API 請求
2. **後端** (routes.py) → 驗證、處理、調用模型
3. **模型層** (models.py) → 操作資料庫
4. **資料庫** (SQLite) → 儲存資料
5. **後端** → 回傳 JSON 響應給前端

---

## 🔐 核心功能模塊

### 1. 身分驗證系統 (Authentication)

#### 資料模型
```python
class User:
  - id (主鍵)
  - username (唯一、必填)
  - password_hash (密碼雜湊)
  - created_at (建立時間)
```

#### API 端點

| 方法 | 端點 | 描述 | 權限 |
|------|------|------|------|
| POST | `/register` | 新用戶註冊 | 公開 |
| POST | `/login` | 用戶登入 | 公開 |
| POST | `/logout` | 用戶登出 | 需登入 |
| GET | `/me` | 獲取當前用戶信息 | 公開 |

#### 安全特性
- ✅ **密碼雜湊儲存**: 使用 `Werkzeug.security` 的 `generate_password_hash()`
- ✅ **Session Cookie 加固**: 設置 `HttpOnly`, `SameSite=Lax`
- ✅ **Flask-Login 集成**: 自動 Session 管理
- ✅ **輸入驗證**: 帳號最少 3 字元，密碼最少 6 字元

---

### 2. 匿名回報系統 (Anonymous Reports)

#### 資料模型
```python
class Report:
  - id (主鍵)
  - room (房號，如 "Z301")
  - content (回報內容，最多 1000 字)
  - nickname (伺服器端隨機生成，如 "可愛的貓咪")
  - likes (點讚計數)
  - status (狀態，預設 "pending")
  - created_at (建立時間)
```

#### API 端點

| 方法 | 端點 | 描述 | 權限 |
|------|------|------|------|
| POST | `/report` | 提交新回報 | 公開（無需登入） |
| GET | `/reports` | 獲取所有回報列表 | 公開 |
| POST | `/report/<id>/like` | 對回報點讚 | 需登入 |

#### 功能特性
- ✅ **完全匿名**: 使用者無需登入即可提交回報
- ✅ **服務端昵稱生成**: 防止用戶偽造昵稱
  - 由 6 個形容詞 × 6 個動物名稱組成
  - 示例: "瘋狂的水獺", "懶惰的貓咪"
- ✅ **速率限制**: 每 IP 每分鐘最多 5 個報告
- ✅ **輸入驗證**: 房號 ≤20 字元，內容 ≤1000 字元
- ✅ **XSS 防護**: 使用 `html.escape()` 轉義內容

---

### 3. 點讚系統 (Like System)

#### 資料模型
```python
class ReportLike:
  - id (主鍵)
  - user_id (外鍵 → User)
  - report_id (外鍵 → Report)
  - created_at (建立時間)
  - 唯一約束: (user_id, report_id) 不允許重複
```

#### 功能特性
- ✅ **需要登入**: 只有已登入使用者可點讚
- ✅ **防重複讚**: 同一用戶無法對同一報告點讚多次
- ✅ **速率限制**: 每 IP 每分鐘最多 10 個點讚請求
- ✅ **實時計數**: 點讚數實時更新並返回給前端

---

## 🎨 前端架構

### 技術棧
- **HTML5**: 語意化標記
- **CSS3**: 響應式設計與動畫效果
- **原生 JavaScript**: 無框架依賴（ES6+）
- **Fetch API**: 與後端通信

### 核心組件

#### 1. 身分驗證區域
```
┌─────────────────────────┐
│   登入 / 註冊 Form      │
│ ├─ Username Input       │
│ ├─ Password Input       │
│ ├─ Login Button         │
│ └─ Register Button      │
└─────────────────────────┘
```

#### 2. 回報提交區域
```
┌─────────────────────────┐
│   新增回報 Form         │
│ ├─ Room Input (房號)   │
│ ├─ Content Textarea     │
│ └─ Send Button          │
└─────────────────────────┘
```

#### 3. 回報列表區域
```
┌─────────────────────────┐
│   Report Card           │
│ ├─ 昵稱 + 房號 + 讚數  │
│ └─ 回報內容             │
│ (動態加載，新回報置頂)  │
└─────────────────────────┘
```

### JavaScript 主要功能

#### 全局變數
- `currentUser`: 追蹤當前登入用戶（null = 未登入）
- `reportList`: DOM 元素參考（回報列表容器）

#### 主要函式

| 函式 | 功能 |
|------|------|
| `buildReportDOM(report)` | 構建回報卡片 DOM 元素 |
| `loadReports()` | 非同步加載並顯示所有回報 |
| `disableForSeconds(btn, s)` | 按鈕暫時禁用（UX 限流) |
| `doRegister()` | 執行註冊邏輯 |
| `doLogin()` | 執行登入邏輯 |
| `doLogout()` | 執行登出邏輯 |
| `checkMe()` | 啟動時驗證用戶狀態 |
| `updateUserUI()` | 更新用戶 UI 顯示 |

#### 安全設計
- ✅ **XSS 防護**: 使用 `textContent` 而非 `innerHTML`
- ✅ **CORS 限制**: 僅允許本地源 (localhost:5000, 127.0.0.1:5000)
- ✅ **輸入驗證**: 客戶端和伺服器雙層驗證

---

## 🔒 安全機制總結

### 身分驗證安全
| 機制 | 說明 |
|------|------|
| 密碼雜湊 | Werkzeug PBKDF2 雜湊 |
| Session Cookie | HttpOnly, SameSite=Lax |
| Flask-Login | 自動登入狀態管理 |
| @login_required | API 級別存取控制 |

### 資料安全
| 機制 | 說明 |
|------|------|
| 輸入驗證 | 長度、格式驗證 |
| SQL 隱碼 (SQLi) 防護 | SQLAlchemy 參數化查詢 |
| XSS 防護 | html.escape() + textContent |
| 速率限制 | 按 IP 地址限流 |

### 網路安全
| 機制 | 說明 |
|------|------|
| CORS | 僅允許指定源 |
| HTTPS 支持 | SESSION_COOKIE_SECURE 可配置 |
| 環境變數 | SECRET_KEY 外部化 (非硬編碼) |

---

## 📦 依賴列表 (requirements.txt)

```
Flask==2.2.5                # Web 框架
Flask-Cors==3.0.10         # 跨域資源共享
Flask-Login==0.6.2         # 登入管理
Flask-SQLAlchemy==3.0.3    # ORM 層
Werkzeug==2.2.3            # WSGI 工具 + 加密
```

---

## 🐳 Docker 部署

### Dockerfile
```dockerfile
# 自動化構建後端容器
# - 安裝 Python 依賴
# - 設置工作目錄
# - 暴露 5000 端口
```

### docker-compose.yml
```yaml
version: '3.8'
services:
  backend:
    build: ./backend              # 根據 Dockerfile 構建
    ports:
      - "5000:5000"              # 映射端口
    environment:
      - SECRET_KEY=change_this_secret_in_prod
      - SESSION_COOKIE_SECURE=False  # 開發環境設 False
    volumes:
      - ./backend:/app            # 代碼卷掛載
      - ./backend/dormwatch.db:/app/dormwatch.db  # 資料庫卷掛載
```

### 啟動指令
```bash
docker-compose up --build    # 構建並啟動
docker-compose down          # 停止容器
```

---

## 🚀 啟動流程

### 開發環境 (本地)

1. **安裝依賴**
   ```bash
   pip install -r backend/requirements.txt
   ```

2. **啟動後端服務**
   ```bash
   cd backend
   python app.py
   ```
   服務將運行在: `http://localhost:5000`

3. **存取前端**
   - 在瀏覽器中打開: `http://localhost:5000/`
   - 自動提供 `index.html`

### Docker 環境 (容器化)

1. **構建並啟動**
   ```bash
   docker-compose up --build
   ```

2. **存取服務**
   - 打開: `http://localhost:5000/`

3. **停止服務**
   ```bash
   docker-compose down
   ```

---

## 📊 核心流程圖

### 用戶註冊流程
```
前端 Register Form
     ↓
  輸入驗證 (長度檢查)
     ↓
  POST /register
     ↓
後端檢查 (重複、有效性)
     ↓
Werkzeug 密碼雜湊
     ↓
存入 User 表
     ↓
返回 201 Created / 400 Error
```

### 匿名回報流程
```
前端 Report Form
     ↓
  輸入驗證 (長度檢查)
     ↓
  POST /report (無需登入)
     ↓
後端 IP 限流檢查
     ↓
伺服器生成隨機昵稱
     ↓
內容 HTML 轉義 (XSS 防護)
     ↓
存入 Report 表
     ↓
返回 201 Created + 報告數據
```

### 點讚流程
```
前端點擊讚按鈕
     ↓
檢查登入狀態
     ↓
  POST /report/<id>/like
     ↓
檢查 @login_required (驗證 Session)
     ↓
後端 IP 限流檢查
     ↓
查詢是否已讚過 (防重複)
     ↓
插入 ReportLike 記錄
     ↓
更新 Report.likes 計數
     ↓
返回 200 OK + 新計數
```

---

## 🎓 設計亮點

1. **前後端責任分離**
   - 前端: UI 交互、輸入驗證、狀態管理
   - 後端: 業務邏輯、資料驗證、安全控制

2. **雙層驗證**
   - 客戶端: 快速反饋、改善 UX
   - 服務器: 真正的安全保障

3. **無狀態 RESTful API**
   - 易於擴展、部署
   - Session 儲存在伺服器端

4. **匿名性與安全性平衡**
   - 允許完全匿名回報 (鼓勵使用)
   - 限制高級功能 (點讚需登入)
   - 伺服器端控制昵稱 (防止濫用)

5. **容器化部署**
   - 開發與生產環境一致性
   - 易於橫向擴展

---

## 📝 環境變數配置

| 變數 | 預設值 | 說明 |
|------|--------|------|
| `SECRET_KEY` | `change_this_in_prod` | Flask 會話加密密鑰 |
| `DATABASE_URI` | `sqlite:///dormwatch.db` | 資料庫連接字符串 |
| `SESSION_COOKIE_SECURE` | `False` | 僅 HTTPS 傳輸 Cookie (開發設 False) |

---

## 🔧 擴展方向

1. **用戶管理**
   - 用戶檔案頁面、頭像上傳
   - 管理員後台、審核系統

2. **回報管理**
   - 標籤/分類、搜索功能
   - 評論、多級討論

3. **通知系統**
   - 郵件通知、WebSocket 實時更新
   - 推播通知

4. **分析統計**
   - 報告熱力圖、趨勢分析
   - 用戶行為追蹤

5. **部署優化**
   - PostgreSQL 取代 SQLite
   - Redis 緩存層
   - CDN 靜態資源加速

---

## 📌 總結

**DormWatch** 是一個麻雀雖小、五臟俱全的全棧 Web 示範專案，涵蓋：
- ✅ 現代 Web 框架 (Flask)
- ✅ 資料庫設計與 ORM
- ✅ 身分驗證與授權
- ✅ 安全性最佳實踐
- ✅ 前後端分離架構
- ✅ Docker 容器化
- ✅ RESTful API 設計

適合作為學習全棧開發、Web 安全、工程實踐的參考項目。

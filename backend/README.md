# DormWatch（Dorm 專案）

DormWatch 是一個以 **Web 為基礎的宿舍匿名回報與管理系統示範專案**，  
後端採用 **Python Flask**，前端使用 **HTML / CSS / JavaScript**，  
並透過 **Docker / docker-compose** 進行容器化部署。

本專案重點放在：
- 使用者身分驗證與權限控管
- 基本 Web 資安設計
- 前後端責任分離
- 良好專案結構與工程實務

---

## 一、系統架構說明

- **後端**
  - Flask
  - Flask-Login（身分驗證）
  - Flask-SQLAlchemy（ORM）
  - SQLite（示範用）
- **前端**
  - 原生 HTML / CSS / JavaScript
  - 與後端透過 RESTful API 溝通
- **部署**
  - Docker
  - docker-compose

---

## 二、後端安全設計（Backend Security）

### 1. 身分驗證與授權（Authentication & Authorization）
- 使用 **Flask-Login** 管理登入狀態
- 系統可辨識「未登入使用者」與「已登入使用者」
- 部分功能（如：點讚回報）僅限登入後使用
- 透過 `@login_required` 限制 API 存取權限

**目的：**
避免未授權使用者執行需具備身分的操作，示範基本存取控制（Access Control）。

---

### 2. 密碼雜湊儲存（Password Hashing）
- 使用 `Werkzeug` 提供的：
  - `generate_password_hash`
  - `check_password_hash`
- 資料庫中不儲存明文密碼

**目的：**
即使資料庫外洩，也能降低使用者帳密被直接濫用的風險。

---

### 3. 環境變數管理敏感資訊
- 使用 `.env` / docker-compose 的 `environment` 設定：
  - `SECRET_KEY`
  - `DATABASE_URI`
- 避免在程式碼中硬編碼敏感資訊

**目的：**
防止金鑰、密碼被直接暴露在原始碼中，符合實務安全做法。

---

### 4. ORM 操作資料庫（防止 SQL Injection）
- 使用 **SQLAlchemy ORM**
- 不直接拼接 SQL 字串
- 所有資料庫操作皆透過 Model 層進行

**目的：**
降低 SQL Injection 攻擊風險。

---

### 5. 請求驗證與錯誤處理
- 檢查使用者輸入：
  - 是否為空
  - 長度是否合理
- 統一回傳錯誤格式（JSON）
- 不回傳系統內部錯誤細節

**目的：**
避免錯誤訊息洩漏系統實作資訊。

---

### 6. 簡易 Rate Limiting（防暴力請求）
- 針對 IP 設計簡易請求次數限制
- 避免短時間內大量送出請求（如洗回報、狂點讚）

**目的：**
降低濫用 API 或簡易 DoS 行為的風險。

---

### 7. Session Cookie 安全設定
- `SESSION_COOKIE_HTTPONLY = True`
- `SESSION_COOKIE_SAMESITE = 'Lax'`
- 可於 HTTPS 環境啟用 `SESSION_COOKIE_SECURE`

**目的：**
降低 XSS 竊取 Session 與 CSRF 攻擊風險。

---

## 三、前端安全設計（Frontend Security）

### 1. XSS 防護（Cross-Site Scripting）
- 前端使用 `textContent` 插入文字
- 不使用 `innerHTML`
- 後端回傳前使用 `html.escape()`

**目的：**
避免惡意腳本被儲存或執行（Stored / Reflected XSS）。

---

### 2. 前後端責任分離
- 前端僅負責顯示與操作介面
- 所有權限判斷由後端控制
- 前端不可單獨決定使用者是否有權操作 API

**目的：**
避免只靠前端限制造成權限被繞過。

---

### 3. API 存取限制設計
- 未登入使用者：
  - 可瀏覽回報
  - 可匿名新增回報
- 已登入使用者：
  - 可對回報點讚
- 未授權 API 會被後端拒絕

**目的：**
示範不同使用者身分的資源存取差異。

---

## 四、可再優化與擴充方向（Future Improvements）

### 1. 多因子認證（MFA / OTP）
- 登入時加入一次性驗證碼
- 提升帳號安全性

---

### 2. 角色權限擴充（RBAC）
- 新增管理者角色（Admin）
- 管理者可：
  - 處理回報狀態
  - 刪除不當內容

---

### 3. CSRF 防護
- 導入 CSRF Token 機制
- 強化表單與狀態變更請求安全性

---

### 4. 安全性自動化檢測
- SAST：Bandit
- DAST：OWASP ZAP
- 整合至 CI/CD Pipeline

---

### 5. 正式反向代理與 HTTPS
- 使用 Nginx 作為反向代理
- 啟用 HTTPS（Let’s Encrypt）

---

## 五、專案總結

DormWatch 專案展示了：
- 基本 Web 身分驗證與權限控管
- 常見 Web 資安風險的防護方式
- 前後端分離的良好設計
- Docker 化部署流程

適合作為：
- Web 安全課程示範
- 後端安全設計練習
- 專題或課堂報告展示專案

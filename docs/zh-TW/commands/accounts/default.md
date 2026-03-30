# accounts default

## 功能定位

查詢目前在 Shioaji CLI 運行環境中被優先預設啟用的「證券帳號」與「期貨帳號」。這讓你確認後續所有的委託下單和帳務查詢，如果未刻意指定帳號時，系統會套用哪一個。

## 適用情境

- 程式或手動操作初期，確認系統將證券與期貨的預設帳號指派給誰。
- 當你擁有多個同類型帳號時，需要知道未加 `--account-id` 會觸發哪一個。

## 命令語法

```powershell
python scripts/shioaji_cli.py accounts default
```

## 參數詳解

| 參數 | 必填 | 預設值 | 可選值 | 說明 |
|---|---|---|---|---|
| 無 | | | | 本命令不需額外參數 |

## 核心回傳資料結構

回傳主要包含兩個屬性，分別指向當前設定的預設物件：

- `stock_account`: 當前的預設證券帳號資料。
- `futopt_account`: 當前的預設期貨與選擇權帳號資料。

## 實戰範例

```powershell
python scripts/shioaji_cli.py accounts default
```

## 注意事項與雷區

- 剛登入後，系統通常預設會拿回傳清單裡第一個對應類型的帳戶作為 default。
- 若要修改預設帳號，請使用 `accounts set-default` 命令。

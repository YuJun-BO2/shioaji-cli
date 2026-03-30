# accounts set-default

## 功能定位

用於修改系統當前的「預設操作帳號」。讓你能在多帳戶環境中，靈活切換哪個帳號是後續指令預設執行的對象，不需在每個命令中反覆輸入 ID。

## 適用情境

- 使用者同時擁有兩個以上同質帳號（例如兩個期貨帳號），且這段時間內的操作皆針對特定的非預設帳號時。
- 自動化程式一開始初始化階段，將目標設為特定帳號。

## 命令語法

```powershell
python scripts/shioaji_cli.py accounts set-default --account-id <目標ID>
```

## 參數詳解

| 參數 | 必填 | 預設值 | 可選值 | 說明 |
|---|---|---|---|---|
| `--account-id` | 是 | 無 | ID 字串 | 若設定的帳號包含於登入帳號列表，將會被設為新預設。 |

## 核心回傳資料結構

回傳你修改完成後的全域帳號綁定狀態，幫助你確認切換成功：

- 包含更新後的 `stock_account` 與 `futopt_account` 狀態展示。

## 實戰範例

```powershell
python scripts/shioaji_cli.py accounts set-default --account-id <YOUR_ACCOUNT_ID>
```

## 注意事項與雷區

- 修改只影響本次連線實例 (CLI 當次執行中的邏輯)，若執行完離開 CLI，狀態不會跨進程自動記憶（端看外層腳本如何設計）。因此若 CLI 為單次生命週期呼叫，應直接在目標命令上帶入 `--account-id`。

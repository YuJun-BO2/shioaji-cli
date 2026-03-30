# contracts status

## 功能定位

這是一個系統檢查命令：**查詢本機商品檔狀態 (Contracts Status)**。
在你能使用 `contracts find` 或者進行下單前，本機必須已具備最新的商品檔。此命令用來檢查昨日收盤到今日開盤期間，交易所的合約資料（例如新上市股票、當日漲跌停價等）是否已經成功被下載至實體記憶體中。

## 適用情境

- 你的系統每天自動啟動，此命令可用來當作 `while loop` 的檢查哨，確定商品檔下載到 `Fetched` 狀態後才開始接下來的自動下單邏輯。
- 當遇到「找不到代碼」錯誤時，作為第一線除錯，確認目前本機到底有沒有正確載入 `stock`, `futures`, `options` 的清單。

## 命令語法

```powershell
python scripts/shioaji_cli.py contracts status
```

## 參數詳解

*(此命令不需亦不接受任何參數)*

---

## 核心回傳資料結構

執行完畢後會回傳一個簡易的狀態字典：

| 欄位名稱  | 型別 | 說明與實務應用 |
|:--------|:----|:-----------|
| `status`| `str` (Enum)| 目前的下載狀態。這最關鍵！<br/>1. **`Unfetch`**: 完全沒下載（連線可能有問題，或被 `--contracts-auto-download false` 阻擋）。<br/>2. **`Fetching`**: 正在下載中... (請用迴圈等它)。<br/>3. **`Fetched`**: **已經下載完畢並可以使用！** |
| `summary`| `str` | 呈現一個純文字的摘要，列出目前記憶體中載入了多少市場別，例如 `Stocks: 1750, Futures: 380, Options: 10200` 等。 |

## 實戰範例

### 1. 寫成腳本的啟動斷言 (Assertion)
你可以在啟動自動交易前先做一次確認：
```powershell
# 呼叫並查看狀態
python scripts/shioaji_cli.py contracts status

# 如果回傳的 status 不是 "Fetched"，就強制觸發 fetch
python scripts/shioaji_cli.py contracts fetch
```

## 注意事項與雷區

1. **依賴自動下載**: 預設情況下，只要 `shioaji_cli.py` 一完成登入，API 背景就會自動開始拉取（此時狀態會瞬間變成 `Fetching`），通常只需要 1~3 秒鐘就會自動變成 `Fetched`。
2. **斷線不會重置**: 如果一開始就 `Fetched` 成功了，盤中即使短暫斷線重連，你的 `contracts status` 依然會是 `Fetched`，你可以繼續拿著舊快取下單。除非你想更新新的除權息參考價，才需要手動去 call `contracts fetch`。

# contracts find

## 功能定位

這是一個靜態商品知識庫命令：**查詢合約資訊 (Find Contract)**。
Shioaji 需要依賴一個精確的「合約物件 (Contract)」才能進行下單（`orders place`）或訂閱行情（`quote subscribe`）。當你只有商品代號 (例如 "2330" 或 "TXFR1")，你可以透過此命令搜尋並印出這個商品今天的所有靜態參數（如漲跌停價、交割日、跳動單位等）。

## 適用情境

- 程式交易在開盤前，根據策略動態計算並查詢今天該標的的漲停價 (`limit_up`) 或跌停價 (`limit_down`) 以佈置限價單。
- 查詢期貨或選擇權合約的結算交割日 (`delivery_date`)。
- 開發除錯時，確認某個較冷門的代號是屬於哪一個交易所 (例如 OES, OTC, TSE)。

## 命令語法

```powershell
python scripts/shioaji_cli.py contracts find --code <代碼> [--market <市場別>]
```

## 參數詳解

| 參數 | 必填 | 預設值 | 說明 |
|---|---|---|---|
| `--code` | **是** | 無 | 標的代碼。例如台股的 `2330` 或期貨的 `TXFR1`。 |
| `--market` | 否 | `auto` | 市場類別，可選 `auto` (自動偵測) / `futures` (期貨) / `options` (選擇權) / `stock` (股票/零股) / `indexs` (加權指數)。如果代號在多個市場都有重複，請明確指定以防拿錯合約。 |

---

## 核心回傳資料結構

依據你查詢的商品不同，CLI 會回傳對應的合約物件（JSON 格式）。主要的共通與特有欄位如下：

### 共通欄位 (Contract)
| 欄位名稱    | 說明與實務應用 |
|:----------|:-----------------------------------------------------------|
| `code`    | 商品交易代碼，也是你帶入 `--code` 的字串。 |
| `name`    | 商品中文長名稱（例如 "台積電" 或 "台指期10"）。注意此欄位會有編碼差異。 |
| `exchange`| 交易所代碼 (`TSE` 證交所 / `OTC` 櫃買中心 / `TAIFEX` 期交所 等)。下單時常常用作過濾依據。 |
| `update_date` | 這個商品檔更新的日期。每天清晨會更新一次。 |

### 證券特有重點欄位 (StockContract)
| 欄位名稱       | 說明與實務應用 |
|:-------------|:-----------------------------------------------------------|
| `reference`  | **平盤參考價**。用來計算目前漲跌幅的基準點（通常是昨收）。 |
| `limit_up`   | **漲停價**。不論你是手動還程式下單，掛單價超過這個值會直接被退單！ |
| `limit_down` | **跌停價**。掛單價低於這個值會被退單！ |
| `day_trade`  | 此檔股票是否為「可當沖」標的。型別為列舉 (Yes / No / Only)。 |

### 期權特有重點欄位 (FutureContract / OptionContract)
| 欄位名稱            | 說明與實務應用 |
|:------------------|:-----------------------------------------------------------|
| `delivery_month`  | 交割月份。例如 `202403`。 |
| `delivery_date`   | **最後結算日**。例如 `2024/03/20`。程式交易如需在結算日提早平倉換月，必須依靠此欄位的值來判斷。 |
| `underlying_kind` | 標的物種類，例如台指期對應 `I` (Index)。 |
| `strike_price`    | *(僅選擇權)* 該合約的履約價。 |
| `option_right`    | *(僅選擇權)* 買權或賣權 (`Call` / `Put`)。 |

---

## 實戰與進階範例

### 1. 查詢台股漲跌停價
```powershell
python scripts/shioaji_cli.py contracts find --code 2330 --market stock
```

### 2. 查詢台指期近月合約的結算日期
台指連續近月合約代碼固定為 `TXFR1`：
```powershell
python scripts/shioaji_cli.py contracts find --code TXFR1 --market futures
```

### 3. 查詢加權指數參考配置
大盤加權指數屬於 `indexs` 市場，注意：指數商品**不能用來下單**，通常只拿來給 `--code` 查詢 `quote subscribe` 接收大盤報價。加權指數代號通常為 `TSE01` 或是 `001` (依底層對應而定)。
```powershell
python scripts/shioaji_cli.py contracts find --code "TSE01" --market indexs
```

## 注意事項與雷區

1. **找不到商品 (Not Found)**: 如果 CLI 回報找不到這個商品且你確定代號正確，絕大多數是因為「**你的本機商品檔快取已過期**」。請立刻執行 `contracts fetch` 強制下載最新商品檔至本機後再試一次。
2. **夜盤切換問題**: 許多期權合約在日盤與夜盤使用的物件是一樣的，不過仍須注意某些期交所的夜盤專屬代號。如果是以統一單一 `TXFR1` 操作，請參閱行情日夜盤切割說明。

```powershell
python scripts/shioaji_cli.py contracts find --code TXFR1 --market futures
```

## 延伸閱讀

- [全域參數說明](../../global-options.md)

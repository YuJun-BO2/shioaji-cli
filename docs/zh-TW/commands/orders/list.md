# orders list

## 功能定位

這是一個委託查詢命令：**列出本日所有委託單與成交狀態 (List Trades)**。
有別於 `accounts positions` 看的是「最終留倉庫存」，`orders list` 看的是「你今天發出了多少委託單，這些單現在是掛在小本冊裡排隊、還是被拒絕、或是已經成交」。

## 適用情境

- 查詢一筆或多筆委託單目前的進度與詳細狀態 (`status.status`)。
- 在準備進行 `cancel` (刪單) 或 `update` (改單) 之前，撈取每一筆委託的本地識別碼 (`id`)。
- 盤後核對今天每一筆委託單的 `deals` (明細成交紀錄)，看看均價與滑價。

## 命令語法

```powershell
python scripts/shioaji_cli.py orders list [--refresh true/false] [--order-id <ID>]
```

## 參數詳解

| 參數 | 必填 | 預設值 | 說明 |
|---|---|---|---|
| `--account-kind` | 否 | `futures` | 篩選要看的帳戶類別。|
| `--account-id`   | 否 | 無 | 指定 7 碼帳戶編號。 |
| `--refresh`      | 否 | `true` | 是否在列出清單前，先自動發起一次 `update_status()` 向主機對時？對網路可能有額外負擔，但可確保資料精確。預設開啟。 |
| `--order-id`     | 否 | 無 | 當你只想針對「某張特定委託單」進行查詢時，帶入這個本地 ID，回傳陣列將只包含該筆單。 |

---

## 核心回傳資料結構 (`Trade` 物件)

回傳結果為 JSON 陣列。清單中每一個元素都是一個完整的 `Trade` 生命週期物件，它由三大塊屬性構成：

| 大區塊 (`Trade.`) | 內部關鍵欄位 | 說明與拆解 |
|:---|:---|:---|
| `contract` | `code`, `target_name` | 這是這筆單子買賣的**標的合約**（對應了一張獨立的 `Contract` 物件）。 |
| `order` | `action`, `price`, `quantity`, `id`, `seqno` | 這是你當初發送的**原始委託條件**。<br/>- `id`: 本地產生的雜湊或流水編號（改刪單必備）。<br/>- `seqno`: 券商主機給的委託書號 (例如 A0B1C)。 |
| **`status`** | **`status`**, `cancel_quantity`, `deal_quantity`, `deals` | **目前狀態**。這是最常被查看的地方：<br/>- `status.status`: 狀態列舉 (`PendingSubmit`-處理中 / `Submitted`-已送出 / `Filled`-完全成交 / `PartFilled`-部分成交 / `Cancelled`-已刪單 / `Failed`-失敗或退單)。<br/>- `deals`: 陣列，裡面詳細記錄這張單**拆了多少筆才成交完**，每一筆的價位與時間。 |

## 實戰與進階範例

### 1. 查詢所有的委託單
```powershell
python scripts/shioaji_cli.py orders list --account-kind stock
```

### 2. 為了確保極致效能，不刷新主機直接查本地快取
如果你的腳本非常頻繁地監控狀態，你不希望每次 `list` 都觸發 API 連線回補，你可以手動關掉 refresh，只撈本地已經收到的 callback 狀態。
```powershell
python scripts/shioaji_cli.py orders list --refresh false
```

### 3. 專注追蹤特定一單的成交進度
當你在 `orders place` 取到了回傳的交易 `id` 之後，你可以定期用 `--order-id` 單獨追看這張單，直到其狀態變為 `Filled`。
```powershell
python scripts/shioaji_cli.py orders list --order-id 45d3e090
```

## 注意事項與雷區

1. **僅限當日**: 這個命令 (對應原生的 `api.list_trades()`) **只有記錄「今天」發生過的委託**。也就是說如果你想挖出昨天或上個月的歷史交易明細，你不能用這個指令，必須使用帳務系統的 `accounts settlements` 或者是其他的交割報表指令。
2. **連動改單行為**: 如果這筆委託經過了 `orders update` 的修改數量（例如 10 改 5），在 `status` 裡面的 `cancel_quantity` 可能會出現 `5` 的紀錄，這反映了「少掉的那五張」在主機上是被視為刪除的。
python scripts/shioaji_cli.py orders list
```

## 延伸閱讀

- [下單與回報參考](../../../references/order_manager.md)
- [全域參數說明](../../global-options.md)

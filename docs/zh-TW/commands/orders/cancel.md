# orders cancel

## 功能定位

這是一個交易控制命令：**刪單 (Cancel Order)**。
當你已經送出一筆委託單 (可能是掛價排隊中，或是預約單)，但策略改變或想重新以不同價格下單時，使用此命令將其從交易所的等待隊列中撤銷。

## 適用情境

- 委託單送出後，遲遲未成交，想取消重下。
- 取消盤後定價交易或預約單。
- 在程式交易風控機制觸發時，快速撤銷所有未成交的活動掛單 (Active Orders)。

## 命令語法

```powershell
python scripts/shioaji_cli.py orders cancel --order-id <委託單編號>
```

## 參數詳解

| 參數 | 必填 | 說明 |
|---|---|---|
| `--order-id` | **是** | 目標委託的 `id`（本地 ID）或是券商端給予的 `seqno` (委託書號)。建議使用 CLI 先查詢過目前掛單，取得準確的 ID 後再執行。 |

---

## 執行邏輯與狀態變更

執行這個命令時，CLI 會在底層進行以下步驟：
1. **本地快取搜尋**: CLI 會先調用 `api.list_trades()`，從本地的委託紀錄中，試圖找出吻合你所提供的 `--order-id` 的那筆 `Trade` 物件。
2. **送出刪除要求**: 找到後，將該物件交由 `api.cancel_order(trade)` 送出。
3. **異步回報更新**: **請注意！命令本身會立刻回傳已經請求刪單的訊息。** 但真正決定是否刪單成功的是券商主機。主機可能因為「已經全部成交」、「已經完全取消過了」等理由拒絕刪單。這時需追蹤 `status` 的變化。

### 刪單的生命週期狀態 (Status 變化)
一筆原本掛單排隊中的委託，被呼叫 cancel 之後，其狀態通常會經歷：
1. 原本狀態：`PendingSubmit` 或 `Submitted` (已送出正在排隊)。
2. 本命令執行瞬間：轉置為 `Cancelling` (取消請求傳送中)。
3. 券商確認後：正式轉為 **`Cancelled`**。這時才算真正刪單成功。

---

## 實戰與進階範例

### 1. 查詢後進行刪單

通常**純刪單不會盲狙**，而是有一個前置動作：
```powershell
# 步驟 1: 先更新並列出所有委託單
python scripts/shioaji_cli.py orders update-status
python scripts/shioaji_cli.py orders list

# 步驟 2: 在剛才的清單中找到你想殺掉的那張單，假設是 id 45d3e090
python scripts/shioaji_cli.py orders cancel --order-id 45d3e090
```

## 注意事項與雷區

1. **不可撤銷已經成交的單**: 如果該筆訂單 `status` 已經是 `Filled` (完全成交) 或是 `Failed` (一開始就被交易所拒絕)，調用 cancel 命令將會引發錯誤或遭主機無效駁回。
2. **多執行緒或非同步同步問題**: 如果在刪單前，本地的 Trades 快取狀態沒有與主機同步 (例如你剛重開程式，或是經歷斷線)，CLI 會找不到這個 `--order-id`。建議在改刪單前，先執行 `orders update-status` 來向券商主機請求一次狀態回補，確保有拿到這筆訂單的實體。
3. **部分成交的退單**: 如果你下單 10 張，已經成交 3 張，送出強制 Cancel 後，這筆訂單的 `status` 會變成 **`PartFilled`** (部分成交並終結，剩下的 7 張被取消)，而不是單純的 `Cancelled`。這是一般人在對帳時容易誤判的地方。

## 延伸閱讀

- [下單與回報參考](../../../references/order_manager.md)
- [全域參數說明](../../global-options.md)

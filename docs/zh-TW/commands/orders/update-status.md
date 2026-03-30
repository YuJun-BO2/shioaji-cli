# orders update-status

## 功能定位

這是一個強制狀態同步命令：**更新委託狀態 (Update Status)**。
在某些情況下（例如網路短暫斷線、非阻塞下單後、或者多個程式同時操作同一個帳號），你本地的 CLI 或腳本所記錄的委託單狀態，可能與券商主機的真實狀態脫節。此命令會透過 API 向券商伺服器請求一次完整的狀態同步。

## 適用情境

- 執行 `orders list` 前，為了確保你看到的委託不是舊的連線快取。
- 執行 `orders cancel` 或 `orders update` 前，為了確保本地快取擁有每一筆單最新的 `seqno` 與 `status`。
- 開發自動化程式時，作為斷線重連機制的第一步復原動作。

## 命令語法

```powershell
python scripts/shioaji_cli.py orders update-status
```

## 參數詳解

| 參數 | 必填 | 預設值 | 說明 |
|---|---|---|---|
| `--account-kind` | 否 | `futures` | 鎖定要更新狀態的帳號類別。這與你下的單是股票還是期貨有關，可選 `stock` / `futures` / `any`。 |
| `--account-id`   | 否 | 無 | 指定 7 碼帳號 ID。未填使用預設帳號。 |

---

## 執行邏輯與狀態變更

在 CLI 底層對應了原生的 `api.update_status(account)`，它執行的過程如下：
1. **主動請求**: 通知 Shioaji API 主動連線至主機，比對今天的所有的委託紀錄與成交明細。
2. **覆寫快取**: Shioaji API 會覆寫其內部的 `api.list_trades()` 記憶體陣列。
3. **成功回傳**: 當你看到 `{"status": "updated"}` 時，代表同步已完成。由於此命令只做「同步」動作，並**不會直接把所有委託單印出來**，你必須緊接著執行 `orders list`。

## 實戰範例

### 1. 同步與查詢二連擊
這是實務上排解「單子明明成交了，但我怎麼看還是 Pending」的標準應對流程：
```powershell
# 強制抓最新的期貨狀態回來
python scripts/shioaji_cli.py orders update-status --account-kind futures

# 接著將更新後的最新單子列印出來
python scripts/shioaji_cli.py orders list
```

## 注意事項與雷區

1. **流量管制**: 請不要在 `while True` 迴圈中無延遲地瘋狂呼叫此命令，這等同於對券商伺服器不斷發起狀態查詢。頻繁請求可能遭風控系統鎖定 IP。
2. **通常依賴自動回報**: 如果你的網路非常穩定，且有訂閱 `subscribe_trade` 或正在監聽 callback，Shioaji 背景通常會自動幫你更新狀態，不需要一直手動去 Call `update-status`。此命令主要用於非預期的狀態脫節急救。

1. 同步伺服器狀態。
2. 查出目標委託單。
3. 執行下單、改單或刪單。

## 進階範例

```powershell
python scripts/shioaji_cli.py orders update-status
```

## 延伸閱讀

- [全域參數說明](../../global-options.md)

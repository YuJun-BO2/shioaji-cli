# orders subscribe-trade

## 功能定位

這是一個委託的長連線監聽命令：**訂閱帳戶成交與狀態回報 (Subscribe Trade)**。
當你使用 `orders place --timeout 0` (非阻塞模式) 下開單後，因為不想卡住程式，你無法馬上取得成交狀態。這時可以開啟一個獨立的 Process 執行 `subscribe-trade`，它會跟主機建立推送通道。當此帳戶產生任何的新刪改定，或是任何一筆大單敲進成交時，這個命令會「即時在背景」把發生的 `Trade` 事件當作 JSON 結構吐出到標準輸出 (stdout)。

## 適用情境

- 作為非阻塞/極速下單機制的搭配：主腳本專門負責發單，輔助腳本專門監聽回報並寫入資料庫/Line推播。
- 券商主動通知斷頭或者代為平倉時的神經中樞。
- 防止輪詢 (Polling)。與其寫一個 `while True: orders list` 瘋狂轟炸伺服器拿資料，不如掛著這條連線被動等資料倒給自己。

## 命令語法

```powershell
python scripts/shioaji_cli.py orders subscribe-trade [--account-kind <類別>]
```

## 參數詳解

| 參數 | 必填 | 預設值 | 說明 |
|---|---|---|---|
| `--account-kind` | 否 | `any` | 要訂閱回報的帳戶類別可以指定為 `stock` 或是 `futures`，或者 `any` 全收。如果不指定，將使用第一個帳號。 |
| `--account-id`   | 否 | 無 | 指定要綁定回報的 7 碼實體帳號。 |

---

## 核心回傳資料結構與運作機制

一旦成功啟動，這個命令**不會在取得一筆回報後結束，而是會持續執行 (一直掛著)**。
有賴於 CLI 的封裝，每當你送出的單有狀態改變：
1. 主機會推播 `Trade` 或 `OrderState` 給本機。
2. 你的 stdout 會跳出一行完整序列化為 JSON 字典的字串，結構就如同 `orders list` 單獨抓出來的一筆資料。包含 `contract`, `order`, 以及最新更新進去的 `status` (通常會看到 `status: Filled` 或是新跳進來的 `deals` 成交明細)。

## 實戰與進階範例

### 1. 監聽期貨帳戶的所有委託變動
適合使用 Python 原生的 `subprocess` 或 Node.js 的 `child_process.spawn()` 在背景啟動它，並串接 stdout 的 `data` 事件：
```powershell
python scripts/shioaji_cli.py orders subscribe-trade --account-kind futures
```

### 2. 結合極速下單使用
終端機 A (維持長開):
```powershell
python scripts/shioaji_cli.py orders subscribe-trade
```

終端機 B (只管極速送資料，不到 10 毫秒就結束):
```powershell
python scripts/shioaji_cli.py orders place --code TXFR1 --market futures --action Buy --price-type MKT --order-type IOC --timeout 0
```
馬上你就會在終端機 A 看到它印出這筆市價單的成交回報 `deals` 和 `Filled` 的狀態！

## 注意事項與雷區

1. **不用反覆訂閱**: 單一個帳號只要建立一次通道就可以了。如果你多次呼叫 `subscribe-trade` 綁在同一個帳號背後，不會讓他變快，反而可能浪費主機資源或引發重複輸出的 Bug。
2. **斷線重連機制**: Shioaji 在底層有寫基本的斷線心跳與重連邏輯，但如果在非常極端的不穩定網路中，長連線仍有可能失效。如果遲遲沒有收到推送，可以適時利用 `orders update-status` 做輔助的回補。
3. **不能查歷史**: 這個指令的定位是「從現在開始聽未來的廣播」，它**不會**在訂閱的瞬間把早上發生過的明細補吐給你。要看舊的狀態，請去查 `orders list`。

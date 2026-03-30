# api call

## 功能定位

泛用 API 呼叫入口，補齊未封裝子命令。 你可以用這個命令處理 api 領域中的 call 任務。

## 適用情境

- 快速測試新 API
- 臨時查詢尚未封裝的方法的測試與喚起

## 命令語法

```powershell
python scripts/shioaji_cli.py api call
```

## 參數詳解

| 參數 | 必填 | 預設值 | 可選值 | 說明 |
|---|---|---|---|---|
| --method | 是 | 無 | 不限 | Example: usage, account_balance, quote.subscribe |
| --args-json | 否 | [] | 不限 | JSON array for positional args. |
| --kwargs-json | 否 | {} | 不限 | JSON object for keyword args. |

## 核心回傳資料結構

- 回傳目標 API 方法的執行結果之 JSON 結構。
- 特別支援 `$contract`, `$contracts`, `$account` 等特殊 payload 的自動解析。

## 實戰範例

```powershell
python scripts/shioaji_cli.py api call --method snapshots --args-json "[{\"\$contracts\":[\"2330\",\"2317\"],\"\$market\":\"stock\"}]"

python scripts/shioaji_cli.py api call --method usage --args-json "[]" --kwargs-json "{}"
```

## 注意事項與雷區

- 可呼叫任意方法路徑，如 `usage` 或 `quote.subscribe`。
- args-json 必須是強型別的 JSON 陣列。
- kwargs-json 必須是強型別的 JSON 物件。
- 常見操作順序：先用 `api methods` 找目標方法，再組裝參數。

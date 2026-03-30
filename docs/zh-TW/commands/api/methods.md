# api methods

## 功能定位

泛用 API 呼叫入口，補齊未封裝子命令。你可以用這個命令處理 api 領域中的 methods 任務。

## 適用情境

- 快速測試新 API
- 臨時查詢尚未封裝的方法

## 命令語法

```powershell
python scripts/shioaji_cli.py api methods
```

## 參數詳解

| 參數 | 必填 | 預設值 | 可選值 | 說明 |
|---|---|---|---|---|
| --match | 否 | 無 | 不限 | |

## 核心回傳資料結構

- 回傳可呼叫方法名稱清單。

## 實戰範例

```powershell
python scripts/shioaji_cli.py api methods --match profit
```

## 注意事項與雷區

- 泛用 API 區提供方法探索與任意呼叫能力。
- 建議先 methods 再 call，降低呼叫錯誤。
- 常見操作順序：先用 api methods 找目標方法，再組裝 args-json 與 kwargs-json 透過 api call 驗證結果。
- JSON 參數格式需嚴格正確。
- args-json 必須是 JSON 陣列。
- kwargs-json 必須是 JSON 物件。

# accounts open-position

## 功能定位

查詢期貨或選擇權的「未平倉部位」(Open Position)。此命令用來讓你即時掌握目前手頭上留倉的期權數量與平均成本等關鍵資訊。

## 適用情境

- 盤中隨時監控期權留倉數量，判斷是否需要進行平倉。
- 開發程式自動化追蹤部位曝險時的基礎資料來源。

## 命令語法

```powershell
python scripts/shioaji_cli.py accounts open-position
```

## 參數詳解

| 參數 | 必填 | 預設值 | 可選值 | 說明 |
|---|---|---|---|---|
| `--account-kind` | 否 | `futures` | `stock`, `futures` | 預設為期權；由於未平倉部位多用於期貨，建議保持預設。 |
| `--account-id` | 否 | 無 | ID 字串 | 若有多組帳號可輸入 ID 以指定。 |
| `--product-type` | 否 | `0` | 數字 | `0` (全部), 其他對應實體型別（詳見 API 參考）。 |
| `--query-type` | 否 | `0` | `0`, `1` | `0` 查詢彙總，`1` 查詢明細部位。 |

## 核心回傳資料結構

執行後回傳目前留倉的未平倉合約陣列，常見關鍵欄位包含：

- `Code`: 合約代碼（如 TX00）。
- `ContractAverPrice`: 該留倉合約的平均成本價。
- `FlowProfitLoss`: 浮動損益，隨著目前市價持續變動。
- `Volume`: 目前留倉口數（多單正數、空單可能依顯示呈現）。

## 實戰範例

```powershell
python scripts/shioaji_cli.py accounts open-position --account-kind futures --product-type 0 --query-type 1
```

## 注意事項與雷區

- `query-type` 的設定會直接影響回傳結構是每一筆獨立記錄還是一個合併加總記錄，寫自動化腳本時需特別注意。
- 即時浮動損益受盤中行情跳動影響，需搭配最新的報價資料才更精確。

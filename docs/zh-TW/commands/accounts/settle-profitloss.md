# accounts settle-profitloss

## 功能定位

查詢期貨與選擇權的「已實現損益」(Settled Profit and Loss)。這個命令協助你檢視在給定日期區間內，已經平倉的期權部位所產生的實際盈虧。

## 適用情境

- 盤後盤點績效，結算本日或本月的投資成果。
- 回測或成效稽核時收集歷史損益數據。

## 命令語法

```powershell
python scripts/shioaji_cli.py accounts settle-profitloss --start-date <YYYY-MM-DD> --end-date <YYYY-MM-DD> [選項]
```

## 參數詳解

| 參數 | 必填 | 預設值 | 可選值 | 說明 |
|---|---|---|---|---|
| `--account-kind` | 否 | `futures` | `stock`, `futures` | 查詢已平倉損益通常針對期權設定為 `futures`。 |
| `--start-date` | 是 | 無 | YYYY-MM-DD | 查詢區間的起算日。 |
| `--end-date` | 是 | 無 | YYYY-MM-DD | 查詢區間的結束日。 |
| `--summary` | 否 | `Y` | `Y`, `N` | `Y` 回傳彙總金額，`N` 回傳交易明細。 |

## 核心回傳資料結構

回報特定區間內的損益數字，視為彙總或明細會有所不同：

- 彙總模式 (`summary=Y`) 將提供這段時間內的總體損益概況。
- 明細模式 (`summary=N`) 則提供每筆平倉交易的進出細節、手續費、稅金及實收實付金額。

## 實戰範例

```powershell
python scripts/shioaji_cli.py accounts settle-profitloss --account-kind futures --product-type 0 --summary Y --start-date 2026-03-01 --end-date 2026-03-30
```

## 注意事項與雷區

- 查詢的時間區間有限制，超出資料庫保留的歷史天數可能會出現無法查詢或是查詢失敗的問題。
- 日期格式必須嚴格依照 `YYYY-MM-DD` 或是其 API 支援之格式，避免發生時間解析錯誤。

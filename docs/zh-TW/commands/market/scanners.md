# market scanners

## 功能定位
透過不同條件類型獲取市場個股排行榜（如漲幅、跌幅、成交量、成交金額排行），方便快速掌握大盤熱點與強弱勢個股。

## 適用情境
- 尋找當日強勢股 / 弱勢股進行趨勢跟單或動能交易
- 盤前、盤中快速掃描全市場，過濾成交量或金額極大的個股
- 將特定榜單結果輸出至其他選股程式進行二次過濾

## 命令語法
```powershell
python scripts/shioaji_cli.py market scanners [--scanner-type <排行類型>] [--count <筆數>] [--ascending <布林值>]
```

## 參數詳解
| 參數 | 必填 | 預設值 | 可選值 | 說明 |
|---|---|---|---|---|
| `--scanner-type` | 否 | `ChangePercentRank` | `ChangePercentRank` (漲跌幅), `ChangePriceRank` (漲跌價), `DayRangeRank` (高低區間), `VolumeRank` (成交量), `AmountRank` (成交金額) | 欲查詢的排行榜類型 |
| `--count` | 否 | 20 | 任意正整數 | 回傳的資料筆數，如 20 代表前 20 名 |
| `--ascending` | 否 | `true` | `true`, `false` | 排序方式。`false` 代表數值由大到小（如漲幅最大），`true` 則相反（如跌幅最大） |

## 核心回傳資料結構
回傳的項目為多筆排名資訊的陣列，每筆包含：
- `code`: 個股代號
- `name`: 股票名稱（部分可能支援）
- `close`: 最新收盤或成交價
- `change_price`: 漲跌金額
- `volume`: 總成交量
- `amount`: 總成交金額
- `ts`: 更新時間

## 實戰範例
**查詢單日成交量前 50 大個股（數值由大至小）**：
```powershell
python scripts/shioaji_cli.py market scanners --scanner-type VolumeRank --count 50 --ascending false
```

**查詢漲幅前 10 名強勢股**：
```powershell
python scripts/shioaji_cli.py market scanners --scanner-type ChangePercentRank --count 10 --ascending false
```

## 注意事項與雷區
- **參數邏輯容易混淆**：`ascending=false` (降冪) 才是取數值**最大**的前幾名（例如找出漲跌幅最高＝漲停板）；若設為 `true` 則是取數值最小（跌幅最大）。
- **非盤中即時流**：此命令發動的是快照式的 API 請求，若需要極高頻的即時變動，應使用 WebSocket (Quote Subscribe)，而非高頻輪詢此 Scanner。
- **無類股過濾**：目前的 Scanner 條件為跨大全市場，無法僅針對單一產業或概念股撈取排行。

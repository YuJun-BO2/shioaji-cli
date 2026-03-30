# accounts trading-limits

## 功能定位

查詢該證券帳戶的「交易額度與限制」。這是風險控制與資金管理的關鍵功能，確保委託不超過券商賦予的當沖、資券或現股買賣上限。

## 適用情境

- 程式啟動自動交易前的防呆檢查，確認剩餘額度是否足以發動後續批次委託。
- 開立新帳戶後確認券商放行的總授信額度額度。

## 命令語法

```powershell
python scripts/shioaji_cli.py accounts trading-limits [選項]
```

## 參數詳解

| 參數 | 必填 | 預設值 | 可選值 | 說明 |
|---|---|---|---|---|
| `--account-kind` | 否 | `stock` | `stock`, `futures` | 通常查詢交易額度都是針對證券類別。 |
| `--account-id` | 否 | 無 | ID 字串 | 若有多組帳號可輸入 ID 以指定。 |

## 核心回傳資料結構

回傳額度相關數據，這對於資金水位監控很重要：

- `trading_limit`: 券商所給予的單日現股買賣最高額度。
- `trading_used`: 今日已經使用掉的額度。
- `trading_available`: 剩餘還可下單的額度空間。
- 另包含 `margin_limit` (融資相關額度) 與 `short_limit` (融券相關額度)。

## 實戰範例

```powershell
python scripts/shioaji_cli.py accounts trading-limits --account-kind stock
```

## 注意事項與雷區

- 額度僅是「交易權限上限」，並不等於你的交割帳戶「真實銀行餘額」。下單前仍需透過餘額查詢確認有現金可以扣繳。
- 買進與賣出均可能佔用交易額度（視該帳戶設定與現沖規範而定），發生退單時須檢查此項數據。

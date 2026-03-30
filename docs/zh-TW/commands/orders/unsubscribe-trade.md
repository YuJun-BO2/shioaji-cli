# orders unsubscribe-trade

## 功能定位

取消成交回報訂閱。這可用於停止監聽伺服器推播的交易即時回報。

## 適用情境

- 盤中結束追蹤特定帳號的狀態
- 風控條件達成後終止背景監聽機制

## 命令語法

```powershell
python scripts/shioaji_cli.py orders unsubscribe-trade
```

## 參數詳解

| 參數 | 必填 | 預設值 | 可選值 | 說明 |
|---|---|---|---|---|
| --account-kind | 否 | any | auto / any / stock / futures | 目標帳號的種類 |
| --account-id | 否 | 無 | 不限 | 目標 account id 取消訂閱。 |

## 核心回傳資料結構

- 回傳取消訂閱的結果，通常包含 account 物件的資訊。

## 實戰範例

```powershell
python scripts/shioaji_cli.py orders unsubscribe-trade --account-kind any

python scripts/shioaji_cli.py orders unsubscribe-trade
```

## 注意事項與雷區

- 取消前請確認已經不再需要處理成交回報，以免遺漏重要斷頭或成交提示。
- 取消訂閱操作也是即時影響底層 Shioaji 物件的 `on_trade` 等 callback 觸發與否。

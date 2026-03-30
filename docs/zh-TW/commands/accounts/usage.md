# accounts usage

## 功能定位

查詢當日 API 服務的「流量使用狀態與限制」。能用來檢查使用者的 Shioaji 行情或下單 API 發送是否快觸碰到每日連線流量或是傳輸位元組限制。

## 適用情境

- 發現在盤中遭遇連線不穩定或拋出警告時，用以排查是否遭到節流（Throttling）。
- 部署高頻報價抓取系統時監控剩餘的資源消耗速率。

## 命令語法

```powershell
python scripts/shioaji_cli.py accounts usage
```

## 參數詳解

| 參數 | 必填 | 預設值 | 可選值 | 說明 |
|---|---|---|---|---|
| 無 | | | | 本命令不需額外帶入查詢參數 |

## 核心回傳資料結構

給出目前的連線統計，幫助使用者優化架構：

- `connections`: 目前已建立的連線數量。
- `bytes`: 已經消耗掉的傳輸量（位元組）。
- `limit_bytes`: 券商端設定的總限制額度上限。
- `remaining_bytes`: 剩餘可用之傳輸量。

## 實戰範例

```powershell
python scripts/shioaji_cli.py accounts usage
```

## 注意事項與雷區

- 高頻率或是長時間的無間斷行情訂閱，會逐漸消耗分配的字節數。
- 如果發現流量見底，應檢討系統架構是否訂閱了過多不必要且異動量極大的標的 TICK，而不是全面拉取。

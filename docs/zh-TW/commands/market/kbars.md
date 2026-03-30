# market kbars

## 功能定位

這是一個市場資料查詢命令：**取得歷史 K 線圖 (K-bars)**。
該命令能抓取商品在一分鐘線（標準設定）層級的開、高、低、收、量等資料。適合用在盤前訓練或回測你的交易策略模型，或者開盤時繪製初步圖表。

## 適用情境

- 演算法交易抓取回測資料 (例如取得一整週的台指期 1 分 K)。
- 盤後產生技術指標 (如 MA, MACD, RSI) 計算所需的基礎數列。

## 命令語法

```powershell
python scripts/shioaji_cli.py market kbars --code <代碼> --start <開始日期> --end <結束日期>
```

## 參數詳解

| 參數 | 必填 | 預設值 | 說明 |
|---|---|---|---|
| `--code` | **是** | 無 | 目標商品代碼（如 `2330`, `TXFR1`）。 |
| `--market` | 否 | `auto` | 市場類別。多市場重名時用以精確指定合約。 |
| `--start` | **是** | 無 | 查詢區間的開始日期，格式必須為 `YYYY-MM-DD` (例如 `2024-01-01`)。 |
| `--end` | **是** | 無 | 查詢區間的結束日期，格式必須為 `YYYY-MM-DD` (例如 `2024-01-31`)。 |

---

## 核心回傳資料結構 (`Kbars` 物件)

成功呼叫後，會回傳列狀陣列 (Columnar format) 型態的 JSON 物件。**這與常見的逐筆物件陣列不同，它將同一個屬性的資料全部放在同一個陣列內以壓縮空間**。

| 欄位名稱 | 型別 | 說明與實務應用 |
|:-------|:----|:-----------|
| `ts`   | `list[int]` | K 線的 Unix Timestamp 陣列 (奈秒級)。你可以透過 Python 的 `datetime.fromtimestamp(ts/1e9)` 轉換回人類可讀時間。 |
| `Open` | `list[float]` | 開盤價陣列。 |
| `High` | `list[float]` | 最高價陣列。 |
| `Low`  | `list[float]` | 最低價陣列。 |
| `Close`| `list[float]` | 收盤價陣列。 |
| `Volume`| `list[int]` | 該一分鐘的總成交量。 |
| `Amount`| `list[float]`| 該分鐘的總成交金額。 |

## 實戰與進階範例

### 1. 查詢台股現貨歷史 K 線
抓取台積電 (2330) 2024 年 1 月份的 K 線資料：
```powershell
python scripts/shioaji_cli.py market kbars --code 2330 --market stock --start 2024-01-01 --end 2024-01-31
```

### 2. 查詢台指期近月歷史 K 線
```powershell
python scripts/shioaji_cli.py market kbars --code TXFR1 --market futures --start 2024-01-01 --end 2024-01-15
```

## 注意事項與雷區

1. **僅支援 1 分 K**: 主機端提供的 `Kbars` 資料結構預設基準就是**一分鐘 (1-minute)**，如果你的策略需要 5 分 K、日 K，你的程式必須自己對拿到的 `ts` 時間戳與價格進行聚合/重抽樣(Resampling)。
2. **回傳格式需轉置 (Transpose)**: 如果你要丟進 Pandas DataFrame，由於回傳的是 Dictionary of Arrays，你可以直接用 `pandas.DataFrame(result)` 無縫接軌，這也是原廠這樣設計的原因。
3. **資料長度限制**: 券商的伺服器有回溯限制與單次查詢極限，若查詢時間區間太過龐大（例如一次查 5 年），不僅會超時，還可能被主機強制阻斷或回傳空值，建議實作「按月分批抓取」的自動化腳本。

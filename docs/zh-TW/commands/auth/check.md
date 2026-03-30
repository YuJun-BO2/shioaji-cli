# auth check

## 功能定位

`auth check` 命令的主要任務是進行「登入驗證」與「連線與帳號狀態檢查」。
這是一個非常基礎但至關重要的命令，用以確認使用者在 `.env` 或命令列參數中指定的 `API_KEY` 與 `SECRET_KEY` 等驗證資料是否合法有效，並且確保成功登入後能無誤取得券商系統授權的帳號清單。

## 適用情境

- 第一次完成專案建置與 `.env` 配置後，驗證登入及憑證配置是否能順利連接到 Shioaji 伺服器。
- 開發時切換環境，例行確認目前是否正確在「正式環境」或「模擬模式 (Simulation)」運作。
- 開發自動化指令碼前，用以探勘並確認登入者的所有 `Account` 狀態（例如 `account_type` 支援證券或期貨、`signed` 狀態是否完備）。

## 命令語法

```powershell
python scripts/shioaji_cli.py auth check
```
*(你也可以加上 `--raw` 來觀察直接從核心回傳的 Python dict 結構)*

---

## 執行邏輯與程式碼對應分析

根據 `scripts/shioaji_cli.py` 原始碼，此命令底層由 `cmd_auth_check` 函式驅動：

1. **環境載入與登入（全域）**: Shioaji 在執行所有的 CLI 命令之前，都會先在頂層 `main()` 的 `init_api()` 中吃入環境變數（含 `SIMULATION`）並呼叫 `api.login()`。
2. **獲取帳號狀態**: `cmd_auth_check` 執行時，主架構的連線已經就緒，直接調用原生的 `api.list_accounts()` 取得帳號。
3. **組裝回傳**: 除了帳號陣列，還擴充回傳了檢查結果（`ok=True`）、是否為模擬模式（`simulation`）、以及環境設定檔路徑（`env_file`），讓除錯更直覺。

### 回傳重點與資料結構對照

執行 `auth check` 會回傳被 JSON 序列化的字典。回傳結果的關鍵欄位對照如下：

| JSON 欄位名稱 | 原生型別          | 說明與常見陷阱                                                                                           |
|:------------|:-----------------|:-------------------------------------------------------------------------------------------------------|
| `ok`        | `bool`           | CLI 內部封裝的回傳值。當你看到這個值為 `True`，即代表底層的 `api.login(...)` 呼叫沒有遭遇憑證超時等中斷錯誤。           |
| `simulation`| `bool`           | 直接對映 `sj.Shioaji(simulation=...)` 的設定。注意：模擬環境登入與真實環境的 API 金鑰與後台是分離的。                 |
| `env_file`  | `str`            | 開發者在啟動指令中 `--env-file` 指定的路徑，用以除錯多開環境配置檔問題。                                         |
| `accounts`  | `list[Account]`  | 對應 Shioaji 原生 Account 物件陣列。若是第一次登入未預設帳號，下單等操作預設會拿這清單的第一個 (`accounts[0]`) 帳號。   |

**`accounts` 內個別物件的重要屬性 (API 客戶端參考):**
- **`account_type`**: 指示帳號類型。`'S'`(證券), `'F'`(期貨/選擇權), `'H'`(複委託海外證券)。下單時常常需要根據這個欄位篩選適用的帳號！
- **`person_id`**: 使用者身分證字號。
- **`broker_id`**: 券商代碼 (如 `9A95`)。
- **`account_id`**: 該帳號的實體帳號編號 (7碼數字)，如 `0000000`。
- **`signed`**: **極度重要**！代表該帳號是否已經在本機完成憑證 CA 簽署。若為 `False` 將無法對該帳號送出委託下單，會被主機拒絕。`auto auth check` 中如果搭配了 `--activate-ca auto` (全域選項)，此欄位才能確保被正確啟動為 `True`。

---

## 官方文檔延伸重點與排障

根據官方 Reference 摘要，登入相關常見的雷區與除錯重點：

1. **Sign data is timeout (簽署逾時)**:
   由於 API 登入底層有非對稱加密驗證，非常要求本機終端機系統的時間必須準確。若與 NTP 標準時間落差大於幾秒鐘，可能引發 `Timeout` 登入失敗。**解法：**強制於 Windows/Linux 校時，或於腳本中調高 `api.login(..., receive_window=60000)` 等待時間。
2. **凭證路徑錯誤**:
   如果要交易正式環境，你的本機 CA 憑證（通常為 `.pfx` 或 `.p12`）與密碼必須正確配置（全域 `--ca-cert` 與 `--ca-passwd` 或對應環境變數）。登入失敗多半是此環節漏掉。

## 常見操作順序與自動化應用

`auth check` 通常作為建置 Workflow 的第一塊基石：

1. [第一次準備] 確認 `.env` 內 `SHIOAJI_API_KEY`, `SHIOAJI_SECRET_KEY` 等變數已填妥。
2. [CLI 檢測] 執行 `python scripts/shioaji_cli.py auth check`。
3. [結果驗證] 確保能印出 `ok: True` 且 `accounts` 陣列內至少有一個對應的實體帳號，且 `signed` 值為 `true`。
4. [進入開發] 若皆成功，即可安心執行其他 `contracts` 或 `market / orders` 命令。
2. 執行 auth check 驗證連線成功。
3. 再進行 contracts/accounts/orders 等操作。

## 進階範例

```powershell
python scripts/shioaji_cli.py auth check --raw
```

## 延伸閱讀

- [登入與帳號背景](../../../references/account_info.md)
- [全域參數說明](../../global-options.md)

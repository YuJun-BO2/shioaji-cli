# 全域參數

本頁整理 scripts/shioaji_cli.py 可用的全域參數，所有子命令都可共用。

## 基本用法

```powershell
python scripts\\shioaji_cli.py [全域參數] <command> <subcommand> [子命令參數]
```

## 參數清單

| 參數 | 必填 | 預設值 | 可選值 | 說明 |
|---|---|---|---|---|
| --env-file | 否 | .env | 不限 | Path to .env file. |
| --simulation | 否 | 無 | true / false |  |
| --fetch-contract | 否 | true | true / false |  |
| --contracts-timeout | 否 | 10000 | 不限 |  |
| --subscribe-trade | 否 | true | true / false |  |
| --activate-ca | 否 | auto | auto / true / false | auto: activate when CA_CERT_PATH/CA_PASSWORD/PERSON_ID exist. |
| --raw | 否 | 無 | 不限 | Print raw Python object instead of JSON. |

## 範例

```powershell
python scripts\\shioaji_cli.py --env-file .env --activate-ca auto auth check
```


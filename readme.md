# Shioaji Unified CLI

> **【法律與免責聲明 Disclaimer】**
> 本專案 (`shioaji-cli`) 依據 **Apache License 2.0** 開源釋出。
> **使用本軟體即代表您完全且無條件同意附帶的 [EULA (使用者授權與免責協議)](EULA.md)。** 作者/開發者對於任何人因使用本程式進行真實交易、量化操作或 API 串接所導致之任何「直接或間接財務損失」、「下單錯誤」或「資料延遲」，**一概不負任何法律及賠償責任**。程式僅供學術與技術交流，所有金融投資盈虧風險皆由使用者自行承擔。
>
> **【非官方聲明】** 本軟體為第三方獨立開發之非官方開源工具，本專案及開發者與「永豐金控」、「永豐金證券」及其相關企業皆無任何官方關聯、投資、合作或背書關係。所有關於 Shioaji API 之商標及服務名稱其智慧財產權均屬原權利人所有。

Single entry CLI for Shioaji operations across:

- auth/session
- contracts
- accounts, margin, positions, pnl
- market data and scanners
- order placement and trade management
- realtime quote subscription
- generic API passthrough for methods not covered by fixed subcommands

## 0) One-click environment setup

Create venv and install all required dependencies in one command:

```powershell
./setup_venv.bat
```

Or run PowerShell directly:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup_venv.ps1
```

Recreate venv from scratch:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup_venv.ps1 -Recreate
```

After setup:

```powershell
.\.venv\Scripts\Activate.ps1
python scripts\shioaji_cli.py --help
```

Docs entry:

- `docs/index.md`
- `docs/zh-TW/index.md`

## 1) Auth and .env

All credentials and cert settings are loaded from one `.env` file.

Required / supported fields:

```env
API_KEY=
SECRET_KEY=
CA_CERT_PATH=
CA_PASSWORD=
PERSON_ID=
EXPIRE_DATE=
SIMULATION=true
```


## 2) Main CLI

Main entry:

```bash
python scripts/shioaji_cli.py --help
```

Top-level command groups:

- `auth`
- `contracts`
- `accounts`
- `orders`
- `market`
- `quote`
- `api`

Global options:

```bash
python scripts/shioaji_cli.py \
	--env-file .env \
	--simulation true \
	--fetch-contract true \
	--contracts-timeout 10000 \
	--subscribe-trade true \
	--activate-ca auto \
	auth check
```

## 3) Common examples

Auth check:

```bash
python scripts/shioaji_cli.py auth check
```

Find contract:

```bash
python scripts/shioaji_cli.py contracts find --code TXFR1 --market futures
```

Get positions:

```bash
python scripts/shioaji_cli.py accounts positions --account-kind futures
```

Get realized pnl:

```bash
python scripts/shioaji_cli.py accounts pnl --account-kind stock --start 2026-03-01 --end 2026-03-30
```

Get kbars:

```bash
python scripts/shioaji_cli.py market kbars --code TXFR1 --market futures --start 2026-03-20 --end 2026-03-30
```

Place futures order:

```bash
python scripts/shioaji_cli.py orders place \
	--code TXFR1 \
	--market futures \
	--action Buy \
	--price-type MKT \
	--order-type IOC \
	--quantity 1
```

List trades:

```bash
python scripts/shioaji_cli.py orders list --account-kind futures
```

Cancel order:

```bash
python scripts/shioaji_cli.py orders cancel --order-id YOUR_ORDER_ID
```

Subscribe quote for 60 seconds:

```bash
python scripts/shioaji_cli.py quote subscribe --code TXFR1 --quote-type tick --version v1 --duration 60
```

## 4) Full coverage via generic api call

For methods not yet mapped to a fixed subcommand, use:

```bash
python scripts/shioaji_cli.py api methods
python scripts/shioaji_cli.py api call --method usage
```

Special placeholders in `api call` payload:

- `{"$contract": "TXFR1", "$market": "futures"}` -> auto-resolve to contract object
- `{"$contracts": ["2330", "2317"], "$market": "stock"}` -> auto-resolve to contract list
- `{"$account": "futures"}` or `{"$account": "ACCOUNT_ID"}` -> auto-resolve to account object

Example:

```bash
python scripts/shioaji_cli.py api call \
	--method snapshots \
	--args-json '[{"$contracts":["2330","2317"],"$market":"stock"}]'
```

## 5) Full Command Docs

All commands are documented in paginated docs with one page per command:

- `docs/zh-TW/index.md` (main entry)
- `docs/zh-TW/commands/`

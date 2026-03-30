from __future__ import annotations

import argparse
import json
import time
from typing import Any

import shioaji as sj

from cli_common import (
    AuthConfig,
    compact_date,
    create_api,
    iso_date,
    lookup_contract,
    lookup_contracts,
    pick_account,
    resolve_special_payload,
    safe_logout,
    str_to_bool,
    to_serializable,
)


def emit(data: Any, raw: bool = False) -> None:
    if data is None:
        return

    if raw:
        print(data)
        return

    print(json.dumps(to_serializable(data), ensure_ascii=False, indent=2))


def parse_json_argument(text: str, expected_type: type, label: str) -> Any:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid {label} JSON: {exc}") from exc

    if not isinstance(parsed, expected_type):
        raise RuntimeError(f"{label} must be a {expected_type.__name__} JSON value.")

    return parsed


def enum_value(enum_name: str, member: str, fallback: Any = None) -> Any:
    enum_cls = getattr(sj.constant, enum_name, None)
    if enum_cls is None:
        return fallback if fallback is not None else member

    candidates = [member, member.upper(), member.capitalize(), member.replace("-", "")]
    for candidate in candidates:
        if hasattr(enum_cls, candidate):
            return getattr(enum_cls, candidate)

    return fallback if fallback is not None else member


def quote_type_value(name: str) -> Any:
    normalized = name.strip().lower()
    mapping = {
        "tick": "Tick",
        "bidask": "BidAsk",
        "quote": "Quote",
    }
    return enum_value("QuoteType", mapping.get(normalized, name), fallback=name)


def quote_version_value(name: str) -> Any:
    normalized = name.strip().lower()
    mapping = {
        "v0": "v0",
        "v1": "v1",
        "v2": "v2",
    }
    return enum_value("QuoteVersion", mapping.get(normalized, name), fallback=name)


def scanner_type_value(name: str) -> Any:
    return enum_value("ScannerType", name, fallback=name)


def pick_trade_by_order_id(api: sj.Shioaji, order_id: str) -> Any:
    trades = api.list_trades()
    for trade in trades:
        order = getattr(trade, "order", None)
        if order is None:
            continue

        trade_order_id = str(getattr(order, "id", ""))
        trade_seqno = str(getattr(order, "seqno", ""))
        if order_id in {trade_order_id, trade_seqno}:
            return trade

    raise RuntimeError(f"Order ID not found in current trades: {order_id}")


def infer_account_kind(requested_kind: str, contract: Any) -> str:
    if requested_kind != "auto":
        return requested_kind

    contract_type_text = type(contract).__name__.lower()
    if "stock" in contract_type_text:
        return "stock"
    return "futures"


def infer_market(requested_market: str, contract: Any) -> str:
    if requested_market != "auto":
        return requested_market

    contract_type_text = type(contract).__name__.lower()
    if "stock" in contract_type_text:
        return "stock"
    if "option" in contract_type_text:
        return "options"
    if "index" in contract_type_text:
        return "indexs"
    return "futures"


def resolve_price_type(market: str, member: str) -> Any:
    normalized_market = market.lower()
    if normalized_market in {"futures", "future", "options", "option", "auto"}:
        return enum_value("FuturesPriceType", member, fallback=member)
    return enum_value("StockPriceType", member, fallback=member)


def active_ca_flag(mode: str, cfg: AuthConfig) -> bool:
    normalized = mode.lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    return bool(cfg.ca_cert_path and cfg.ca_password and cfg.person_id)


def ensure_contract(api: sj.Shioaji, code: str, market: str = "auto") -> Any:
    contract = lookup_contract(api, code=code, market=market)
    if contract is None:
        raise RuntimeError(f"Contract not found: {code}")
    return contract


def cmd_auth_check(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    accounts = api.list_accounts()
    return {
        "ok": True,
        "simulation": cfg.simulation,
        "env_file": cfg.env_file,
        "accounts": accounts,
    }


def cmd_contracts_status(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    return {
        "status": getattr(api.Contracts, "status", None),
        "summary": str(api.Contracts),
    }


def cmd_contracts_fetch(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    return api.fetch_contracts(contract_download=str_to_bool(args.contract_download, default=True))


def cmd_contracts_find(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    return ensure_contract(api, code=args.code, market=args.market)


def cmd_accounts_usage(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    return api.usage()


def cmd_accounts_list(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    return api.list_accounts()


def cmd_accounts_default(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    return {
        "stock_account": api.stock_account,
        "futopt_account": api.futopt_account,
    }


def cmd_accounts_set_default(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    account = pick_account(api, account_kind="any", account_id=args.account_id)
    api.set_default_account(account)
    return {
        "default_set_to": account,
        "stock_account": api.stock_account,
        "futopt_account": api.futopt_account,
    }


def cmd_accounts_balance(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    account = pick_account(api, account_kind=args.account_kind, account_id=args.account_id)
    return api.account_balance(account=account)


def cmd_accounts_margin(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    account = pick_account(api, account_kind=args.account_kind, account_id=args.account_id)
    return api.margin(account)


def cmd_accounts_positions(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    account = pick_account(api, account_kind=args.account_kind, account_id=args.account_id)
    return api.list_positions(account)


def cmd_accounts_position_detail(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    account = pick_account(api, account_kind=args.account_kind, account_id=args.account_id)
    return api.list_position_detail(account, args.detail_id)


def cmd_accounts_pnl(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    account = pick_account(api, account_kind=args.account_kind, account_id=args.account_id)
    return api.list_profit_loss(account, args.start, args.end)


def cmd_accounts_pnl_detail(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    account = pick_account(api, account_kind=args.account_kind, account_id=args.account_id)
    return api.list_profit_loss_detail(account, args.detail_id)


def cmd_accounts_pnl_summary(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    account = pick_account(api, account_kind=args.account_kind, account_id=args.account_id)
    return api.list_profit_loss_summary(account, args.start, args.end)


def cmd_accounts_settlements(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    account = pick_account(api, account_kind=args.account_kind, account_id=args.account_id)
    return api.settlements(account)


def cmd_accounts_trading_limits(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    account = pick_account(api, account_kind=args.account_kind, account_id=args.account_id)
    return api.trading_limits(account)


def cmd_accounts_account_margin(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    account = pick_account(api, account_kind=args.account_kind, account_id=args.account_id)
    return api.get_account_margin(
        currency=args.currency,
        margin_type=args.margin_type,
        account=account,
    )


def cmd_accounts_open_position(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    account = pick_account(api, account_kind=args.account_kind, account_id=args.account_id)
    return api.get_account_openposition(
        product_type=args.product_type,
        query_type=args.query_type,
        account=account,
    )


def cmd_accounts_settle_profitloss(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    account = pick_account(api, account_kind=args.account_kind, account_id=args.account_id)
    return api.get_account_settle_profitloss(
        product_type=args.product_type,
        summary=args.summary,
        start_date=args.start_date,
        end_date=args.end_date,
        currency=args.currency,
        account=account,
    )


def cmd_orders_update_status(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    account = pick_account(api, account_kind=args.account_kind, account_id=args.account_id)
    api.update_status(account)
    return {"updated": True, "account": account}


def cmd_orders_list(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    if str_to_bool(args.refresh, default=True):
        account = pick_account(api, account_kind=args.account_kind, account_id=args.account_id)
        api.update_status(account)

    trades = api.list_trades()
    if args.order_id:
        filtered = []
        for trade in trades:
            order = getattr(trade, "order", None)
            if order is None:
                continue

            order_id = str(getattr(order, "id", ""))
            seqno = str(getattr(order, "seqno", ""))
            if args.order_id in {order_id, seqno}:
                filtered.append(trade)
        return filtered

    return trades


def cmd_orders_place(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    contract = ensure_contract(api, code=args.code, market=args.market)
    market = infer_market(args.market, contract)
    account_kind = infer_account_kind(args.account_kind, contract)
    account = pick_account(api, account_kind=account_kind, account_id=args.account_id)

    order_kwargs: dict[str, Any] = {
        "action": enum_value("Action", args.action, fallback=args.action),
        "price": args.price,
        "quantity": args.quantity,
        "order_type": enum_value("OrderType", args.order_type, fallback=args.order_type),
        "account": account,
    }

    if args.price_type:
        order_kwargs["price_type"] = resolve_price_type(market, args.price_type)
    if args.octype:
        order_kwargs["octype"] = enum_value("FuturesOCType", args.octype, fallback=args.octype)
    if args.order_cond:
        order_kwargs["order_cond"] = enum_value("StockOrderCond", args.order_cond, fallback=args.order_cond)
    if args.order_lot:
        order_kwargs["order_lot"] = enum_value("StockOrderLot", args.order_lot, fallback=args.order_lot)

    if args.order_json:
        extra = parse_json_argument(args.order_json, dict, "order-json")
        order_kwargs.update(extra)

    order = api.Order(**order_kwargs)

    place_kwargs = {}
    if args.timeout >= 0:
        place_kwargs["timeout"] = args.timeout

    return api.place_order(contract, order, **place_kwargs)


def cmd_orders_cancel(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    trade = pick_trade_by_order_id(api, args.order_id)
    api.cancel_order(trade)
    return {"cancelled_order_id": args.order_id}


def cmd_orders_update(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    trade = pick_trade_by_order_id(api, args.order_id)

    update_kwargs: dict[str, Any] = {}
    if args.price is not None:
        update_kwargs["price"] = args.price
    if args.quantity is not None:
        update_kwargs["qty"] = args.quantity

    if not update_kwargs:
        raise RuntimeError("At least one of --price or --quantity is required for update.")

    api.update_order(trade, **update_kwargs)
    return {"updated_order_id": args.order_id, "changes": update_kwargs}


def cmd_orders_subscribe_trade(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    account = pick_account(api, account_kind=args.account_kind, account_id=args.account_id)
    api.subscribe_trade(account)
    return {"subscribed": True, "account": account}


def cmd_orders_unsubscribe_trade(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    account = pick_account(api, account_kind=args.account_kind, account_id=args.account_id)
    api.unsubscribe_trade(account)
    return {"subscribed": False, "account": account}


def cmd_market_snapshots(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    contracts = lookup_contracts(api, codes=args.codes, market=args.market)
    return api.snapshots(contracts)


def cmd_market_ticks(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    contract = ensure_contract(api, code=args.code, market=args.market)

    kwargs: dict[str, Any] = {"date": args.date}
    if args.last_count is not None:
        kwargs["last_cnt"] = args.last_count
    if args.start_time:
        kwargs["start"] = args.start_time
    if args.end_time:
        kwargs["end"] = args.end_time

    return api.ticks(contract, **kwargs)


def cmd_market_kbars(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    contract = ensure_contract(api, code=args.code, market=args.market)
    return api.kbars(contract, start=args.start, end=args.end)


def cmd_market_scanners(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    return api.scanners(
        scanner_type=scanner_type_value(args.scanner_type),
        ascending=str_to_bool(args.ascending, default=True),
        count=args.count,
    )


def cmd_market_short_stock_sources(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    contracts = lookup_contracts(api, codes=args.codes, market="stock")
    return api.short_stock_sources(contracts)


def cmd_market_credit_enquires(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    contracts = lookup_contracts(api, codes=args.codes, market="stock")
    return api.credit_enquires(contracts)


def cmd_market_notice(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    return api.notice()


def cmd_market_punish(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    return api.punish()


def cmd_quote_subscribe(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    contract = ensure_contract(api, code=args.code, market=args.market)

    def quote_callback(topic: str, quote: dict) -> None:
        payload = {"topic": topic, "quote": quote}
        print(json.dumps(to_serializable(payload), ensure_ascii=False))

    api.quote.set_quote_callback(quote_callback)

    api.quote.subscribe(
        contract,
        quote_type=quote_type_value(args.quote_type),
        version=quote_version_value(args.version),
        intraday_odd=str_to_bool(args.intraday_odd, default=False),
    )

    started_at = time.time()
    try:
        while time.time() - started_at < args.duration:
            time.sleep(0.2)
    finally:
        if str_to_bool(args.auto_unsubscribe, default=True):
            api.quote.unsubscribe(
                contract,
                quote_type=quote_type_value(args.quote_type),
                version=quote_version_value(args.version),
                intraday_odd=str_to_bool(args.intraday_odd, default=False),
            )

    return {
        "subscribed_code": args.code,
        "quote_type": args.quote_type,
        "version": args.version,
        "duration": args.duration,
    }


def cmd_api_methods(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    methods = []
    for name in dir(api):
        if name.startswith("_"):
            continue
        try:
            value = getattr(api, name)
        except Exception:
            continue
        if callable(value):
            methods.append(name)

    methods.sort()
    if args.match:
        token = args.match.lower()
        methods = [name for name in methods if token in name.lower()]

    return methods


def cmd_api_call(api: sj.Shioaji, args: argparse.Namespace, cfg: AuthConfig) -> Any:
    target: Any = api
    for part in args.method.split("."):
        if not hasattr(target, part):
            raise RuntimeError(f"Method path not found: {args.method}")
        target = getattr(target, part)

    if not callable(target):
        raise RuntimeError(f"Target is not callable: {args.method}")

    call_args = parse_json_argument(args.args_json, list, "args-json")
    call_kwargs = parse_json_argument(args.kwargs_json, dict, "kwargs-json")

    resolved_args = resolve_special_payload(call_args, api)
    resolved_kwargs = resolve_special_payload(call_kwargs, api)

    return target(*resolved_args, **resolved_kwargs)


def with_common_account_args(parser: argparse.ArgumentParser, default_kind: str = "any") -> None:
    parser.add_argument("--account-kind", choices=["auto", "any", "stock", "futures"], default=default_kind)
    parser.add_argument("--account-id", default="", help="Target account id.")


def add_auth_commands(subparsers: argparse._SubParsersAction) -> None:
    auth = subparsers.add_parser("auth", help="Authentication and session checks.")
    auth_sub = auth.add_subparsers(dest="auth_command", required=True)

    check = auth_sub.add_parser("check", help="Login test and print accounts.")
    check.set_defaults(handler=cmd_auth_check)


def add_contract_commands(subparsers: argparse._SubParsersAction) -> None:
    contracts = subparsers.add_parser("contracts", help="Contract related commands.")
    contracts_sub = contracts.add_subparsers(dest="contracts_command", required=True)

    status = contracts_sub.add_parser("status", help="Show contracts download status.")
    status.set_defaults(handler=cmd_contracts_status)

    fetch = contracts_sub.add_parser("fetch", help="Force fetch contracts from server.")
    fetch.add_argument("--contract-download", choices=["true", "false"], default="true")
    fetch.set_defaults(handler=cmd_contracts_fetch)

    find = contracts_sub.add_parser("find", help="Find one contract by code.")
    find.add_argument("--code", required=True)
    find.add_argument("--market", choices=["auto", "futures", "options", "stock", "indexs"], default="auto")
    find.set_defaults(handler=cmd_contracts_find)


def add_accounts_commands(subparsers: argparse._SubParsersAction) -> None:
    accounts = subparsers.add_parser("accounts", help="Account and position commands.")
    accounts_sub = accounts.add_subparsers(dest="accounts_command", required=True)

    usage = accounts_sub.add_parser("usage", help="Show API usage status.")
    usage.set_defaults(handler=cmd_accounts_usage)

    list_accounts = accounts_sub.add_parser("list", help="List all accounts.")
    list_accounts.set_defaults(handler=cmd_accounts_list)

    default_account = accounts_sub.add_parser("default", help="Show current default stock/futures account.")
    default_account.set_defaults(handler=cmd_accounts_default)

    set_default = accounts_sub.add_parser("set-default", help="Set default account by account id.")
    set_default.add_argument("--account-id", required=True)
    set_default.set_defaults(handler=cmd_accounts_set_default)

    balance = accounts_sub.add_parser("balance", help="Query stock account balance.")
    with_common_account_args(balance, default_kind="stock")
    balance.set_defaults(handler=cmd_accounts_balance)

    margin = accounts_sub.add_parser("margin", help="Query futures margin.")
    with_common_account_args(margin, default_kind="futures")
    margin.set_defaults(handler=cmd_accounts_margin)

    positions = accounts_sub.add_parser("positions", help="List unrealized positions.")
    with_common_account_args(positions, default_kind="any")
    positions.set_defaults(handler=cmd_accounts_positions)

    position_detail = accounts_sub.add_parser("position-detail", help="List position detail by detail id.")
    with_common_account_args(position_detail, default_kind="any")
    position_detail.add_argument("--detail-id", type=int, required=True)
    position_detail.set_defaults(handler=cmd_accounts_position_detail)

    pnl = accounts_sub.add_parser("pnl", help="List realized profit/loss records by date range.")
    with_common_account_args(pnl, default_kind="any")
    pnl.add_argument("--start", type=iso_date, required=True, help="YYYY-MM-DD")
    pnl.add_argument("--end", type=iso_date, required=True, help="YYYY-MM-DD")
    pnl.set_defaults(handler=cmd_accounts_pnl)

    pnl_detail = accounts_sub.add_parser("pnl-detail", help="List detailed realized PnL for one detail id.")
    with_common_account_args(pnl_detail, default_kind="any")
    pnl_detail.add_argument("--detail-id", type=int, required=True)
    pnl_detail.set_defaults(handler=cmd_accounts_pnl_detail)

    pnl_summary = accounts_sub.add_parser("pnl-summary", help="List realized PnL summary for date range.")
    with_common_account_args(pnl_summary, default_kind="any")
    pnl_summary.add_argument("--start", type=iso_date, required=True, help="YYYY-MM-DD")
    pnl_summary.add_argument("--end", type=iso_date, required=True, help="YYYY-MM-DD")
    pnl_summary.set_defaults(handler=cmd_accounts_pnl_summary)

    settlements = accounts_sub.add_parser("settlements", help="Query stock settlements.")
    with_common_account_args(settlements, default_kind="stock")
    settlements.set_defaults(handler=cmd_accounts_settlements)

    trading_limits = accounts_sub.add_parser("trading-limits", help="Query stock trading limits.")
    with_common_account_args(trading_limits, default_kind="stock")
    trading_limits.set_defaults(handler=cmd_accounts_trading_limits)

    account_margin = accounts_sub.add_parser("account-margin", help="Query get_account_margin.")
    with_common_account_args(account_margin, default_kind="futures")
    account_margin.add_argument("--currency", default="NTD")
    account_margin.add_argument("--margin-type", default="1")
    account_margin.set_defaults(handler=cmd_accounts_account_margin)

    open_position = accounts_sub.add_parser("open-position", help="Query get_account_openposition.")
    with_common_account_args(open_position, default_kind="futures")
    open_position.add_argument("--product-type", default="0")
    open_position.add_argument("--query-type", default="0")
    open_position.set_defaults(handler=cmd_accounts_open_position)

    settle_profitloss = accounts_sub.add_parser("settle-profitloss", help="Query get_account_settle_profitloss.")
    with_common_account_args(settle_profitloss, default_kind="futures")
    settle_profitloss.add_argument("--product-type", default="0")
    settle_profitloss.add_argument("--summary", choices=["Y", "N"], default="Y")
    settle_profitloss.add_argument("--start-date", type=compact_date, required=True, help="YYYY-MM-DD")
    settle_profitloss.add_argument("--end-date", type=compact_date, required=True, help="YYYY-MM-DD")
    settle_profitloss.add_argument("--currency", default="")
    settle_profitloss.set_defaults(handler=cmd_accounts_settle_profitloss)


def add_orders_commands(subparsers: argparse._SubParsersAction) -> None:
    orders = subparsers.add_parser("orders", help="Order and trade commands.")
    orders_sub = orders.add_subparsers(dest="orders_command", required=True)

    update_status = orders_sub.add_parser("update-status", help="Update order status from server.")
    with_common_account_args(update_status, default_kind="futures")
    update_status.set_defaults(handler=cmd_orders_update_status)

    list_trades = orders_sub.add_parser("list", help="List trades.")
    with_common_account_args(list_trades, default_kind="futures")
    list_trades.add_argument("--refresh", choices=["true", "false"], default="true")
    list_trades.add_argument("--order-id", default="")
    list_trades.set_defaults(handler=cmd_orders_list)

    place = orders_sub.add_parser("place", help="Place an order.")
    place.add_argument("--code", required=True)
    place.add_argument("--market", choices=["auto", "futures", "options", "stock"], default="auto")
    place.add_argument("--account-kind", choices=["auto", "stock", "futures"], default="auto")
    place.add_argument("--account-id", default="")
    place.add_argument("--action", choices=["Buy", "Sell"], required=True)
    place.add_argument("--price", type=float, default=0)
    place.add_argument("--quantity", type=int, default=1)
    place.add_argument("--price-type", default="MKT")
    place.add_argument("--order-type", default="IOC")
    place.add_argument("--octype", default="")
    place.add_argument("--order-cond", default="")
    place.add_argument("--order-lot", default="")
    place.add_argument("--timeout", type=int, default=-1, help="-1 means use API default blocking timeout.")
    place.add_argument("--order-json", default="", help="Additional order fields in JSON object.")
    place.set_defaults(handler=cmd_orders_place)

    cancel = orders_sub.add_parser("cancel", help="Cancel by order id or seqno.")
    cancel.add_argument("--order-id", required=True)
    cancel.set_defaults(handler=cmd_orders_cancel)

    update = orders_sub.add_parser("update", help="Update order price/quantity by order id.")
    update.add_argument("--order-id", required=True)
    update.add_argument("--price", type=float)
    update.add_argument("--quantity", type=int)
    update.set_defaults(handler=cmd_orders_update)

    subscribe_trade = orders_sub.add_parser("subscribe-trade", help="Subscribe order/deal callback for one account.")
    with_common_account_args(subscribe_trade, default_kind="any")
    subscribe_trade.set_defaults(handler=cmd_orders_subscribe_trade)

    unsubscribe_trade = orders_sub.add_parser("unsubscribe-trade", help="Unsubscribe order/deal callback for one account.")
    with_common_account_args(unsubscribe_trade, default_kind="any")
    unsubscribe_trade.set_defaults(handler=cmd_orders_unsubscribe_trade)


def add_market_commands(subparsers: argparse._SubParsersAction) -> None:
    market = subparsers.add_parser("market", help="Market data and ranking commands.")
    market_sub = market.add_subparsers(dest="market_command", required=True)

    snapshots = market_sub.add_parser("snapshots", help="Get snapshots for multiple contracts.")
    snapshots.add_argument("--codes", nargs="+", required=True)
    snapshots.add_argument("--market", choices=["auto", "futures", "options", "stock", "indexs"], default="auto")
    snapshots.set_defaults(handler=cmd_market_snapshots)

    ticks = market_sub.add_parser("ticks", help="Get ticks for one contract.")
    ticks.add_argument("--code", required=True)
    ticks.add_argument("--market", choices=["auto", "futures", "options", "stock", "indexs"], default="auto")
    ticks.add_argument("--date", type=iso_date, required=True, help="YYYY-MM-DD")
    ticks.add_argument("--start-time", default="", help="Optional time string for range query.")
    ticks.add_argument("--end-time", default="", help="Optional time string for range query.")
    ticks.add_argument("--last-count", type=int)
    ticks.set_defaults(handler=cmd_market_ticks)

    kbars = market_sub.add_parser("kbars", help="Get kbars for one contract.")
    kbars.add_argument("--code", required=True)
    kbars.add_argument("--market", choices=["auto", "futures", "options", "stock", "indexs"], default="auto")
    kbars.add_argument("--start", type=iso_date, required=True, help="YYYY-MM-DD")
    kbars.add_argument("--end", type=iso_date, required=True, help="YYYY-MM-DD")
    kbars.set_defaults(handler=cmd_market_kbars)

    scanners = market_sub.add_parser("scanners", help="Get scanner ranks.")
    scanners.add_argument(
        "--scanner-type",
        default="ChangePercentRank",
        choices=[
            "ChangePercentRank",
            "ChangePriceRank",
            "DayRangeRank",
            "VolumeRank",
            "AmountRank",
        ],
    )
    scanners.add_argument("--count", type=int, default=20)
    scanners.add_argument("--ascending", choices=["true", "false"], default="true")
    scanners.set_defaults(handler=cmd_market_scanners)

    short_sources = market_sub.add_parser("short-stock-sources", help="Get short stock source info.")
    short_sources.add_argument("--codes", nargs="+", required=True)
    short_sources.set_defaults(handler=cmd_market_short_stock_sources)

    credit = market_sub.add_parser("credit-enquires", help="Get credit enquire data.")
    credit.add_argument("--codes", nargs="+", required=True)
    credit.set_defaults(handler=cmd_market_credit_enquires)

    notice = market_sub.add_parser("notice", help="Get attention stocks.")
    notice.set_defaults(handler=cmd_market_notice)

    punish = market_sub.add_parser("punish", help="Get disposition stocks.")
    punish.set_defaults(handler=cmd_market_punish)


def add_quote_commands(subparsers: argparse._SubParsersAction) -> None:
    quote = subparsers.add_parser("quote", help="Realtime quote subscriptions.")
    quote_sub = quote.add_subparsers(dest="quote_command", required=True)

    subscribe = quote_sub.add_parser("subscribe", help="Subscribe quote stream and print callback payload.")
    subscribe.add_argument("--code", required=True)
    subscribe.add_argument("--market", choices=["auto", "futures", "options", "stock", "indexs"], default="auto")
    subscribe.add_argument("--quote-type", choices=["tick", "bidask", "quote"], default="tick")
    subscribe.add_argument("--version", choices=["v0", "v1", "v2"], default="v1")
    subscribe.add_argument("--intraday-odd", choices=["true", "false"], default="false")
    subscribe.add_argument("--duration", type=int, default=30, help="Subscription duration in seconds.")
    subscribe.add_argument("--auto-unsubscribe", choices=["true", "false"], default="true")
    subscribe.set_defaults(handler=cmd_quote_subscribe)


def add_api_commands(subparsers: argparse._SubParsersAction) -> None:
    api = subparsers.add_parser("api", help="Generic API exploration and call.")
    api_sub = api.add_subparsers(dest="api_command", required=True)

    methods = api_sub.add_parser("methods", help="List callable methods on api instance.")
    methods.add_argument("--match", default="")
    methods.set_defaults(handler=cmd_api_methods)

    call = api_sub.add_parser("call", help="Call any API method by method path.")
    call.add_argument("--method", required=True, help="Example: usage, account_balance, quote.subscribe")
    call.add_argument("--args-json", default="[]", help="JSON array for positional args.")
    call.add_argument("--kwargs-json", default="{}", help="JSON object for keyword args.")
    call.set_defaults(handler=cmd_api_call)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Unified Shioaji CLI for account, market, order, quote, and generic API operations. "
            "All auth and cert values are loaded from one .env file."
        )
    )

    parser.add_argument("--env-file", default=".env", help="Path to .env file.")
    parser.add_argument("--simulation", choices=["true", "false"], default=None)
    parser.add_argument("--fetch-contract", choices=["true", "false"], default="true")
    parser.add_argument("--contracts-timeout", type=int, default=10000)
    parser.add_argument("--subscribe-trade", choices=["true", "false"], default="true")
    parser.add_argument(
        "--activate-ca",
        choices=["auto", "true", "false"],
        default="auto",
        help="auto: activate when CA_CERT_PATH/CA_PASSWORD/PERSON_ID exist.",
    )
    parser.add_argument("--raw", action="store_true", help="Print raw Python object instead of JSON.")

    subparsers = parser.add_subparsers(dest="command", required=True)
    add_auth_commands(subparsers)
    add_contract_commands(subparsers)
    add_accounts_commands(subparsers)
    add_orders_commands(subparsers)
    add_market_commands(subparsers)
    add_quote_commands(subparsers)
    add_api_commands(subparsers)

    return parser


def run(args: argparse.Namespace) -> int:
    if not hasattr(args, "handler"):
        raise RuntimeError("No command handler matched.")

    simulation_override = None
    if args.simulation is not None:
        simulation_override = str_to_bool(args.simulation, default=True)

    cfg = AuthConfig.from_env(args.env_file, simulation_override=simulation_override)

    api = None
    try:
        api = create_api(
            cfg=cfg,
            fetch_contract=str_to_bool(args.fetch_contract, default=True),
            contracts_timeout=args.contracts_timeout,
            subscribe_trade=str_to_bool(args.subscribe_trade, default=True),
            activate_ca=active_ca_flag(args.activate_ca, cfg),
        )

        result = args.handler(api, args, cfg)
        emit(result, raw=args.raw)
        return 0

    except Exception as exc:
        error_payload = {
            "ok": False,
            "error": str(exc),
        }
        print(json.dumps(error_payload, ensure_ascii=False, indent=2))
        return 1

    finally:
        safe_logout(api)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())

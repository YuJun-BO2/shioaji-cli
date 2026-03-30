from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import Any, Optional

from dotenv import load_dotenv
import shioaji as sj


def str_to_bool(value: str | bool | None, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value

    normalized = value.strip().lower()
    if normalized in {"1", "true", "t", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "f", "no", "n", "off"}:
        return False
    return default


def resolve_env_path(env_file: str) -> str:
    if os.path.isabs(env_file):
        return env_file

    cwd_candidate = os.path.abspath(env_file)
    if os.path.exists(cwd_candidate):
        return cwd_candidate

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    root_candidate = os.path.join(project_root, env_file)
    return root_candidate


@dataclass
class AuthConfig:
    api_key: str
    secret_key: str
    ca_cert_path: str
    ca_password: str
    person_id: str
    expire_date: str
    simulation: bool
    env_file: str

    @classmethod
    def from_env(cls, env_file: str, simulation_override: Optional[bool] = None) -> "AuthConfig":
        resolved_env_file = resolve_env_path(env_file)
        load_dotenv(resolved_env_file, override=True)

        api_key = os.getenv("API_KEY", "").strip()
        secret_key = os.getenv("SECRET_KEY", "").strip()
        if not api_key or not secret_key:
            raise RuntimeError(
                f"Missing API_KEY or SECRET_KEY in env file: {resolved_env_file}"
            )

        env_simulation = str_to_bool(os.getenv("SIMULATION"), default=True)
        simulation = env_simulation if simulation_override is None else simulation_override

        return cls(
            api_key=api_key,
            secret_key=secret_key,
            ca_cert_path=os.getenv("CA_CERT_PATH", "").strip(),
            ca_password=os.getenv("CA_PASSWORD", "").strip(),
            person_id=os.getenv("PERSON_ID", "").strip(),
            expire_date=os.getenv("EXPIRE_DATE", "").strip(),
            simulation=simulation,
            env_file=resolved_env_file,
        )


def create_api(
    cfg: AuthConfig,
    fetch_contract: bool = True,
    contracts_timeout: int = 10000,
    subscribe_trade: bool = True,
    activate_ca: bool = True,
) -> sj.Shioaji:
    api = sj.Shioaji(simulation=cfg.simulation)
    api.login(
        api_key=cfg.api_key,
        secret_key=cfg.secret_key,
        fetch_contract=fetch_contract,
        contracts_timeout=contracts_timeout,
        subscribe_trade=subscribe_trade,
    )

    if activate_ca and cfg.ca_cert_path and cfg.ca_password and cfg.person_id:
        if os.path.exists(cfg.ca_cert_path):
            api.activate_ca(
                ca_path=cfg.ca_cert_path,
                ca_passwd=cfg.ca_password,
                person_id=cfg.person_id,
            )

    return api


def safe_logout(api: Optional[sj.Shioaji]) -> None:
    if api is None:
        return
    try:
        api.logout()
    except Exception:
        pass


def is_futures_account(account: Any) -> bool:
    return "Future" in str(getattr(account, "account_type", ""))


def is_stock_account(account: Any) -> bool:
    return "Stock" in str(getattr(account, "account_type", ""))


def pick_account(
    api: sj.Shioaji,
    account_kind: str = "any",
    account_id: str = "",
) -> Any:
    accounts = api.list_accounts()
    if not accounts:
        raise RuntimeError("No accounts found after login.")

    if account_id:
        for account in accounts:
            if str(getattr(account, "account_id", "")) == account_id:
                return account
        raise RuntimeError(f"Account ID not found: {account_id}")

    normalized_kind = account_kind.lower()
    if normalized_kind == "any":
        return accounts[0]

    if normalized_kind in {"futures", "future", "futopt", "f"}:
        for account in accounts:
            if is_futures_account(account):
                return account
        raise RuntimeError("No futures account found.")

    if normalized_kind in {"stock", "stocks", "s"}:
        for account in accounts:
            if is_stock_account(account):
                return account
        raise RuntimeError("No stock account found.")

    raise RuntimeError(f"Unsupported account kind: {account_kind}")


def _lookup_by_code(container: Any, code: str) -> Any:
    if container is None:
        return None

    try:
        contract = container[code]
        if contract:
            return contract
    except Exception:
        pass

    getter = getattr(container, "get", None)
    if callable(getter):
        try:
            contract = getter(code)
            if contract:
                return contract
        except Exception:
            pass

    return None


def _scan_contract_group(group: Any, code: str) -> Any:
    if group is None:
        return None

    direct = _lookup_by_code(group, code)
    if direct is not None:
        return direct

    for name in dir(group):
        if name.startswith("_"):
            continue

        try:
            item = getattr(group, name)
        except Exception:
            continue

        contract = _lookup_by_code(item, code)
        if contract is not None:
            return contract

        try:
            for child in item:
                child_code = str(getattr(child, "code", ""))
                if child_code == code:
                    return child
        except Exception:
            continue

    return None


def lookup_contract(api: sj.Shioaji, code: str, market: str = "auto") -> Any:
    normalized_market = market.lower()

    groups = []
    if normalized_market == "auto":
        groups = ["futures", "options", "stocks", "indexs"]
    else:
        groups = [normalized_market]

    for group_name in groups:
        if group_name in {"futures", "future"}:
            contract = _scan_contract_group(api.Contracts.Futures, code)
            if contract is not None:
                return contract

        elif group_name in {"options", "option"}:
            contract = _scan_contract_group(api.Contracts.Options, code)
            if contract is not None:
                return contract

        elif group_name in {"stocks", "stock"}:
            contract = _scan_contract_group(api.Contracts.Stocks, code)
            if contract is not None:
                return contract

        elif group_name in {"indexs", "indexes", "index"}:
            contract = _scan_contract_group(api.Contracts.Indexs, code)
            if contract is not None:
                return contract

    return None


def lookup_contracts(api: sj.Shioaji, codes: list[str], market: str = "auto") -> list[Any]:
    contracts: list[Any] = []
    missing: list[str] = []

    for code in codes:
        contract = lookup_contract(api, code=code, market=market)
        if contract is None:
            missing.append(code)
        else:
            contracts.append(contract)

    if missing:
        missing_str = ", ".join(missing)
        raise RuntimeError(f"Contracts not found: {missing_str}")

    return contracts


def enum_member(enum_name: str, member_name: str) -> Any:
    enum_cls = getattr(sj.constant, enum_name, None)
    if enum_cls is None:
        raise RuntimeError(f"Unknown enum type: {enum_name}")

    if hasattr(enum_cls, member_name):
        return getattr(enum_cls, member_name)

    # Fallback for lowercase input values.
    upper_name = member_name.upper()
    if hasattr(enum_cls, upper_name):
        return getattr(enum_cls, upper_name)

    raise RuntimeError(f"Enum member not found: {enum_name}.{member_name}")


def account_like(value: Any) -> bool:
    return hasattr(value, "account_id") and hasattr(value, "broker_id")


def resolve_special_payload(value: Any, api: sj.Shioaji) -> Any:
    if isinstance(value, list):
        return [resolve_special_payload(item, api) for item in value]

    if isinstance(value, dict):
        if "$contract" in value:
            market = value.get("$market", "auto")
            contract = lookup_contract(api, code=str(value["$contract"]), market=market)
            if contract is None:
                raise RuntimeError(f"Contract not found: {value['$contract']}")
            return contract

        if "$contracts" in value:
            market = value.get("$market", "auto")
            codes = [str(code) for code in value["$contracts"]]
            return lookup_contracts(api, codes=codes, market=market)

        if "$account" in value:
            selector = str(value["$account"])
            if selector.lower() in {"any", "stock", "stocks", "futures", "future", "futopt", "f"}:
                return pick_account(api, account_kind=selector)
            return pick_account(api, account_id=selector)

        return {key: resolve_special_payload(val, api) for key, val in value.items()}

    return value


def to_serializable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, (datetime, date, time, Decimal)):
        return str(value)

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, list):
        return [to_serializable(item) for item in value]

    if isinstance(value, tuple):
        return [to_serializable(item) for item in value]

    if isinstance(value, set):
        return [to_serializable(item) for item in value]

    if isinstance(value, dict):
        return {str(key): to_serializable(val) for key, val in value.items()}

    if account_like(value):
        return {
            "account_id": getattr(value, "account_id", ""),
            "broker_id": getattr(value, "broker_id", ""),
            "person_id": getattr(value, "person_id", ""),
            "signed": getattr(value, "signed", None),
            "username": getattr(value, "username", ""),
            "account_type": str(getattr(value, "account_type", "")),
        }

    if hasattr(value, "__dict__"):
        data: dict[str, Any] = {}
        for key, val in value.__dict__.items():
            if key.startswith("_"):
                continue
            data[key] = to_serializable(val)
        if data:
            return data

    return str(value)


def iso_date(text: str) -> str:
    datetime.strptime(text, "%Y-%m-%d")
    return text


def compact_date(text: str) -> str:
    return datetime.strptime(text, "%Y-%m-%d").strftime("%Y%m%d")

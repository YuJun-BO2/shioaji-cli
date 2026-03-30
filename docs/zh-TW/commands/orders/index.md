# orders 指令群

## 角色定位

下單、查單、改單、刪單與成交回報訂閱。

## 適用情境

- 盤中建立委託並追蹤狀態
- 風控條件達成後改刪單

## 子指令

- [orders cancel](./cancel.md)
- [orders list](./list.md)
- [orders place](./place.md)
- [orders subscribe-trade](./subscribe-trade.md)
- [orders unsubscribe-trade](./unsubscribe-trade.md)
- [orders update](./update.md)
- [orders update-status](./update-status.md)

## 操作提醒

- timeout=0 為非阻塞下單。
- 改刪單前建議先 update-status + list 同步狀態。

## 延伸閱讀

- [下單與回報參考](../../../references/order_manager.md)

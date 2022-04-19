
            ####
            quantity, stoploss, limit = self.calculate_position_size_stoploss_limit()
            trade.quantity = quantity
            trade.save(updated_fields=["quantity"])
            trade.open_position()

        if stoploss:
            data: dict = {
                "trade_size": trade.trade_size,
                "position_stop_loss": trade.trade_stop_loss,
                "trade_limit": trade.trade_limit,
                "quantity": trade.quantity * -1,
                "symbol": trade.symbol,
                "order_type": OrderType.LMT.value,
                "price": stoploss,
                "position_type": PositionType.BUY.value if trade.position_type == PositionType.SELL.value else PositionType.SELL.value,
                "trade_type": TradeType.CLOSE.value,
                "broker": trade.broker,
                "executor": trade.executor,
            }
            stoploss_trade: Trade = Trade.objects.create(**data)
            stoploss_trade.open_position()

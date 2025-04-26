class Platform:
    def __init__(self, plat_id, fund_plat_fee, plat_name, enabled, fund_deal_fee,
                 share_plat_fee, share_plat_max_fee, share_deal_fee,
                 share_deal_reduce_trades, share_deal_reduce_amount,
        ):

        self.plat_id                    = plat_id
        self.fund_plat_fee              = fund_plat_fee
        self.plat_name                  = plat_name
        self.enabled                    = enabled
        self.fund_deal_fee              = fund_deal_fee
        self.share_plat_fee             = share_plat_fee
        self.share_plat_max_fee         = share_plat_max_fee
        self.share_deal_fee             = share_deal_fee
        self.share_deal_reduce_trades   = share_deal_reduce_trades
        self.share_deal_reduce_amount   = share_deal_reduce_amount

from constants.protocol import addresses


def contract_mappings(chain):
    return {
        "X7100 Liquidity Hub": (
            (
                "setShares\n"
                "setRouter\n"
                "setOffRampPair\n"
                "setBalanceThreshold\n"
                "setLiquidityBalanceThreshold\n"
                "setLiquidityRatioTarget\n"
                "setLiquidityTokenReceiver\n"
                "setDistributionTarget\n"
                "setLendingPoolTarget\n"
                "setTreasuryTarget\n"
                "freezeTreasuryTarget\n"
                "freezeDistributeTarget\n"
                "freezeLendingPoolTarget\n"
                "freezeBalanceThreshold\n"
                "freezeLiquidityBalanceThreshold"
            ),
            addresses.x7100_liquidity_hub(chain),
        ),
        "X7DAO Liquidity Hub": (
            (
                "setShares\n"
                "setRouter\n"
                "setOffRampPair\n"
                "setBalanceThreshold\n"
                "setLiquidityRatioTarget\n"
                "setLiquidityTokenReceiver\n"
                "setDistributionTarget\n"
                "setAuxiliaryTarget\n"
                "setTreasuryTarget\n"
                "freezeTreasuryTarget\n"
                "freezeDistributeTarget\n"
                "freezeAuxiliaryTarget\n"
                "freezeBalanceThreshold"
            ),
            addresses.x7dao_liquidity_hub(chain),
        ),
        "X7R Liquidity Hub": (
            (
                "setShares\n"
                "setRouter\n"
                "setOffRampPair\n"
                "setBalanceThreshold\n"
                "setLiquidityRatioTarget\n"
                "setLiquidityTokenReceiver\n"
                "setDistributionTarget\n"
                "setTreasuryTarget \n"
                "freezeTreasuryTarget\n"
                "freezeDistributeTarget\n"
                "freezeBalanceThreshold"
            ),
            addresses.x7r_liquidity_hub(chain),
        ),
        "X7D": (
            (
                "setAuthorizedMinter\n"
                "setAuthorizedRedeemer\n"
                "setRecoveredTokenRecipient\n"
                "setRecoveredETHRecipient"
            ),
            addresses.x7d(chain),
        ),
        "Ecosystem Splitter": (
            ("setWETH\nsetOutlet\nfreezeOutletChange\nsetShares\n"),
            addresses.eco_splitter(chain),
        ),
        "Treasury Splitter": (
            ("freezeOutlet\nsetOutletRecipient\nsetSlotShares"),
            addresses.treasury_splitter(chain),
        ),
        "Factory": (
            (
                "setFeeTo\nsetDiscountAuthority\nsetTrusted\nsetFailsafeLiquidator"
            ),
            addresses.factory(chain),
        ),
        "Borrowing Maxi": (
            ("setMintFeeDestination\nsetBaseURI\nsetMintPrice"),
            addresses.borrow_maxi(chain),
        ),
        "DEX Maxi": (
            ("setMintFeeDestination\nsetBaseURI\nsetMintPrice"),
            addresses.dex_maxi(chain),
        ),
        "Ecosystem Maxi": (
            ("setMintFeeDestination\nsetBaseURI\nsetMintPrice"),
            addresses.eco_maxi(chain),
        ),
        "Liquidity Maxi": (
            ("setMintFeeDestination\nsetBaseURI\nsetMintPrice"),
            addresses.liq_maxi(chain),
        ),
        "Magister": (
            ("setMintFeeDestination\nsetBaseURI\nsetMintPrice"),
            addresses.magister(chain),
        ),
        "Lending Pool": (
            (
                "setEcosystemRecipientAddress\n"
                "setRouter\n"
                "setWETH\n"
                "setX7D\n"
                "setLoanTermActiveState\n"
                "setLiquidationReward\n"
                "setOriginationShares\n"
                "setPremiumShares"
            ),
            addresses.lending_pool(chain),
        ),
        "Lending Pool Reserve": (
            (
                "setLendingPool\n"
                "setEcosystemRecipientAddress\n"
                "setX7D\n"
                "setEcosystemPayer\n"
                "fundLendingPool\n"
                "setRecoveredTokenRecipient"
            ),
            addresses.lending_pool_reserve(chain),
        ),
        "Token Time Lock": (
            (
                "setWETH\n"
                "setGlobalUnlockTimestamp\n"
                "extendGlobalUnlockTimestamp\n"
                "setTokenUnlockTimestamp\n"
                "extendTokenUnlockTimestamp\n"
                "setTokenOwner"
            ),
            addresses.token_time_lock(chain),
        ),
        "Token Burner": (
            ("setRouter\nsetTargetToken"),
            addresses.token_burner(chain),
        ),
        "X7100 Discount Authority": (
            (
                "setEcosystemMaxiNFT\nsetLiquidityMaxiNFT\nsetMagisterNFT\nsetX7DAO\n"
            ),
            addresses.x7100_discount(chain),
        ),
        "X7DAO Discount Authority": (
            ("setEcosystemMaxiNFT\nsetLiquidityMaxiNFT\n"),
            addresses.x7dao_discount(chain),
        ),
        "X7R Discount Authority": (
            ("setEcosystemMaxiNFT\nsetLiquidityMaxiNFT\nsetMagisterNFT\n"),
            addresses.x7r_discount(chain),
        ),
        "Lending Discount Authority": (
            (
                "setAuthorizedConsumer\n"
                "setTimeBasedDiscount\n"
                "setAmountBasedDiscount\n"
                "setDiscountNFT\n"
                "setConsumableDiscountNFT\n"
                "setDiscountNFTDiscounts\n"
                "setConsumableDiscountNFTDiscounts"
            ),
            addresses.lending_discount(chain),
        ),
        "Xchange Discount Authority": (
            ("setDEXMaxiNFT"),
            addresses.xchange_discount(chain),
        ),
    }

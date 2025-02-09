from constants import ca


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
            ca.X7100_LIQ_HUB(chain),
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
            ca.X7DAO_LIQ_HUB(chain),
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
            ca.X7R_LIQ_HUB(chain),
        ),
        "X7D": (
            (
                "setAuthorizedMinter\n"
                "setAuthorizedRedeemer\n"
                "setRecoveredTokenRecipient\n"
                "setRecoveredETHRecipient"
            ),
            ca.X7D(chain),
        ),
        "Ecosystem Splitter": (
            ("setWETH\nsetOutlet\nfreezeOutletChange\nsetShares\n"),
            ca.ECO_SPLITTER(chain),
        ),
        "Treasury Splitter": (
            ("freezeOutlet\nsetOutletRecipient\nsetSlotShares"),
            ca.TREASURY_SPLITTER(chain),
        ),
        "Factory": (
            (
                "setFeeTo\nsetDiscountAuthority\nsetTrusted\nsetFailsafeLiquidator"
            ),
            ca.FACTORY(chain),
        ),
        "Borrowing Maxi": (
            ("setMintFeeDestination\nsetBaseURI\nsetMintPrice"),
            ca.BORROW(chain),
        ),
        "DEX Maxi": (
            ("setMintFeeDestination\nsetBaseURI\nsetMintPrice"),
            ca.DEX(chain),
        ),
        "Ecosystem Maxi": (
            ("setMintFeeDestination\nsetBaseURI\nsetMintPrice"),
            ca.ECO(chain),
        ),
        "Liquidity Maxi": (
            ("setMintFeeDestination\nsetBaseURI\nsetMintPrice"),
            ca.LIQ(chain),
        ),
        "Magister": (
            ("setMintFeeDestination\nsetBaseURI\nsetMintPrice"),
            ca.MAGISTER(chain),
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
            ca.LPOOL(chain),
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
            ca.LPOOL_RESERVE(chain),
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
            ca.TIME_LOCK(chain),
        ),
        "Token Burner": (("setRouter\nsetTargetToken"), ca.BURNER(chain)),
        "X7100 Discount Authority": (
            (
                "setEcosystemMaxiNFT\nsetLiquidityMaxiNFT\nsetMagisterNFT\nsetX7DAO\n"
            ),
            ca.X7100_DISCOUNT(chain),
        ),
        "X7DAO Discount Authority": (
            ("setEcosystemMaxiNFT\nsetLiquidityMaxiNFT\n"),
            ca.X7DAO_DISCOUNT(chain),
        ),
        "X7R Discount Authority": (
            ("setEcosystemMaxiNFT\nsetLiquidityMaxiNFT\nsetMagisterNFT\n"),
            ca.X7R_DISCOUNT(chain),
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
            ca.LENDING_DISCOUNT(chain),
        ),
        "Xchange Discount Authority": (
            ("setDEXMaxiNFT"),
            ca.XCHANGE_DISCOUNT(chain),
        ),
    }

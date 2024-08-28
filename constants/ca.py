# TOKEN CA

def X7R(chain):
    if chain == "base":
        return "0x70008F18Fc58928dcE982b0A69C2c21ff80Dca54"
    else:
        return "0x70008F18Fc58928dcE982b0A69C2c21ff80Dca54"
    
def X7DAO(chain):
    if chain == "base":
        return "0x7105E64bF67ECA3Ae9b123F0e5Ca2b83b2eF2dA0"
    else:
        return "0x7105E64bF67ECA3Ae9b123F0e5Ca2b83b2eF2dA0"

def X7101(chain):
    if chain == "base":
        return "0x7101a9392eac53b01e7c07ca3baca945a56ee105"
    else:
        return "0x7101a9392eac53b01e7c07ca3baca945a56ee105"
    
def X7102(chain):
    if chain == "base":
        return "0x7102dc82ef61bfb0410b1b1bf8ea74575bf0a105"
    else:
        return "0x7102dc82ef61bfb0410b1b1bf8ea74575bf0a105"
    
def X7103(chain):
    if chain == "base":
        return "0x7103eBdbF1f89be2d53EFF9B3CF996C9E775c105"
    else:
        return "0x7103eBdbF1f89be2d53EFF9B3CF996C9E775c105"
    
def X7104(chain):
    if chain == "base":
        return "0x7104D1f179Cc9cc7fb5c79Be6Da846E3FBC4C105"
    else:
        return "0x7104D1f179Cc9cc7fb5c79Be6Da846E3FBC4C105"
    
def X7105(chain):
    if chain == "base":
        return "0x7105FAA4a26eD1c67B8B2b41BEc98F06Ee21D105"
    else:
        return "0x7105FAA4a26eD1c67B8B2b41BEc98F06Ee21D105"
    
def X7100(chain):
    return [
        X7101(chain), 
        X7102(chain), 
        X7103(chain), 
        X7104(chain), 
        X7105(chain)
    ]

def X7D(chain):
    if chain == "base":
        return "0x7D000a1B9439740692F8942A296E1810955F5000"
    else:
        return "0x7D000a1B9439740692F8942A296E1810955F5000"


# NFTS
    
def ECO(chain):
    if chain == "base":
        return "0x7000cae2c1016e7de45ec9b54f1835b966bca4f7"
    else:
        return "0x7000cae2c1016e7de45ec9b54f1835b966bca4f7"
    
def LIQ(chain):
    if chain == "base":
        return "0x7000f8270b955377e047da8202ae3c408186b4f7"
    else:
        return "0x7000f8270b955377e047da8202ae3c408186b4f7"

def DEX(chain):
    if chain == "base":
        return "0x7000b3B5e4e126610A7b7d1Af2D2DE8685c7C4f7"
    else:
        return "0x7000b3B5e4e126610A7b7d1Af2D2DE8685c7C4f7"


def BORROW(chain):
    if chain == "base":
        return "0x7000D5d7707Bf86b317deC635e459E47b9aBD4F7"
    else:
        return "0x7000D5d7707Bf86b317deC635e459E47b9aBD4F7"
    
def MAGISTER(chain):
    if chain == "base":
        return "0x7dA0bb55E4097FC2d78a1822105057F36C5F360d"
    else:
        return "0x7dA0bb55E4097FC2d78a1822105057F36C5F360d"
    
PIONEER = "0x70000299ee8910ccacd97b1bb560e34f49c9e4f7"


# SMART CA

def BURNER(chain):
    if chain == "base":
        return "0x70008F0B06060A31515733DB6dCB515c64f3DeAd"
    else:
        return "0x70008F0B06060A31515733DB6dCB515c64f3DeAd"
    
def DEFAULT_TOKEN_LIST(chain):
    if chain  == "base":
        return "0x7deF192aDB727777c5f24c05018cfbaFDFaD805a"
    else:
        return "0x7deF192aDB727777c5f24c05018cfbaFDFaD805a"

def DISCOUNT_ROUTER(chain):
    if chain == "base":
        return "0x7de8dd6146aa8b4a2ed8343aa83bc8874fb17000"
    else:
        return "0x7de8dd6146aa8b4a2ed8343aa83bc8874fb17000"

def ECO_SPLITTER(chain):
    if chain == "base":
        return "0x70001BA1BA4d85739E7B6A7C646B8aba5ed6c888"
    else:
        return "0x70001BA1BA4d85739E7B6A7C646B8aba5ed6c888"

def FACTORY(chain):
    return "0x8B76C05676D205563ffC1cbd11c0A6e3d83929c5"

def LENDING_DISCOUNT(chain):
    if chain == "base":
        return "0x74001e463b3c7dc95d96a1fdbe621678c24d47da"
    else:
        return "0x74001e463b3c7dc95d96a1fdbe621678c24d47da"

def LPOOL(chain, loan_id=None):
    if chain == "eth":
        if loan_id is not None and loan_id < 21:
            return "0x740015c39da5d148fca25a467399d00bce10c001"
        else:
            return "0x74001DcFf64643B76cE4919af4DcD83da6Fe1E02"
    else:
        return "0x740015c39da5d148fca25a467399d00bce10c001"

def LPOOL_RESERVE(chain):
    if chain == "base":
        return "0x7Ca54e9Aa3128bF15f764fa0f0f93e72b5267000"
    else:
        return "0x7Ca54e9Aa3128bF15f764fa0f0f93e72b5267000"
    

def ROUTER(chain):
    if chain == "base":
        return "0xC2defaD879dC426F5747F2A5b067De070928AA50"
    else:
        return "0x6b5422D584943BC8Cd0E10e239d624c6fE90fbB8"

def TIME_LOCK(chain):
    if chain == "base":
        return "0x7000F4Cddca46FB77196466C3833Be4E89ab810C"
    else:
        return "0x7000F4Cddca46FB77196466C3833Be4E89ab810C"
    
def TREASURY_SPLITTER(chain):
    if chain == "base" or chain == "eth":
        return "0x7000706E2727686eDF46cA0E42690F87b9de1999"
    else:
        return "0x70006B785AA87821331a974C3d5af81CdE5BB999"

def X7100_DISCOUNT(chain):
    if chain == "base":
        return "0x7100AAcC6047281b105201cb9e0DEcF9Ae5431DA"
    else:
        return "0x7100AAcC6047281b105201cb9e0DEcF9Ae5431DA"
    
def X7100_LIQ_HUB(chain):
    if chain == "base":
        return "0xA4437E62CD7E8E6199a0199deA7E78641f181825"
    else:
        return "0xA4437E62CD7E8E6199a0199deA7E78641f181825"
    
def X7DAO_DISCOUNT(chain):
    if chain == "base":
        return "0x7da05D75f51056f3B83b43F397668Cf6A5051cDa"
    else:
        return "0x7da05D75f51056f3B83b43F397668Cf6A5051cDa"
    
def X7DAO_LIQ_HUB(chain):
    if chain == "base":
        return "0x6913Bb5E6b85De1C47f0bc5C8ed3409d3aB14130"
    else:
        return "0x6913Bb5E6b85De1C47f0bc5C8ed3409d3aB14130"
    
def X7R_DISCOUNT(chain):
    if chain == "base":
        return "0x712bC6ddcd97A776B2482531058C629456B93eda"
    else:
        return "0x712bC6ddcd97A776B2482531058C629456B93eda"
    
def X7R_LIQ_HUB(chain):
    if chain == "base":
        return "0xDD53194e7Ea18402513b823fa5BE47be83352173"
    else:
        return "0xDD53194e7Ea18402513b823fa5BE47be83352173"

def XCHANGE_DISCOUNT(chain):
    if chain == "base":
        return "0x7de8ab0dd777561ce98b7ef413f6fd564e89c1da"
    else:
        return "0x7de8ab0dd777561ce98b7ef413f6fd564e89c1da"

def HUBS(chain):
    return {
    "x7r": X7R_LIQ_HUB(chain),
    "x7dao": X7DAO_LIQ_HUB(chain),
    "x7100": X7100_LIQ_HUB(chain),
}

def TEMP_HUBS(token):
    if token == "x7r":
        return "0x734B81d7De2b8D85eb71E5c7548f5f8D220a7782"
    if token == "x7dao":
        return "0xB06D584a30225A05583905C599a7A9990FEF062b"
    if token == "x7100":
        return "0x27a24a9a1Ee636E0C675964185e1f13545bA8605"


# LOANS

def ILL001(chain):
    if chain == "base":
        return "0x7400165E167479a3c81C8fC8CC3df3D2a92E9017"
    else:
        return "0x7400165E167479a3c81C8fC8CC3df3D2a92E9017"
    
def ILL003(chain):
    if chain == "base":
        return "0x74001C747B6cc9091EE63bC9424DfF633FBAc617"
    else:
        return "0x74001C747B6cc9091EE63bC9424DfF633FBAc617"
    
def ILL004(chain):
    if chain == "base":
        return "0xF9832C813104a6256771dfBDd3a243D24B7D7941"
    else:
        return "0xF9832C813104a6256771dfBDd3a243D24B7D7941"

def WETH(chain):
    if chain == "eth":
        return "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    if chain == "bsc":
        return "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
    if chain == "poly":
        return  "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270"
    if chain == "arb":
        return "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1"
    else:
        return "0x4200000000000000000000000000000000000006"


# MULTI SIGS

def DAO_MULTI(chain): 
    return "0x7dcb82DecBEb1f41BC9eb00a552B085ba356a256"

def COM_MULTI(chain): 
    return "0xc8804440275c0B60a081e832bb027DDaAE4A2daa"


# PAIRS

def X7R_PAIR(chain):
    return ["0x6139240a5907e4ce74673257c320ea366c521aea",
            "0x8e0d035787e7083d4292536005dd6a69682e4f64"]

def X7DAO_PAIR(chain):
    return "0x75311ee016c82e7770e4aca73a0d142f96ddb969"

def X7101_PAIR(chain):
    return "0x81b786ed4b2f1118e0fa0343ad4760e15448e3e8"

def X7102_PAIR(chain):
    return "0x49c838c60170c36e90cfa6021a57f2268dda3254"

def X7103_PAIR(chain):
    return "0xcecf54edc42c5c9f6ee10cb1efcc23e49f7d5a5d"

def X7104_PAIR(chain):
    return "0x7d0d7c088233cbc08ee2400b96d10bf24c40e93a"

def X7105_PAIR(chain):
    return "0x6d9d1b6b4d53f090639ae8d9e9c83b796da694ee"


# WALLETS
DEPLOYER = "0x7000a09c425abf5173ff458df1370c25d1c58105"

# OTHER
SUPPLY = 100000000
DEAD = "0x000000000000000000000000000000000000dEaD"


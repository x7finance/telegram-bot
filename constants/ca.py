# TOKEN CA

def X7R(chain):
    map = {
        "base": "0xEe6bA04895613b20a9B200e9EB25293576f8F1e4",
    }
    return map.get(chain, "0x70008F18Fc58928dcE982b0A69C2c21ff80Dca54")

def X7DAO(chain):
    map = {
        "base": "0xa30494c8bE9360a1Dd25108b7074628274b9fd6c",
    }
    return map.get(chain, "0x7105E64bF67ECA3Ae9b123F0e5Ca2b83b2eF2dA0")

def X7101(chain):
    map = {
        "base": "0x6b7B78552aCB26B161f39E5731B1A2ebc2436253",
    }
    return map.get(chain, "0x7101a9392eac53b01e7c07ca3baca945a56ee105")

def X7102(chain):
    map = {
        "base": "0xA4A002ee15Ed6fc6C9459e4789856dD20ffdfe62",
    }
    return map.get(chain, "0x7102dc82ef61bfb0410b1b1bf8ea74575bf0a105")

def X7103(chain):
    map = {
        "base": "0xfF3a265b30450b41BaCf1B2413792da4769C7003",
    }
    return map.get(chain, "0x7103eBdbF1f89be2d53EFF9B3CF996C9E775c105")

def X7104(chain):
    map = {
        "base": "0xEDFc68F09d4B6211ede5ee06acF9f560FC561F04",
    }
    return map.get(chain, "0x7104D1f179Cc9cc7fb5c79Be6Da846E3FBC4C105")

def X7105(chain):
    map = {
        "base": "0x941d37f4BCc92236ebE5aF46777b7E816d6d418A",
    }
    return map.get(chain, "0x7105FAA4a26eD1c67B8B2b41BEc98F06Ee21D105")
    
def X7100(chain):
    return [
        X7101(chain), 
        X7102(chain), 
        X7103(chain), 
        X7104(chain), 
        X7105(chain)
    ]

def X7D(chain):
    map = {
        "base": "0x446906ed090364EC7d1b16cA8Fb6D0fFC50854bD",
    }
    return map.get(chain, "0x7D000a1B9439740692F8942A296E1810955F5000")

# NFTS

def ECO(chain):
    map = {
        "base": "0xBc7A6859514D1874d2F14Af083F4e86DDd79fd32",
    }
    return map.get(chain, "0x7000cae2c1016e7de45ec9b54f1835b966bca4f7")

def LIQ(chain):
    map = {
        "base": "0xEe6bA04895613b20a9B200e9EB25293576f8F1e4",
    }
    return map.get(chain, "0x7000f8270b955377e047da8202ae3c408186b4f7")

def DEX(chain):
    map = {
        "base": "0x1AC7633C465f87A5620703eC27cf067588BDb095",
    }
    return map.get(chain, "0x7000b3B5e4e126610A7b7d1Af2D2DE8685c7C4f7")

def BORROW(chain):
    map = {
        "base": "0x7000D5d7707Bf86b317deC635e459E47b9aBD4F7",
    }
    return map.get(chain, "0xE1c7244Cc32980Db8dB191FD87731E091057Dc6F")

def MAGISTER(chain):
    map = {
        "base": "0x54E52e3Df66Ee56871c3c7672aD6F04889C11477",
    }
    return map.get(chain, "0x7dA0bb55E4097FC2d78a1822105057F36C5F360d")

PIONEER = "0x70000299ee8910ccacd97b1bb560e34f49c9e4f7"


# SMART CA

def BURNER(chain):
    map = {
        "eth": "0x70008F0B06060A31515733DB6dCB515c64f3DeAd",
        "base": "0xA649b52295b4DB30648e633504f1714337603DEa",
        "bsc": "0xA4fA641C8AB0a94Ad9CaAbaDcd43F91730b24676",
        "poly": "0x5c95C015b9E3B2deE4d2E4112cEa97F6209b489e",
        "arb": "0xA1A0744f4195F7058333A464a3Be90a771B22d98",
        "op": "0x1675ad54b0c41413b6e6c563b89E6b1C3c5b5796",
    }
    return map.get(chain)

def DEFAULT_TOKEN_LIST(chain):
    return "0x7deF192aDB727777c5f24c05018cfbaFDFaD805a"

def DISCOUNT_ROUTER(chain):
    return "0x7de8dd6146aa8b4a2ed8343aa83bc8874fb17000"

def ECO_SPLITTER(chain):
    map = {
        "eth": "0x70001BA1BA4d85739E7B6A7C646B8aba5ed6c888",
    }
    return map.get(chain, "0xA65DF22BC2ec986859B43D1803b75D48232f2902")

def FACTORY(chain):
    return "0x8B76C05676D205563ffC1cbd11c0A6e3d83929c5"

def LENDING_DISCOUNT(chain):
    map = {
        "eth": "0x74001e463B3c7dC95D96a1FDBE621678C24D47Da",
        "base": "0x758808B831E3f58c040c1D4A179EFFc9f2e31E0C",
        "bsc": "0x87A53C0d9691c742C819189B86E444A4236b91B",
        "poly": "0xBeaCd59B75224c07fca41bC6F36c76Cce3E7D1FF",
        "arb": "0x45A529953014E38aF4e38Bbc173d256433A3Ac94",
        "op": "0x758808B831E3f58c040c1D4A179EFFc9f2e31E0C",
    }
    return map.get(chain)

def LIQUIDITY_TREASURY(chain):
    map = {
        "arb": "0xA9570aDDC58A86C44A50401c03d40418BAe76F5B",
        "bsc": "0x303e92d44B17a75Ae06c7F624e0c8EE6Ab596172",
        "base": "0xc6726216f8f77Ac17ACc0B2Fb28310B5F283241e",
        "eth": "0xDDC2DeC8ce4Ab39dB581FC441403b3e3288eB637",
        "op": "0x32391B59107Af19944CA630Cb50E2e80B3E443BF",
        "poly": "0xa413f4d546321407D4e809d681094be31d4a70d2"
    }
    return map.get(chain) 

def LPOOL(chain, loan_id=None):
    eth_map = {
        True: "0x740015c39da5d148fca25a467399d00bce10c001",
        False: "0x74001DcFf64643B76cE4919af4DcD83da6Fe1E02"
    }
    map = {
        "eth": lambda loan_id: eth_map[loan_id is not None and loan_id < 21],
        "base": "0x4eE199B7DFED6B96402623BdEcf2B1ae2f3750Dd",
        "bsc": "0x6396898c25b2bbF824DcdEc99A6F4061CC12f573",
        "poly": "0xF57C56270E9FbF18B254E05168C632c9f3D9a442",
        "arb": "0x7F3F8bcF93e17734AEec765128156690e8c7e8d3",
        "op": "0x94ada63c4B836AbBA14D2a20624bDF39b9DD5Ed5"
    }
    if chain == "eth":
        return map["eth"](loan_id)
    return map.get(chain)

def LPOOL_RESERVE(chain):
    map = {
        "eth": "0x7Ca54e9Aa3128bF15f764fa0f0f93e72b5267000",
        "base": "0x1C17a7E472CDded644b1a9bC2dd52304d6215Af3",
        "bsc": "0x3dE169E39A91519C16497C60510d7AE1ddf443B",
        "poly": "0x6e77E844CDac13698d06a00a9Ddb0465c5a78429",
        "arb": "0xB9a7346CeFc95aE5C4105c31453824A737Cd2760",
        "op": "0xb71016b5BdbbAB0f8d1A50e66B6a757D1Dcd1Db2"
    }
    return map.get(chain)

def ROUTER(chain):
    map = {
        "arb": "0x7C79C9483Ee518783b31C78920f73D0fDeabe246",
        "bsc": "0x32e9eDEaBd5A8034468497A4782b1a9EB95C4A67",
        "base": "0xC2defaD879dC426F5747F2A5b067De070928AA50",
        "eth": "0x6b5422D584943BC8Cd0E10e239d624c6fE90fbB8",
        "op": "0x2A382e8eB22Ecb02dD67C30243A4D0A01474b042",
        "poly": "0xA72618ff64468Dff871e980fB657dE3Ca5Ae0aba"
    }
    return map.get(chain) 

def TIME_LOCK(chain):
    map = {
        "eth": "0x7000F4Cddca46FB77196466C3833Be4E89ab810C",
        "bsc": "0x8135bDc81185969A4F7eCf2F65d737C6e119C5f4",
        "poly": "0xf748Fc84EEe0caa845eDF0C56781f77161D10Ae2",
        "arb": "0x029D9B5bC816638864402dACdFe5540488D3c3Fe",
        "op": "0xeB108169a1962874A02bbBBAE8F123C97EA297dA",
        "base": "0xeB108169a1962874A02bbBBAE8F123C97EA297dA"
    }
    return map.get(chain)
    
def TREASURY_SPLITTER(chain):
    map = {
        "eth": "0x7000706E2727686eDF46cA0E42690F87b9de1999",
        "base": "0x75cb47A14BFEb7EFB7fD616904935E44F19580BE",
        "bsc": "0x9f94e2A7b4AE351eb6A9d1c09E8d005b8d94C08",
        "poly": "0x6767095743cfED43B7B758BCc022FeaBBb7BcEBa",
        "arb": "0x9f168f2e3CB2F94031A8aec5bBfb37a2928b4c86",
        "op": "0x75cb47A14BFEb7EFB7fD616904935E44F19580BE"
    }
    return map.get(chain)

def X7100_DISCOUNT(chain):
    map = {
        "eth": "0x7100AAcC6047281b105201cb9e0DEcF9Ae5431DA",
    }
    return map.get(chain, "0x383f768222818aE9C391600913DD8Ab309254F39")
    
def X7100_LIQ_HUB(chain):
    map = {
        "eth": "0xA4437E62CD7E8E6199a0199deA7E78641f181825",
        "bsc": "0xA9fE3c1Fc5705044C33409B87486daf57f2630bf",
        "poly": "0x950c0685E6eAf16Fb7643a3EAB7EE57a91DB8cc3",
        "arb": "0x84f864Bf33607fD42663db4823D8f30093711b37",
        "op": "0x62c72ce2B7ec919888238C8d866227b726ea2CEA",
        "base": "0xa6433641803102AC2be4fff17C339762d9C9C2E0"
    }
    return map.get(chain)

def X7DAO_DISCOUNT(chain):
    map = {
        "eth": "0x7da05D75f51056f3B83b43F397668Cf6A5051cDa",
    }
    return map.get(chain, "0x864C53A08A99DaDc219b309Aa867c45D222d0938")

def X7DAO_LIQ_HUB(chain):
    map = {
        "eth": "0x6913Bb5E6b85De1C47f0bc5C8ed3409d3aB14130",
        "base": "0x005eB898b4557aFf72ef4c28934AdDba19c12b0b",
        "bsc": "0xE2E8a085025Eaf7130111aD82c18799f047d7278",
        "poly": "0x0Bf5f8B61360b2abff48547C4558f50389cf0221",
        "arb": "0x22B31DC2D1cD37788202a4b9AbFfd17b56b186aa"
    }
    return map.get(chain)
    
def X7R_DISCOUNT(chain):
    map = {
        "eth": "0x712bC6ddcd97A776B2482531058C629456B93eda",
    }
    return map.get(chain, "0xdd2cD5fe4248FD5656d3240EB7FdbD5c9930a686")

def X7R_LIQ_HUB(chain):
    map = {
        "eth": "0xDD53194e7Ea18402513b823fa5BE47be83352173",
        "base": "0x34AeB703bf00Bf6033231bf964a7714f0f9A215C",
        "bsc": "0x4B0d2d38f080f94634Bfe42B405A623a419389EF",
        "poly": "0xBa7a7956716F32DF5F958A895Ba860f41889D828",
        "arb": "0xeC6a8dE27138D686D96A60F2E9B7ccB5bA53C94C",
        "op": "0xFAa2B600c430d01dEB94D8955Ad02F100E2066D4"
    }
    return map.get(chain)

def XCHANGE_DISCOUNT(chain):
    map = {
        "eth": "0x6377c6219c7Ab053F17cA9E3D823e63473e669A2",
        "base": "0x6fD8d2a09a090A69d05b0d21a3c187de6a9A57E7",
        "bsc": "0x75163692e0081d20C965c45fBb027A01694431bB",
        "poly": "0x976Cc8346085e06896D37B6dCA01cD08535F37EB",
        "arb": "0xC5f73c308a35606B700746113AaCF5FFd175a3c0",
        "op": "0x6fD8d2a09a090A69d05b0d21a3c187de6a9A57E7"
    }
    return map.get(chain)

def HUBS(chain):
    return {
        "x7r": X7R_LIQ_HUB(chain),
        "x7dao": X7DAO_LIQ_HUB(chain),
        **{f"x710{i}": X7100_LIQ_HUB(chain) for i in range(6)},
    }

def TEMP_HUBS(token):
    map = {
        "x7r": "0x734B81d7De2b8D85eb71E5c7548f5f8D220a7782",
        "x7dao": "0xB06D584a30225A05583905C599a7A9990FEF062b",
        "x7100": "0x27a24a9a1Ee636E0C675964185e1f13545bA8605",
    }
    return map.get(token)


# PAIRS

def X7R_PAIR(chain):
    return ["0x6139240A5907e4CE74673257c320ea366c521AEA",
            "0x8e0D035787e7083D4292536005dD6A69682e4f64"]

def X7DAO_PAIR(chain):
    return ["0x75311ee016c82e7770E4ACa73a0d142f96ddB969",
            "0xb8dE6270640092463988B6860d68CA63dC7cF700"]

def X7101_PAIR(chain):
    return "0xb8dE6270640092463988B6860d68CA63dC7cF700"

def X7102_PAIR(chain):
    return "0x49C838c60170C36E90CFA6021a57f2268dda3254"

def X7103_PAIR(chain):
    return "0xcecf54EDC42c5C9f6Ee10cb1eFcc23E49F7D5A5d"

def X7104_PAIR(chain):
    return "0x7d0D7c088233cBC08ee2400B96D10BF24C40E93a"

def X7105_PAIR(chain):
    return "0x6d9D1B6B4D53f090639ae8D9E9C83B796Da694eE"


# WALLETS

def DAO_MULTI(chain): 
    return "0x7dcb82DecBEb1f41BC9eb00a552B085ba356a256"

def COM_MULTI(chain): 
    return "0x7063E83dF5349833A21f744398fD39D42fbC00f8"

DEPLOYER = "0x7000a09c425abf5173ff458df1370c25d1c58105"


# OTHER

def WETH(chain):
    map = {
        "arb": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
        "bsc": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
        "eth": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "poly": "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270"
    }
    return map.get(chain, "0x4200000000000000000000000000000000000006")


ILL_ADDRESSES = {
    "eth": {
        "004": "0x3c0E49D9b72FdDAeF36e2962368b073Bc5A76481",
        "005": "0x90482AD3aa56675ba313dAC14C3a7717bAD5B24D"
    },
    "base": {
        "004": "0x3c0E49D9b72FdDAeF36e2962368b073Bc5A76481",
        "005": "0x90482AD3aa56675ba313dAC14C3a7717bAD5B24D"
    },
    "arb": {
        "005": "0x90482AD3aa56675ba313dAC14C3a7717bAD5B24D"
    },
    "bsc": {
        "005": "0x90482AD3aa56675ba313dAC14C3a7717bAD5B24D"
    },
    "op": {
        "005": "0x90482AD3aa56675ba313dAC14C3a7717bAD5B24D"
    },
    "poly": {
        "005": "0x90482AD3aa56675ba313dAC14C3a7717bAD5B24D"
    }
}


SUPPLY = 100000000
DEAD = "0x000000000000000000000000000000000000dEaD"

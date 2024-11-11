from telegram import *
from telegram.ext import *

import asyncio, math, pytz, random, re, requests, time
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont
from constants import abis, ca, chains, dao, nfts, settings, splitters, tax, text, tokens, urls  
from hooks import api, db, dune 
import pricebot
import media

bitquery = api.BitQuery()
coingecko = api.CoinGecko()
dextools = api.Dextools()
opensea = api.Opensea()
warpcast = api.WarpcastApi()
etherscan = api.Etherscan()


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        text.ABOUT,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text="X7Finance.org", url=f"{urls.XCHANGE}")],
            ]
        ),
    )


async def admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    administrators = await context.bot.get_chat_administrators(urls.TG_MAIN_CHANNEL_ID)
    team = [
        f"@{admin.user.username}" 
        for admin in administrators 
        if admin.custom_title and 'x7' in admin.custom_title.lower() and admin.user.username
    ]
    team.sort(key=lambda username: username.lower())
    
    await update.message.reply_photo(
            photo=api.get_random_pioneer(),
            caption=
                "*X7 Finance Telegram Admins*\n\n"
                + "\n".join(team),
            parse_mode="Markdown",
        )


async def alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=f"\n",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text="XChange Alerts", url=f"{urls.TG_ALERTS}")],
            ]
        ),
    )


async def announcements(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption="\n",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="X7 Announcement Channel",
                        url="https://t.me/X7announcements",
                    )
                ],
            ]
        ),
    )


async def blocks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    when = round(time.time())
    try:
        blocks = {chain: etherscan.get_block(chain, when) for chain in chains.CHAINS}
    except Exception:
        blocks = 0
    blocks_text = "\n".join([f"{block_type.upper()}: `{block}`" for block_type, block in blocks.items()])
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            f"*Latest Blocks*\n\n"
            f"{blocks_text}",
        parse_mode="Markdown"
    )


async def blog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=f"\n",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="X7 Finance Blog", url=f"{urls.XCHANGE}blog"
                    )
                ],
            ]
        ),
    )


async def borrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) >=  1:
        await context.bot.send_chat_action(update.effective_chat.id, "typing")
        amount = context.args[0]
        amount_in_wei = int(float(amount) * 10 ** 18)
        chain = chains.get_chain(update.effective_message.message_thread_id) if len(context.args) < 2 else context.args[1]
    else:
        await update.message.reply_photo(
            photo=api.get_random_pioneer(),
            caption=
                f"*X7 Finance Loan Rates*\n\n"
                "Follow the /borrow command with an amount to borrow",
            parse_mode="Markdown"
            )
        return
    chain_info, error_message = chains.get_info(chain)
    if error_message:
        await update.message.reply_text(error_message)
        return

    message = await update.message.reply_text("Getting Loan Rates Info, Please wait...")

    loan_info = ""
    native_price = etherscan.get_native_price(chain)
    borrow_usd = native_price * float(amount)
    lending_pool = chain_info.w3.eth.contract(
            address=chain_info.w3.to_checksum_address(ca.LPOOL(chain)), abi=abis.read("lendingpool")
        )
    active_terms_count = lending_pool.functions.countOfActiveLoanTerms().call()
    liquidation_fee = lending_pool.functions.liquidationReward().call() / 10 ** 18
    liquidation_dollar = liquidation_fee * native_price
    active_loan_addresses = []

    for i in range(active_terms_count):
        loan_address = lending_pool.functions.activeLoanTerms(i).call()
        active_loan_addresses.append(loan_address)

    if not active_loan_addresses:
        loan_info = "N/A\n\n"
    else:
        for loan_term in active_loan_addresses:
            loan_contract = chain_info.w3.eth.contract(
                address=chain_info.w3.to_checksum_address(loan_term), abi=etherscan.get_abi(loan_term, chain)
            )
            
            loan_name = loan_contract.functions.name().call()
            loan_data = loan_contract.functions.getQuote(int(amount_in_wei)).call()
            
            min_loan = loan_contract.functions.minimumLoanAmount().call()
            max_loan = loan_contract.functions.maximumLoanAmount().call()
            min_loan_duration = loan_contract.functions.minimumLoanLengthSeconds().call()
            max_loan_duration = loan_contract.functions.maximumLoanLengthSeconds().call()
            
            premium_periods = loan_contract.functions.numberOfPremiumPeriods().call()
            origination_fee, total_premium = [value / 10**18 for value in loan_data[1:]]
            origination_dollar, total_premium_dollar = [value * native_price for value in [origination_fee, total_premium]]
            
            loan_info += (
                f"*{loan_name}*\n"
                f"Origination Fee: {origination_fee} {chain_info.native.upper()} (${origination_dollar:,.0f})\n"
            )

            if premium_periods > 0:
                per_period_premium = total_premium / premium_periods
                per_period_premium_dollar = total_premium_dollar / premium_periods

                loan_info += f"Premium Fees: {total_premium} {chain_info.native.upper()} (${total_premium_dollar:,.0f}) over {premium_periods} payments:\n"
                for period in range(1, premium_periods + 1):
                    loan_info += f"  - Payment {period}: {per_period_premium:.4f} {chain_info.native.upper()} (${per_period_premium_dollar:,.2f})\n"
            else:
                loan_info += f"Premium Fees: {total_premium} {chain_info.native.upper()} (${total_premium_dollar:,.0f})\n"

            loan_info += (
                f"Loan Cost: {total_premium + origination_fee} {chain_info.native.upper()} (${origination_dollar + total_premium_dollar:,.0f})\n"
                f"Min Loan: {min_loan / 10 ** 18} {chain_info.native.upper()}\n"
                f"Max Loan: {max_loan / 10 ** 18} {chain_info.native.upper()}\n"
                f"Min Loan Duration: {math.floor(min_loan_duration / 84600)} days\n"
                f"Max Loan Duration: {math.floor(max_loan_duration / 84600)} days \n\n"
            )

    await message.delete()
    await update.message.reply_text(
        f"*X7 Finance Loan Rates ({chain_info.name})*\n\n"
        f"Borrowing {amount} {chain_info.native.upper()} (${borrow_usd:,.0f}) will cost:\n\n"
        f"{loan_info}"
        f"Principal Repayment Condition:\nPrincipal must be returned by the end of the loan term.\n\n"
        f"Liquidation Deposit: {liquidation_fee} {chain_info.native.upper()} (${liquidation_dollar:,.0f})\n"
        f"Failure to make a premium payment by its due date or repay the principal by the end of the loan term will result in loan liquidation, and the deposit will be forfeited.",
        parse_mode="Markdown"
    )


async def burn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(update.effective_message.message_thread_id)
    chain_info, error_message = chains.get_info(chain, token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return

    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    burn = etherscan.get_token_balance(ca.DEAD, ca.X7R(chain), chain)
    percent = round(burn / ca.SUPPLY * 100, 2)
    price,_ = dextools.get_price(ca.X7R(chain), "eth")
    burn_dollar = float(price) * float(burn)
    native = burn_dollar / etherscan.get_native_price(chain)
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            f"*X7R Tokens Burned ({chain_info.name})*\n\n"
            f'{"{:0,.0f}".format(float(burn))} / {native:,.3f} {chain_info.native.upper()} (${"{:0,.0f}".format(float(burn_dollar))})\n'
            f"{percent}% of Supply",
        parse_mode="markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Burn Wallet",
                        url=f"{chain_info.scan_token}{ca.X7R(chain)}?a={ca.DEAD}",
                    )
                ],
            ]
        ),
    )


async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(update.effective_message.message_thread_id)
    chain_info, error_message = chains.get_info(chain, token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return
    
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            f"*X7 Finance Buy Links ({chain_info.name})*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="X7R - Rewards Token", url=f"{urls.XCHANGE_BUY(chain_info.id, ca.X7R(chain))}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="X7DAO - Governance Token", url=f"{urls.XCHANGE_BUY(chain_info.id, ca.X7DAO(chain))}"
                    )
                ],
            ]
        ),
    )


async def channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [
            InlineKeyboardButton(
                text="X7 Portal", url=f"{urls.TG_PORTAL}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Xchange Alerts", url=f"{urls.TG_ALERTS}"
            ),
        ],
        [
            InlineKeyboardButton(
                text="DAO Chat", url=f"{urls.TG_DAO}",
            ),
        ],

        [
            InlineKeyboardButton(
                text="Xchange Create Bot", url=f"{urls.TG_XCHANGE_CREATE}")
        ],
    ]
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=f"\n",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def chart(update: Update, context: ContextTypes.DEFAULT_TYPE = None):
    chain = " ".join(context.args).lower() or chains.get_chain(update.effective_message.message_thread_id)
    chain_info, error_message = chains.get_info(chain, token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return
    
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            f"*X7 Finance Chart Links ({chain_info.name})*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="X7R - Rewards Token", url=f"https://www.dextools.io/app/{chain_info.dext}/pair-explorer/{ca.X7R(chain)}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="X7DAO - Governance Token",
                        url=f"https://www.dextools.io/app/{chain_info.dext}/pair-explorer/{ca.X7DAO(chain)}",
                    )
                ],
            ]
        ),
    )


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    first = context.args[0]
    second = context.args[1]
    if first == second:
        reply = "✅ Both inputs match"
    else:
        reply = f"❌ Inputs do not match"
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            f"*X7 Finance Input Checker*\n\n"
            f"First:\n{first}\n\n"
            f"Second:\n{second}\n\n"
            f"{reply}",
        parse_mode="Markdown")


async def compare(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(update.effective_message.message_thread_id)
    chain_info, error_message = chains.get_info(chain, token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return
    
    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    
    try:
        token_names = {
            "x7r": {"contract": ca.X7R(chain), "image": media.X7R_LOGO},
            "x7dao": {"contract": ca.X7DAO(chain), "image": media.X7DAO_LOGO},
            "x7101": {"contract": ca.X7101(chain), "image": media.X7101_LOGO},
            "x7102": {"contract": ca.X7102(chain), "image": media.X7102_LOGO},
            "x7103": {"symbol": ca.X7103(chain), "image": media.X7103_LOGO},
            "x7104": {"contract": ca.X7104(chain), "image": media.X7104_LOGO},
            "x7105": {"contract": ca.X7105(chain), "image": media.X7105_LOGO},
        }

        x7token = context.args[0].lower()
        if x7token not in token_names:
            await update.message.reply_photo(
                photo=api.get_random_pioneer(),
                caption=
                    f"*X7 Finance Market Cap Comparison*\n\n"
                    f"Please enter X7 token first followed by token to compare\n\n"
                    f"ie. `/compare x7r uni`",
                parse_mode="Markdown",
            )
            return
        
        token2 = context.args[1].lower()
        search = coingecko.search(token2)
        if "coins" in search and search["coins"]:
            token_id = search["coins"][0]["api_symbol"]

        token_market_cap = coingecko.get_mcap(token_id)
        if x7token == ca.X7R(chain):
            x7_supply = etherscan.get_x7r_supply("eth")
        else:
            x7_supply = ca.SUPPLY
        token_info = token_names[x7token]
        x7_price,_ = dextools.get_price(token_info["contract"], "eth")
        x7_market_cap = float(x7_price) * float(x7_supply)
        percent = ((token_market_cap - x7_market_cap) / x7_market_cap) * 100
        x = (token_market_cap - x7_market_cap) / x7_market_cap
        token_value = token_market_cap / x7_supply
        await update.message.reply_photo(
            photo=api.get_random_pioneer(),
            caption=
                f"*X7 Finance Market Cap Comparison*\n\n"
                f"{context.args[1].upper()} Market Cap:\n"
                f'${"{:,.0f}".format(token_market_cap)}\n\n'
                f'Token value of {context.args[0].upper()} at {context.args[1].upper()} Market Cap:\n'
                f'${"{:,.2f}".format(token_value)}\n'
                f'{"{:,.0f}%".format(percent)}\n'
                f'{"{:,.0f}x".format(x)}',
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=f"{context.args[1].upper()} Chart",
                            url=f"https://www.coingecko.com/en/coins/{token_id}",
                        )
                    ],
                ]
            ),
        )
    except Exception:
        await update.message.reply_photo(
                photo=api.get_random_pioneer(),
                caption=
                    f"*X7 Finance Market Cap Comparison*\n\n"
                    f"Comparison not avaliable",
                parse_mode="Markdown",
            )


async def constellations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(update.effective_message.message_thread_id)
    chain_info, error_message = chains.get_info(chain, token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return
    
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            f'*X7 Finance Constellation Addresses ({chain_info.name})*\n\n'
            f'X7101\n'
            f'`{ca.X7101(chain)}`\n\n'
            f'X7102:\n'
            f'`{ca.X7101(chain)}`\n\n'
            f'X7103\n'
            f'`{ca.X7103(chain)}`\n\n'
            f'X7104\n'
            f'`{ca.X7104(chain)}`\n\n'
            f'X7105\n'
            f'`{ca.X7105(chain)}`',
        parse_mode="Markdown")


async def contracts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(update.effective_message.message_thread_id)
    chain_info, error_message = chains.get_info(chain)
    if error_message:
        await update.message.reply_text(error_message)
        return
    
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            f"*X7 Finance Contract Addresses ({chain_info.name})*\n\n"
            f"*X7R - Rewards Token *\n`{ca.X7R(chain)}`\n\n"
            f"*X7DAO - Governance Token*\n`{ca.X7DAO(chain)}`\n\n"
            f"For advanced trading and arbitrage opportunities see `/constellations`",
        parse_mode="Markdown",
    )


async def contribute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=text.CONTRIBUTE,
        parse_mode="Markdown"  
    )


async def convert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) >= 2:
        await context.bot.send_chat_action(update.effective_chat.id, "typing")
        amount_raw = context.args[0]
        amount = amount_raw.replace(',', '')
        token = context.args[1]
        chain = chains.get_chain(update.effective_message.message_thread_id) if len(context.args) < 3 else context.args[2]

        if not amount.isdigit():
            await context.bot.send_message(update.effective_chat.id, "Please provide a valid amount")
            return
    else:
        await context.bot.send_message(update.effective_chat.id, "Please provide the amount and X7 token name")
        return

    chain_info, error_message = chains.get_info(chain, token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return
    if token.upper() in tokens.TOKENS:
        token_info = tokens.TOKENS[token.upper()].get(chain)
        address = token_info.ca
        price, _ = dextools.get_price(address, chain)
            
            
    elif token.upper() == "X7D":
        token_info = chains.CHAINS[chain]
        price = etherscan.get_native_price(chain)
    else:
        await update.message.reply_text("Token not found, please use X7 tokens only")
        return

    value = float(price) * float(amount)
    output = '{:0,.0f}'.format(value)
    
    amount_str = float(amount)

    caption = (f"*X7 Finance Price Conversion ({token_info.name.upper()})*\n\n"
            f"{amount_str:,.0f} {token.upper()}  is currently worth:\n\n${output}\n\n")
    
    if amount == "500000" and token.upper() == "X7DAO":
        caption+= "Holding 500,000 X7DAO tokens earns you the right to make X7DAO proposals\n\n"
        
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=caption,
        parse_mode="Markdown")


async def dao_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(update.effective_message.message_thread_id)
    chain_info, error_message = chains.get_info(chain, token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return
    
    buttons = []
    input_contract = " ".join(context.args).lower()
    contract_names = list(dao.contract_mappings(chain))
    formatted_contract_names = '\n'.join(contract_names)
    keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Vote Here",url=urls.SNAPSHOT,)],
            [InlineKeyboardButton(text="DAO Chat",url=urls.TG_DAO,)],])
    if not input_contract:
        snapshot = api.get_snapshot()
        proposal = snapshot["data"]["proposals"][0]
        end = datetime.fromtimestamp(proposal["end"])
        duration = end - datetime.now()
        days, hours, minutes = api.get_duration_days(duration)
        if proposal["state"] == "active":
            end_status = f'Vote Closing: {end.strftime("%Y-%m-%d %H:%M:%S")} UTC\n{days} days, {hours} hours and {minutes} minutes\n\n'
            header = 'Current Open Proposal'
            buttons.extend([
            [InlineKeyboardButton(
                text="Vote Here",
                url=f"{urls.SNAPSHOT}/proposal/{proposal['id']}")
            ],
            [InlineKeyboardButton(
                    text="DAO Chat",
                    url=f"{urls.TG_DAO}")
            ]
            ])
        else:
            end_status = f'Vote Closed: {end.strftime("%Y-%m-%d %H:%M:%S")}'
            header = 'No Current Open Proposal\n\nLast Proposal:'
            buttons.extend([
            [InlineKeyboardButton(
                text="X7 Finance DAO",
                url=f"{urls.SNAPSHOT}")
            ],
            [InlineKeyboardButton(
                text="DAO Chat",
                url=f"{urls.TG_DAO}")
            ]
            ])

        choices_text = "\n".join(
            f'{choice} - {"{:0,.0f}".format(score)} Votes'
            for choice, score in zip(proposal["choices"], proposal["scores"])
        )
        
        await update.message.reply_photo(
            photo=api.get_random_pioneer(),
            caption=
                f'*X7 Finance DAO*\n'
                f'use `/dao functions` for a list of call callable contracts\n\n'
                f'*{header}*\n\n'
                f'{proposal["title"]} by - '
                f'{proposal["author"][-5:]}\n\n'
                f'{choices_text}\n\n'
                f'{"{:0,.0f}".format(proposal["scores_total"])} Total Votes\n\n'
                f'{end_status}',
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return
    else:
        if input_contract == "functions":
            await update.message.reply_photo(
                photo=api.get_random_pioneer(),
                caption=
                    f"*X7 Finance DAO*\n\nUse `/dao [contract-name]` for a list of DAO callable functions\n\n"
                    f"*Contract Names:*\n\n{formatted_contract_names}\n\n",
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        else:
            matching_contract = None
            for contract in dao.contract_mappings(chain).keys():
                if contract.lower() == input_contract:
                    matching_contract = contract
                    break
            if matching_contract:
                contract_text, contract_ca = dao.contract_mappings(chain)[matching_contract]
                await update.message.reply_photo(
                    photo=api.get_random_pioneer(),
                    caption=
                        f"*X7 Finance DAO Functions* - {matching_contract}\n\n"
                        f"The following functions can be called on the {matching_contract} contract:\n\n"
                        f"{contract_text}",
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
            else:
                await update.message.reply_photo(
                    photo=api.get_random_pioneer(),
                    caption=
                        f"*X7 Finance DAO Functions*\n\n"
                        f"'{input_contract}' not found - Use `/dao` followed by one of the contract names below:\n\n"
                        f"{formatted_contract_names}",
                    parse_mode="Markdown"
                )


async def onchains(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            "*X7 Finance Onchain Messages*\n\n"
            'The stealth launch story of X7 Finance was heralded as an '
            '"incredible way to launch a project in this day and age."\n\n'
            "The on-chain, decentralized communications from X7's global collective "
            'of developers to the community provide chronological evidence on how the '
            'X7 community and ecosystem was born - and how the foundation was built.',
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="View all on chain messages",
                        url=f"{urls.XCHANGE}docs/onchains",
                    )
                ],
            ]
        ),
    )


async def docs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [
            InlineKeyboardButton(text="Get Started", url=f"{urls.XCHANGE}getstarted/"),
            InlineKeyboardButton(text="Trader", url=f"{urls.XCHANGE}docs/guides/trade/"),
        ],
        [
            InlineKeyboardButton(text="Liquidity Provider", url=f"{urls.XCHANGE}docs/guides/liquidity-provider/"),
            InlineKeyboardButton(text="Capital Allocator", url=f"{urls.XCHANGE}docs/guides/lending/"),
        ],
        [
            InlineKeyboardButton(text="Project Engineer", url=f"{urls.XCHANGE}docs/guides/integrate-ui/"),
            InlineKeyboardButton(text="Project Launcher", url=f"{urls.XCHANGE}docs/guides/launch/"),

        ],
    ]

    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=f"\n",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def ecosystem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"{text.ECOSYSTEM}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text="X7Finance.org", url=f"{urls.XCHANGE}")],
            ]
        ),
    )


async def factory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = []
    for chain in chains.CHAINS:
        buttons_row = []
        name = chains.CHAINS[chain].name
        address = chains.CHAINS[chain].scan_address
        buttons_row.append(
                InlineKeyboardButton(
                    text=name,
                    url=f"{address}{ca.FACTORY(chain)}"
                )
            )
        buttons.append(buttons_row)

    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=f"\n",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [
            InlineKeyboardButton(
                text="Airdrop Questions",
                url=f"{urls.XCHANGE}docs/faq/airdrop",
            ),
            InlineKeyboardButton(
                text="Constellation Tokens",
                url=f"{urls.XCHANGE}docs/faq/constellations",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Developer Questions",
                url=f"{urls.XCHANGE}docs/faq/devs",
            ),
            InlineKeyboardButton(
                text="General Questions",
                url=f"{urls.XCHANGE}docs/faq/general",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Governance Questions",
                url=f"{urls.XCHANGE}docs/faq/governance",
            ),
            InlineKeyboardButton(
                text="Investor Questions",
                url=f"{urls.XCHANGE}faq/investors",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Liquidity Lending Questions",
                url=f"{urls.XCHANGE}docs/faq/liquiditylending",
            ),
            InlineKeyboardButton(
                text="NFT Questions",
                url=f"{urls.XCHANGE}faq/nfts"
            ),
        ],
        [
            InlineKeyboardButton(
                text="Snapshot.org Questions",
                url=f"{urls.XCHANGE}docs/faq/daosnapshot",
            ),
            InlineKeyboardButton(
                text="Xchange Questions",
                url=f"{urls.XCHANGE}faq/xchange",
            ),
        ],
    ]

    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=f"\n",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def gas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(update.effective_message.message_thread_id)
    chain_info, error_message = chains.get_info(chain)
    if error_message:
        await update.message.reply_text(error_message)
        return

    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    try:
        gas_data = etherscan.get_gas(chain)
        gas_text = (
            f"Gas:\n"
            f'Low: {float(gas_data["result"]["SafeGasPrice"]):.0f} Gwei\n'
            f'Average: {float(gas_data["result"]["ProposeGasPrice"]):.0f} Gwei\n'
             f'High: {float(gas_data["result"]["FastGasPrice"]):.0f} Gwei\n\n'
             )
    except Exception:
        gas_text = ""
    
    gas_price = chain_info.w3.eth.gas_price / 10**9
    eth_price = etherscan.get_native_price(chain)

    swap_cost_in_eth = gas_price * tax.SWAP_GAS
    swap_cost_in_dollars = (swap_cost_in_eth / 10**9)* eth_price
    swap_text = f"Swap: {swap_cost_in_eth / 10**9:.4f} {chain_info.native.upper()} (${swap_cost_in_dollars:.2f})"
    
    try:
        pair_data = "0xc9c65396" + ca.WETH(chain)[2:].lower().rjust(64, '0') + ca.DEAD[2:].lower().rjust(64, '0')
        pair_gas_estimate = chain_info.w3.eth.estimate_gas({
            'from': chain_info.w3.to_checksum_address(ca.DEPLOYER),
            'to': chain_info.w3.to_checksum_address(ca.FACTORY(chain)),
            'data': pair_data,})
        pair_cost_in_eth = gas_price * pair_gas_estimate
        pair_cost_in_dollars = (pair_cost_in_eth / 10**9)* eth_price
        pair_text = f"Create Pair: {pair_cost_in_eth / 10**9:.2f} {chain_info.native.upper()} (${pair_cost_in_dollars:.2f})"
    except Exception:
        pair_text = "Create Pair: N/A"

    try:
        split_gas = chain_info.w3.eth.estimate_gas({
            'from': chain_info.w3.to_checksum_address(ca.DEPLOYER),
            'to': chain_info.w3.to_checksum_address(ca.TREASURY_SPLITTER(chain)),
            'data': "0x11ec9d34"})
        split_eth = gas_price * split_gas
        split_dollars = (split_eth / 10**9)* eth_price
        split_text = f"Splitter Push: {split_eth / 10**9:.4f} {chain_info.native.upper()} (${split_dollars:.2f})"
    except Exception:
        split_text = "Splitter Push: N/A"

    try:
        deposit_data = "0xf6326fb3"
        deposit_gas = chain_info.w3.eth.estimate_gas({
            'from': chain_info.w3.to_checksum_address(ca.DEPLOYER),
            'to': chain_info.w3.to_checksum_address(ca.LPOOL_RESERVE(chain)),
            'data': deposit_data,})
        deposit_eth = gas_price * deposit_gas
        deposit_dollars = (deposit_eth / 10**9)* eth_price
        deposit_text = f"Mint X7D: {deposit_eth / 10**9:.4f} {chain_info.native.upper()} (${deposit_dollars:.2f})"
    except Exception:
        deposit_text = "Mint X7D: N/A"

    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            f"*Live Xchange Gas Fees ({chain_info.name})*\n\n"
            f"{swap_text}\n"
            f"{pair_text}\n"
            f"{split_text}\n"
            f"{deposit_text}\n\n"
            f"{gas_text}",
        parse_mode="markdown",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=f"{chain_info.name} Gas Tracker", url=chain_info.scan_address)]]
        ),
    )


async def feeto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(update.effective_message.message_thread_id)
    chain_info, error_message = chains.get_info(chain)
    if error_message:
        await update.message.reply_text(error_message)
        return

    native_price = etherscan.get_native_price(chain)
    eth = etherscan.get_native_balance(ca.LIQUIDITY_TREASURY(chain), chain)
    weth = etherscan.get_token_balance(ca.LIQUIDITY_TREASURY(chain), ca.WETH(chain), chain)
    eth_dollar = (float(eth) + float(weth) * float(native_price))

    tx = etherscan.get_tx(ca.LIQUIDITY_TREASURY(chain), chain)
    tx_filter = [
        d for d in tx["result"]
        if ca.LIQUIDITY_TREASURY(chain).lower() in d["to"].lower() and
        any(fn in d.get("functionName", "").lower() for fn in ["breaklp", "breaklpandsendeth", "withdraweth"])
        ]
    recent_tx = max(tx_filter, key=lambda tx: int(tx["timeStamp"]), default=None)

    if recent_tx:
        time = datetime.fromtimestamp(int(recent_tx["timeStamp"]))
        now = datetime.now()
        duration = now - time
        days = duration.days
        hours, remainder = divmod(duration.seconds, 3600)
        minutes = (remainder % 3600) // 60
        recent_tx_text = (f"Last Liquidation: {time} UTC\n"
                        f"{days} days, {hours} hours and {minutes} minutes ago\n\n")
    else:
        recent_tx_text = 'Last Liquidation: Not Found'

    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            f"*Xchange Liquidity Treasury ({chain_info.name})*\n\n"
            f"{eth} (${eth_dollar})\n\n"
            f"{recent_tx_text}",
        parse_mode="markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=chain_info.scan_name,
                        url=f"{chain_info.scan_address}{ca.LIQUIDITY_TREASURY(chain)}",
                    )
                ],
            ]
        ),
    )


async def fg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fear_response = requests.get("https://api.alternative.me/fng/?limit=0")
    fear_data = fear_response.json()
    fear_values = []
    for i in range(7):
        timestamp = float(fear_data["data"][i]["timestamp"])
        localtime = datetime.fromtimestamp(timestamp)
        fear_values.append(
            (
                fear_data["data"][i]["value"],
                fear_data["data"][i]["value_classification"],
                localtime,
            )
        )
    duration_in_s = float(fear_data["data"][0]["time_until_update"])
    days = divmod(duration_in_s, 86400)
    hours = divmod(days[1], 3600)
    minutes = divmod(hours[1], 60)
    caption = "*Market Fear and Greed Index*\n\n"
    caption += f'{fear_values[0][0]} - {fear_values[0][1]} - {fear_values[0][2].strftime("%B %d")}\n\n'
    caption += "Change:\n"
    for i in range(1, 7):
        caption += f'{fear_values[i][0]} - {fear_values[i][1]} - {fear_values[i][2].strftime("%B %d")}\n'
    caption += "\nNext Update:\n"
    caption += (
        f"{int(hours[0])} hours and {int(minutes[0])} minutes"
    )
    await update.message.reply_photo(
        photo=f"https://alternative.me/crypto/fear-and-greed-index.png?timestamp={int(time.time())}",
        caption=caption,
        parse_mode="Markdown",
    )


async def holders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(update.effective_message.message_thread_id)
    chain_info, error_message = chains.get_info(chain, token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return
    
    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    if chain == "eth": 
        x7dao_proposers = bitquery.get_proposers(chain)
    else:
        x7dao_proposers = "N/A"
    x7dao_info = dextools.get_token_info(ca.X7DAO(chain), chain)
    x7dao_holders = x7dao_info["holders"]
    x7r_info = dextools.get_token_info(ca.X7R(chain), chain)
    x7r_holders = x7r_info["holders"]
    x7d_info = dextools.get_token_info(ca.X7D(chain), chain)
    x7d_holders = x7d_info["holders"]
    
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            f"*X7 Finance Token Holders ({chain_info.name})*\n\n"
            f"X7R:        {x7r_holders}\n"
            f"X7DAO:  {x7dao_holders}\n"
            f"X7DAO ≥ 500K: {x7dao_proposers}\n"
            f"X7D:        {x7d_holders}",
        parse_mode="Markdown",
    )


async def hub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not (1 <= len(context.args) <= 2):
        await update.message.reply_text("Please follow the command with token liquidity hub name")
        return

    token = context.args[0].lower()
    chain = context.args[1].lower() if len(context.args) == 2 else chains.get_chain(update.effective_message.message_thread_id)

    
    chain_info, error_message = chains.get_info(chain, token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return

    if token in ca.HUBS(chain):
        if token.startswith("x710") and token in {f"x710{i}" for i in range(1, 6)}:
            token = "x7100"
        hub_address = ca.HUBS(chain)[token]
    else:
        await update.message.reply_text("Please follow the command with X7 token name")
        return
    message = await update.message.reply_text("Getting Liquidity Hub data, Please wait...")
    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    try:
        (
            value,
            dollar,
            time,
            days,
            hours,
            minutes,
        ) = api.get_liquidity_hub_data(hub_address, chain)

        buy_back_text = (
            f'Last Buy Back: {time} UTC\n{value} {chain_info.native.upper()} (${"{:0,.0f}".format(dollar)})\n'
            f"{days} days, {hours} hours and {minutes} minutes ago"
        )
    except Exception:
        buy_back_text = f'Last Buy Back: None Found'

    eth_price = etherscan.get_native_price(chain)
    contract = chain_info.w3.eth.contract(
        address=chain_info.w3.to_checksum_address(hub_address), abi=etherscan.get_abi(hub_address, chain)
    )
    try:
        distribute = contract.functions.distributeShare().call() / 10
        liquidity = contract.functions.liquidityShare().call() / 10
        treasury = contract.functions.treasuryShare().call() / 10
        liquidity_ratio_target = contract.functions.liquidityRatioTarget().call()
        balance_threshold = contract.functions.balanceThreshold().call() / 10 ** 18
        liquidity_balance = contract.functions.liquidityBalance().call() / 10 ** 18
        distribute_balance = contract.functions.distributeBalance().call() / 10 ** 18
        treasury_balance = contract.functions.treasuryBalance().call() / 10 ** 18
    except Exception as e:
        distribute = "N/A"
        liquidity = "N/A"
        treasury = "N/A"
        liquidity_ratio_target = "N/A"
        balance_threshold = "N/A"

    split_text = (
        f"Ecosystem Share: {distribute}% - {distribute_balance:,.3f} {chain_info.native.upper()}\n"
        f"Liquidity Share: {liquidity}% - {liquidity_balance:,.3f} {chain_info.native.upper()}\n"
        f"Treasury Share: {treasury}% - {treasury_balance:,.3f} {chain_info.native.upper()}"
    )

    if token.upper() in tokens.TOKENS:
        token_info = tokens.TOKENS[token.upper()].get(chain)
        address = token_info.ca
        price, _ = dextools.get_price(address, chain)

    if token == "x7dao":
        try:
            auxiliary = contract.functions.auxiliaryShare().call() / 10
            auxiliary_balance = contract.functions.auxiliaryBalance().call() / 10 ** 18
        except Exception:
            auxiliary = "N/A"
            auxiliary_balance = 0
        auxiliary_text = f"Auxiliary Share: {auxiliary}% - {auxiliary_balance:,.3f}  {chain_info.native.upper()}"
        split_text += "\n" + auxiliary_text

    if token == "x7100":
        token_str = "x7101-x7105"
        address = ca.X7100(chain)
        try:
            lending_pool = contract.functions.lendingPoolShare().call() / 10
            lending_pool_balance = contract.functions.lendingPoolBalance().call() / 10 ** 18
        except Exception:
            lending_pool = "N/A"
            lending_pool_balance = 0
        lending_pool_text = f"Lending Pool Share: {lending_pool}% - {lending_pool_balance:,.3f}  {chain_info.native.upper()}"
        split_text += "\n" + lending_pool_text
    else:
        token_str = token
    balance = 0

    eth_balance = etherscan.get_native_balance(hub_address, chain)
    eth_dollar = (float(eth_balance) * float(eth_price))

    if isinstance(address, str):
        balance += etherscan.get_token_balance(hub_address, address, chain)
        dollar = float(price) * float(balance)
        balance_text = f"{balance:,.0f} {token_str.upper()} (${dollar:,.0f})"
    elif isinstance(address, list):
        for quint in address:
            balance += etherscan.get_token_balance(hub_address, quint, chain)
        balance_text = f"{balance:,.0f} {token_str.upper()}"
    await message.delete()
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            f"*{token.upper()} Liquidity Hub ({chain_info.name})*\n\n"
            f"{round(float(eth_balance), 2)} {chain_info.native.upper()} (${eth_dollar:,.0f})\n"
            f"{balance_text}\n\n"
            f"Liquidity Ratio Target: {liquidity_ratio_target}%\n"
            f"Balance Threshold: {balance_threshold} {chain_info.native.upper()}\n\n"
            f"{split_text}\n\n"
            f"{buy_back_text}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=f"{token.upper()} Liquidity Hub", url=f"{chain_info.scan_address}{hub_address}"
                    )
                ],
            ]
        ),
    )


async def leaderboard(update: Update, context: CallbackContext):
    board = db.clicks_get_leaderboard()
    click_counts_total = db.clicks_get_total()
    fastest = db.clicks_fastest_time()
    fastest_user = fastest[0]
    fastest_time = fastest[1]
    streak = db.clicks_check_highest_streak()
    streak_user, streak_value = streak

    if settings.CLICK_ME_BURN:
        clicks_needed = settings.CLICK_ME_BURN - (click_counts_total % settings.CLICK_ME_BURN)
        await update.message.reply_text(
            text=
                f"*X7 Finance Fastest Pioneer 2024 Leaderboard\n(Top 10)\n\n*"
                f"{api.escape_markdown(board)}\n"
                f"Total clicks: *{click_counts_total}*\n"
                f"Clicks till next X7R Burn: *{clicks_needed}*\n\n"
                f"Fastest Click:\n{fastest_time} seconds\nby {api.escape_markdown(fastest_user)}\n\n"
                f"{api.escape_markdown(streak_user)} clicked the button last and is on a *{streak_value}* click streak!",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            text=
                f"*X7 Finance Fastest Pioneer 2024 Leaderboard\n(Top 10)\n\n*"
                f"{api.escape_markdown(board)}\n"
                f"Total clicks: *{click_counts_total}*\n"
                f"Fastest Click:\n{fastest_time} seconds\nby {api.escape_markdown(fastest_user)}\n\n"
                f"{api.escape_markdown(streak_user)} clicked the button last and is on a *{streak_value}* click streak!",
            parse_mode="Markdown"
        )
    

async def links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [
            InlineKeyboardButton(text="X7Finance.org", url=f"{urls.XCHANGE}"),
        ],
        [
            InlineKeyboardButton(text="Snapshot", url=f"{urls.SNAPSHOT}"),
            InlineKeyboardButton(text="Twitter", url=f"{urls.TWITTER}"),
        ],
        [
            InlineKeyboardButton(text="Reddit", url=f"{urls.REDDIT}"),
            InlineKeyboardButton(text="Warpcast", url=f"{urls.WARPCAST}"),
        ],
        [
            InlineKeyboardButton(text="Github", url=f"{urls.GITHUB}"),
            InlineKeyboardButton(text="Dune", url=f"{urls.DUNE}"),
        ],
    ]

    await update.message.reply_photo(
        photo=media.WEBSITE_LOGO,
        caption=f"\n",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def liquidity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(update.effective_message.message_thread_id)
    chain_info, error_message = chains.get_info(chain, token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return
    
    message = await update.message.reply_text("Getting Liquidity data, Please wait...")

    x7r_pairs = tokens.TOKENS["X7R"].get(chain).pairs
    x7dao_pairs = tokens.TOKENS["X7DAO"].get(chain).pairs

    if isinstance(x7r_pairs, str):
        x7r_pairs = [x7r_pairs]
    if isinstance(x7dao_pairs, str):
        x7dao_pairs = [x7dao_pairs]

    total_x7r_liquidity = 0
    total_x7dao_liquidity = 0
    total_x7r_supply = 0
    total_x7dao_supply = 0
    total_x7r_eth = 0
    total_x7dao_eth = 0

    x7r_liquidity_data = [dextools.get_liquidity(pair, chain) for pair in x7r_pairs]
    
    x7r_text = "*X7R*\n"
    for i, liquidity in enumerate(x7r_liquidity_data):
        exchange_name = "Uniswap" if i == 0 else "Xchange"
        token_liquidity = liquidity.get('token', 'N/A')
        eth_liquidity = liquidity.get('eth', 'N/A')
        total_liquidity = liquidity.get('total', 'N/A')

        if token_liquidity != 'N/A':
            token_liquidity_float = float(token_liquidity.replace(',', ''))
            total_x7r_supply += token_liquidity_float
            percentage = (token_liquidity_float / ca.SUPPLY) * 100
        else:
            percentage = 'N/A'

        if eth_liquidity != 'N/A':
            total_x7r_eth += float(eth_liquidity.replace(',', ''))

        x7r_text += (
            f"{exchange_name}\n{token_liquidity} X7R ({percentage:.2f}%)\n"
            f"{eth_liquidity} {chain_info.native.upper()} \n{total_liquidity}\n\n"
        )

        if total_liquidity != 'N/A':
            total_x7r_liquidity += float(total_liquidity.replace('$', '').replace(',', ''))

    total_x7r_percentage = (total_x7r_supply / ca.SUPPLY) * 100
    x7r_text += (
        f"Total:\n{total_x7r_supply:,.2f} X7R ({total_x7r_percentage:.2f}%)\n"
        f"{total_x7r_eth:,.2f} {chain_info.native.upper()}\n"
        f"${total_x7r_liquidity:,.2f}\n"
    )

    x7dao_liquidity_data = [dextools.get_liquidity(pair, chain) for pair in x7dao_pairs]
    x7dao_text = "*X7DAO*\n"

    for i, liquidity in enumerate(x7dao_liquidity_data):
        exchange_name = "Uniswap" if i == 0 else "Xchange"
        token_liquidity = liquidity.get('token', 'N/A')
        eth_liquidity = liquidity.get('eth', 'N/A')
        total_liquidity = liquidity.get('total', 'N/A')

        if token_liquidity != 'N/A':
            token_liquidity_float = float(token_liquidity.replace(',', ''))
            total_x7dao_supply += token_liquidity_float
            percentage = (token_liquidity_float / ca.SUPPLY) * 100
        else:
            percentage = 'N/A'

        if eth_liquidity != 'N/A':
            total_x7dao_eth += float(eth_liquidity.replace(',', ''))

        x7dao_text += (
            f"{exchange_name}\n{token_liquidity} X7DAO ({percentage:.2f}%)\n"
            f"{eth_liquidity} {chain_info.native.upper()} \n{total_liquidity}\n\n"
        )

        if total_liquidity != 'N/A':
            total_x7dao_liquidity += float(total_liquidity.replace('$', '').replace(',', ''))

    total_x7dao_percentage = (total_x7dao_supply / ca.SUPPLY) * 100
    x7dao_text += (
        f"Total:\n{total_x7dao_supply:,.2f} X7DAO ({total_x7dao_percentage:.2f}%)\n"
        f"{total_x7dao_eth:,.2f} {chain_info.native.upper()}\n"
        f"${total_x7dao_liquidity:,.2f}\n"
    )

    buttons = []
    for i, pair in enumerate(x7r_pairs):
        exchange_name = "Uniswap" if i == 0 else "Xchange"
        buttons.append([InlineKeyboardButton(text=f"X7R - {exchange_name}", url=f"{chain_info.scan_address}{pair}")])

    for i, pair in enumerate(x7dao_pairs):
        exchange_name = "Uniswap" if i == 0 else "Xchange"
        buttons.append([InlineKeyboardButton(text=f"X7DAO - {exchange_name}", url=f"{chain_info.scan_address}{pair}")])

    keyboard = InlineKeyboardMarkup(buttons)

    final_text = f"{x7r_text}\n------\n\n{x7dao_text}\n"
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            f"*X7 Finance Liquidity ({chain_info.name})*\n\n"
            f"{final_text}",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

async def liquidate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(update.effective_message.message_thread_id)
    chain_info, error_message = chains.get_info(chain)
    if error_message:
        await update.message.reply_text(error_message)
        return
    
    message = await update.message.reply_text("Getting Liquidation Info, Please wait...")
    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    chain_lpool = ca.LPOOL(chain)
    contract = chain_info.w3.eth.contract(
        address=chain_info.w3.to_checksum_address(chain_lpool), abi=abis.read("lendingpool")
    )
    num_loans = contract.functions.nextLoanID().call()
    liquidatable_loans = 0
    results = []
    for loan_id in range(num_loans):
        try:
            result = contract.functions.canLiquidate(int(loan_id)).call()
            if result > 0:
                liquidatable_loans += 1
                results.append(f"Loan ID {loan_id}")
        except Exception:
            continue

    liquidatable_loans_text = f"Total liquidatable loans: {liquidatable_loans}"
    output = "\n".join([liquidatable_loans_text] + results) 
    await message.delete()
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            f"*X7 Finance Loan Liquidations ({chain_info.name})*\n\n"
            f"{output}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Lending Dashboard",
                        url=f"{urls.XCHANGE}lending",
                    )
                ],
            ]
        ),
    )



async def loan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text(
            "Please follow command with loan ID number\n",
            parse_mode="Markdown",
        )
        return

    loan_id = context.args[0]
    chain = context.args[1].lower() if len(context.args) > 1 else chains.get_chain(update.effective_message.message_thread_id)
    chain_info, error_message = chains.get_info(chain)
    if error_message:
        await update.message.reply_text(error_message)
        return

    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    chain_lpool = ca.LPOOL(chain, int(loan_id))
    price = etherscan.get_native_price(chain)
    contract = chain_info.w3.eth.contract(address=chain_info.w3.to_checksum_address(chain_lpool), abi=abis.read("lendingpool"))
    liquidation_status = ""
    
    try:
        liquidation = contract.functions.canLiquidate(int(loan_id)).call()
        if liquidation != 0:
            reward = contract.functions.liquidationReward().call() / 10**18
            liquidation_status = (
                f"\n\n*Eligible For Liquidation*\n"
                f"Cost: {liquidation / 10 ** 18} {chain_info.native.upper()} "
                f'(${"{:0,.0f}".format(price * liquidation / 10 ** 18)})\n'
                f'Reward: {reward} {chain_info.native.upper()} (${"{:0,.0f}".format(price * reward)})'
            )
    except Exception:
        pass

    try:
        liability = contract.functions.getRemainingLiability(int(loan_id)).call() / 10**18
        remaining = f'Remaining Liability:\n{liability} {chain_info.native.upper()} (${"{:0,.0f}".format(price * liability)})'
        schedule1 = contract.functions.getPremiumPaymentSchedule(int(loan_id)).call()
        schedule2 = contract.functions.getPrincipalPaymentSchedule(int(loan_id)).call()
        schedule_str = api.format_schedule(schedule1, schedule2, chain_info.native.upper())

        token = contract.functions.loanToken(int(loan_id)).call()
        name = dextools.get_token_name(token, chain)["name"]
        pair = contract.functions.loanPair(int(loan_id)).call()

        term = contract.functions.loanTermLookup(int(loan_id)).call()
        term_contract = chain_info.w3.eth.contract(address=chain_info.w3.to_checksum_address(term), abi=etherscan.get_abi(term, chain))
        index = 0
        token_by_id = None
        while True:
            try:
                token_id = term_contract.functions.tokenByIndex(index).call()
                if token_id == int(loan_id):
                    token_by_id = index
                    break
                index += 1
            except Exception:
                break
    
        ill_number = api.get_ill_number(term)

        await update.message.reply_photo(
            photo=api.get_random_pioneer(),
            caption=
                f"*X7 Finance Initial Liquidity Loan - {loan_id} ({chain_info.name})*\n\n"
                f"{name}\n\n"
                f"Payment Schedule UTC:\n{schedule_str}\n\n"
                f"{remaining}"
                f"{liquidation_status}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=f"Chart",
                            url=f"{urls.DEX_TOOLS(chain_info.dext)}{pair}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text=f"View Loan",
                            url=f"{urls.XCHANGE}lending/{chain_info.name.lower()}/{ill_number}/{token_by_id}",
                        )
                    ]
                ]
            ),
        )
    except Exception:
        await update.message.reply_text(f"Loan ID {loan_id} on {chain_info.name} not found")


async def loans_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption= text.LOANS,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="X7 Finance Whitepaper", url=f"{urls.WP_LINK}"
                    )
                ],
            ]
        ),
    )


async def locks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(update.effective_message.message_thread_id)
    chain_info, error_message = chains.get_info(chain, token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return

    await context.bot.send_chat_action(update.effective_chat.id, "typing")
        
    contract = chain_info.w3.eth.contract(
        address=chain_info.w3.to_checksum_address(ca.TIME_LOCK(chain)), 
        abi=etherscan.get_abi(ca.TIME_LOCK(chain), chain)
    )
    now = datetime.now()

    x7r_pairs = ca.X7R_PAIR(chain)
    x7r_uni_remaining_time_str, x7r_uni_unlock_datetime_str = api.get_unlock_time(chain_info.w3, contract, x7r_pairs[0], now)
    x7r_xchange_remaining_time_str, x7r_xchange_unlock_datetime_str = api.get_unlock_time(chain_info.w3, contract, x7r_pairs[1], now)
    
    x7dao_pairs = ca.X7DAO_PAIR(chain)
    x7dao_uni_remaining_time_str, x7dao_uni_unlock_datetime_str = api.get_unlock_time(chain_info.w3, contract, x7dao_pairs[0], now)
    x7dao_xchange_remaining_time_str, x7dao_xchange_unlock_datetime_str = api.get_unlock_time(chain_info.w3, contract, x7dao_pairs[1], now)
    
    x7d_remaining_time_str, x7d_unlock_datetime_str = api.get_unlock_time(chain_info.w3, contract, ca.X7D(chain), now)

    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            f"*X7 Finance Liquidity Locks ({chain_info.name})*\n\n"
            f"*X7R*\nUniswap - {x7r_uni_unlock_datetime_str}\n{x7r_uni_remaining_time_str}\n\n"
            f"Xchange - {x7r_xchange_unlock_datetime_str}\n{x7r_xchange_remaining_time_str}\n\n"
            f"*X7DAO*\nUniswap - {x7dao_uni_unlock_datetime_str}\n{x7dao_uni_remaining_time_str}\n\n"
            f"Xchange - {x7dao_xchange_unlock_datetime_str}\n{x7dao_xchange_remaining_time_str}\n\n"
            f"*X7D*\n{x7d_unlock_datetime_str}\n{x7d_remaining_time_str}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=chain_info.scan_name,
                        url=f"{chain_info.scan_address}{ca.TIME_LOCK(chain)}",
                    )
                ],
            ]
        ),
    )


async def magisters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(update.effective_message.message_thread_id)
    chain_info, error_message = chains.get_info(chain, token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return

    data = api.get_nft_data(ca.MAGISTER(chain), chain)
    holders = data["holder_count"]
    try:
        magisters = bitquery.get_nft_holder_list(ca.MAGISTER(chain), chain)
        address = "\n\n".join(map(lambda x: f"`{x}`", magisters))
    except Exception:
        address = ""
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            f"*X7 Finance Magister Holders ({chain_info.name})*\n\n"
            f"Holders - {holders}\n\n"
            f"{address}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Magister Holder List",
                        url=f"{chain_info.scan_token}{ca.MAGISTER(chain)}#balances",
                    )
                ],
            ]
        ),
    )


async def mcap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(update.effective_message.message_thread_id)
    chain_info, error_message = chains.get_info(chain, token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return
    
    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    
    caps_info = {}
    caps = {}

    for token, chains_info in tokens.TOKENS.items():
        token_info = chains_info.get(chain)
        if token_info:
            address = token_info.ca
            caps_info[address] = dextools.get_token_info(address, chain)
            caps[address] = caps_info[address]["mcap"]

    total_mcap = 0
    for token, mcap in caps.items():
        if mcap == 'N/A':
            continue
        mcap_value = float(''.join(filter(str.isdigit, mcap)))
        total_mcap += mcap_value

    total_cons = 0
    for token, mcap in caps.items():
        if token in (ca.X7DAO(chain), ca.X7R(chain)):
            continue
        if mcap == 'N/A':
            continue
        cons_mcap_value = float(''.join(filter(str.isdigit, mcap)))
        total_cons += cons_mcap_value

    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            f"*X7 Finance Market Cap Info ({chain_info.name})*\n\n"
            f'`X7R: `            {caps[ca.X7R(chain)]}\n'
            f'`X7DAO:`         {caps[ca.X7DAO(chain)]}\n'
            f'`X7101:`         {caps[ca.X7101(chain)]}\n'
            f'`X7102:`         {caps[ca.X7102(chain)]}\n'
            f'`X7103:`         {caps[ca.X7103(chain)]}\n'
            f'`X7104:`         {caps[ca.X7104(chain)]}\n'
            f'`X7105:`         {caps[ca.X7105(chain)]}\n\n'
            f'`Constellations Combined:` ${total_cons:,.0f}\n'
            f'`Total Market Cap:` ${total_mcap:,.0f}',
        parse_mode="Markdown",
    )


async def me(update: Update, context: CallbackContext):
    user = update.effective_user
    user_info = user.username or f"{user.first_name} {user.last_name}"
    user_data = db.clicks_get_by_name(user_info)
    clicks = user_data[0]
    fastest_time = user_data[1]
    streak = user_data[2]

    if streak != 0:
        streak_message = f"and currently on a *{streak}* click streak!"
    else:
        streak_message = ""    

    if fastest_time is None:
        message = f"*X7 Finance Fastest Pioneer Leaderboard*\n\n" \
                  f"{api.escape_markdown(user_info)}, You have been the Fastest Pioneer *{clicks}* times {streak_message}\n\n" \
                  f"Your fastest time has not been logged yet\n\n"
    else:
        message = f"*X7 Finance Fastest Pioneer Leaderboard*\n\n" \
                  f"{api.escape_markdown(user_info)}, You have been the Fastest Pioneer *{clicks}* times {streak_message}\n\n" \
                  f"Your fastest time is {fastest_time} seconds\n\n"

    await update.message.reply_text(
        text=message,
        parse_mode="Markdown",
    )


async def media_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [
            InlineKeyboardButton(
                text="X7 Official Images", url="https://imgur.com/a/WEszZTa"
            ),
            InlineKeyboardButton(
                text="X7 Official Token Logos Pack 1",
                url="https://t.me/X7announcements/58",
            ),
        ],
        [
            InlineKeyboardButton(
                text="X7 Official Token Logos Pack 2",
                url="https://t.me/X7announcements/141",
            ),
            InlineKeyboardButton(
                text="X7 TG Sticker Pack 1",
                url="https://t.me/addstickers/x7financestickers",
            ),
        ],
        [
            InlineKeyboardButton(
                text="X7 TG Sticker Pack 2",
                url="https://t.me/addstickers/X7finance",
            ),
            InlineKeyboardButton(
                text="X7 TG Sticker Pack 3",
                url="https://t.me/addstickers/x7financ",
            ),
        ],
        [
            InlineKeyboardButton(
                text="X7 TG Sticker Pack 4",
                url="https://t.me/addstickers/GavalarsX7",
            ),
            InlineKeyboardButton(
                text="X7 Emojis Pack",
                url="https://t.me/addemoji/x7FinanceEmojis",
            ),
        ],
    ]

    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=f"\n",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def nft(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(update.effective_message.message_thread_id)
    chain_info, error_message = chains.get_info(chain)
    if error_message:
        await update.message.reply_text(error_message)
        return
    
    message = await update.message.reply_text("Getting NFT Info, Please wait...")
    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    chain_prices = nfts.mint_prices(chain)
    chain_data = nfts.data(chain)
    discount = nfts.discounts()

    eco_price = chain_prices.get("eco")
    liq_price = chain_prices.get("liq")
    dex_price = chain_prices.get("dex")
    borrow_price = chain_prices.get("borrow")
    magister_price = chain_prices.get("magister")

    eco_floor = chain_data.get("eco", {}).get("floor_price")
    liq_floor = chain_data.get("liq", {}).get("floor_price")
    dex_floor = chain_data.get("dex", {}).get("floor_price")
    borrow_floor = chain_data.get("borrow", {}).get("floor_price")
    magister_floor = chain_data.get("magister", {}).get("floor_price")

    eco_count = chain_data.get("eco", {}).get("holder_count")
    liq_count = chain_data.get("liq", {}).get("holder_count")
    dex_count = chain_data.get("dex", {}).get("holder_count")
    borrow_count = chain_data.get("borrow", {}).get("holder_count")
    magister_count = chain_data.get("magister", {}).get("holder_count")

    eco_discount = discount.get("eco", {})
    liq_discount = discount.get("liq", {})
    dex_discount = discount.get("dex", {})
    borrow_discount = discount.get("borrow", {})
    magister_discount = discount.get("magister", {})

    eco_discount_text = "\n".join(
        [
            f"> {discount}% discount on {token}"
            for token, discount in eco_discount.items()
        ]
    )
    liq_discount_text = "\n".join(
        [
            f"> {discount}% discount on {token}"
            for token, discount in liq_discount.items()
        ]
    )
    dex_discount_text = "\n".join([f"> {discount}" for discount in dex_discount])
    borrow_discount_text = "\n".join([f"> {discount}" for discount in borrow_discount])
    magister_discount_text = "\n".join(
        [
            f"> {discount}% discount on {token}"
            for token, discount in magister_discount.items()
        ]
    )

    buttons = [
        [
            InlineKeyboardButton(text="Mint Here", url=f"{urls.XCHANGE}dashboard/marketplace"),
            InlineKeyboardButton(text="OS - Ecosystem Maxi", url=f"{urls.OS_LINK('eco')}{chain_info.opensea}"),
        ],
        [
            InlineKeyboardButton(text="OS - Liquidity Maxi", url=f"{urls.OS_LINK('liq')}{chain_info.opensea}"),
            InlineKeyboardButton(text="OS - DEX Maxi", url=f"{urls.OS_LINK('dex')}{chain_info.opensea}"),
        ],
        [
            InlineKeyboardButton(text="OS - Borrowing Maxi", url=f"{urls.OS_LINK('borrow')}{chain_info.opensea}"),
            InlineKeyboardButton(text="OS - Magister", url=f"{urls.OS_LINK('magister')}{chain_info.opensea}"),
        ],
    ]

    await message.delete()
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            f"*NFT Info ({chain_info.name})*\n\n"
            f"*Ecosystem Maxi*\n{eco_price}\n"
            f"Available - {500 - eco_count}\nFloor price - {eco_floor} {chain_info.native.upper()}\n"
            f"{eco_discount_text}\n\n"
            f"*Liquidity Maxi*\n{liq_price}\n"
            f"Available - {250 - liq_count}\nFloor price - {liq_floor} {chain_info.native.upper()}\n"
            f"{liq_discount_text}\n\n"
            f"*Dex Maxi*\n{dex_price}\n"
            f"Available - {150 - dex_count}\nFloor price - {dex_floor} {chain_info.native.upper()}\n"
            f"{dex_discount_text}\n\n"
            f"*Borrow Maxi*\n{borrow_price}\n"
            f"Available - {100 - borrow_count}\nFloor price - {borrow_floor} {chain_info.native.upper()}\n"
            f"{borrow_discount_text}\n\n"
            f"*Magister*\n{magister_price}\n"
            f"Available - {49 - magister_count}\nFloor price - {magister_floor} {chain_info.native.upper()}\n"
            f"{magister_discount_text}\n",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def pair(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = await update.message.reply_text("Getting Pair Info, Please wait...")
    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    pair_text = ""
    total = 0
    for chain in chains.CHAINS:
        chain_info, error_message = chains.get_info(chain)
        contract = chain_info.w3.eth.contract(
            address=chain_info.w3.to_checksum_address(ca.FACTORY(chain)),
            abi=abis.read("factory"),
        )
        amount = contract.functions.allPairsLength().call()
        if chain == "eth":
            amount += 141
        pair_text += f"`{chain_info.name}:`   {amount}\n"
        total += amount
    await message.delete()
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            f"*X7 Finance Pair Count*\n\n"
            f"{pair_text}\n"
            f"`TOTAL:`  {total}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Xchange Pairs Dashboard",
                        url=f"{urls.XCHANGE}/liquidity?=all-pools",
                    )
                ],
            ]
        ),
    )


async def pfp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(update.effective_chat.id, "upload_photo")
    text = " ".join(context.args)
    if text == "":
        await update.message.reply_text("Please follow the command with desired name")
    elif len(text) > 17:
        await update.message.reply_text("Name too long, please use under 17 characters")
    else:
        img = Image.open(requests.get(api.get_random_pioneer(), stream=True).raw)
        i1 = ImageDraw.Draw(img)
        position = (380, 987.7)
        font = ImageFont.truetype(r"media/Bartomes.otf", 34)
        for char in text:
            i1.text(position, char, font=font, fill=(255, 255, 255))
            position = (position[0] + 37.5, position[1])
        img.save(r"media/pfp.png")
        await update.message.reply_photo(
            photo=open(r"media/pfp.png", "rb"))


async def pioneer(update: Update, context: ContextTypes.DEFAULT_TYPE = None):
    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    pioneer_id = " ".join(context.args)
    chain = "eth"

    if pioneer_id == "":
        floor_data = api.get_nft_data(ca.PIONEER, "eth")
        floor = floor_data["floor_price"]
        native_price = etherscan.get_native_price("eth")
        if floor != "N/A":
            floor_round = round(floor, 2)
            floor_dollar = floor * float(native_price)
        else:
            floor_round = "N/A"
            floor_dollar = 0 
        pioneer_pool = float(etherscan.get_native_balance(ca.PIONEER, "eth"))
        each = float(pioneer_pool) / 639
        each_dollar = float(each) * float(native_price)
        total_dollar = float(pioneer_pool) * float(native_price)
        tx = etherscan.get_tx(ca.PIONEER, "eth")
        tx_filter = [d for d in tx["result"] if ca.PIONEER.lower() in d["to"].lower() and d.get("functionName", "") == "claimRewards(uint256[] _pids)"]
        recent_tx = max(tx_filter, key=lambda tx: int(tx["timeStamp"]), default=None)

        if recent_tx:
            by = recent_tx["from"][-5:]
            time = datetime.fromtimestamp(int(recent_tx["timeStamp"]))
            now = datetime.now()
            duration = now - time
            days = duration.days
            hours, remainder = divmod(duration.seconds, 3600)
            minutes = (remainder % 3600) // 60
            recent_tx_text = (f"Last Claim: {time} UTC (by {by})\n"
                             f"{days} days, {hours} hours and {minutes} minutes ago\n\n")
        else:
            recent_tx_text = 'Last Claim: Not Found\n\n'

        await update.message.reply_photo(
            photo=api.get_random_pioneer(),
            caption=
                f"*X7 Pioneer NFT Info*\n\n"
                f"Floor Price: {floor_round} ETH (${'{:0,.0f}'.format(floor_dollar)})\n"
                f"Pioneer Pool: {pioneer_pool:.3f} ETH (${'{:0,.0f}'.format(total_dollar)})\n"
                f"Per Pioneer: {each:.3f} ETH (${each_dollar:,.2f})\n\n"
                f"{recent_tx_text}",
            parse_mode="markdown",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="X7 Pioneer Dashboard",
                            url=f"{urls.XCHANGE}dashboard/pioneer",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Opensea",
                            url=f"{urls.OS_LINK('pioneer')}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text=chains.CHAINS[chain].scan_name,
                            url=f"{chains.CHAINS[chain].scan_token}{ca.PIONEER}",
                        )
                    ],
                ]
            ),
        )
    else:
        data = opensea.get_nft_id(ca.PIONEER, pioneer_id)
        if "nft" in data and data["nft"]:
            status = data["nft"]["traits"][0]["value"]
            image_url = data["nft"]["image_url"]
        else:
            await update.message.reply_text(f"Pioneer {pioneer_id} not found")
            return
        
        await update.message.reply_text(
            f"*X7 Pioneer {pioneer_id} NFT Info*\n\n"
            f"Transfer Lock Status: {status}\n\n"
            f"https://pro.opensea.io/nft/ethereum/{ca.PIONEER}/{pioneer_id}",
        parse_mode="markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="X7 Pioneer Dashboard",
                        url="https://x7.finance/x/nft/pioneer",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Opensea",
                        url=f"https://pro.opensea.io/nft/ethereum/{ca.PIONEER}/{pioneer_id}",
                    )
                ],
            ]
        ),
    )


async def pool(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(update.effective_message.message_thread_id)
    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    message = await update.message.reply_text("Getting Lending Pool Info, Please wait...")
    if chain == "all":
        pool_text = ""
        total_lpool_reserve_dollar = 0
        total_lpool_dollar = 0
        total_dollar = 0
        for chain in chains.CHAINS:
            native = chains.CHAINS[chain].native.lower()
            chain_name = chains.CHAINS[chain].name
            chain_lpool = ca.LPOOL(chain)
            try:
                price = etherscan.get_native_price(chain)
                lpool_reserve = etherscan.get_native_balance(ca.LPOOL_RESERVE(chain), chain)
                lpool = etherscan.get_native_balance(chain_lpool, chain)
            except Exception:
                price = 0
                lpool_reserve = 0
                lpool = 0
            lpool_reserve_dollar = (float(lpool_reserve) * float(price))
            lpool_dollar = (float(lpool) * float(price))
            pool = round(float(lpool_reserve) + float(lpool), 2)
            dollar = lpool_reserve_dollar + lpool_dollar
            pool_text += f'`{chain_name}:`   {pool} {native.upper()} (${"{:0,.0f}".format(dollar)})\n'
            total_lpool_reserve_dollar += lpool_reserve_dollar
            total_lpool_dollar += lpool_dollar
            total_dollar += dollar 
        await message.delete()
        await update.message.reply_photo(
            photo=api.get_random_pioneer(),
            caption=
                f"*X7 Finance Lending Pool Info *\n\n"
                f"{pool_text}\n"
                f'Lending Pool: ${"{:0,.0f}".format(total_lpool_dollar)}\n'
                f'Lending Pool Reserve: ${"{:0,.0f}".format(total_lpool_reserve_dollar)}\n'
                f'Total: ${"{:0,.0f}".format(total_dollar)}',
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=f"Lending Pool Dashboard",
                            url=f"{urls.XCHANGE}/lending",
                        )
                    ]
                ]
            ),
        )
    else:
        chain_info, error_message = chains.get_info(chain)
        if error_message:
            await update.message.reply_text(error_message)
            return
        
        chain_lpool = ca.LPOOL(chain)
        native_price = etherscan.get_native_price(chain)
        lpool_reserve = etherscan.get_native_balance(ca.LPOOL_RESERVE(chain), chain)
        lpool_reserve_dollar = (float(lpool_reserve) * float(native_price))
        lpool = float(etherscan.get_native_balance(chain_lpool, chain))
        lpool_dollar = (float(lpool) * float(native_price))
        pool = round(float(lpool_reserve) + float(lpool), 2)
        dollar = lpool_reserve_dollar + lpool_dollar
        lpool_reserve = round(float(lpool_reserve), 2)
        lpool = round(float(lpool), 2)

        try:
            contract = chain_info.w3.eth.contract(
                address=chain_info.w3.to_checksum_address(ca.LPOOL(chain)),
                abi=abis.read("lendingpool"),
                )
            count = contract.functions.nextLoanID().call()
            total_borrowed = 0
            for loan_id in range(21, count):
                borrowed = contract.functions.getRemainingLiability(loan_id).call() / 10 ** 18
                total_borrowed += borrowed
            
            total_borrowed_dollar = (float(total_borrowed) * float(native_price))

        except Exception as e:
            total_borrowed = 0
            total_borrowed_dollar = 0

            
        await message.delete()
        await update.message.reply_photo(
            photo=api.get_random_pioneer(),
            caption=
                f"*X7 Finance Lending Pool Info ({chain_info.name})*\n\n"
                f"Lending Pool:\n"
                f'{lpool} {chain_info.native.upper()} (${"{:0,.0f}".format(lpool_dollar)})\n\n'
                f"Lending Pool Reserve:\n"
                f'{lpool_reserve} {chain_info.native.upper()} (${"{:0,.0f}".format(lpool_reserve_dollar)})\n\n'
                f"Total\n"
                f'{pool} {chain_info.native.upper()} (${"{:0,.0f}".format(dollar)})\n\n'
                f'Total Currently Borrowed\n'
                f'{total_borrowed:,.3f} {chain_info.native.upper()} (${"{:0,.0f}".format(total_borrowed_dollar)})',
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=f"Lending Pool Dashboard",
                            url=f"{urls.XCHANGE}/lending",
                        )
                    ]
                ]
            ),
        )


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(update.effective_message.message_thread_id)
    chain_info, error_message = chains.get_info(chain,token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return

    x7r_price, x7r_change  = dextools.get_price(ca.X7R(chain), chain)
    x7dao_price, x7dao_change  = dextools.get_price(ca.X7DAO(chain), chain)

    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            f"*X7 Finance Token Price Info ({chain_info.name})*\n\n"
            f"X7R\n"
            f"💰 Price: {x7r_price}\n"
            f"{x7r_change}\n\n"
            f"X7DAO\n"
            f"💰 Price: {x7dao_price}\n"
            f"{x7dao_change}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="X7R Chart - Rewards Token",
                        url=f"{urls.DEX_TOOLS(chain_info.dext)}{ca.X7R(chain)}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="X7DAO Chart - Governance Token",
                        url=f"{urls.DEX_TOOLS(chain_info.dext)}{ca.X7DAO(chain)}",
                    )
                ],
            ]
        ),
    )


async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = []
    for chain in chains.CHAINS:
        buttons_row = []
        name = chains.CHAINS[chain].name
        address = chains.CHAINS[chain].scan_address
        buttons_row.append(
                InlineKeyboardButton(
                    text=name,
                    url=f"{address}{ca.ROUTER(chain)}"
                )
            )
        buttons.append(buttons_row)
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=f"\n",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def smart(update: Update, context: ContextTypes.DEFAULT_TYPE = None):
    chain = " ".join(context.args).lower() or chains.get_chain(update.effective_message.message_thread_id)

    chain_info, error_message = chains.get_info(chain)
    if error_message:
        await update.message.reply_text(error_message)
        return
        
    buttons = [
    [
        InlineKeyboardButton(
            text="Contracts Dashboard",
            url=f"{urls.XCHANGE}dashboard",
        ),
    ],
    [
        InlineKeyboardButton(
            text="X7100 Liquidity Hub",
            url=f"{chain_info.scan_address}{ca.X7100_LIQ_HUB(chain)}"
        ),
        InlineKeyboardButton(
            text="X7R Liquidity Hub",
            url=f"{chain_info.scan_address}{ca.X7R_LIQ_HUB(chain)}"
        ),
    ],
    [
        InlineKeyboardButton(
            text="X7DAO Liquidity Hub",
            url=f"{chain_info.scan_address}{ca.X7DAO_LIQ_HUB(chain)}"
        ),
        InlineKeyboardButton(
            text="X7100 Discount Authority",
            url=f"{chain_info.scan_address}{ca.X7100_DISCOUNT(chain)}",
        ),
        
    ],
    [
        InlineKeyboardButton(
            text="X7R Discount Authority",
            url=f"{chain_info.scan_address}{ca.X7R_DISCOUNT(chain)}",
        ),
        InlineKeyboardButton(
            text="X7DAO Discount Authority",
            url=f"{chain_info.scan_address}{ca.X7DAO_DISCOUNT(chain)}",
        ),
    ],
    [
        InlineKeyboardButton(
            text="Xchange Discount Authority",
            url=f"{chain_info.scan_address}{ca.XCHANGE_DISCOUNT(chain)}",
        ),
        InlineKeyboardButton(
            text="Lending Discount Authority",
            url=f"{chain_info.scan_address}{ca.LENDING_DISCOUNT(chain)}",
        ),
    ],
    [
        InlineKeyboardButton(
            text="Token Burner",
            url=f"{chain_info.scan_address}{ca.BURNER(chain)}"
        ),
        InlineKeyboardButton(
            text="Token Time Lock",
            url=f"{chain_info.scan_address}{ca.TIME_LOCK(chain)}"
        ),
    ],
    [
        InlineKeyboardButton(
            text="Ecosystem Splitter",
            url=f"{chain_info.scan_address}{ca.ECO_SPLITTER(chain)}",
        ),
        InlineKeyboardButton(
            text="Treasury Splitter",
            url=f"{chain_info.scan_address}{ca.TREASURY_SPLITTER(chain)}",
        ),
    ],
    [
        InlineKeyboardButton(
            text="Liquidity Treasury",
            url=f"{chain_info.scan_address}{ca.LIQUIDITY_TREASURY(chain)}",
        ),
        InlineKeyboardButton(
            text="Default Token List",
            url=f"{chain_info.scan_address}{ca.DEFAULT_TOKEN_LIST(chain)}"
        ),
    ],
    [
        InlineKeyboardButton(
            text="Lending Pool",
            url=f"{chain_info.scan_address}{ca.LPOOL(chain)}"
        ),
        InlineKeyboardButton(
            text="Lending Pool Reserve",
            url=f"{chain_info.scan_address}{ca.LPOOL_RESERVE(chain)}",
        ),
    ],
    [
        
        InlineKeyboardButton(
            text="Xchange Factory",
            url=f"{chain_info.scan_address}{ca.FACTORY(chain)}"
        ),
        InlineKeyboardButton(
            text="Xchange Router",
            url=f"{chain_info.scan_address}{ca.ROUTER(chain)}"
        ),
    ],
    ]

    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            f"*X7 Finance Smart Contracts ({chain_info.name})*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def splitters_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(update.effective_message.message_thread_id)
    chain_info, error_message = chains.get_info(chain)
    if error_message:
        await update.message.reply_text(error_message)
        return
    
    message = await update.message.reply_text("Getting Splitter Info, Please wait...")
    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    treasury_eth = float(etherscan.get_native_balance(ca.TREASURY_SPLITTER(chain), chain))
    eco_eth = float(etherscan.get_native_balance(ca.ECO_SPLITTER(chain), chain))
    native_price = etherscan.get_native_price(chain)
    eco_dollar = float(eco_eth) * float(native_price)
    treasury_dollar = float(treasury_eth) * float(native_price)

    eco_splitter_text = "Distribution:\n"
    eco_distribution = splitters.generate_eco_split(chain, eco_eth)
    for location, (share, percentage) in eco_distribution.items():
        eco_splitter_text += f"{location}: {share:.2f} {chain_info.native.upper()} ({percentage:.0f}%)\n"

    treasury_splitter_text = "Distribution:\n"
    treasury_distribution = splitters.generate_treasury_split(chain, treasury_eth)
    for location, (share, percentage) in treasury_distribution.items():
        treasury_splitter_text += f"{location}: {share:.2f} {chain_info.native.upper()} ({percentage:.0f}%)\n"
    
    await message.delete()
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            f"*X7 Finance Ecosystem Splitters ({chain_info.name})*\n\n"
            f"Ecosystem Splitter\n{eco_eth:.2f} {chain_info.native.upper()} (${'{:0,.0f}'.format(eco_dollar)})\n"
            f"{eco_splitter_text}\n"
            f"Treasury Splitter\n{treasury_eth:.2f} {chain_info.native.upper()} (${'{:0,.0f}'.format(treasury_dollar)})\n"
            f"{treasury_splitter_text}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text="Ecosystem Splitter", url=f"{chain_info.scan_address}{ca.ECO_SPLITTER(chain)}")],
                [InlineKeyboardButton(text="Treasury Splitter", url=f"{chain_info.scan_address}{ca.TREASURY_SPLITTER(chain)}")],
            ]
        ),
    )


async def tax_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(update.effective_message.message_thread_id)
    chain_info, error_message = chains.get_info(chain, token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return
    
    tax_info = tax.generate_info(chain)
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            f"*X7 Finance Tax Info ({chain_info.name})*\n\n"
            f"{tax_info}\n",
        parse_mode="Markdown",
    )


async def timestamp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = " ".join(context.args)
        if text == "":
            await update.message.reply_text(
                "Please follow the command with the timestamp you wish to convert"
            )
        else:  
            stamp = int(" ".join(context.args).lower())
            time = api.convert_timestamp_to_datetime(stamp)
            current_time = datetime.now()
            timestamp_time = datetime.fromtimestamp(stamp)
            time_difference = current_time - timestamp_time
            if time_difference.total_seconds() > 0:
                time_message = "ago"
            else:
                time_message = "away"
                time_difference = abs(time_difference)
            years = time_difference.days // 365
            months = (time_difference.days % 365) // 30
            days = time_difference.days % 30
            hours, remainder = divmod(time_difference.seconds, 3600)
            minutes = remainder // 60
            await update.message.reply_photo(
                photo=api.get_random_pioneer(),
                caption=
                    f"*X7 Finance Timestamp Conversion*\n\n"
                    f"{stamp}\n{time} UTC\n\n"
                    f"{years} years, {months} months, {days} days, "
                    f"{hours} hours, {minutes} minutes {time_message}",
                parse_mode="Markdown",
            )
    except Exception:
        await update.message.reply_text(
            "Timestamp not recognised"
        )


async def time_command(update: Update, context: CallbackContext):
    message = update.message.text.split(" ")
    timezones = [
        ("America/Los_Angeles", "PST"),
        ("America/New_York", "EST"),
        ("UTC", "UTC"),
        ("Europe/London", "GMT"),
        ("Europe/Berlin", "CET"),
        ("Asia/Dubai", "GST"),
        ("Asia/Kolkata", "IST"),
        ("Asia/Tokyo", "JST"),
        ("Australia/Queensland", "AEST"),
    ]
    current_time = datetime.now(pytz.timezone("UTC"))
    local_time = current_time.astimezone(pytz.timezone("UTC"))
    try:
        if len(message) > 1:
            time_variable = message[1]
            time_format = "%I%p"
            if re.match(r"\d{1,2}:\d{2}([ap]m)?", time_variable):
                time_format = (
                    "%I:%M%p"
                    if re.match(r"\d{1,2}:\d{2}am", time_variable, re.IGNORECASE)
                    else "%I:%M%p"
                )
            input_time = datetime.strptime(time_variable, time_format).replace(
                year=local_time.year, month=local_time.month, day=local_time.day
            )
            if len(message) > 2:
                time_zone = message[2]
                for tz, tz_name in timezones:
                    if time_zone.lower() == tz_name.lower():
                        tz_time = pytz.timezone(tz).localize(input_time)
                        time_info = f"{input_time.strftime('%A %B %d %Y')}\n"
                        time_info += f"{input_time.strftime('%I:%M %p')} - {time_zone.upper()}\n\n"
                        for tz_inner, tz_name_inner in timezones:
                            converted_time = tz_time.astimezone(pytz.timezone(tz_inner))
                            time_info += f"{converted_time.strftime('%I:%M %p')} - {tz_name_inner}\n"
                        await update.message.reply_text(
                            time_info, parse_mode="Markdown"
                        )
                        return
            time_info = f"{input_time.strftime('%A %B %d %Y')}\n"
            time_info += (
                f"{input_time.strftime('%I:%M %p')} - {time_variable.upper()}\n\n"
            )
            for tz, tz_name in timezones:
                tz_time = input_time.astimezone(pytz.timezone(tz))
                time_info += f"{tz_time.strftime('%I:%M %p')} - {tz_name}\n"
            await update.message.reply_text(time_info, parse_mode="Markdown")
            return
        time_info = f"{local_time.strftime('%A %B %d %Y')}\n"
        time_info += (
            f"{local_time.strftime('%I:%M %p')} - {local_time.strftime('%Z')}\n\n"
        )
        for tz, tz_name in timezones:
            tz_time = local_time.astimezone(pytz.timezone(tz))
            time_info += f"{tz_time.strftime('%I:%M %p')} - {tz_name}\n"
        await update.message.reply_text(time_info, parse_mode="Markdown")
    except Exception:
        await update.message.reply_text(
            "use `/time HH:MMPM or HHAM TZ`", parse_mode="Markdown"
        )


async def treasury(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(update.effective_message.message_thread_id)
    chain_info, error_message = chains.get_info(chain)
    if error_message:
        await update.message.reply_text(error_message)
        return

    message = await update.message.reply_text("Getting Treasury Info, Please wait...")
    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    native_price = etherscan.get_native_price(chain)
    eth = round(float(etherscan.get_native_balance(chain_info.dao_multi, chain)), 2)
    dollar = float(eth) * float(native_price)
    x7r_balance = etherscan.get_token_balance(chain_info.dao_multi, ca.X7R(chain), chain)
    x7r_price,_ = dextools.get_price(ca.X7R(chain), chain)
    x7r_price = float(x7r_balance) * float(x7r_price)
    x7dao_balance = etherscan.get_token_balance(chain_info.dao_multi, ca.X7DAO(chain), chain)
    x7dao_price,_ = dextools.get_price(ca.X7DAO(chain), chain)
    x7dao_price = float(x7dao_balance) * float(x7dao_price)
    x7d_balance = etherscan.get_token_balance(chain_info.dao_multi, ca.X7D(chain), chain)
    x7d_price = x7d_balance * native_price
    total = x7r_price + dollar + x7d_price + x7dao_price
    x7r_percent = round(x7r_balance / ca.SUPPLY * 100, 2)
    x7dao_percent = round(x7dao_balance / ca.SUPPLY * 100, 2)
    await message.delete()
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            f"*X7 Finance Treasury ({chain_info.name})*\n\n"
            f'{eth} {chain_info.native.upper()} (${"{:0,.0f}".format(dollar)})\n'
            f'{x7d_balance} X7D (${"{:0,.0f}".format(x7d_price)})\n'
            f'{"{:0,.0f}".format(x7r_balance)} X7R ({x7r_percent}%) (${"{:0,.0f}".format(x7r_price)})\n'
            f'{"{:0,.0f}".format(x7dao_balance)} X7DAO ({x7dao_percent}%) (${"{:0,.0f}".format(x7dao_price)})\n'
            f'Total: (${"{:0,.0f}".format(total)})',
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="DAO Multi-sig Wallet",
                        url=f"{chain_info.scan_address}{chain_info.dao_multi}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Community Multi-sig Wallet",
                        url=f"{chain_info.scan_address}{chain_info.com_multi}",
                    )
                ]
            ]
        ),
    )

async def trending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async def trending_error():
        await message.delete()
        await update.message.reply_photo(
            photo=api.get_random_pioneer(),
            caption=f'*Xchange Trending*\n\nUnable to get Dune data, please use the link below',
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="X7 Dune Dashboard", url=f"{urls.DUNE}"
                        )
                    ],
                ]
            ),
        )

    chain = " ".join(context.args).lower() or chains.get_chain(update.effective_message.message_thread_id)

    chain_info, error_message = chains.get_info(chain)
    if error_message:
        await update.message.reply_text(error_message)
        return
    chain_name = "ethereum" if chain == "eth" else chain_info.name
    chain_name_title = f"({chain_info.name.upper()})"

    if chain_name.upper() not in dune.TRENDING_FLAG:
        dune.TRENDING_TEXT[chain_name.upper()] = ""
        dune.TRENDING_FLAG[chain_name.upper()] = False
        dune.TRENDING_TIMESTAMP[chain_name.upper()] = datetime.now().timestamp()
        dune.TRENDING_LAST_DATE[chain_name.upper()] = datetime.fromtimestamp(dune.TRENDING_TIMESTAMP[chain_name.upper()]).strftime("%Y-%m-%d %H:%M:%S")

    try:
        if dune.TRENDING_FLAG[chain_name.upper()] == False:
            message = await update.message.reply_text(f"Getting Xchange Trending {chain_name}, Please wait...")
            await context.bot.send_chat_action(update.effective_chat.id, "typing")

            execution_id = dune.execute_query(dune.TOP_PAIRS_ID, "medium")
            response_data = None
            for attempt in range(4):
                try:
                    response = dune.get_query_results(execution_id)
                    response_data = response.json()
                except ValueError:
                    await trending_error()
                    return

                if response_data.get('is_execution_finished', False):
                    break
                await asyncio.sleep(5)

            if 'result' not in response_data:
                await trending_error()
                return

            rows = response_data["result"]["rows"]
            rows = [row for row in rows if row["pair"] != "TOTAL" and row["blockchain"].lower() == chain_name]
            
            valid_rows = [row for row in rows if row.get('last_24hr_amt') is not None and row.get("pair") is not None]
            sorted_rows = sorted(valid_rows, key=lambda x: x.get('last_24hr_amt', 0), reverse=True)

            if len(sorted_rows) < 3:
                top_trending = sorted_rows
            else:
                top_trending = sorted_rows[:3]

            trending_text = f"*Xchange Trending Pairs {chain_name_title.upper()}*\n\n"

            if not any(item.get("pair") for item in top_trending):
                await message.delete()
                await update.message.reply_photo(
                    photo=api.get_random_pioneer(),
                    caption=
                        f'*Xchange Trending {chain_name_title.upper()}*\n\n'
                        f'No trending data for {chain_name}',
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="X7 Dune Dashboard", url=f"{urls.DUNE}"
                                )
                            ],
                        ]
                    ),
                )
                return

            else:
                for idx, item in enumerate(top_trending, start=1):
                    pair = item.get("pair")
                    last_24hr_amt = item.get("last_24hr_amt")
                    chain = item.get("blockchain")
                    if pair is not None and last_24hr_amt is not None:
                        trending_text += f'{idx}. {pair} ({chain.upper()}) \n24 Hour Volume: ${"{:0,.0f}".format(last_24hr_amt)}\n\n'

            await message.delete()
            await update.message.reply_photo(
                photo=api.get_random_pioneer(),
                caption=trending_text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="X7 Dune Dashboard", url=f"{urls.DUNE}"
                            )
                        ],
                    ]
                ),
            )

            dune.TRENDING_FLAG[chain_name.upper()] = True
            dune.TRENDING_TEXT[chain_name.upper()] = trending_text
            dune.TRENDING_TIMESTAMP[chain_name.upper()] = datetime.now().timestamp()
            dune.TRENDING_LAST_DATE[chain_name.upper()] = datetime.fromtimestamp(
                dune.TRENDING_TIMESTAMP[chain_name.upper()]
            ).strftime("%Y-%m-%d %H:%M:%S")

        else:
            await update.message.reply_photo(
                photo=api.get_random_pioneer(),
                caption=
                    f'{dune.TRENDING_TEXT[chain_name.upper()]}Last Updated: {dune.TRENDING_LAST_DATE[chain_name.upper()]}',
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="X7 Dune Dashboard", url=f"{urls.DUNE}"
                            )
                        ]
                    ]
                ),
            )
    except Exception:
        await trending_error()

async def twitter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_sticker(sticker=media.TWITTER_STICKER)
    await update.message.reply_text(
        f"*X7 Finance Twitter/X*\n\n" f"{random.choice(text.X_REPLIES)}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=f"{urls.TWITTER}",
                        url=f"{urls.TWITTER}",
                    )
                ],
            ]
        ),
    )


async def volume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async def volume_error():
        await message.delete()
        await update.message.reply_photo(
            photo=api.get_random_pioneer(),
            caption=
                f'*Xchange Volume*\n\nUnable to get Dune data, please use the link below',
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="X7 Dune Dashboard", url=f"{urls.DUNE}"
                        )
                    ],
                ]
            ),
        )

    message = await update.message.reply_text("Getting Volume Info, Please wait...")
    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    try:
        if dune.VOLUME_FLAG == False:
            execution_id = dune.execute_query(dune.VOLUME_ID, "medium")
            response_data = None
            for _ in range(10):
                response = dune.get_query_results(execution_id)
                try:
                    response_data = response.json()
                except ValueError:
                    await volume_error()
                    return

                if response_data.get('is_execution_finished', False):
                    break
                await asyncio.sleep(2)

            if 'result' not in response_data:
                await volume_error()
                return

            try:
                last_24hr_amt = response_data['result']['rows'][0]['last_24hr_amt']
                last_30d_amt = response_data['result']['rows'][0]['last_30d_amt']
                last_7d_amt = response_data['result']['rows'][0]['last_7d_amt']
                lifetime_amt = response_data['result']['rows'][0]['lifetime_amt']
            except (KeyError, IndexError):
                await volume_error()
                return

            volume_text = (
                f'Total:       ${"{:0,.0f}".format(lifetime_amt)}\n'
                f'30 Day:    ${"{:0,.0f}".format(last_30d_amt)}\n'
                f'7 Day:      ${"{:0,.0f}".format(last_7d_amt)}\n'
                f'24 Hour:  ${"{:0,.0f}".format(last_24hr_amt)}'
            )

            await message.delete()
            await update.message.reply_photo(
                photo=api.get_random_pioneer(),
                caption=
                    f"*Xchange Trading Volume*\n\n{volume_text}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="X7 Dune Dashboard", url=f"{urls.DUNE}"
                            )
                        ],
                    ]
                ),
            )

            dune.VOLUME_TIMESTAMP = datetime.now().timestamp()
            dune.VOLUME_FLAG = True
            dune.VOLUME_TEXT = volume_text
        else:
            await message.delete()
            await update.message.reply_photo(
                photo=api.get_random_pioneer(),
                caption=f'*Xchange Trading Volume*\n\n'
                        f'{dune.VOLUME_TEXT}\n\nLast Updated: {dune.VOLUME_LAST_DATE} (UTC)',
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="X7 Dune Dashboard", url=f"{urls.DUNE}"
                            )
                        ],
                    ]
                ),
            )
    except Exception:
        await volume_error()


async def warpcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = " ".join(context.args).lower()
    if name:
        if name.startswith("@"):
            name = name[1:]
        last_cast = warpcast.get_cast(name)
        if not last_cast:
            await update.message.reply_text(f"{name} not found on Warpcast")
            return
    else:
        name = "X7Finance"
        last_cast = warpcast.get_cast()

    casters = warpcast.get_recasters(last_cast[0].hash)
    likes = last_cast[0].reactions.count if last_cast[0].reactions else 0
    replies = last_cast[0].replies.count if last_cast[0].replies else 0
    recasts =  last_cast[0].recasts.count if last_cast[0].recasts else 0

    if casters is not None:
        names = [caster.username for caster in casters[:20]]
        remaining_count = len(casters) - 20
        recasters_text = "\n\nRecasted by:\n" + "\n".join(names)
        if remaining_count > 0:
            recasters_text += f"\n...and {remaining_count} more"
    else:
        recasters_text = ""

    timestamp = str(last_cast[0].timestamp)[:10]
    timestamp_int = int(timestamp)
    current_time = datetime.now()
    timestamp_time = datetime.fromtimestamp(timestamp_int)
    time_difference = current_time - timestamp_time
    days = time_difference.days % 30
    hours, remainder = divmod(time_difference.seconds, 3600)
    minutes = remainder // 60

    if last_cast[0].embeds and last_cast[0].embeds.images:
        photo_url = last_cast[0].embeds.images[0].url
    else:
        photo_url = api.get_random_pioneer()

    await update.message.reply_photo(
        photo=photo_url,
        caption=
            f"*X7 Finance Warpcast*\n\n"
            f"Latest Cast by {name}:\n{days} days, {hours} hours and {minutes} minutes ago\n\n{api.escape_markdown(last_cast[0].text)}\n\n"
            f"Likes: {likes}\n"
            f"Replies: {replies}\n"
            f"Recasts: {recasts}"
            f"{recasters_text}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Latest Cast",
                        url=f"https://warpcast.com/{name}/{last_cast[0].hash}",
                    )
                ],
            ]
        ),
    )


async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args

    if not (1 <= len(args) <= 2):
        await update.message.reply_text(
            "Please follow command with wallet address",
            parse_mode="Markdown"
        )
        return
    
    wallet = args[0].lower()
    chain = args[1].lower() if len(args) == 2 else chains.get_chain(update.effective_message.message_thread_id)

    if not re.match(r'^0x[a-fA-F0-9]{40}$', wallet):
        await update.message.reply_text(
            "Please follow command with wallet address",
            parse_mode="Markdown"
        )
        return
    chain_info, error_message = chains.get_info(chain)
    if error_message:
        await update.message.reply_text(error_message)
        return
    
    message = await update.message.reply_text("Getting Wallet Info, Please wait...")
    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    native_price = etherscan.get_native_price(chain)
    eth = etherscan.get_native_balance(wallet, chain)
    dollar = float(eth) * float(native_price)
    x7r,_ = dextools.get_price(ca.X7R(chain), chain)
    x7dao,_ = dextools.get_price(ca.X7DAO(chain), chain)

    x7r_balance = etherscan.get_token_balance(wallet, ca.X7R(chain), chain)
    x7r_price = float(x7r_balance) * float(x7r)
    
    x7dao_balance = etherscan.get_token_balance(wallet, ca.X7DAO(chain), chain)
    x7dao_price = float(x7dao_balance) * float(x7dao)

    x7d_balance = etherscan.get_token_balance(wallet, ca.X7D(chain), chain)
    x7d_price = x7d_balance * native_price
    total = (
        x7d_price
        + x7r_price
        + x7dao_price
    )

    if x7dao_balance == 0:
        x7dao_percentage = 0
    else:
        x7dao_percentage = round(x7dao_balance / ca.SUPPLY * 100, 2)
    if x7r_balance == 0:
        x7r_percent = 0
    else:
        x7r_percent = round(x7r_balance / etherscan.get_x7r_supply(chain) * 100, 2)
    txs = etherscan.get_daily_tx_count(wallet, chain)
    
    await message.delete()
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            f"*X7 Finance Wallet Info ({chain_info.name})*\n\n"
            f"`{wallet}`\n\n"
            f"{float(eth):.3f} {chain_info.native.upper()} (${'{:0,.0f}'.format(dollar)})\n\n"
            f"{x7r_balance:,.0f} X7R {x7r_percent}% (${'{:0,.0f}'.format(x7r_price)})\n"
            f"{x7dao_balance:,.0f} X7DAO {x7dao_percentage}% (${'{:0,.0f}'.format(x7dao_price)})\n"
            f"{x7d_balance:.3f} X7D (${'{:0,.0f}'.format(x7d_price)})\n\n"
            f"{txs} tx's in the last 24 hours\n\n"
            f"Total X7 Finance token value ${'{:0,.0f}'.format(total)}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Wallet Link",
                        url=f"{chain_info.scan_address}{wallet}",
                    )
                ],
            ]
        ),
    )


async def website(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=media.WEBSITE_LOGO,
        caption=f"\n",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="X7Finance.org",
                        url=f"{urls.XCHANGE}",
                    )
                ],
            ]
        ),
    )


async def wei(update: Update, context: ContextTypes.DEFAULT_TYPE):
    eth = " ".join(context.args)
    if eth == "":
        await update.message.reply_text("Please follow the command with the amount of eth you wish to convert")
    else:
        wei = int(float(eth) * 10**18)
        await update.message.reply_text(
            f"{eth} ETH is equal to \n" f"`{wei}` wei", parse_mode="Markdown"
        )


async def wp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        text=f"*X7 Finance Whitepaper Quote*\n\n{random.choice(text.QUOTES)}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text="Website", url=f"{urls.XCHANGE}")],
                [InlineKeyboardButton(text="Full WP", url=f"{urls.WP_LINK}")],
            ]
        ),
    )


async def x7d(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(update.effective_message.message_thread_id)
    chain_info, error_message = chains.get_info(chain)
    if error_message:
        await update.message.reply_text(error_message)
        return
    
    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    
    chain_lpool = ca.LPOOL(chain)
    native_price = etherscan.get_native_price(chain)
    lpool_reserve = etherscan.get_native_balance(ca.LPOOL_RESERVE(chain), chain)
    lpool_reserve_dollar = (float(lpool_reserve) * float(native_price))
    lpool = etherscan.get_native_balance(chain_lpool, chain)
    lpool_dollar = (float(lpool) * float(native_price))
    dollar = lpool_reserve_dollar + lpool_dollar
    supply = round(float(lpool_reserve) + float(lpool), 2)
    lpool_rounded = round(float(lpool), 2)
    lpool_reserve_rounded = round(float(lpool_reserve), 2)
    info = dextools.get_token_info(ca.X7D(chain), chain)
    holders = info["holders"]

    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            f"*X7D ({chain_info.name}) Info*\n\n"
            f"Holders: {holders}\n\n"
            f'Lending Pool:\n{lpool_rounded} X7D (${"{:0,.0f}".format(lpool_dollar)})\n\n'
            f'Lending Pool Reserve:\n{lpool_reserve_rounded} X7D (${"{:0,.0f}".format(lpool_reserve_dollar)})\n\n'
            f'Total Supply:\n{supply} X7D (${"{:0,.0f}".format(dollar)})',
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="X7D Funding Dashboard",
                        url=f"{urls.XCHANGE}fund",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=chain_info.scan_name,
                        url=f"{chain_info.scan_token + ca.X7D(chain)}",
                    )
                ],
            ]
        ),
    )


async def x7dao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(update.effective_message.message_thread_id)
    chain_info, error_message = chains.get_info(chain,token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return
    
    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    chain_pair = tokens.TOKENS["X7DAO"].get(chain).pairs
    info = dextools.get_token_info(ca.X7DAO(chain), chain)
    holders = info["holders"]
    market_cap = info["mcap"]
    price, price_change = dextools.get_price(ca.X7DAO(chain), chain)
    volume = dextools.get_volume(chain_pair, chain)
    liquidity_data = dextools.get_liquidity(chain_pair, chain)
    liquidity = liquidity_data["total"]
    if liquidity == "0":
        liquidity = "N/A"
    if chain == "eth":
        ath_data = coingecko.get_ath("x7dao")
        if ath_data:
            ath_change = f'{ath_data[1]}'
            ath_value = ath_data[0]
            ath = f'${ath_value} (${"{:0,.0f}".format(ath_value * etherscan.get_x7r_supply(chain))}) {ath_change[:3]}%'
        else:
            ath = "Unavailable"    
    else:
        ath = "Unavailable"    
    
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            f"*X7DAO Info ({chain_info.name})*\n\n"
            f"💰 Price: {price}\n"
            f'💎 Market Cap:  {market_cap}\n'
            f"📊 24 Hour Volume: {volume}\n"
            f"💦 Liquidity: {liquidity}\n"
            f"👪 Holders: {holders}\n"
            f"🔝 ATH: {ath}\n\n"
            f"{price_change}\n\n"
            f"Contract Address:\n`{ca.X7DAO(chain)}`",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text=chain_info.scan_name, url=f"{chain_info.scan_token}{ca.X7DAO(chain)}")],
                [InlineKeyboardButton(text="Chart", url=f"{urls.DEX_TOOLS(chain_info.dext)}{ca.X7DAO(chain)}")],
                [InlineKeyboardButton(text="Buy", url=f"{urls.XCHANGE_BUY(chain_info.id, ca.X7DAO(chain))}")],
            ]
        ),
    )


async def x7r(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(update.effective_message.message_thread_id)
    chain_info, error_message = chains.get_info(chain,token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return
    
    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    chain_pair = tokens.TOKENS["X7R"].get(chain).pairs
    info = dextools.get_token_info(ca.X7R(chain), chain)
    holders = info["holders"]
    market_cap = info["mcap"]
    price, price_change = dextools.get_price(ca.X7R(chain), chain)
    volume = dextools.get_volume(chain_pair, chain)
    liquidity_data = dextools.get_liquidity(chain_pair, chain)
    liquidity = liquidity_data["total"]
    if liquidity == "0":
        liquidity = "N/A"
    if chain == "eth":
        ath_data = coingecko.get_ath("x7r")
        if ath_data:
            ath_change = f'{ath_data[1]}'
            ath_value = ath_data[0]
            ath = f'${ath_value} (${"{:0,.0f}".format(ath_value * etherscan.get_x7r_supply(chain))}) {ath_change[:3]}%'
        else:
            ath = "Unavailable"    
    else:
        ath = "Unavailable"        
    
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            f"*X7R Info ({chain_info.name})*\n\n"
            f"💰 Price: {price}\n"
            f'💎 Market Cap:  {market_cap}\n'
            f"📊 24 Hour Volume: {volume}\n"
            f"💦 Liquidity: {liquidity}\n"
            f"👪 Holders: {holders}\n"
            f"🔝 ATH: {ath}\n"
            f"{price_change}\n\n"
            f"Contract Address:\n`{ca.X7R(chain)}`",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text=chain_info.scan_name, url=f"{chain_info.scan_token}{ca.X7R(chain)}")],
                [InlineKeyboardButton(text="Chart", url=f"{urls.DEX_TOOLS(chain_info.dext)}{ca.X7R(chain)}")],
                [InlineKeyboardButton(text="Buy", url=f"{urls.XCHANGE_BUY(chain_info.id, ca.X7R(chain))}")],
            ]
        ),
    )


async def x7101(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(update.effective_message.message_thread_id)
    chain_info, error_message = chains.get_info(chain,token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return
    
    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    chain_pair = tokens.TOKENS["X7101"].get(chain).pairs
    info = dextools.get_token_info(ca.X7101(chain), chain)
    holders = info["holders"]
    market_cap = info["mcap"]
    price, price_change = dextools.get_price(ca.X7101(chain), chain)
    volume = dextools.get_volume(chain_pair, chain)
    liquidity_data = dextools.get_liquidity(chain_pair, chain)
    liquidity = liquidity_data["total"]
    if liquidity == "0":
        liquidity = "N/A"
    if chain == "eth":
        ath_data = coingecko.get_ath("x7101")
        if ath_data:
            ath_change = f'{ath_data[1]}'
            ath_value = ath_data[0]
            ath = f'${ath_value} (${"{:0,.0f}".format(ath_value * ca.SUPPLY)}) {ath_change[:3]}%'
        else:
            ath = "Unavailable"      
    else:
        ath = "Unavailable"        
    
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            f"*X7101 Info ({chain_info.name})*\n\n"
            f"💰 Price: {price}\n"
            f'💎 Market Cap:  {market_cap}\n'
            f"📊 24 Hour Volume: {volume}\n"
            f"💦 Liquidity: {liquidity}\n"
            f"👪 Holders: {holders}\n"
            f"🔝 ATH: {ath}\n\n"
            f"{price_change}\n\n"
            f"Contract Address:\n`{ca.X7101(chain)}`",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text=chain_info.scan_name, url=f"{chain_info.scan_token}{ca.X7101(chain)}")],
                [InlineKeyboardButton(text="Chart", url=f"{urls.DEX_TOOLS(chain_info.dext)}{ca.X7101(chain)}")],
                [InlineKeyboardButton(text="Buy", url=f"{urls.XCHANGE_BUY(chain_info.id, ca.X7101(chain))}")],
            ]
        ),
    )


async def x7102(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(update.effective_message.message_thread_id)
    chain_info, error_message = chains.get_info(chain,token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return
    
    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    
    chain_pair = tokens.TOKENS["X7102"].get(chain).pairs
    info = dextools.get_token_info(ca.X7102(chain), chain)
    holders = info["holders"]
    market_cap = info["mcap"]
    price, price_change = dextools.get_price(ca.X7102(chain), chain)
    volume = dextools.get_volume(chain_pair, chain)
    liquidity_data = dextools.get_liquidity(chain_pair, chain)
    liquidity = liquidity_data["total"]
    if liquidity == "0":
        liquidity = "N/A"
    if chain == "eth":
        ath_data = coingecko.get_ath("x7102")
        if ath_data:
            ath_change = f'{ath_data[1]}'
            ath_value = ath_data[0]
            ath = f'${ath_value} (${"{:0,.0f}".format(ath_value * ca.SUPPLY)}) {ath_change[:3]}%'
        else:
            ath = "Unavailable"     
    else:
        ath = "Unavailable"        
    
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            f"*X7102 Info ({chain_info.name})*\n\n"
            f"💰 Price: {price}\n"
            f'💎 Market Cap:  {market_cap}\n'
            f"📊 24 Hour Volume: {volume}\n"
            f"💦 Liquidity: {liquidity}\n"
            f"👪 Holders: {holders}\n"
            f"🔝 ATH: {ath}\n\n"
            f"{price_change}\n\n"
            f"Contract Address:\n`{ca.X7102(chain)}`",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text=chain_info.scan_name, url=f"{chain_info.scan_token}{ca.X7102(chain)}")],
                [InlineKeyboardButton(text="Chart", url=f"{urls.DEX_TOOLS(chain_info.dext)}{ca.X7102(chain)}")],
                [InlineKeyboardButton(text="Buy", url=f"{urls.XCHANGE_BUY(chain_info.id, ca.X7102(chain))}")],
            ]
        ),
    )


async def x7103(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(update.effective_message.message_thread_id)
    chain_info, error_message = chains.get_info(chain,token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return
    
    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    
    chain_pair = tokens.TOKENS["X7103"].get(chain).pairs
    info = dextools.get_token_info(ca.X7103(chain), chain)
    holders = info["holders"]
    market_cap = info["mcap"]
    price, price_change = dextools.get_price(ca.X7103(chain), chain)
    volume = dextools.get_volume(chain_pair, chain)
    liquidity_data = dextools.get_liquidity(chain_pair, chain)
    liquidity = liquidity_data["total"]
    if liquidity == "0":
        liquidity = "N/A"
    if chain == "eth":
        ath_data = coingecko.get_ath("x7103")
        if ath_data:
            ath_change = f'{ath_data[1]}'
            ath_value = ath_data[0]
            ath = f'${ath_value} (${"{:0,.0f}".format(ath_value * ca.SUPPLY)}) {ath_change[:3]}%'
        else:
            ath = "Unavailable"   
    else:
        ath = "Unavailable"        
    
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            f"*X7103 Info ({chain_info.name})*\n\n"
            f"💰 Price: {price}\n"
            f'💎 Market Cap:  {market_cap}\n'
            f"📊 24 Hour Volume: {volume}\n"
            f"💦 Liquidity: {liquidity}\n"
            f"👪 Holders: {holders}\n"
            f"🔝 ATH: {ath}\n\n"
            f"{price_change}\n\n"
            f"Contract Address:\n`{ca.X7103(chain)}`",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text=chain_info.scan_name, url=f"{chain_info.scan_token}{ca.X7103(chain)}")],
                [InlineKeyboardButton(text="Chart", url=f"{urls.DEX_TOOLS(chain_info.dext)}{ca.X7103(chain)}")],
                [InlineKeyboardButton(text="Buy", url=f"{urls.XCHANGE_BUY(chain_info.id, ca.X7103(chain))}")],
            ]
        ),
    )


async def x7104(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(update.effective_message.message_thread_id)
    chain_info, error_message = chains.get_info(chain,token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return
    
    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    
    chain_pair = tokens.TOKENS["X7104"].get(chain).pairs
    info = dextools.get_token_info(ca.X7104(chain), chain)
    holders = info["holders"]
    market_cap = info["mcap"]
    price, price_change = dextools.get_price(ca.X7104(chain), chain)
    volume = dextools.get_volume(chain_pair, chain)
    liquidity_data = dextools.get_liquidity(chain_pair, chain)
    liquidity = liquidity_data["total"]
    if liquidity == "0":
        liquidity = "N/A"
    if chain == "eth":
        ath_data = coingecko.get_ath("x7104")
        if ath_data:
            ath_change = f'{ath_data[1]}'
            ath_value = ath_data[0]
            ath = f'${ath_value} (${"{:0,.0f}".format(ath_value * ca.SUPPLY)}) {ath_change[:3]}%'
        else:
            ath = "Unavailable"   
    else:
        ath = "Unavailable"        
    
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            f"*X7104 Info ({chain_info.name})*\n\n"
            f"💰 Price: {price}\n"
            f'💎 Market Cap:  {market_cap}\n'
            f"📊 24 Hour Volume: {volume}\n"
            f"💦 Liquidity: {liquidity}\n"
            f"👪 Holders: {holders}\n"
            f"🔝 ATH: {ath}\n\n"
            f"{price_change}\n\n"
            f"Contract Address:\n`{ca.X7104(chain)}`",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text=chain_info.scan_name, url=f"{chain_info.scan_token}{ca.X7104(chain)}")],
                [InlineKeyboardButton(text="Chart", url=f"{urls.DEX_TOOLS(chain_info.dext)}{ca.X7104(chain)}")],
                [InlineKeyboardButton(text="Buy", url=f"{urls.XCHANGE_BUY(chain_info.id, ca.X7104(chain))}")],
            ]
        ),
    )


async def x7105(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chain = " ".join(context.args).lower() or chains.get_chain(update.effective_message.message_thread_id)
    chain_info, error_message = chains.get_info(chain,token=True)
    if error_message:
        await update.message.reply_text(error_message)
        return
    
    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    
    chain_pair = tokens.TOKENS["X7105"].get(chain).pairs
    info = dextools.get_token_info(ca.X7105(chain), chain)
    holders = info["holders"]
    market_cap = info["mcap"]
    price, price_change = dextools.get_price(ca.X7105(chain), chain)
    volume = dextools.get_volume(chain_pair, chain)
    liquidity_data = dextools.get_liquidity(chain_pair, chain)
    liquidity = liquidity_data["total"]
    if liquidity == "0":
        liquidity = "N/A"
    if chain == "eth":
        ath_data = coingecko.get_ath("x7105")
        if ath_data:
            ath_change = f'{ath_data[1]}'
            ath_value = ath_data[0]
            ath = f'${ath_value} (${"{:0,.0f}".format(ath_value * ca.SUPPLY)}) {ath_change[:3]}%'
        else:
            ath = "Unavailable"   
    else:
        ath = "Unavailable"          
    
    await update.message.reply_photo(
        photo=api.get_random_pioneer(),
        caption=
            f"*X7105 Info* ({chain_info.name})\n\n"
            f"💰 Price: {price}\n"
            f'💎 Market Cap:  {market_cap}\n'
            f"📊 24 Hour Volume: {volume}\n"
            f"💦 Liquidity: {liquidity}\n"
            f"👪 Holders: {holders}\n"
            f"🔝 ATH: {ath}\n\n"
            f"{price_change}\n\n"
            f"Contract Address:\n`{ca.X7105(chain)}`",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text=chain_info.scan_name, url=f"{chain_info.scan_token}{ca.X7105(chain)}")],
                [InlineKeyboardButton(text="Chart", url=f"{urls.DEX_TOOLS(chain_info.dext)}{ca.X7105(chain)}")],
                [InlineKeyboardButton(text="Buy", url=f"{urls.XCHANGE_BUY(chain_info.id, ca.X7105(chain))}")],
            ]
        ),
    )

async def x(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        if len(context.args) > 1:
            search = " ".join(context.args[:-1])
            chain_name = context.args[-1].lower()
        
            if chain_name in chains.CHAINS:
                chain = chains.CHAINS[chain_name].name.lower()
            else:
                search = " ".join(context.args)
                chain = None
        else: 
            search = " ".join(context.args)
            chain = None
    else:
        await update.message.reply_text(
            f"Please provide Contract Address/Project Name and optional chain name",
    )
        return
    await pricebot.command(update, context, search, chain)
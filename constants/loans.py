# LOANS

import math
from constants import ca, chains


class LoanTerm:
    def __init__(
        self,
        ca,
        name,
        min_loan,
        max_loan,
        num_premium_periods,
        min_loan_duration,
        max_loan_duration,
        loan_origination_fee,
    ):
        self.name = name
        self.ca = ca
        self.min_loan = min_loan
        self.max_loan = max_loan
        self.num_premium_periods = num_premium_periods
        self.min_loan_duration = min_loan_duration
        self.max_loan_duration = max_loan_duration
        self.loan_origination_fee = loan_origination_fee

    def generate_terms(self, chain):
        if chain in chains.CHAINS:
            chain_native = chains.CHAINS[chain].token
        return (
            f"> Min Loan: {self.min_loan} {chain_native.upper()}\n"
            f"> Max Loan: {self.max_loan} {chain_native.upper()}\n"
            f"> Min Loan Duration: {math.floor(self.min_loan_duration / 84600)} days\n"
            f"> Max Loan Duration: {math.floor(self.max_loan_duration / 84600)} days \n\n"
            f"> Loan Origination Fee:\n{self.loan_origination_fee / 100}% of borrowed capital, payable within the transaction for adding initial liquidity\n\n"
            f"> Number of premium payments: {self.num_premium_periods}\n\n"
            f"> Principal Repayment Condition:\nPrincipal must be returned by the end of the loan term.\n\n"
            f"> Liquidation conditions:\nFailure to pay a premium payment by its due date or repay the principal by the end of the loan term will make the loan eligible for liquidation.\n\n")


def LOANS(chain): 
    return {
    "ill001": LoanTerm(
        ca.ILL001(chain),
        "X7 Initial Liquidity Loan (001) - X7ILL001",
        0.5,
        5,
        0,
        86400,
        2419200,
        2500
    ),
    "ill003": LoanTerm(
        ca.ILL003(chain),
        "X7 Initial Liquidity Loan (003) - X7ILL003",
        0.5,
        5,
        4,
        86400,
        2419200,
        1500
    ),
    "ill004": LoanTerm(
        ca.ILL004(chain),
        "X7 Initial Liquidity Loan (004) - X7ILL004",
        0.5,
        5,
        0,
        2419200,
        86400,
        200
    )
    
}

def loans_list(chain):
    loan_list = []
    for loan_key, loan_term in LOANS(chain).items():
        loan_list.append(f"{loan_key}")
    return ",".join(loan_list)


def OVERVIEW(chain):
    return (
    "*X7 Finance Loan Terms*\n\n"
    f"Use /loans {loans_list(chain)} for more details on individual loan contracts\n\n"
    "Loan terms are defined by standalone smart contracts that provide the following:\n\n"
    "1. Loan origination fee\n"
    "2. Loan retention premium fee schedule\n"
    "3. Principal repayment condition/maximum loan duration\n"
    "4. Liquidation conditions and Reward\n"
    "5. Loan duration\n\n"
    "The lending process delegates the loan terms to standalone smart contracts (see whitepaper below for "
    "more details). These loan terms contracts must be deployed, and then “added” or “removed” from the "
    "Lending Pool as “available” loan terms for new loans. The DAO will be able to add or remove these term "
    "contracts.\n\nLoan term contracts may be created by any interested third party, enabling a market "
    "process by which new loan terms may be invented, provided they implement the proper interface."
)

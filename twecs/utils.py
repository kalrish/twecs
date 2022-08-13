import math


def calculate_monthly_payment(
	amount: float,
	months: int,
	decimals: int = 2,
):
	factor = 10 ** decimals
	unrounded_monthly_amount = amount / months
	rounded_monthly_amount = math.ceil(
		unrounded_monthly_amount * factor,
	) / factor
	return rounded_monthly_amount

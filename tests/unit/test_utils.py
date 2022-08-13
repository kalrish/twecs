import twecs.utils


class TestComputeMonthlyAmount:
	def test_round_up(
		self,
	):
		calculated_monthly_payment = twecs.utils.calculate_monthly_payment(
			amount=10,
			decimals=2,
			months=3,
		)
		minimum_monthly_payment = 3.34
		assert calculated_monthly_payment >= minimum_monthly_payment

	def test_installments_cover_total(
		self,
	):
		amount = 100
		installments = 7
		calculated_monthly_payment = twecs.utils.calculate_monthly_payment(
			amount=amount,
			decimals=2,
			months=installments,
		)
		assert installments * calculated_monthly_payment >= amount

# PEP 8 stipulates[1] that imports be grouped such that modules from Python's standard library, such as `logging`, be imported before modules from third parties, such as `requests`.
# 1: https://peps.python.org/pep-0008/#imports

import logging

import init


logger = logging.getLogger(
	__name__,
)


def aws_lambda_handler(
	event,
	context,
):
	logger.debug(
		"Wise API host: %s",
		init.Wise_currency_exchange_scheduler.API_host,
	)
	logger.debug(
		"Wise profile ID: %s",
		init.Wise_profile_ID,
	)
	init.Wise_currency_exchange_scheduler.set_up_currency_conversion(
		profile_ID=init.Wise_profile_ID,
		**event,
	)

# AWS Lambda executes the so-called "INIT code" when a new execution environment is run for the first time[1]; if an execution environment has been run already, AWS Lambda does not initialize it again. This Python module contains objects that can be cached across invocations of the AWS Lambda function and should not be initialized in each of its invocations. It also carries out initialization routines.
# 1: https://docs.aws.amazon.com/lambda/latest/operatorguide/static-initialization
# initialization routines that should be invoked only once for each AWS Lambda execution environment

import logging
import os

import boto3

import wise


def set_up_logging(
):
	root_logger = logging.getLogger(
		name=None,
	)
	logging_level = getattr(
		logging,
		os.environ["logging_level"],
	)
	root_logger.setLevel(
		logging_level,
	)
	formatter = logging.Formatter(
		fmt="%(name)s: %(levelname)s: %(message)s",
		style="%",
	)
	for handler in root_logger.handlers:
		handler.setFormatter(
			formatter,
		)


def retrieve_Wise_API_token(
):
	Wise_API_token_secret_ARN = os.environ["Wise_API_token_secret_ARN"]
	secret = boto3_secretsmanager.get_secret_value(
		SecretId=Wise_API_token_secret_ARN,
	)
	Wise_API_token = secret["SecretString"]
	logger.debug(
		"retrieved Wise API token ending in %s from secret with ARN %s",
		Wise_API_token[-4:],
		Wise_API_token_secret_ARN,
	)
	return Wise_API_token


def retrieve_Wise_profile_ID(
):
	Wise_profile_ID_parameter_name = os.environ["Wise_profile_ID_parameter_name"]
	parameter = boto3_ssm.get_parameter(
		Name=Wise_profile_ID_parameter_name,
	)
	Wise_profile_ID = parameter["Parameter"]["Value"]
	logger.debug(
		"retrieved Wise profile ID %s from parameter %s",
		Wise_profile_ID,
		Wise_profile_ID_parameter_name,
	)
	return Wise_profile_ID


set_up_logging(
)

logger = logging.getLogger(
	__name__,
)

logger.debug(
	"running in a new Lambda execution environment (cold start); carrying out cacheable initialization procedures",
)

boto3_session = boto3.session.Session(
)
boto3_secretsmanager = boto3_session.client(
	"secretsmanager",
)
boto3_ssm = boto3_session.client(
	"ssm",
)

Wise_API_host = os.environ["Wise_API_host"]
Wise_profile_ID = retrieve_Wise_profile_ID(
)

# Preserving a `requests.Session` object across multiple invocations of the Lambda function might enable the use of the HTTP connection pool, thereby reducing invocation times.
Wise_currency_exchange_scheduler = wise.CurrencyExchangeScheduler(
	API_host=Wise_API_host,
	# Getting the Wise API token as part of the "INIT code" is a double-edged sword[1]: on warm starts it reduces the execution time of the Lambda function as well as the cost it incurs for its usage of the AWS Secrets Manager API[2], but it renders existing execution environments unaware of API token updates. Fetching the Wise API token again whenever the Wise API responded with an HTTP 403 would help only whenever the API token expired und was regenerated. If, instead, its usage is no longer wished, the user must not remove it from Secrets Manager, but revoke it altogether.
	# 1: https://en.wiktionary.org/wiki/double-edged_sword
	# 2: https://aws.amazon.com/secrets-manager/pricing/
	API_token=retrieve_Wise_API_token(
	),
)

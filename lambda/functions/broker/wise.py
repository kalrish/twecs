import logging
import uuid

import requests


logger = logging.getLogger(
	__name__,
)


def requests_response_hook(
	response,
	*args,
	**kwargs,
):
	logger.debug(
		"response: %s",
		response.text,
	)


class CurrencyExchangeScheduler:
	def __init__(
		self,
		API_host,
		API_token,
	):
		self.requests_session = requests.Session(
		)
		self.requests_session.headers["Authorization"] = "Bearer " + API_token
		self.requests_session.hooks["response"].append(
			requests_response_hook,
		)
		self.API_host = API_host
		logger.debug(
			"initialized Wise API connection object",
		)

	def set_up_currency_conversion(
		self,
		amount,
		amount_fix_side,
		profile_ID,
		reference,
		source_currency,
		target_currency,
	):
		# response = self.requests_session.get(
		# 	f"https://{API_host}/v2/profiles",
		# )
		# if response.status_code == requests.codes.ok:
		# 	profiles = response.json(
		# 	)

		# 	personal_profile_id = None

		# 	for profile in profiles:
		# 		if profile["type"] == "personal":
		# 			personal_profile_id = profile["id"]

		# 			logger.debug(
		# 				"ID of personal profile: %i",
		# 				personal_profile_id,
		# 			)

		# 			break

		# 	assert personal_profile_id

		# 	profile_id = personal_profile_id

		# 	logger.debug(
		# 		"using profile ID %i",
		# 		profile_id,
		# 	)

		# https://api-docs.wise.com/multi-currency-accounts#multi-currency-accounts-get-multi-currency-account
		response = self.requests_session.get(
			f"https://{self.API_host}/v4/profiles/{profile_ID}/multi-currency-account",
		)
		if response.status_code == requests.codes.ok:
			response_data = response.json(
			)
			recipient_ID = response_data["recipientId"]
			logger.debug(
				"got recipient ID %s for profile ID %s",
				recipient_ID,
				profile_ID,
			)

			# https://api-docs.wise.com/#quotes-create
			response = self.requests_session.post(
				f"https://{self.API_host}/v3/profiles/{profile_ID}/quotes",
				json={
					"preferredPayIn": "BANK_TRANSFER",
					"sourceCurrency": source_currency,
					# The request parameter `targetAccount` is not required, but it saves a subsequent PATCH request
					"targetAccount": recipient_ID,
					"targetCurrency": target_currency,
					amount_fix_side + "Amount": amount,
				},
			)
			if response.status_code == requests.codes.ok:
				response_data = response.json(
				)
				quote_ID = response_data["id"]
				currency_conversion_rate = response_data["rate"]
				logger.debug(
					"quote created under ID %s at rate %f",
					quote_ID,
					currency_conversion_rate,
				)

				payment_options = response_data["paymentOptions"]
				payment_option_bank_transfer = next(
					payment_option
					for payment_option in payment_options
					if payment_option["payIn"] == "BANK_TRANSFER"
				)
				assert payment_option_bank_transfer["disabled"] is False
				assert payment_option_bank_transfer["payOut"] == "BALANCE"
				source_amount_via_bank_transfer = payment_option_bank_transfer["sourceAmount"]
				logger.info(
					"funding quote %s via bank transfer requires %s %.2f",
					quote_ID,
					source_currency,
					source_amount_via_bank_transfer,
				)

				transfer_creation_uuid = uuid.uuid4(
				)
				transfer_creation_identifier = str(
					transfer_creation_uuid,
				)
				logger.debug(
					"transfer creation idempotency identifier: %s",
					transfer_creation_identifier,
				)
				# https://api-docs.wise.com/multi-currency-accounts#transfers-create
				response = self.requests_session.post(
					f"https://{self.API_host}/v1/transfers",
					json={
						"customerTransactionId": transfer_creation_identifier,
						"details": {
							"reference": reference,
						},
						"quoteUuid": quote_ID,
						"targetAccount": recipient_ID,
					},
				)
				if response.status_code == requests.codes.ok:
					response_data = response.json(
					)
					transfer_ID = response_data["id"]
					logger.debug(
						"transfer set up under ID %s",
						transfer_ID,
					)

					response = self.requests_session.get(
						f"https://{self.API_host}/v1/profiles/{profile_ID}/transfers/{transfer_ID}/deposit-details/bank-transfer",
					)
					if response.status_code == requests.codes.ok:
						response_data = response.json(
						)
						payment_details = response_data["payinBankAccount"]["details"]
						IBAN = next(
							payment_detail["value"]
							for payment_detail in payment_details
							if payment_detail["type"] == "iban"
						)
						BIC = next(
							payment_detail["value"]
							for payment_detail in payment_details
							if payment_detail["type"] == "bic"
						)
						logger.info(
							"%s %.2f must be transferred into the escrow account with the IBAN %s and the BIC %s to fund the transfer %s",
							response_data["payinBankAccount"]["currency"],
							source_amount_via_bank_transfer,
							IBAN,
							BIC,
							transfer_ID,
						)
					else:
						logger.warning(
							"cannot get deposit details for transfer %s",
							transfer_ID,
						)
				else:
					logger.error(
						"cannot set up transfer",
					)
			else:
				logger.error(
					"cannot create Wise quote",
				)
		else:
			logger.error(
				"cannot get recipient ID for profile ID %s",
				profile_ID,
			)

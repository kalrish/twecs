#!/usr/bin/env node


import "source-map-support/register";
import * as cdk from "aws-cdk-lib";

import {
	CoreStack,
	CurrencyConversionAmountFixSide,
	CurrencyConversionScheduleStack,
	WiseEnvironment,
} from "../lib/twecs";


function compute_monthly_amount(
	amount: number,
	term_in_months: number,
)
{
	const amount_monthly = amount / term_in_months
	const factor = 10 ** 2
	const foo = amount_monthly * factor
	const bar = Math.ceil(
		foo,
	)
	const dfd = bar / factor
	return dfd
}


const env = {
	account: "659664769788",
	region: "us-east-1",
};
const app = new cdk.App(
);

const Wise_profile_IDs = {
	[WiseEnvironment.Live]: "13914146",
	[WiseEnvironment.Sandbox]: "16206006",
}
const core_stack = new CoreStack(
	app,
	"wise-cec",
	{
		description: "currency exchanges through Wise",
		env: env,
		environment: WiseEnvironment.Sandbox,
		tags: {
			purpose: "scheduled currency exchanges",
		},
		Wise_profile_ID: Wise_profile_IDs[WiseEnvironment.Sandbox],
	},
);

const first_of_month = cdk.aws_events.Schedule.cron(
	{
		day: "1",
		hour: "5",
		minute: "0",
	},
);
const schedules = {
	fastmail: {
		amount: compute_monthly_amount(
			166.60,
			3 * 12, // three years
		),
		amount_fix_side: CurrencyConversionAmountFixSide.Target,
		reference: "Fastmail",
		schedule: first_of_month,
		source_currency: "EUR",
		target_currency: "USD",
	},
	foreignaffairs: {
		amount: compute_monthly_amount(
			74.95,
			1 * 12, // one year
		),
		amount_fix_side: CurrencyConversionAmountFixSide.Target,
		reference: "Foreign Affairs",
		schedule: first_of_month,
		source_currency: "EUR",
		target_currency: "USD",
	},
	/*
	lwn: {
		reference: "Todoist",
		schedule: first_of_month,
		source_currency: "EUR",
		target_amount: round(
			70,
			10, // ten months
		),
		target_currency: "USD",
	},
	*/
	todoist: {
		amount: compute_monthly_amount(
			36,
			1 * 12, // one year
		),
		amount_fix_side: CurrencyConversionAmountFixSide.Target,
		reference: "Todoist",
		schedule: first_of_month,
		source_currency: "EUR",
		target_currency: "USD",
	},
};

let schedule_codename : keyof typeof schedules;
for ( schedule_codename in schedules ) {
	const schedule_data = schedules[schedule_codename];
	/*
	core_stack.addSchedule(
		`wise-schedule-${schedule_codename}`,
		schedule_data,
	);
	*/
	new CurrencyConversionScheduleStack(
		app,
		`wise-cec-schedule-${schedule_codename}`,
		{
			description: `scheduled ${schedule_data['source_currency']} to ${schedule_data['target_currency']} exchanges for ${schedule_data['reference']} through Wise`,
			env: env,
			handler: core_stack.currency_conversion_scheduling_function,
			... schedule_data,
		},
	);
}

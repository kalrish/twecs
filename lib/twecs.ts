import * as aws_cdk from "aws-cdk-lib";
import * as aws_cdk_constructs from "constructs";
import * as aws_events from "aws-cdk-lib/aws-events";
import * as aws_events_targets from "aws-cdk-lib/aws-events-targets";
import * as aws_lambda from "aws-cdk-lib/aws-lambda";
import * as aws_lambda_python from "@aws-cdk/aws-lambda-python-alpha";
import * as aws_secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import * as aws_ssm from 'aws-cdk-lib/aws-ssm';


/*
export interface WiseCurrencyConversionSchedulesProps {
	schedules: Array<CurrencyConversionScheduleStackProps>;
}

export class WiseCurrencyConversionSchedules extends constructs.Construct {
	constructor(
		scope: constructs.Construct,
		id: string,
		props: WiseCurrencyConversionSchedulesProps,
	)
	{
		super(
			scope,
			id,
		);
	}
}
*/


export enum LoggingLevels {
	debug = "DEBUG",
	error = "ERROR",
	info = "INFO",
	warning = "WARNING",
}

// https://api-docs.wise.com/
export enum WiseEnvironment {
	Live = "api.transferwise.com",
	Sandbox = "api.sandbox.transferwise.tech",
}

export interface CoreStackProps extends aws_cdk.StackProps {
	environment: WiseEnvironment;
	logging_level?: LoggingLevels,
	Wise_profile_ID: string,
}

export class CoreStack extends aws_cdk.Stack {
	public readonly currency_conversion_scheduling_function: aws_lambda.Function;

	constructor(
		scope: aws_cdk_constructs.Construct,
		id: string,
		props: CoreStackProps,
	)
	{
		super(
			scope,
			id,
			props,
		);

		const Wise_API_token_secret = new aws_secretsmanager.Secret(
			this,
			"WiseApiToken",
			{
				description: "token for Wise API",
			}
		)

		const Wise_profile_ID_parameter = new aws_ssm.StringParameter(
			this,
			"WiseProfileId",
			{
				description: "Wise profile ID",
				// parameterName: "/wise/cec/",
				stringValue: props.Wise_profile_ID,
			}
		)

		this.currency_conversion_scheduling_function = new aws_lambda_python.PythonFunction(
			this,
			"CurrencyConversionScheduler",
			{
				architecture: aws_lambda.Architecture.ARM_64,
				description: "scheduled currency conversions with Wise",
				entry: "lambda/functions/wise/",
				environment: {
					logging_level: props.logging_level ? props.logging_level : LoggingLevels.info,
					Wise_API_host: props.environment,
					Wise_API_token_secret_ARN: Wise_API_token_secret.secretArn,
					Wise_profile_ID_parameter_name: Wise_profile_ID_parameter.parameterName,
				},
				handler: "aws_lambda_handler",
				index: "index.py",
				// 128 MB is the minimum amount of memory that can be allocated to a Lambda function
				memorySize: 128,
				runtime: aws_lambda.Runtime.PYTHON_3_9,
				// Setting up a currency conversion on Wise programmatically should not take more than a few seconds
				timeout: aws_cdk.Duration.seconds(
					15,
				),
			},
		);

		Wise_API_token_secret.grantRead(
			this.currency_conversion_scheduling_function,
		)
		Wise_profile_ID_parameter.grantRead(
			this.currency_conversion_scheduling_function,
		)

		new aws_lambda_python.PythonFunction(
			this,
			"QrCodeGenerator",
			{
				architecture: aws_lambda.Architecture.ARM_64,
				entry: "lambda/functions/qrcode/",
				handler: "aws_lambda_handler",
				index: "index.py",
				// 128 MB is the minimum amount of memory that can be allocated to a Lambda function
				memorySize: 128,
				runtime: aws_lambda.Runtime.PYTHON_3_9,
				// Encoding a QR code should not take more than half a minute
				timeout: aws_cdk.Duration.seconds(
					30,
				),
			},
		)
	}
}


export enum CurrencyConversionAmountFixSide {
	Source = "source",
	Target = "target",
}

export interface CurrencyConversionScheduleStackProps extends aws_cdk.StackProps {
	amount: number;
	amount_fix_side: CurrencyConversionAmountFixSide,
	handler: aws_lambda.IFunction;
	reference: string;
	schedule: aws_events.Schedule;
	source_currency: string;
	target_currency: string;
}

export class CurrencyConversionScheduleStack extends aws_cdk.Stack {
	constructor(
		scope: aws_cdk_constructs.Construct,
		id: string,
		props: CurrencyConversionScheduleStackProps,
	)
	{
		super(
			scope,
			id,
			props,
		);

		const rule = new aws_events.Rule(
			this,
			"Rule",
			{
				schedule: props.schedule,
			},
		);

		const event_data = {
			amount: props.amount,
			amount_fix_side: props.amount_fix_side,
			reference: props.reference,
			source_currency: props.source_currency,
			target_currency: props.target_currency,
		};

		const target = new aws_events_targets.LambdaFunction(
			props.handler,
			{
				event: aws_events.RuleTargetInput.fromObject(
					event_data,
				),
			},
		);

		rule.addTarget(
			target,
		);
	}
}

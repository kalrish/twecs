set -e

export \
	AWS_PROFILE=personal \
	#

python_version="$(
	yq \
		-r \
		.python_version \
		-- \
		config/config.yaml \
		#
)"

function package
{
	layer="$1"
	dir="$2"

	git_commit_id="$(
		yq \
			-r \
			.parameters.GitCommitId \
			-- \
			"config/layers/${layer}.yaml" \
			#
	)"

	bash \
		-- \
		~/dev/own/aws-lambda-python-pack/script.sh \
		"${HOME}/dev/twecs/${dir}" \
		"${git_commit_id}" \
		"${repository_bucket}" \
		"${python_version}" \
		#
}

sceptre \
	--var-file secrets/prod.yaml \
	launch \
	--yes \
	-- \
	repository.yaml \
	#

repository_bucket="$(
	sceptre \
		--output json \
		--var-file secrets/prod.yaml \
		list \
		outputs \
		repository.yaml \
		| \
		jq \
		-r \
		'.[0].repository[] | select(.OutputKey == "BucketName").OutputValue' \
		#
)"

package \
	core \
	aws-lambda \
	#
package \
	wise \
	wise \
	#

sceptre \
	--var-file secrets/prod.yaml \
	launch \
	--yes \
	-- \
	'' \
	#

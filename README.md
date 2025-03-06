# Tools for Azure Machine Learning

## Examples

### Download and show user logs from a run

#### Create config file if needed

```shell
uv tool install --python "<3.13" --prerelease=allow --with pip azure-cli

uvx az extension remove --name ml  # if needed
uvx az extension add --name ml  # if needed

config_query='{resource_group: .resource_group, workspace_name: .name, subscription_id: (.id | split("/")[2])}'
uvx az ml workspace show | uvx jq --raw-output $config_query > config.json
cat config.json
```

#### Download and display logs

```shell
run_id="khaki_jelly_s70lr4lk7b"  # replace with your run ID
logs_dir="user_logs"  # default directory where logs are saved

config_path="config.json"  # workspace properties

# We need to specify the Python version because uv's resolver ignores upper
# bounds for Python version in pyproject.toml
# https://docs.astral.sh/uv/reference/resolver-internals/#requires-python
# and azureml.core._metrics breaks for Python >= 3.13
uvx --python "<3.13" --from azure-tools \
    aml download \
        --config $config_path \
        --run-id $run_id \
        --source-aml-path $logs_dir \
        --convert-logs

uvx --from toolong tl $run_id/$logs_dir/*.log
```

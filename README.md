# Some tools for Azure Machine Learning

```shell
uv tool install git+https://github.com/fepegar/azure-tools
uvx aml download
uvx aml snapshot
```

## Examples

### Download and show user logs from a run

```shell
run_id="khaki_jelly_s70lr4lk7b"
logs_dir="user_logs"
config_path="workspace_properties.json"

uv tool install --python 3.11 --prerelease=allow --with pip azure-cli

config_query='{resource_group: .resource_group, workspace_name: .name, subscription_id: (.id | split("/")[2])}'
uvx az extension add --name ml
uvx az ml workspace show | uvx jq --raw-output $config_query > $config_path
cat $config_path

uvx --from azure-tools \
    aml download \
        --config $config_path \
        --run-id $run_id \
        --source-aml-path $logs_dir \
        --convert-logs

uvx --from toolong tl $run_id/$logs_dir/*.log
```

from mcp_sandbox.services.file import YAMLService

my_yaml2 = YAMLService(path="config/model_config.yaml")
model_list = my_yaml2.doRead()

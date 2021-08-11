from swagger_specs import SwaggerSpecs

if __name__ == "__main__":
    specs = SwaggerSpecs(folder_path=r"C:\Users\kairu\projects\azure-rest-api-specs")
    print("--------- Mgmt Plan --------")
    for m in specs.get_mgmt_plan_modules():
        m.get_resource_providers()

    print("--------- Data Plan --------")
    for m in specs.get_data_plan_modules():
        m.get_resource_providers()
    # print(len(swagger.get_mgmt_plan_modules()))
    # print(len(swagger.get_data_plan_modules()))

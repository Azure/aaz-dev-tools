from swagger import Swagger

if __name__ == "__main__":
    swagger = Swagger(folder_path=r"C:\Users\kairu\projects\azure-rest-api-specs")
    for m in swagger.get_mgmt_plan_modules():
        m.get_resource_providers()

    # for m in swagger.get_data_plan_modules():
    #     m.get_resource_providers()
    # print(len(swagger.get_mgmt_plan_modules()))
    # print(len(swagger.get_data_plan_modules()))

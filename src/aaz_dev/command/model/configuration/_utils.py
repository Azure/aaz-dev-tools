class CMDDiffLevelEnum:

    BreakingChange = 1  # diff breaking change part
    Structure = 2    #
    Associate = 5    # include diff for links
    All = 10    # including description and help messages


class CMDArgBuildPrefix:
    Query = '$Query'
    Header = '$Header'
    Path = '$Path'
    ClientEndpoint = '$Client.Endpoint'  # It's used for client config endpoints related args


DEFAULT_CONFIRMATION_PROMPT = "Are you sure you want to perform this operation?"


class CMDBuildInVariants:

    Instance = "$Instance"
    # It's used in client config which endpoints is by http operation
    EndpointInstance = "$EndpointInstance"

    Subresource = "$Subresource"
    Endpoint = "$Endpoint"

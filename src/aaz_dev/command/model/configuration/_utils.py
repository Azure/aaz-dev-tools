class CMDDiffLevelEnum:

    BreakingChange = 1  # diff breaking change part
    Structure = 2    #
    Associate = 5    # include diff for links
    All = 10    # including description and help messages


class CMDArgBuildPrefix:
    Query = '$Query'
    Header = '$Header'
    Path = '$Path'


DEFAULT_CONFIRMATION_PROMPT = "Are you sure you want to perform this operation?"

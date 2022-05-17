from schematics.models import Model


class CMDDiffLevelEnum:

    BreakingChange = 1  # diff breaking change part
    Structure = 2    #
    Associate = 5    # include diff for links
    All = 10    # including description and help messages


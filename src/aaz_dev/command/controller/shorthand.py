def serialize(obj):
    def dfs(obj):
        if isinstance(obj, dict):
            return "{" + ",".join(f'{k}:{dfs(v)}' for k, v in obj.items()) + "}"

        elif isinstance(obj, list):
            return "[" + ",".join(dfs(i) for i in obj) + "]"

        else:
            if obj is None:
                return "null"  # replace None by null

            escaped = str(obj)
            escaped = escaped.replace("'", "'/")  # use '/ to input '

            # with space, null/help expressions or other special characters
            if any(char in escaped for char in (" ", "null", "??", ":", ",", "{", "}", "[", "]")):
                escaped = "'" + escaped + "'"

            return repr(escaped)[1:-1]  # ignore quotes

    return '"' + dfs(obj) + '"' if isinstance(obj, dict) or isinstance(obj, list) else obj

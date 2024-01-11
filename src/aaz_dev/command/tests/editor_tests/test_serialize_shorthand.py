from command.controller.shorthand import serialize


def test_with_nesting():
    obj = {
        "microsoft-azure-monitor-single-resource-multiple-metric-criteria": {
            "all-of": [{
                "name": "High_CPU_80",
                "metric-name": "Time",
                "dimensions": [],
                "operator": "GreaterThan",
                "threshold": 80.5,
                "time-aggregation": "Average"
            }]
        }
    }

    assert serialize(obj) == '"{microsoft-azure-monitor-single-resource-multiple-metric-criteria:{all-of:[{name:High_CPU_80,metric-name:Time,dimensions:[],operator:GreaterThan,threshold:80.5,time-aggregation:Average}]}}"'


def test_with_single_quote():
    obj = {
        "name": "monitor's"
    }

    assert serialize(obj) == '"{name:monitor\'/s}"'


def test_with_special_characters():
    obj = {
        "name": "monitor metric",
        "dimensions": None,
        "data": "{a: [1, 2]}"
    }

    assert serialize(obj) == '"{name:\'monitor metric\',dimensions:null,data:\'{a: [1, 2]}\'}"'

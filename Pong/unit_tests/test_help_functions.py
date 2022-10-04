from server_functions.help_functions import *


def test_pylist2protlist():
    test_list = ["FeatureName", 2]
    protocol_list = "FeatureName,2"
    assert pylist2protlist(test_list) == protocol_list

    test_list = ["FeatureName", 2, "Testname", "test"]
    protocol_list = "FeatureName,2,Testname,test"
    assert pylist2protlist(test_list) == protocol_list

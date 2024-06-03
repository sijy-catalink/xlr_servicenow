#
# Copyright (c) 2024. All rights reserved.
#
# This software and all trademarks, trade names, and logos included herein are the property of Catalink and its affiliates, subsidiaries and licensors.
#


def assert_not_null(val, error_msg):
    if not bool(val):
        raise RuntimeError(error_msg)

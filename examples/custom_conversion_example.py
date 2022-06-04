from dataclasses import dataclass
from dictgest import default_convertor, from_dict
from dataclasses import dataclass

# Get any already registered bool convertor
default_bool_conv = default_convertor.get(bool)

# create a custom converter
def custom_bool_conv(val):
    if val == "oups":
        return False

    # Let the other cases be treated as before
    return default_bool_conv(val)


# register the custom converter for bool
default_convertor.register(bool, custom_bool_conv)


@dataclass
class Result:
    finished: bool
    notified: bool


result = from_dict(Result, {"finished": True, "notified": "oups"})
print(result)

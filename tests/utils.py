def check_fields(obj, ref_dict):
    for key, val in obj.__dict__.items():
        if key in ref_dict:
            assert val == ref_dict[key]

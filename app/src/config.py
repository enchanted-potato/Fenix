import yaml
import numpy as np
from typing import Union, Any


def load_yml(path: str, replace_null: bool = True) -> dict:
    """
    Loads a yaml file from the given path and returns a dictionary.

    Args:
        path: path of folder to be created
        replace_null: replace all 'null' values are replaced with np.nan
    """
    with open(path) as f:
        yml_file = yaml.safe_load(f)
    if replace_null:
        yml_file = replace_nulls_with_npnan(yml_file)
    return yml_file


def replace_nulls_with_npnan(data: Union[dict, list, Any]) -> Union[dict, list, Any]:
    """
    Replace null values with np.nan.

    Args:
        data: structure to clean null values, if list or dict the nulls will be
        replaced with np.nan otherwise the original object will be returned.
    """
    if isinstance(data, dict):
        return {
            k: np.nan if v is None else replace_nulls_with_npnan(v)
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [replace_nulls_with_npnan(v) for v in data]
    else:
        return data

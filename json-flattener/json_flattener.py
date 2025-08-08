import sys
import json
import argparse
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Any


class JsonFlattener:
    """
    A utility class to convert nested JSON into flatten JSON.
    """
    def __init__(self, dict_sep: str = ".", list_sep: str = "__") -> None:
        self._set_dict_sep(dict_sep)
        self._set_list_sep(list_sep)
    
    @property
    def dict_sep(self) -> str:
        return self._dict_sep
    
    def _set_dict_sep(self, dict_sep: str) -> None:
        if not isinstance(dict_sep, str):
            raise TypeError(
                f"Invalid type for 'dict_sep' (in method '{self.__class__.__name__}._set_dict_sep'): "
                f"expected 'str', got '{type(dict_sep).__name__}'."
            )
        self._dict_sep = dict_sep

    @property
    def list_sep(self) -> str:
        return self._list_sep
    
    def _set_list_sep(self, list_sep: str) -> None:
        if not isinstance(list_sep, str):
            raise TypeError(
                f"Invalid type for 'list_sep' (in method '{self.__class__.__name__}._set_list_sep'): "
                f"expected 'str', got '{type(list_sep).__name__}'."
            )
        self._list_sep = list_sep

    def flatten(self, data: Any, parent_key: str = "") -> dict:
        """
        Recursively flattens nested dictionaries and lists into a single-level dictionary.
    
        Example:
            [
              {"name": "alice"}, 
              {"name": "bob"}
            ] → 
            {
              "0.name": "alice", 
              "1.name": "bob"
            }
        """
        flat_data = {}  # Final flattened key-value pairs
    
        # If the top-level data is a primitive (int, str, etc.) and not inside a parent key,
        # there is nothing to flatten → return empty dict.
        if not isinstance(data, (dict, list)) and not parent_key:
            return flat_data
    
        # Convert top-level lists into {index: value} format so they can be processed like dicts.
        data = dict(enumerate(data)) if isinstance(data, list) else data
    
        for k, v in data.items():
            # Choose separator: list_sep for numeric keys, dict_sep for string keys
            sep = self.list_sep if isinstance(k, int) else self.dict_sep
    
            # Build the current flattened key
            cur_key = f"{parent_key}{sep}{k}" if parent_key else str(k)
    
            if isinstance(v, dict):
                # Recurse into nested dictionary
                flat_data.update(self.flatten(v, cur_key))
            elif isinstance(v, list):
                # Convert list to {index: value} and recurse
                flat_data.update(self.flatten(dict(enumerate(v)), cur_key))
            else:
                # Store primitive value
                flat_data[cur_key] = v
    
        return flat_data


class AppJsonFlattener(JsonFlattener):
    def __init__(self, dict_sep: str = ".", list_sep: str = "__"):
        super().__init__(dict_sep, list_sep)

    def main(self) -> None:
        source: Namespace = self._get_source_fpath()

        source_fpath: Path = Path(source.source)

        if not source_fpath.exists():
            raise FileNotFoundError(
                f"The source file path '{source_fpath}' does not exist."
            )
        
        if source_fpath.suffix.lower() != ".json":
            raise ValueError(
                f"Invalid file type: expected '.json', got '{source_fpath.suffix}'."
            )
        
        # output file path
        output_fpath: Path = Path(source_fpath.parent).joinpath(f"flat_{source_fpath.name}")

        if output_fpath.exists() and not source.overwrite:
            raise FileExistsError(
                f"The output file path '{output_fpath}' already exist. "
                "Use -w or --overwrite to overwrite the output file."
            )
        
        try:
            data: Any = self._read_json(source_fpath)
            flat_data: dict = self.flatten(data)
            self._write_json(flat_data, output_fpath)
            print(f"Output location: '{output_fpath}'")
        except PermissionError as e:
            raise PermissionError(
                f"Permission denied while accessing '{source_fpath}' or '{output_fpath}': {e}."
            )
        except UnicodeDecodeError as e:
            raise ValueError(f"Could not decode JSON from '{source_fpath}': {e}.")
        except UnicodeEncodeError as e:
            raise ValueError(f"Could not encode JSON to '{output_fpath}': {e}.")
        except Exception as e:
            raise RuntimeError(
                f"Unexpected error while processing '{source_fpath}' → '{output_fpath}': {e}."
            )
        
    def _get_source_fpath(self) -> Namespace:
        parser: ArgumentParser = argparse.ArgumentParser()
        parser.add_argument("-s", "--source", required=True, help="Source JSON file path.")
        parser.add_argument("-w", "--overwrite", action="store_true", help="Overwrite the existing output JSON file.")
        return parser.parse_args()
    
    def _read_json(self, fpath: Path) -> Any:
        with fpath.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _write_json(self, data: Any, fpath: Path) -> None:
        with fpath.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


if __name__ == "__main__":
    try:
        app: AppJsonFlattener = AppJsonFlattener()
        app.main()
    except Exception as e:
        print(f"Note: {e}")
        sys.exit(1)
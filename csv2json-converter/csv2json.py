import sys
import csv
import json
import argparse 
from pathlib import Path


class Csv2JsonConverter:
   def __init__(self, source: str | Path, destination: str | Path, 
                over_write: bool = False) -> None:
      self._set_source(source)
      self._set_destination(destination)
      self._set_over_write(over_write)

   @property
   def source(self) -> Path:
      return self._source
   
   def _set_source(self, source: str | Path) -> None:
      if not isinstance(source, (str, Path)):
         raise TypeError(f"Invalid type for 'source': expected 'str' or 'Path', got '{type(source).__name__}'.")
      
      self._source = Path(source)

      if self._source.suffix.lower() != ".csv":
         raise ValueError("The source file must have a '.csv' extension.")

      if not self._source.exists():
         raise FileNotFoundError(f"The source file '{self._source}' does not exist.")

   @property
   def destination(self) -> Path:
      return self._destination
   
   def _set_destination(self, destination: str | Path) -> None:
      if not isinstance(destination, (str, Path)):
         raise TypeError(f"Invalid type for 'destination': expected 'str' or 'Path', got '{type(destination).__name__}'.")
      
      self._destination = Path(destination)

      if not self._destination.suffix:
         fname = self._source.with_suffix(".json").name
         self._destination = self._destination.joinpath(fname) 
         self._destination.parent.mkdir(parents=True, exist_ok=True)
      elif self._destination.suffix.lower() != ".json":
         raise ValueError("The destination file must have a '.json' extension.")
   
   @property
   def over_write(self) -> bool:
      return self._over_write
   
   def _set_over_write(self, over_write: bool = False) -> None:
      if not isinstance(over_write, bool):
         raise TypeError(f"Invalid type for 'over_write': expected 'bool', got '{type(over_write).__name__}'.")
      
      self._over_write = over_write
   
   def convert(self) -> None:
      if self._destination.exists() and not self._over_write:
         raise FileExistsError(
            f"The destination file '{self._destination}' already exists. "
            "Use '--over-write' to overwrite it."
         )
            
      try:
         with self._source.open("r", encoding="utf-8") as file:
            data = list(csv.DictReader(file))
            if not data:
               raise ValueError(f"The source file '{self._source}' is empty. Nothing to convert.")

         with self._destination.open("w", newline="", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

      except PermissionError as e:
         raise PermissionError(f"Permission denied: {e}.")
      except UnicodeDecodeError as e:
          raise ValueError(f"Could not decode file '{self._source}': {e}")
      except csv.Error as e:
          raise ValueError(f"CSV format error in '{self._source}': {e}")
      except TypeError as e:
          raise ValueError(f"Could not serialize to JSON: {e}")
      except Exception as e:
          raise RuntimeError(f"Unexpected error during conversion: {e}")


if __name__ == "__main__":
   parser = argparse.ArgumentParser(description="Convert CSV file into JSON format.")
   
   parser.add_argument("-s", "--source", required=True)
   parser.add_argument("-d", "--destination", default="output.json")
   parser.add_argument("--over-write", default=False)

   parsed_args = parser.parse_args()
   
   try:
      converter = Csv2JsonConverter(parsed_args.source, parsed_args.destination, 
                                    parsed_args.over_write)
      converter.convert()
   except Exception as e:
      print(f"Problem: {e}")
      sys.exit(1)

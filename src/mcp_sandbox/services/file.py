"""
Services for reading and writing from and to various file formats
"""

import json
import os
import pickle
from typing import Any, Dict, List, Optional, Union
import importlib.resources
import pandas as pd
import toml
import yaml
from mcp_sandbox.config import global_config as glob
from mcp_sandbox.services.blueprint_file import BaseService
from mcp_sandbox.services.logger import LoggerFactory

my_logger = LoggerFactory(handler_type="Stream", verbose=True).create_module_logger()


class YAMLService(BaseService):
    """
    Service for reading and writing YAML files, supporting both filesystem and package resource access.
    """

    def __init__(
        self,
        path: Optional[str] = "",
        root_path: str = glob.CODE_DIR,
        verbose: bool = False,
        package: Optional[str] = None,
    ):
        """
        Initialize YAMLService.

        Args:
            path (Optional[str]): Filename or resource name. Defaults to "".
            root_path (str): Root path where file is located (for filesystem access). Defaults to glob.CODE_DIR.
            verbose (bool): Should user information be displayed? Defaults to False.
            package (Optional[str]): Package name for importlib.resources (for package resource access).
        """
        self.path = os.path.join(root_path, path or "")
        self.verbose = verbose
        self.package = package
        self.resource_path = path  # relative path inside the package

    def doRead(self, **kwargs: Any) -> Union[Dict, List]:
        """
        Read data from YAML file.

        Returns:
            Union[Dict, List]: Parsed YAML content.

        Raises:
            yaml.YAMLError: If YAML parsing fails.
            FileNotFoundError: If the file/resource does not exist.
        """
        if self.package:
            # Read from package resources
            with (
                importlib.resources.files(self.package)
                .joinpath(self.resource_path)
                .open("r") as stream
            ):
                try:
                    my_yaml_load = yaml.load(stream, Loader=yaml.FullLoader, **kwargs)
                    if self.verbose:
                        my_logger.info(
                            f"Read (pkg): {self.package}/{self.resource_path}"
                        )
                except yaml.YAMLError as exc:
                    my_logger.error(exc)
                    raise
        else:
            with open(self.path, "r") as stream:
                try:
                    my_yaml_load = yaml.load(stream, Loader=yaml.FullLoader, **kwargs)
                    if self.verbose:
                        my_logger.info(f"Read: {self.path}")
                except yaml.YAMLError as exc:
                    my_logger.error(exc)
                    raise
        return my_yaml_load

    def doWrite(self, X: Union[Dict, List], **kwargs: Any) -> None:
        """
        Write dictionary or list to YAML file.

        Args:
            X (Union[Dict, List]): Input data to write.

        Raises:
            yaml.YAMLError: If YAML serialization fails.
        """
        with open(self.path, "w") as outfile:
            try:
                yaml.dump(X, outfile, default_flow_style=False)
                if self.verbose:
                    my_logger.info(f"Write to: {self.path}")
            except yaml.YAMLError as exc:
                my_logger.error(exc)
                raise


# class YAMLService(BaseService):
#     def __init__(
#         self,
#         path: Optional[str] = "",
#         root_path: str = glob.CODE_DIR,
#         verbose: bool = False,
#     ):
#         """
#         Generic read/write service for YAML files.

#         Args:
#             path (Optional[str]): Filename. Defaults to "".
#             root_path (str): Root path where file is located. Defaults to glob.CODE_DIR.
#             verbose (bool): Should user information be displayed? Defaults to False.
#         """
#         self.path = os.path.join(root_path, path or "")
#         self.verbose = verbose

#     def doRead(self, **kwargs: Any) -> Union[Dict, List]:
#         """
#         Read data from YAML file.

#         Returns:
#             Union[Dict, List]: Read-in YAML file.
#         """
#         with open(self.path, "r") as stream:
#             try:
#                 my_yaml_load = yaml.load(stream, Loader=yaml.FullLoader, **kwargs)
#                 if self.verbose:
#                     my_logger.info(f"Read: {self.path}")
#             except yaml.YAMLError as exc:
#                 my_logger.error(exc)
#         return my_yaml_load

#     def doWrite(self, X: Union[Dict, List], **kwargs: Any) -> None:
#         """
#         Write dictionary to YAML file.

#         Args:
#             X (Union[Dict, List]): Input data.
#         """
#         with open(self.path, "w") as outfile:
#             try:
#                 yaml.dump(X, outfile, default_flow_style=False)
#                 if self.verbose:
#                     my_logger.info(f"Write to: {self.path}")
#             except yaml.YAMLError as exc:
#                 my_logger.error(exc)


class TXTService(BaseService):
    def __init__(
        self,
        path: Optional[str] = "",
        root_path: str = glob.DATA_PKG_DIR,
        verbose: bool = True,
    ):
        """
        Generic read/write service for TXT files.

        Args:
            path (Optional[str]): Filename. Defaults to "".
            root_path (str): Root path where file is located. Defaults to glob.DATA_DIR.
            verbose (bool): Should user information be displayed? Defaults to True.
        """
        self.path = os.path.join(root_path, path or "")
        self.verbose = verbose

    def doRead(self, **kwargs: Any) -> List[str]:
        """
        Read data from TXT file.

        Returns:
            List[str]: Input data.
        """
        try:
            with open(self.path, **kwargs) as f:
                df = f.read().splitlines()
            if self.verbose:
                my_logger.info(f"TXT Service read from file: {str(self.path)}")
        except Exception as e0:
            my_logger.error(e0)
            df = []
        return df

    def doWrite(self, X: List[str], **kwargs: Any) -> None:
        """
        Write data to TXT file.

        Args:
            X (List[str]): Input data.
        """
        try:
            with open(self.path, "w", **kwargs) as f:
                f.write("\n".join(X))
            if self.verbose:
                my_logger.info(f"TXT Service output to file: {str(self.path)}")
        except Exception as e0:
            my_logger.error(e0)


class JSONService(BaseService):
    def __init__(
        self,
        path: Optional[str] = "",
        root_path: str = glob.DATA_PKG_DIR,
        verbose: bool = True,
    ):
        """
        Generic read/write service for JSON files.

        Args:
            path (Optional[str]): Filename. Defaults to "".
            root_path (str): Root path where file is located. Defaults to "".
            verbose (bool): Should user information be displayed? Defaults to True.
        """
        self.path = os.path.join(root_path, path or "")
        self.verbose = verbose

    def doRead(self, **kwargs: Any) -> Dict:
        """
        Read data from JSON file.

        Returns:
            Dict: Output imported data.
        """
        if os.stat(self.path).st_size == 0:  # if JSON not empty
            return dict()
        try:
            with open(self.path, "r") as stream:
                my_json_load = json.load(stream, **kwargs)
            if self.verbose:
                my_logger.info(f"Read: {self.path}")
            return my_json_load
        except Exception as exc:
            my_logger.error(exc)
            return {}

    def doWrite(self, X: Dict, **kwargs: Any) -> None:
        """
        Write dictionary to JSON file.

        Args:
            X (Dict): Input data.
        """
        with open(self.path, "w", encoding="utf-8") as outfile:
            try:
                json.dump(X, outfile, ensure_ascii=False, indent=4, **kwargs)
                if self.verbose:
                    my_logger.info(f"Write to: {self.path}")
            except Exception as exc:
                my_logger.error(exc)


class TOMLService(BaseService):
    def __init__(
        self,
        path: Optional[str] = "",
        root_path: str = glob.CODE_DIR,
        verbose: bool = False,
    ):
        """
        Generic read/write service for TOML files.

        Args:
            path (Optional[str]): Filename. Defaults to "".
            root_path (str): Root path where file is located. Defaults to glob.CODE_DIR.
            verbose (bool): Should user information be displayed? Defaults to False.
        """
        self.root_path = root_path
        self.path = path or ""
        self.verbose = verbose

    def doRead(self, **kwargs: Any) -> Dict:
        """
        Read data from TOML file.

        Returns:
            Dict: Imported TOML file.
        """
        with open(os.path.join(self.root_path, self.path), "r") as stream:
            try:
                toml_load = toml.load(stream, **kwargs)
                if self.verbose:
                    my_logger.info(f"Read: {self.root_path + (self.path or '')}")
            except Exception as exc:
                my_logger.error(exc)
                return {}
        return toml_load

    def doWrite(self, X: Dict, **kwargs: Any) -> None:
        """
        Write dictionary to TOML file.

        Args:
            X (Dict): Input dictionary.
        """
        with open(os.path.join(self.root_path, self.path), "w") as outfile:
            try:
                toml.dump(X, outfile)
                if self.verbose:
                    my_logger.info(f"Write to: {self.root_path + (self.path or '')}")
            except Exception as exc:
                my_logger.error(exc)


class PickleService:
    def __init__(
        self,
        path: str = "",
        root_path: str = glob.DATA_PKG_DIR,
        schema_map: Optional[Dict[str, str]] = None,
        is_dataframe: bool = False,
        verbose: bool = False,
    ):
        """
        Generic read/write service for pickle files.

        Args:
            path: Filename (relative to `root_path`).
            root_path: Base directory for the file.
            schema_map: If reading a DataFrame, rename columns via pandas .rename().
            is_dataframe: Whether the object is a pandas.DataFrame.
            verbose: Print status and full tracebacks on error.
        """
        self.path = os.path.join(root_path, path)
        self.schema_map = schema_map or {}
        self.is_dataframe = is_dataframe
        self.verbose = verbose

    def doRead(self, **kwargs) -> Any:
        """Load from disk. Returns a DataFrame if is_dataframe=True, else any pickled object."""
        try:
            if self.is_dataframe:
                df = pd.read_pickle(self.path, **kwargs)
                if self.schema_map:
                    df.rename(columns=self.schema_map, inplace=True)
                result = df
            else:
                with open(self.path, "rb") as f:
                    result = pickle.load(f)

            if self.verbose:
                print(f"[PickleService] Loaded from {self.path}")
            return result

        except Exception:
            if self.verbose:
                print(f"[PickleService] Error loading {self.path}:")
            raise

    def doWrite(self, X: Any, **kwargs) -> None:
        """
        Write to disk.
        - If is_dataframe=True, calls DataFrame.to_pickle().
        - Otherwise pickles any Python object (graphs, models, dicts, etc.).
        """
        try:
            if self.is_dataframe:
                if not isinstance(X, pd.DataFrame):
                    raise TypeError(
                        "Expected a pandas.DataFrame when is_dataframe=True"
                    )
                X.to_pickle(path=self.path, **kwargs)
            else:
                with open(self.path, "wb") as f:
                    pickle.dump(X, f)

            if self.verbose:
                print(f"[PickleService] Written to {self.path}")
        except Exception:
            if self.verbose:
                print(f"[PickleService] Error writing to {self.path}:")
            raise


class XLSXService:
    def __init__(
        self,
        path: Optional[str] = "",
        sheetname: str = "Sheet1",
        root_path: str = glob.DATA_PKG_DIR,
        schema_map: Optional[Dict[str, str]] = None,
        verbose: bool = False,
    ):
        """
        Generic read/write service for XLSX files.

        Args:
            path (Optional[str]): Filename. Defaults to "".
            sheetname (str): Sheet name for Excel file. Defaults to "Sheet1".
            root_path (str): Root path where file is located. Defaults to glob.DATA_DIR.
            schema_map (Optional[Dict[str, str]]): Mapping scheme for renaming columns. Defaults to None.
            verbose (bool): Should user information be displayed? Defaults to False.
        """
        self.path = os.path.join(root_path, path or "")
        self.writer = pd.ExcelWriter(self.path)
        self.sheetname = sheetname
        self.verbose = verbose
        self.schema_map = schema_map

    def doRead(self, **kwargs: Any) -> pd.DataFrame:
        """
        Read data from XLSX file.

        Returns:
            pd.DataFrame: Data converted to DataFrame.
        """
        df = pd.read_excel(self.path, self.sheetname, **kwargs)
        if self.verbose:
            print(f"XLSX Service Read from File: {str(self.path)}")
        if self.schema_map:
            df.rename(columns=self.schema_map, inplace=True)
        return df

    def doWrite(self, X: pd.DataFrame, **kwargs: Any) -> None:
        """
        Write DataFrame to XLSX file.

        Args:
            X (pd.DataFrame): Input data.
        """
        try:
            X.to_excel(self.writer, sheet_name=self.sheetname, index=False, **kwargs)
            self.writer.close()
            if self.verbose:
                print(f"XLSX Service Output to File: {str(self.path)}")
        except Exception as e:
            my_logger.error(f"Error writing XLSX file {self.path}: {e}")
            raise e

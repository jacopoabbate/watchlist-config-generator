"""Implements an automatic Watchlist API configuration file generator.

The module is designed to automate the process of creating configuration files that define
the list of contracts to which the user wants to subscribe. In particular, this module was
designed to solve the issue of creating such files when the instruments to subscribe to
are futures contracts. Due to the presence of contracts on the same underlying presenting
different maturities that are traded at the same time, the manual creation of the
configuration files requires the user to search, for each instrument of interest, all the
maturities that are traded at that moment. Having to deal with multiple sources and
multiple instruments at a time, the process can become time consuming.

To automate the creation of the configuration files, the module makes use of the reference
data files that are downloaded every day as part of the download of the Watchlist data.
In particular, the current implementation uses the information contained in the COREREF
files to discover, using regular expressions, all the traded maturities, for a specific
symbol, that were available the previous day. The program repeats the process for all the
COREREF files that are passed as an input.

In order for the program to know which symbols are of interest for the user, a JSON file
with a structure {"source_id": ["symbol"]} is used. The module includes the functions that
are used to process this file and convert its content in a Python dictionary that can be
used by the functions down the data stream.
"""

import bz2
import csv
import datetime
import json
import pathlib
import re
import sys
from typing import Dict, List, Pattern, Tuple


def search_files(path_to_folder: str, search_pattern: str) -> List[pathlib.Path]:
    """Returns a list containing the paths of all the files matching the search pattern.

    The function searches for all the files that match the search pattern. For some
    examples on how to use the search_pattern functionality, see the Examples section
    below.

    Parameters
    ----------
    path_to_folder: str
        The path to the directory where we want to search the files.
    search_pattern: str
        A string containing the pattern that the function has to use to search for the
        files.

    Returns
    -------
    List[pathlib.Path]
        A list of pathlib.Path objects, pointing to the location of the discovered files.

    Examples
    --------
    Search for all the .py files in the current directory

    >>> python_files = search_files('.', '*.py')

    Search for all the .py files in the direct sub-directory of the current one

    >>> python_files = search_files('.', '*/*.py')

    Search for all the .py files in all the directories and subdirectories rescursively

    >>> python_files = search_files('.', '**/*.py')

    Search for all the files that have a name starting with COREREF and a txt.bz2
    extension in all the subdirectories recursively

    >>> coreref_files = search_files('.', '**/COREREF*.txt.bz2')
    """
    data_folder = pathlib.Path(path_to_folder)
    return list(data_folder.glob(search_pattern))


def find_all_coreref_files(directory: str) -> List[pathlib.Path]:
    """Searches for all the COREREF files in a directory and all its subdirectories.

    Parameters
    ----------
    directory: str
        A string containing the path to directory where we want to search the COREREF
        files.

    Returns
    -------
    List[pathlib.Path]
        A list of pathlib.Path objects, pointing to the location of all the discovered
        COREREF files.
    """
    return list(pathlib.Path(directory).glob("**/COREREF*.txt.bz2"))


def json_loader(path_to_json_file: str) -> Dict[str, List[str]]:
    """Reads a JSON file and converts its content in a dictionary.

    Parameters
    ----------
    path_to_json_file: str
        The path to the JSON file.

    Returns
    -------
    Dict[str, List[str]]
        A dictionary of source codes with the corresponding lists of instrument symbols of
        interest for each source.
    """
    with pathlib.Path(path_to_json_file).open('r') as infile:
        return json.loads(infile.read())  # type: ignore


def get_source_id_from_file_path(file_path: pathlib.Path) -> str:
    """Extrapolates the source id from the file path.

    To retrieve the source id from the file name, the function uses the fact that the
    ICE uses a consistent naming convention consisting of the file type accompanied by
    the source id and the date the data in the file was generated.
    (e.g. COREREF_207_20201023.txt.bz2).

    Parameters
    ----------
    file_path: str
        The path to the file for which the source id has to be extrapolated.

    Returns
    -------
    str
        The source id.
    """
    file_name = file_path.name.split(".")[0]
    name_components = file_name.split('_')
    return name_components[1]


def retrieve_instruments(
    source_id: str,
    source_symbols_dictionary: Dict[str, List[str]],
) -> List[str]:
    """Retrieves the list of instruments of interest for a specific source id.

    Parameters
    ----------
    source_id: str
        An ICE source id.
    source_symbols_dictionary: Dict[str, List[str]]
        A dictionary containing pairs of source-code and list of instruments of interest
        for the specific source.

    Returns
    -------
    List[str]
        A list of instrument's symbols as strings.
    """
    return source_symbols_dictionary.get(source_id)  # type: ignore


def create_equity_regex(instrument_symbol: str) -> str:
    """Creates a regular expression pattern to match the equity symbology.

    To create the regular expression pattern, the function uses the fact that within the
    ICE consolidated feed all the equity instruments (equities, ETFs and funds) are
    identified by the root symbol (a unique mnemonic based on the exchange ticker or
    the ISIN, where no exchange ticker is available), prefixed with the type and the
    optional session indicator. In addition to this minimal setup, the regex pattern is
    extended to include the optional ISO 4217 currency code and the optional sub-market
    indicator. In this way, the resulting regex can be used to search for all the
    available instances of a certain equity instrument, just by passing the root symbol
    prefixed by the type indicator and the eventual session indicator (where required).

    Parameters
    ----------
    instrument_symbol: str
        An equity instrument symbol consisting of the root symbol prefixed with the type
        identifier (E) and optional session indicator (for example E:PRY is used to
        indicate Prysmian Group equities).

    Returns
    -------
    str
        The regular expression pattern that includes the root symbol prefixed with the type
        identifier as well as the optional components (currency code and sub-market).
    """
    return rf"\b{instrument_symbol}\b-{{0,1}}[A-Z]{{0,3}}@{{0,1}}[a-zA-Z0-9]{{0,10}}"


def create_futures_regex(input_symbol: str) -> str:
    """Creates a regular expression pattern to match the standard futures symbology.

    To create the regular expression pattern, the function uses the fact that within the
    ICE consolidated feed all the standard futures contracts are identified by the root
    symbol (a unique mnemonic based on the exchange ticker or the ISIN, where no exchange
    ticker is available), prefixed with the type and the optional session indicator, a
    backslash, and a delivery date (formatted as MYYdd, where M is the month code, YY
    are the last two digits of the year, and dd is 2-digit day of the month that is used
    only for those futures where the day of the month is required to identify the security).

    The function logic allows the user to pass a complete futures name, or to pass the
    root symbol prefixed by the type and optional session indicator, followed by a
    backslash and the * wildcard flag. In the former case, the resulting regex expression
    will be such that it will match only the specific security that is passed as an input
    (for example, by passing F:FDAX\\H21, the resulting regular expression will only
    match the DAX futures contract with expiration in March 2021). If only the symbol
    root (with all the necessary prefixes) followed by a backslash and the * wildcard
    flag, is passed as an input, the resulting regex will be such to allow matching all
    the possible combinations of month year (and optionally day) of expiration.

    Parameters
    ----------
    input_symbol: str
        A standard futures symbol consisting of the root symbol prefixed with the type
        identifier (F) and optional session indicator. If the user wants the function to
        produce a regular expression that can match all the possible combinations of
        month, year (and optionally day) expirations, then the root symbol will be followed
        by a backslash and the * wildcard flag (for example F:FDAX\\* will result in a
        regular expression that will match all the possible combinations of root symbol,
        month code, year and eventually day codes). Alternatively, if the user is only
        interested in creating a regular expression that matches literally only a
        specific contract, the passed instrument symbol (prefixed with the type
        identifier and optional session indicator) will be followed by a backslash and a
        specific maturity, identified by the month code followed by the 2-digit year code
        and the 2-digit day code for those contracts that are identified also by the day
        of the month.

    Returns
    -------
    str
        Depending on the input symbol, the function returns a regular expression pattern
        that either matches literally a specific security symbol or one that matches all
        the possible maturities of the root symbol passed as an input.
    """
    if not input_symbol.endswith('*'):
        symbol_components = input_symbol.split("\\")
        return rf"{symbol_components[0]}\\{symbol_components[1]}"
    else:
        symbol_root = input_symbol.split("\\")[0]
    return rf"{symbol_root}\\[A-Z][0-9]{{2,4}}"


def create_options_regex(input_symbol: str) -> str:
    """Creates a regular expression pattern to match the options symbology.

    To create the regular expression pattern, the function uses the fact that within the
    ICE consolidated feed all the option contracts are identified by the root symbol (a
    unique mnemonic based on the exchange ticker or the ISIN, where no exchange ticker is
    available), prefixed with the type and the optional session indicator; a backslash,
    followed by the expiration date (formatted as MYYdd, where M is the month code, YY
    are the last two digits of the year, and dd is 2-digit day of the month that is used
    only for those futures where the day of the month is required to identify the
    security); another backslash, followed by the full strike price including the decimal
    point, with the leading zeroes removed.

    The function logic allows the user to pass a complete option symbol or to use wildcards
    to specify the type of matching that the generated regular expression should support.
    In particular, if the user passes to the function the root symbol (prefixed by the
    type and the optional session indicator) followed by a backslash and the * wildcard
    flag, the function will generate a regular expression that will match all the
    possible combinations of expiration dates and all the possible strike prices, of the
    root symbol (for example, passing O:PRY\\* to the function, will result in a regular
    expression that will match all the possible combinations of maturity and strike price
    for the Prysmian Group option). Alternatively, if the user wants the regular
    expression to match all the possible strike prices given a certain root symbol and
    delivery date, it can pass to the function the root symbol (prefixed by the type and
    the optional session indicator); a backslash, the chosen maturity, another backslash,
    followed by the * wildcard flag (for example, passing O:PRY\\A21\\* to the function,
    will result in a regular expression that will match all the possible combination of
    strike price for the Prysmian Group call option with January 2021 maturity). Finally,
    if a complete option symbol is passed to the function, without any of the previously
    shown wildcard patterns, the resulting regex expression will be such that it will
    match only the specific contract that is passed as an input (for example, passing
    O:PRY\\A21\\17.0 to the function, will result in a regular expression that will match
    explicitly only the Prysmian Group call option with January 2021 maturity and strike
    price of 17.0 euro).

    Parameters
    ----------
    input_symbol: str
        An option symbol consisting of the root symbol prefixed with the type
        identifier (O) and optional session indicator. If the user wants the function to
        produce a regular expression that can match all the possible combinations of
        expiration date and strike price, the root symbol will be followed by a backslash
        and the * wildcard flag (e.g. O:PRY\\*). Alternatively, if the user wants a
        regular expression that can match all the possible strike prices for a certain
        expiration, the root symbol will be followed by a backslash, the expiration date,
        another backslash, followed by the * wildcard flag (e.g. O:PRY\\A21\\*). Finally,
        if the regular expression has to match a specific maturity and strike price, the
        user can pass the complete symbol for the specific contract, without any wildcard
        (e.g. O:PRY\\A21\\17.0).

    Returns
    -------
    str
        Depending on the input symbol, the function returns a regular expression pattern
        that either matches literally a specific security symbol or one that matches all
        the possible combinations of maturities and strike prices given a root symbol, or
        one that matches all the possible strike prices given a root symbol and a specific
        maturity.
    """
    if not input_symbol.endswith('*'):
        symbol_components = input_symbol.split("\\")
        return rf"{symbol_components[0]}\\{symbol_components[1]}\\{symbol_components[2]}"
    else:
        if len(input_symbol.split('\\')) == 2:
            symbol_components = input_symbol.split('\\')
            return rf"{symbol_components[0]}\\[A-Z][0-9]{{2,4}}\\[0-9.]{{1,10}}"
        elif len(input_symbol.split('\\')) == 3:
            symbol_components = input_symbol.split("\\")
            return rf"{symbol_components[0]}\\{symbol_components[1]}\\[0-9.]{{1,10}}"


def create_fixed_income_regex(input_symbol: str) -> str:
    """Creates a regular expression pattern to match the fixed income symbology.

    To create the regular expression patter, the function uses the fact that within the
    ICE consolidated feed, all the fixed income instruments are identified by the root
    symbol ( a unique mnemonic based on the exchange ticker or the ISIN, where no exchange
    ticker is available), prefixed with the type and the optional session indicator. In
    addition to this minimal symbology setup, fixed income symbols can present optional
    elements such as the "dirty bond" marker and the sub-market indicator.

    The function only requires the root symbol, prefixed with the type and the optional
    session indicator, to generate a regular expression pattern, and takes care to
    autonomously extend the pattern to match as well all the optional components of the
    symbol.

    Parameters
    ----------
    input_symbol: str
        A fixed income symbol consisting of the root symbol prefixed with the type
        identifier (B) and optional session indicator.

    Returns
    -------
    str
        The regular expression pattern that matches the input symbol as well as all the
        optional components.
    """
    return rf"\b{input_symbol}\b\\{{0,1}}D{{0,1}}@{{0,1}}[a-zA-Z0-9]{{1,10}}"


def create_forwards_regex(input_symbol: str) -> str:
    """Creates a regular expression pattern to match the forwards symbology.

    To create the regular expression, the function uses the fact that within the ICE
    consolidated feed all the forwards contracts are identified by the root symbol (a
    unique mnemonic based on the exchange ticker or the ISIN, where no exchange ticker is
    available), prefixed with the type and optional session indicator; a backslash,
    followed by a relative term indicator that expresses the delivery date relatively to
    today (for example SP characterise a spot contract, 5D a contract with delivery date
    in 5 days, 2Y a contract with delivery date in 2 years etc.).

    The function logic allows the user to pass a complete forward contract symbol or to
    use a wildcard flag. In case a full forward symbol is passed to the function, the
    resulting regex expression will be such that it will match only that specific
    contract (for example, passing R2:GAS\\5D as an input, will result in the function
    creating a regular expression matching only the forward contract for GAS traded after
    hours with 5-day delivery). Conversely, if it is passed as an input only the root
    symbol (prefixed with the type and optional session indicator) followed by a
    backslash and the * wildcard flag, the function will generate a regular expression
    that can match all the possible relative terms (for example, passing R2:GAS*, will
    produce a regular expression that can match all the available relative delivery dates
    of the GAS forward).

    Parameters
    ----------
    input_symbol: str
        Either a forward symbol consisting of the root symbol prefixed with the type
        identifier (R) and the optional session indicator, followed by a backslash and
        the chosen relative delivery term, or the root symbol (with all the necessary
        prefixes) followed by a backslash and the * wildcard flag.

    Returns
    -------
    str
        Depending on the input symbol, the function returns a regular expression patter
        that either matches literally a specific forward contract symbol, or one that
        matches all the possible relative term indicators for a specific forward's symbol
        root.
    """
    if not input_symbol.endswith("*"):
        symbol_components = input_symbol.split("\\")
        return rf"{symbol_components[0]}\\{symbol_components[1]}"
    else:
        symbol_root = input_symbol.split("\\")[0]
        return rf"{symbol_root}\\[A-Z0-9]{{2,4}}"


def create_index_regex(input_symbol: str) -> str:
    """Creates a regular expression pattern to match the index symbology.

    To create the regular expression pattern, the function uses the fact that within the
    ICE consolidated feed, all the indices are identified by the root symbol (a unique
    mnemonic based on the exchange ticker or the ISIN), prefixed with the type.

    Parameters
    ----------
    input_symbol: str
        An index symbol consisting of the root symbol prefixed with the type identifier (I).

    Returns
    -------
    str
        The regular expression pattern that matches the index symbol passed as an input.
    """
    return rf"\b{input_symbol}\b"


def create_specific_instrument_regex(input_symbol: str) -> str:
    r"""Creates a regular expression specific to the type of the passed security symbol.

    Since the input symbol consists, at a minimum, of the root symbol, prefixed by the
    type indicator and optionally by a session indicator, the function infer, just
    from the input symbol, what type of security the symbol belongs to. Once the type of
    security is identified, the function returns the regular expression that matches the
    symbol structure appropriate to the security type and the structure of the input
    symbol (depending on whether a certain security type allows for the specification of
    wildcards, the function will return a regular pattern that keeps into account whether
    a wildcard is specified or whether a regex specific to a certain contract is to
    generate instead).

    Parameters
    ----------
    input_symbol: str
        A security symbol, consisting at a minimum of the root symbol of the security,
        prefixed by the type and an optional session indicator. Currently, the following
        security types are supported: Equities, Fixed Income, Forwards (this type
        supports the use of wildcards), Futures (only simple futures, not continuous ones;
        this type supports the use of wildcards), Indices, and Options (this type supports
        the usage of wildcards).

    Returns
    -------
    str
        The regular expression pattern appropriate to the type of security and the
        specification of the input symbol (presence of wildcards or match of a precise
        contract).
    """

    if input_symbol.startswith('B'):
        return create_fixed_income_regex(input_symbol)
    elif input_symbol.startswith('E'):
        return create_equity_regex(input_symbol)
    elif input_symbol.startswith('F'):
        return create_futures_regex(input_symbol)
    elif input_symbol.startswith('I'):
        return create_index_regex(input_symbol)
    elif input_symbol.startswith('O'):
        return create_options_regex(input_symbol)
    elif input_symbol.startswith('R'):
        return create_forwards_regex(input_symbol)


def create_instrument_level_pattern(instrument_symbols: List[str]) -> str:
    """Creates a regular expression pattern to target all the instrument symbols in a list.

    The function creates a regular expression pattern to target, within a specific DC
    message, the portion of the message containing the complete instrument symbol, for
    each instrument symbol included in the list passed as an input of the function.

    Parameters
    ----------
    instrument_symbols: List[str]
        A list of the stable components of the futures instrument symbols.

    Returns
    -------
    str
        A regular expression pattern.
    """
    specific_instrument_regexes = [
        create_specific_instrument_regex(name)
        for name in instrument_symbols
    ]
    return rf"({'|'.join(specific_instrument_regexes)})"


def create_dc_message_level_pattern(source_id: str, instrument_symbols: List[str]) -> str:
    """Creates a regular expression pattern to target DC message types.

    The function creates a list of regular expressions to target the DC messages
    containing the information of all the instruments of interest for the specific
    source id.

    Parameters
    ----------
    source_id: str
        An ICE source id.
    instrument_symbols: List[str]
        A list of the stable portion of futures contracts symbols.

    Returns
    -------
    str
        A regular expression pattern.
    """
    return rf"^DC\|{source_id}\|{create_instrument_level_pattern(instrument_symbols)}"


def combine_multiple_regexes(regexes: List[str]) -> Pattern[str]:
    """Combine multiple regular expressions in a single pattern.

    Parameters
    ----------
    regexes: List[str]
        A list of regular expressions.

    Returns
    -------
    Pattern[str]
        A Pattern object containing the pattern that combines all the passed regular
        expressions.
    """
    return re.compile("|".join(regexes))

##########################################################################################


def retrieve_source_symbol_pairs(
    path_to_coreref_file: pathlib.Path,
    message_level_pattern: str,
    instrument_level_pattern: str,
) -> List[Tuple[str, str]]:
    """Searches for specific instrument symbols in a bz2 compressed COREREF reference data file.

    The function uses regular expressions to first isolate only those reference data
    messages that belong to a specific message type (DC) and refer to a specific subset of
    instrument symbols, and then to extract from the message only the contracts
    corresponding to the subset of source-specific instrument's symbols.
    Each contract discovered is included to a list together with the corresponding
    source_id.

    Parameters
    ----------
    path_to_coreref_file: pathlib.Path
        A pathlib.Path object pointing to a COREREF file containing the reference data to
        search. The file has to be bz2 compressed (the files are bz2 compressed when they
        are downloaded in first place from the Datavault API).
    message_level_pattern: str
        A string containing the regex pattern used to filter only a specific type of
        reference data message.
    instrument_level_pattern: str
        A string containing the regex patter used to filter a specific subset of
        instrument's symbols

    Returns
    -------
    List[Tuple[str, str]]
        A list of tuples each containing the source_id and the instrument's symbol.

    """
    source_symbol_pairs = []
    try:
        with bz2.open(path_to_coreref_file, 'rb') as infile:
            for line in infile:
                if re.search(message_level_pattern, line.decode("utf8")):
                    source_symbol_pairs.append(
                        (get_source_id_from_file_path(path_to_coreref_file),
                         re.search(instrument_level_pattern, line.decode('utf8'))[0],  # type: ignore
                         ),
                    )
    except OSError:
        sys.exit(f"Process finished with exit code 1\n"
                 f"Attempted to process: {path_to_coreref_file.as_posix()}\n"
                 f"The file has extension:'{path_to_coreref_file.suffix}'. Expected:'.bz2'")
    return source_symbol_pairs


def process_coreref_file(
    coreref_file_path: pathlib.Path,
    source_symbols_dictionary: Dict[str, List[str]],
) -> List[Tuple[str, str]]:
    """Searches for source-specific instrument symbols in a COREREF file.

    The function detects the source id specific to the input COREREF file, retrieves from
    the source_symbols_dictionary the list of instrument's symbols relevant for that
    source_id, and proceeds with searching for all the contracts corresponding to the
    source-specific subset of symbols.

    Parameters
    ----------
    coreref_file_path: pathlib.Path
        A pathlib.Path object pointing to the location of the COREREF file.
    source_symbols_dictionary: Dict[str, List[str]]
        A dictionary containing "source_id":["instrument_symbol"] key-value pairs,
        containing, for each source_id, the list of symbols of interest for that specific
        source.

    Returns
    -------
    List[Tuple[str, str]]
        A list of tuples, each containing the source_id, and a contract's symbol.
    """
    top_level_regex = create_dc_message_level_pattern(
        get_source_id_from_file_path(coreref_file_path),
        retrieve_instruments(
            get_source_id_from_file_path(coreref_file_path),
            source_symbols_dictionary,
        ),
    )
    symbol_level_regex = create_instrument_level_pattern(
        retrieve_instruments(
            get_source_id_from_file_path(coreref_file_path),
            source_symbols_dictionary,
        ),
    )
    return retrieve_source_symbol_pairs(coreref_file_path, top_level_regex, symbol_level_regex)


def process_all_coreref_files(
    coreref_file_paths: List[pathlib.Path],
    source_symbols_dictionary: Dict[str, List[str]],
) -> List[Tuple[str, str]]:
    """Searches for source-specific instrument symbols in each COREREF file in the list.

    The function iterates over the list of COREREF files, detects the source id specific
    to each file, retrieves from the source_symbols_dictionary the list of instrument's
    symbols relevant for that source_id, and proceeds with searching for all the contracts
    corresponding to the source-specific subset of symbols.

    Parameters
    ----------
    coreref_file_paths: List[pathlib.Path]
        A list of pathlib.Path objects, each pointing to a different COREREF file.
    source_symbols_dictionary: Dict[str, List[str]]
        A dictionary containing "source_id":["instrument_symbol"] key-value pairs,
        containing, for each source_id, the list of symbols of interest for that specific
        source.

    Returns
    -------
    List[Tuple[str, str]]
        A list of tuples, each containing the source_id, and a contract's symbol.

    """
    discovered_symbols = []
    for file_path in coreref_file_paths:
        if get_source_id_from_file_path(file_path) not in source_symbols_dictionary.keys():
            pass
        else:
            discovered_symbols.extend(process_coreref_file(file_path, source_symbols_dictionary))
    discovered_symbols.sort(key=lambda x: x[0])
    return discovered_symbols


def generate_config_file_path(directory_path: str) -> pathlib.Path:
    """Generates the file path of the configuration file in a given directory.

    Parameters
    ----------
    directory_path: str
        The path to the directory where the configuration file is to be placed.

    Returns
    -------
    pathlib.Path
        A Path object providing the full path to the configuration file.
    """
    return pathlib.Path(directory_path).joinpath(
        f"watchlist_config_{datetime.datetime.utcnow().strftime('%Y%m%d')}.csv",
    )


def config_file_writer(directory_path: str, source_name_pairs: List[Tuple[str, str]]) -> str:
    """Writes the source_id-symbols pairs to a csv file with a compliant header.

    Parameters
    ----------
    directory_path: str
        The path where the file should be written.
    source_name_pairs: List[Tuple[str, str]]
        A list of tuples, each containing a source_id, contract's symbol pair.

    Returns
    -------
    str
        The summary of the operation.
    """
    pathlib.Path(directory_path).mkdir(parents=True, exist_ok=True)
    file_path = generate_config_file_path(directory_path)
    with file_path.open('w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(("sourceId", "RTSsymbol"))
        for item in source_name_pairs:
            csv_writer.writerow(item)
    return (f"Configuration file successfully written.\n"
            f"{len(source_name_pairs)} symbols were added to the file.")

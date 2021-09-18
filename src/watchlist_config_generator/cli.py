"""Module containing the command line app."""

import pathlib

import click

from watchlist_config_generator.watchlist_config_generator import (
    config_file_writer,
    search_files,
    json_loader,
    process_all_coreref_files,
)


@click.command()
@click.argument('data_directory', type=click.Path(exists=True))
@click.argument('input_file', type=click.Path(exists=True))
@click.option(
    "-w", "--write-to",
    type=click.Path(exists=True),
    default=None,
    help=("The directory where to write the configuration file that is generated."
          "If the write-to option is not used, the program writes the generated "
          "configuration file in the current working directory."
          ),
)
@click.option(
    "-p", "--pattern",
    type=click.STRING,
    default="**/COREREF*.txt.bz2",
    help=("The search pattern that is used to discover the COREREF files in a specific "
          "directory or in a directories tree. Possible pattern are: 'COREREF*.txt.bz2' "
          "(if the COREREF file used to create the configuration file is directly inside "
          "the directory to which DATA_DIRECTORY points to), '*/COREREF*.txt.bz2' (if the "
          "files are in a direct subdirectory of DATA_DIRECTORY), '**/COREREF*.txt.bz2' "
          "(if the files are to be searched recursively in all the subdirectories of "
          "DATA_DIRECTORY). The wildcard after the COREREF name can also be placed in "
          "different ways depending on the pattern that we want to search. For example, "
          "if we want to search the COREREF file for all the sources available on a "
          "specific date, we can use the search pattern '**/COREREF_*_20201028.txt.bz2'."
          ),
)
def makeconfig(data_directory: str, input_file: str, write_to: str, pattern: str):
    r"""Generates a Watchlist API configuration file.

    Using the reference data files that are found in the DATA_DIRECTORY and the structure
    found in the INPUT FILE, this application creates a Watchlist API configuration file
    with the correct header and with the source id and symbols information written in
    conformity with the API specification.

    \b
    Arguments:
    DATA_DIRECTORY is the path to the directory that contains the COREREF files used as a
    source for the creation of the configuration file. Thanks to the flexibility of the
    program and its ability to explore recursively all the directories and subdirectories
    that are within the DATA_DIRECTORY, it is possible to set as the path represented by
    DATA_DIRECTORY, the path to the top-level directory that contains the data, and then
    use the --pattern option to specify which COREREF files to target.

    INPUT_FILE is the path to the json file that contains, for each source ID, the list of
    instrument's symbols that are of interest for the user.
    """
    reference_data_files = search_files(data_directory, pattern)
    instruments_input_file = json_loader(input_file)
    discovered_contracts = process_all_coreref_files(reference_data_files, instruments_input_file)
    if not write_to:
        write_to = pathlib.Path.cwd()
    summary = config_file_writer(write_to, discovered_contracts)
    click.echo(summary)


if __name__ == '__main__':
    makeconfig()

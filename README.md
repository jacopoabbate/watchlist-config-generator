# Watchlist Configuration File Generator Library for Python

## Overview

The Watchlist Configuration File Generator was created to automate the process of creating and updating the ICE Watchlist configuration files given a user-defined portfolio of instruments. The application offers a command line interface that can be used to create Watchlist configuration files on-demand, but, as any other Python library, its functions can also be used for the creation of scripts that could be used within an automated pipeline to create the configuration file before sending it to the Watchlist API.

The program was created for all the user of the Intercontinental Exchange (abbreviated from now own to ICE) DataVault, the cloud-based platform that is used to manage and source historical tick-by-tick data from the ICE Consolidated Feed, that would like a way to automate a process of generating every day the configuration file for the subscription to the Watchlist API.

## Background

### Watchlist Files

The Watchlist files are a type of data files that are offered within ICE DataVault; they provide tick history pricing data for a select subset of instruments on specific markets. These files are normally used in place of the Replay files when a user is interested in capturing and analysing the tick data of a portfolio of security instead of the data coming from the full market. 

Watchlist files are generated on a subscription basis: the users need to specify on day *t*, before the closing of the market of interest,  a list of sources and instruments that they want to be included in the Watchlist file that is generated at day *t+1*. The preferences are specified in a .csv or .txt configuration file, which is then submitted through the dedicated Watchlist API. 

The configuration file must conform to a specific structure:

- The file should start with the header `sourceID,RTSsymbol`.
- Each entry in the portfolio is identified as a combination of a source ID and an ICE Consolidated Feed contract symbol. The source ID identifies the market where the specific contract is traded.

An example of configuration file is the following:

```
sourceId,RTSsymbol
207,F:FDAX\Z20
207,F:FESX\Z20
207,F:FESX\H21
673,F2:ES\Z20
890,F:Z\Z20
```

Changes to configuration file result in the inclusion or removal of specific market sources, or in an update of the sets of contracts of interest for each source.

### Config File Creation and the Issue With Derivative Contracts

Creating these configuration files when the number of source IDs and instrument is very small or when the set of instruments of interest for a specific source is pretty much stable is straightforward. Especially in the case of a portfolio that is stable over time and made of securities whose symbols do not change over time (for example when the portfolio is made of equities, that except in rare occasions, maintain the same symbol over time) one could create a configuration file and roll it over day after day, without having to generate a new configuration file every day. However, when the portfolio composition is not stable and among the securities that constitute the portfolio are derivate contracts such as futures, options or forwards, and the user is interested in having a comprehensive coverage of all the contracts traded for a specific symbol, creating these configuration files becomes a time consuming process. For example, at Peregrine Traders we use Watchlist files coming from the major derivatives exchanges, to create our dataset of historical tick data. For each major exchange, we select a subset of the most liquid futures symbols and, in order to have a comprehensive coverage of all the traded contracts, we include in our portfolio all the contracts available for a specific futures symbol, at the moment of creating the configuration file. Since at every point in time, the set of contracts that are available for a specific symbol is random, as the availability (and hence the inclusion of new maturities in the case of futures) is driven by market demands for specific contracts, and not by pre-defined rules, if we had to create every day the configuration file by hand, we would have to manually search in the Symbol Directory of the ICE Developer Portal, for each source and each symbol of interest for that source, all the maturities that are trading in that specific moment, and then add each of the discovered contracts to the configuration file. Considering that one of our Watchlist configuration files can include easily 200 different contracts at a time, it was clear to us that we needed to develop a way to automate the process of creating these configuration files, in a way that required us only to specify the source IDs that we were interested into and for each source ID the securities of interest, leaving then to the program the job to discover the available securities instances and create automatically the configuration file using the discovered symbols. 

### The Proposed Solution

In order to deal with the uncertainty that is inherently attached to working with a broad set of derivatives contracts, with different expirations and strike prices, we came up with a solution that is self contained and make use of the data that we already have available every day with the daily download of the Watchlist files.

Since every daily download comes with the Watchlist files and the reference-data files for each market source that was included in the previous day configuration file, we realised that we could use these reference-data files as a source of truth to automate the daily generation of the new configuration files, given that each reference data file contains the information of all the instruments that are traded on the specific day the file is generated. In particular, we decided to use as our source of truth the COREREF files, a type of reference data file containing a set of reference tokens that are used for symbology resolution of all the contracts that are traded in a specific market source.

While the use of COREREF files solved the way we could search and discover in an automated fashion all the traded contracts for a specific symbol, we still needed a way to define the portfolios of symbols for which we were interested in retrieving all the traded contracts, in a way that was flexible enough to support multiple instrument types and multiple ways to specify the portfolio requirements.

To solve this second issue, we used the fact that ICE, over time, put in place an effort to standardise the symbology of different types of instruments across the different sources that are included in the ICE Consolidated Feed platform. In particular, we made use of the fact that each instrument type has a clear structure that define its symbology and, even for those securities that have variable components (such as the delivery date or the strike price), it still offered an element of stability across different instances of the same instrument that we could use to define a strategy for the specification of instrument requirements, flexible enough to support different types of instruments and different way to specify the portfolio requirements.

The specification of the set of sources and instruments of interest is done through an user-generated portfolio file, which is a JSON file containing, for each source id, a list of the source-specific symbols of interest. The portfolio file allows each user to define its specific portfolio of symbols, and will therefore vary from user to user (and could possibly vary over time if the portfolio is expanded or reduced, either by adding/removing source IDs or by adding/removing symbols for a specific source).

Once the portfolio file containing the list of sources and the source-specific securities of interest is generated, we then just have to indicate to the Watchlist Configuration File Generator the location where the COREREF files are stored and provide the location of the portfolio file, and then the application will autonomously sieve through the COREREF files and select only the occurrences that match the symbol root or the specific contract symbol, adding each discovered instance to the Watchlist configuration file, respecting the prescribed format of the file. 

## Features

- Accepts a user-defined portfolio of symbols to personalise the content of the created configuration file.
- Supports the specification of multi-asset portfolios.
- Supports both the specification of explicit contracts symbols and, for derivative contracts, supports also the usage of wildcards to specify the set of contracts that have to be included in the configuration file.
- Wildcard support to specify the search pattern of the COREREF files.
- Verify the existence of symbols that are explicitly declared in the portfolio file, in the corresponding COREREF file. The inclusion of symbols that are not found in the COREREF file of the source where the symbol was expected to be found, results in the exclusion from the list of symbols that are added to the Watchlist configuration file.
- Searches, for all those symbols in the portfolio file that are defined using a wildcard, all the instances that match, within the COREREF file, the specified wildcard pattern, and includes the discovered symbols to the list of instances to add to the Watchlist configuration file.
- Generates a Watchlist configuration file that conforms to the prescript format and the user-defined portfolio file.

## Setup Instructions

### Requirements/Pre-requisites

#### Software Requirements

This software requires to have Python 3.6 or above installed.

#### Data Requirements

Since the Watchlist Configuration File Generator uses the COREREF files that comes with every daily download of Watchlist files as a source of truth to generate the configuration file, you will need access to ICE DataVault and to daily downloads of Watchlist files (and accompanying reference data files) for this software to run. 

### Installation

#### Cloning the Repository

To use the Watchlist Configuration File Generator, first clone the repository on your device using the command below:

```shell
# If using the ssh endpoint
$ git clone git@github.com:jacopoabbate/watchlist-config-generator.git

# If using the https endpoint
$ git clone https://github.com/jacopoabbate/watchlist-config-generator.git

cd watchlist-config-generator
```

This creates the directory *watchlist-config-generator* and clones the content of the repository.

#### Installing Within a Virtualenv

We always recommend to create and use a dedicated environment when installing and running the application.

You will need to have at least Python 3.6.1 installed on your system.

##### Unix/Mac OS with virtualenv

```shell
# Create a virtual environment
# Use an ENV_DIR of your choice. We will use ~/virtualenvs/watchlist-config-generator-prod
# Any parent directories should already exist
python3 -m venv ~/virtualenvs/watchlist-config-generator-prod

# Activate the virtualenv
. ~/virtualenvs/watchlist-config-generator-prod/bin/activate

# Install the dependencies
python -m pip install -r requirements-prod.txt

# Install watchlist-config-generator
python -m pip install .
```

At this point you should be able to import `watchlist_config_generator` from your locally built version:

```shell
$ python  # start an interpreter
>>> import watchlist_config_generator
>>> print(watchlist_config_generator.__version__)
1.0.0
```

##### Windows

Below is brief overview on how to set-up a virtual environment with PowerShell under Windows. For further details, please refer to the [official virtualenv user guide](https://virtualenv.pypa.io/en/latest/).

```shell
# Create a virtual environment
# Use an ENV_DIR of your choice. Use %USERPROFILE% from cmd.exe
python -m venv $env:USERPROFILE\virtualenvs\watchlist-config-generator-prod

# Activate the virtualenv. User activate.bat for cmd.exe
~\virtualenvs\watchlist-config-generator-prod\Scripts\Activate.ps1

# Install the package dependencies
python -m pip install -r requirements-prod.txt

# Install watchlist-config-generator
python -m pip install .
```

### Post Installation: Creating the Portfolio File

After installing Watchlist Configuration File Generator, the next step left before using the software is to create the portfolio file. As mentioned in the background section, the portfolio file defines the portfolio of instruments that are of interest for each specific market source. 

#### File Structure 

The portfolio file is a JSON file, where the portfolio of all the securities of interest is defined as a JSON object, where the source IDs are the object's keys, and the lists of source-specific securities of interest, each expressed as an array, are the object's values.

#### Supported Instrument Types

For the specification of the list of source-specific securities of interest, the following instrument types are currently supported: 

- **Equity instruments** (equities, ETF, and funds): their symbol consist of the root symbol (a unique mnemonic based on the exchange ticker or the ISIN, when no exchange ticker is available), prefixed with the type (E) and (optional session indicator). For example, E:ABNA represents the equity issue for ABN Amro.
- **Fixed Income instruments**: their symbol consist of the root symbol, prefixed with the type (B). For example,  B:01NU represents a fixed income contract for Vodafone.
- **Forwards**: their symbol consist of the root symbol, prefixed with the type (R) and (optional) session indicator, a backslash, followed by the delivery date described relative to today. For example, R2:GAS\SP represents the forward contract for GAS traded after hours with spot delivery, while R2:GAS\15M represents the forward contract for GAS with 15 months delivery.
- **Futures**: their symbol consist of the root symbol, prefixed with the type (F) and (optional) session indicator, a backslash, and a delivery date with the format MYYdd (where M is the month ,code, YY the last 2 digits of the year, and 22 is a 2-digit day of the month for those futures that are identified by the day of the month as well). For example, F:FDAX\Z20 represents the future contract for the DAX index with delivery in December 2020, and similarly F2:ES\Z20 represents the S&P 500 e-mini contract, with delivery in December 2020, which is negotiated in the electronic trading session (as the optional session indicator is set to 2).
- **Indices**: their symbol consists of the root symbol, prefixed with the type (I). For example, I:KOSPI200 represents the KOSPI 200 index.
- **Options**: their symbol consists of the root symbol prefixed by the type and the session indicator (optional); a backslash; expiration date in the same format as in the future symbols above; another backslash; and the full strike price including the decimal point, with the leading zeroes removed. For example, `O:PRY\A21\17.0` represents the symbol of the call option for Prysmian Group with delivery in January 2020 and strike price of 17 euro.

Continuous futures, forex instruments, strategies and warrant are currently not supported, even though we plan to add support for these instrument types in the future.

#### Specifying the Symbols of the Securities of Interest

As mentioned in the File Structure section, the list of source-specific securities of interest is specified as an array of comma separated security symbols. The Watchlist Configuration File Generator allows to specify these symbols in two different way:

- **Explicit specification**: for equity instruments, fixed income instruments and indices, this is the only way to specify the symbol (as they do not have delivery dates or other additional elements). For forwards, futures and options, specifying a symbol explicitly, means not only writing the root symbol, prefixed with the type and the optional session indicator, but also the delivery date and, for the options, the strike price. By explicitly specifying the complete symbol of one of these securities, will result in the program to only include (if found in the COREREF files) the passed symbol. 
- **Specification with wildcard**: forwards, futures and options symbols can also be specified including a wildcard. In particular:
  - ***Forwards***: by writing the root symbol, prefixed by the type and the session indicator (optional), and followed by the `*` wildcard flag, the program will look for all the available delivery dates in the respective COREREF file. Therefore, if, for example, we write `R2:GAS\\5D` (explicit specification), only the contract with 5-day delivery will be eventually included in the generated configuration file, while if we use `R2:GAS\\*`, all the available deliveries for the GAS forward contract will be included in the generated configuration file.
  - ***Futures***: similarly to the forward contracts, by writing the root symbol, prefixed by the type and the session indicator (optional), and followed by the `*` wildcard flag, the program will look for all the available delivery dates in the respective COREREF file. Similarly to the above example, writing in the portfolio file `F:FDAX\\H21` (explicit specification) will result in the inclusion in the watchlist configuration file of the sole contract with delivery in March 2021, while passing `F:FDAX*` will inform the program to look for all the available maturities for the DAX future and to include all the found ones in the generated configuration file.
  - ***Options***: since the options symbols have two components that vary from contract to contract, namely the delivery date and the strike price, for the definition of option's symbols, the program supports two different usages of wildcard flags. The first wildcard usage sees the `*` flag placed after the root symbol prefixed by the type and optional session indicator and followed by , means that we are interested in retrieving all the available maturities and strike prices combination available in the COREREF file. The alternative wildcard pattern, consist in placing the `*` wildcard flag after having specified the root symbol and the delivery date of the option; in this case, we are only interested in retrieving all the available strike prices for a certain underlying and maturity. For example, by including in the source-specific array the symbol `O:DAI\\A21\\35` (explicit specification), we explicitly request the Daimler Call option with expiration in January 2021 with strike price of 35 euro, to be included in the configuration file. Alternatively, if we are interested in including in the configuration file all the available option contracts for Daimler, we can instead add to the source-specific array, the option symbol, followed by the `*` wildcard flag, as `O:DAI\\*`. Finally, if we want to have included all the available strike prices for a specific maturity of an option, we can use the `*` flag and write, for example, `O:DAI\\A21\\*` and have included in the configuration file all the available strike prices for the Daimler call option with delivery in January 2021. 

#### An Example of a Multi-Asset Portfolio File

Having specified the file structure, the supported security types, and the modality for specifying the symbol of various securities, we now present an example of a Portfolio File that includes multiple sources and multiple instrument types.

These are the assumptions we used to create the file:

- We are interested in generating a configuration file that includes three source IDs: 207 (Eurex European Market Data - Level 2), 218 (Cboe Europe CXE Market Data - Level 2), 673 (CME eMini - Level 2).
- For source ID 207, we are interested in adding to the configuration file all the available contracts of the DAX future (symbol: FDAX) and of the EuroSTOXX 50 Index future (symbol: FESX). In addition, we are interested in adding also all the call option contracts of Daimler, with delivery data in January 2021 (symbol: DAI), and all the available option contracts of Volkswagen (symbol: VOW) . 
- For source ID 218, we are interested in adding to the configuration file the equities of BNP Paribas (symbol: BNPP), NN Group NV (symbol: NNA).
- Finally, for source ID 673, we are interested in adding to the configuration file the S&P 500 e-mini future with delivery in December 2020 (symbol: ES) and the Nasdaq e-mini future with delivery date December 2020.

Keeping in consideration these specifications, the resulting portfolio file will look like as follows:

```json
{
  "207": [
    "F:FDAX\\*",
    "F:FESX\\*",
    "O:DAI\\A21\\*",
    "O:VOW\\*"
  ],
  "218": [
    "E:BNPP",
    "E:NNA"
  ],
  "673": [
    "F2:ES\\Z20",
    "F2:NQ\\Z20"
  ]
}
```

Note the usage of wildcards where we want to retrieve all the available contracts of a certain future contract or option symbol, or when we want to retrieve all the available strike prices for a certain option symbol and delivery date. Similarly, note the usage of the full symbol for those securities that we want to explicitly have included in the configuration file.  

## Usage

The Watchlist Configuration File Generator Library for Python offers a command line interface that allows the user to initiate the automated creation of the Watchlist configuration file. At the same time, `watchilst-config-generator` can be imported as any other Python library and its functions can be used to create custom made scripts to automate the creation of configuration files.

In this section we will document the usage of the command line interface.

### General Usage

Since you installed the Watchlist Configuration File Generator library inside a virtual environment, the first step to use the program, is always to activate the virtual environment where the program was installed in first place.

The command line interface of the `watchlist-config-generator` library is invoked by running in the shell:

```shell
makeconfig DATA_DIRECTORY PORTFOLIO_FILE [OPTIONS]
```

where:

-  `DATA_DIRECTORY` is the path to the directory where the COREREF files that are used to generate the configuration file are stored.

-  `PORTFOLIO_FILE` is the path to the portfolio file containing the list of instruments symbols of interest for each source.

In addition to these two argument fields, the following options are available:

- `write-to` allows to specify the path to the directory where the configuration file is to be generated. If the `write-to` option is not used, the configuration file will be created in the current working directory.
- `pattern` allows to specify the search pattern that is used to discover the COREREF files (see the dedicated section below for more information on how to use the `pattern` option).

For example, the command:

```shell
makeconfig ~/mkt_data ~/input_files/input_20201101.json
```

will use  the COREREF files discovered in the `~/mkt_data` directory as a source of truth and will use the portfolio file at  `~/input_files/input_20201101.json` to infer, for each source id in the file, the set of instruments of interest. The resulting configuration file will be saved in the current working directory. Conversely, the command:

```shell
makeconfig ~/mkt_data ~/input_files/input_20201101.json -w watchlist_config
```

will write the generated to the `watchlist_config` directory.

### Usage of the Pattern Option

Under the hood, the `makeconfig` command makes use of the `pathlib` library to discover the COREREF files in the `DATA_DIRECTORY`. Depending on how the `DATA_DIRECTORY` is structured, a different search pattern that make use of wildcards, can be used.

Let's assume that the `DATA_DIRECTORY` has the following structure:

```shell
$ tree
.
└── historic_data
    └── 2020
        └── 10
            └── 26
                ├── S207
                │   ├── CORE
                │   │   └── COREREF_207_20201026.txt.bz2
                │   ├── CROSS
                │   │   └── CROSSREF_207_20201026.txt.bz2
                │   └── WATCHLIST
                │       └── WATCHLIST_207_20201026.txt.bz2
                └── S367
                    ├── CORE
                    │   └── COREREF_367_20201026.txt.bz2
                    ├── CROSS
                    │   └── CROSSREF_367_20201026.txt.bz2
                    └── WATCHLIST
                        └── WATCHLIST_207_20201026.txt.bz2

12 directories, 6 files
```

Depending on how we specify the search pattern with the pattern option, we can query the directory tree in different ways:

- Example 1 - Querying the `historic_data` directory and subdirectories recursively, in search for all the COREREF files available:

  ```shell
  makeconfig /historic_data ~/input_files/instruments.json -p '**/COREREF*'
  ```

  The `**` wildcard is used in this case to indicate that the entire directory tree should be traversed recursively. The pattern used in the above example can be used to search for all the available  COREREF files but also to target a specific file only (for example `-p '**/COREREF_367*'` will target only the COREREF file specific to source 367).

- Example 2 - Querying the `historic_data/2020/10/26/S207`:

  ```shell
  makeconfig /historic_data/2020/10/26/S207 ~/input_files/instruments.json -p '*/COREREF*'
  ```

  Here the first `*` wildcard is used to indicate to search for all the COREREF files that are in the pointed directory or in a direct subdirectory of this directory.

- Example 3 - Querying `historic_data/2020/10/26/S207/CORE` directly:

  ```shell
  makeconfig /historic_data/2020/10/26/S207/CORE ~/input_files/instruments.json -p '/COREREF*'
  ```

  This search pattern can be used if, for example, the COREREF files are all stored in a specific directory and no subdirectory need to be traversed in order to find the files.

- Example 4 - Targeting all the COREREF files that belong to a specific day:

  ```shell
  makeconfig /historic_data ~/input_files/instruments.json -p '**/COREREF_*_20201026*'
  ```

  This example is the closest to how the pattern option would be used in a real life scenario. In the `DATA_DIRECTORY` example above, there is only a single month and a single day in the directory tree. However, in real life, the directory tree will present multiple months and multiple days for each month, and therefore a more appropriate query approach would be to designate the root of the data directory as a starting point for the search and then use the pattern option to specify a recursive search across all subdirectories, targeting all the COREREF files that were generated on a specific date, like shown in the above search pattern.

The pattern option is flexible enough to adapt to different naming schemes and different directory structures.

### A Note for the Inclusion of Symbols From New Sources

Since the Watchlist Configuration File Generator relies on the COREREF files for the discovery of the available securities symbols, or for checking the existence within the traded securities of a specific symbol, when we want to introduce new sources to the configuration file, we cannot rely anymore on this mechanism and we will have to edit the configuration file by hand and add the new source and the corresponding symbols of interest. 

In fact, whenever we add a new source, we will always miss the previous day COREREF file that comes with the download of the previous day Watchlist files. In this scenario, therefore, we will have to navigate to the [Symbol Directory](https://idsportal.icedataservices.com/marketdata/symbol_directory.idms) in the ICE Data Services Developer Portal, select the new source ID that we want to add to the configuration file, and search all the symbols of interest for that specific source. 

## TODO

### Features Planned

- Implementation of the support for continuous futures, forex instruments, strategies and warrants. 

## License

Copyright (c) Jacopo Abbate

Distributed under the terms of the MIT license, the Watchlist Configuration File Generator Library for Python is free and open source software.

## Credits

The Watchlist Configuration File Generator Library for Python is developed and maintained by  [Jacopo Abbate](mailto:jacopo.abbate@gmail.com "jacopo.abbate@gmail.com").


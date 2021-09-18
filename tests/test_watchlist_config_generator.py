import csv
import datetime
import pathlib
import pytest

from watchlist_config_generator import watchlist_config_generator as wcg


class TestSearchFiles:
    def test_search_of_crossref_file_in_a_directory(self):
        # Setup
        directory_to_search = (
            pathlib.Path(__file__).resolve().parent / 'static_data' / 'mock_data_dir' /
            "2020" / "10" / "16" / "S207" / "CROSS"
        )
        pattern = "CROSSREF*.txt.bz2"
        # Exercise
        discovered_reference_data_files = wcg.search_files(directory_to_search, pattern)
        # Verify
        expected_files = [
            pathlib.Path(__file__).parent.joinpath(
                'static_data',
                'mock_data_dir',
                '2020',
                '10',
                '16',
                'S207',
                'CROSS',
                'CROSSREF_207_20201016.txt.bz2',
            ),
        ]
        assert discovered_reference_data_files == expected_files
        # Cleanup - none

    def test_search_of_txt_bz2_files_in_all_subdirectories(self):
        # Setup
        data_dir = (
            pathlib.Path(__file__).resolve().parent / 'static_data' / 'mock_data_dir' /
            '2020' / '10'
        )
        pattern = "**/*.txt.bz2"
        # Exercise
        discovered_reference_data_files = wcg.search_files(data_dir, pattern)
        # Verify
        expected_files = [
            pathlib.Path(__file__).parent.joinpath(
                'static_data',
                'mock_data_dir',
                '2020',
                '10',
                '16',
                'S207',
                'CORE',
                'COREREF_207_20201016.txt.bz2',
            ),
            pathlib.Path(__file__).parent.joinpath(
                'static_data',
                'mock_data_dir',
                '2020',
                '10',
                '16',
                'S207',
                'CROSS',
                'CROSSREF_207_20201016.txt.bz2',
            ),
            pathlib.Path(__file__).parent.joinpath(
                'static_data',
                'mock_data_dir',
                '2020',
                '10',
                '16',
                'S207',
                'WATCHLIST',
                'WATCHLIST_207_20201016.txt.bz2',
            ),
            pathlib.Path(__file__).parent.joinpath(
                'static_data',
                'mock_data_dir',
                '2020',
                '10',
                '16',
                'S367',
                'CORE',
                'COREREF_367_20201016.txt.bz2',
            ),
            pathlib.Path(__file__).parent.joinpath(
                'static_data',
                'mock_data_dir',
                '2020',
                '10',
                '16',
                'S367',
                'CROSS',
                'CROSSREF_367_20201016.txt.bz2',
            ),
            pathlib.Path(__file__).parent.joinpath(
                'static_data',
                'mock_data_dir',
                '2020',
                '10',
                '16',
                'S367',
                'WATCHLIST',
                'WATCHLIST_367_20201016.txt.bz2',
            ),
            pathlib.Path(__file__).parent.joinpath(
                'static_data',
                'mock_data_dir',
                '2020',
                '10',
                '16',
                'S673',
                'CORE',
                'COREREF_673_20201016.txt.bz2',
            ),
            pathlib.Path(__file__).parent.joinpath(
                'static_data',
                'mock_data_dir',
                '2020',
                '10',
                '16',
                'S673',
                'CROSS',
                'CROSSREF_673_20201016.txt.bz2',
            ),
            pathlib.Path(__file__).parent.joinpath(
                'static_data',
                'mock_data_dir',
                '2020',
                '10',
                '16',
                'S673',
                'WATCHLIST',
                'WATCHLIST_673_20201016.txt.bz2',
            ),
        ]
        assert discovered_reference_data_files == expected_files
        # Cleanup - none


class TestFindAllCorerefFiles:
    def test_discovery_of_coreref_files(self):
        # Setup
        data_dir = pathlib.Path(__file__).resolve().parent / 'static_data' / 'mock_data_dir'
        # Exercise
        discovered_coreref_files = wcg.find_all_coreref_files(data_dir)
        # Verify
        expected_coreref_files = [
            pathlib.Path(__file__).parent.joinpath(
                'static_data',
                'mock_data_dir',
                '2020',
                '03',
                '16',
                'S794',
                'CORE',
                'COREREF_794_20200316.txt.bz2',
            ),
            pathlib.Path(__file__).parent.joinpath(
                'static_data',
                'mock_data_dir',
                '2020',
                '10',
                '16',
                'S207',
                'CORE',
                'COREREF_207_20201016.txt.bz2',
            ),
            pathlib.Path(__file__).parent.joinpath(
                'static_data',
                'mock_data_dir',
                '2020',
                '10',
                '16',
                'S367',
                'CORE',
                'COREREF_367_20201016.txt.bz2',
            ),
            pathlib.Path(__file__).parent.joinpath(
                'static_data',
                'mock_data_dir',
                '2020',
                '10',
                '16',
                'S673',
                'CORE',
                'COREREF_673_20201016.txt.bz2',
            ),
        ]
        assert discovered_coreref_files == expected_coreref_files
        # Cleanup - none


class TestJsonLoader:
    def test_extrapolation_of_source_instrument_view(self, get_source_symbols_dict):
        # Setup
        path_to_instruments_file = (
            pathlib.Path(__file__).resolve().parent / 'static_data' / 'instruments.json'
        )
        # Exercise
        extrapolated_source_instrument_view = wcg.json_loader(path_to_instruments_file)
        # Verify
        expected_source_instrument_view = get_source_symbols_dict
        assert extrapolated_source_instrument_view == expected_source_instrument_view
        # Cleanup - none

    def test_extrapolation_of_instrument_view_from_complex_input_file(self):
        # Setup
        path_to_instruments_file = (
            pathlib.Path(__file__).resolve().parent / 'static_data' / 'complex_input_file.json'
        )
        # Exercise
        extrapolated_source_instrument_view = wcg.json_loader(path_to_instruments_file)
        # Verify
        expected_source_instrument_view = {
            "207": [
                "F:FDAX\\H21", "F:FDAX\\Z20", "F:FESX\\H21",
                "F:FESX\\Z20", "O:VOW\\A21*", "O:DAI**"
            ],
            "673": [
                "F2:ES*", "F2:NQ*"
            ],
            "794": [
                "E:ADA", "E:BNPP", "E:PHIAA", "E:RDSAA"
            ],
        }
        assert extrapolated_source_instrument_view == expected_source_instrument_view
        # Cleanup - none


class TestGetSourceIdFromFilePath:
    @pytest.mark.parametrize(
        'file_path, source', [
            (pathlib.Path("C:/Users/SomeUser/Data/COREREF_612_20201023.txt.bz2"), '612'),
            (pathlib.Path("C:/Users/SomeUser/Data/COREREF_945_20200815.txt.bz2"), '945'),
        ]
    )
    def test_retrieval_of_source_code(self, file_path, source):
        # Setup
        # Exercise
        retrieved_source_code = wcg.get_source_id_from_file_path(file_path)
        # Verify
        assert retrieved_source_code == source
        # Cleanup - none


class TestRetrieveInstruments:
    @pytest.mark.parametrize(
        'source, expected_list_of_instruments', [
            (
                "207",
                ["F:FBTP", "F:FBTS", "F:FDAX", "F:FESX", "F:FGBL",
                 "F:FGBM", "F:FGBS", "F:FGBX", "F:FOAT", "F:FSMI"
                 ]
             ),
            (
                "367", ["F2:TN", "F2:UB", "F2:ZB", "F2:ZF", "F2:ZN", "F2:ZT"]
            ),
            (
                "611", ["F:FCE"]
            ),
        ]
    )
    def test_retrieval_of_instruments_per_specific_source(
        self,
        get_source_symbols_dict,
        source,
        expected_list_of_instruments

    ):
        # Setup
        source_instruments_view = get_source_symbols_dict
        # Exercise
        retrieved_instruments = wcg.retrieve_instruments(source, source_instruments_view)
        # Verify
        assert retrieved_instruments == expected_list_of_instruments
        # Cleanup - none


class TestCreateEquityRegex:
    def test_creation_of_equity_regex(self):
        # Setup
        instrument_name = "E:VOD"
        # Exercise
        generated_regex = wcg.create_equity_regex(instrument_name)
        # Verify
        correct_regex = r"\bE:VOD\b-{0,1}[A-Z]{0,3}@{0,1}[a-zA-Z0-9]{0,10}"
        assert generated_regex == correct_regex
        # Cleanup - none


class TestCreateFuturesRegex:
    def test_creation_of_futures_regex_without_wildcard(self):
        # Setup
        instrument_name = "F:FBTP\\M21"
        # Exercise
        generated_regex = wcg.create_futures_regex(instrument_name)
        # Verify
        correct_regex = r"F:FBTP\\M21"
        assert generated_regex == correct_regex
        # Cleanup - none

    def test_creation_of_futures_regex_with_wildcard(self):
        # Setup
        instrument_symbol_input = "F:FBTP\\*"
        # Exercise
        generated_regex = wcg.create_futures_regex(instrument_symbol_input)
        # Verify
        correct_regex = r"F:FBTP\\[A-Z][0-9]{2,4}"
        assert generated_regex == correct_regex
        # Cleanup - none


class TestCreateOptionsRegex:
    def test_creation_of_option_regex_without_wildcard(self):
        # Setup
        instrument_symbol_input = "O:PRY\\A21\\25.0"
        # Exercise
        generated_regex = wcg.create_options_regex(instrument_symbol_input)
        # Verify
        expected_regex = r"O:PRY\\A21\\25.0"
        assert generated_regex == expected_regex
        # Cleanup - none

    def test_creation_of_option_regex_with_maturity_wildcard(self):
        # Setup
        instrument_symbol_input = "O:PRY\\*"
        # Exercise
        generated_regex = wcg.create_options_regex(instrument_symbol_input)
        # Verify
        expected_regex = r"O:PRY\\[A-Z][0-9]{2,4}\\[0-9.]{1,10}"
        assert generated_regex == expected_regex
        # Cleanup - none

    def test_creation_of_option_regex_with_strike_wildcard(self):
        # Setup
        instrument_symbol_input = "O:PRY\\A21\\*"
        # Exercise
        generated_regex = wcg.create_options_regex(instrument_symbol_input)
        # Verify
        expected_regex = r"O:PRY\\A21\\[0-9.]{1,10}"
        assert generated_regex == expected_regex
        # Cleanup - none


class TestCreateFixedIncomeRegex:
    def test_creation_of_fixed_income_regex(self):
        # Setup
        instrument_symbol_input = "B:01NU"
        # Exercise
        generated_regex = wcg.create_fixed_income_regex(instrument_symbol_input)
        # Verify
        expected_regex = r"\bB:01NU\b\\{0,1}D{0,1}@{0,1}[a-zA-Z0-9]{1,10}"
        assert generated_regex == expected_regex
        # Cleanup - none


class TestCreateForwardsRegex:
    def test_creation_of_forwards_regex_without_wildcard(self):
        # Setup
        instrument_symbol_input = "R2:GAS\\5D"
        # Exercise
        generated_regex = wcg.create_forwards_regex(instrument_symbol_input)
        # Verify
        expected_regex = r"R2:GAS\\5D"
        assert generated_regex == expected_regex
        # Cleanup - none

    def test_creation_of_forwards_regex_with_wildcard(self):
        # Setup
        instrument_symbol_input = "R2:GAS\\*"
        # Exercise
        generated_regex = wcg.create_forwards_regex(instrument_symbol_input)
        # Verify
        expected_regex = r"R2:GAS\\[A-Z0-9]{2,4}"
        assert generated_regex == expected_regex
        # Cleanup - none


class TestCreateIndexRegex:
    def test_creation_of_index_regex(self):
        # Setup
        instrument_symbol_input = "I:KOSPI200"
        # Exercise
        generated_regex = wcg.create_index_regex(instrument_symbol_input)
        # Verify
        expected_regex = r"\bI:KOSPI200\b"
        assert generated_regex == expected_regex
        # Cleanup - none


class TestCreateSpecificInstrumentRegex:
    @pytest.mark.parametrize(
        "input_symbol, expected_regex_pattern", [
            ("B:01NU", r"\bB:01NU\b\\{0,1}D{0,1}@{0,1}[a-zA-Z0-9]{1,10}"),
            ("E:VOD", r"\bE:VOD\b-{0,1}[A-Z]{0,3}@{0,1}[a-zA-Z0-9]{0,10}"),
            ("F:FBTP\\M21", r"F:FBTP\\M21"),
            ("F:FBTP\\*", r"F:FBTP\\[A-Z][0-9]{2,4}"),
            ("I:KOSPI200", r"\bI:KOSPI200\b"),
            ("O:PRY\\A21\\25.0", r"O:PRY\\A21\\25.0"),
            ("O:PRY\\*", r"O:PRY\\[A-Z][0-9]{2,4}\\[0-9.]{1,10}"),
            ("O:PRY\\A21\\*", r"O:PRY\\A21\\[0-9.]{1,10}"),
            ("R2:GAS\\5D", r"R2:GAS\\5D"),
            ("R2:GAS\\*", r"R2:GAS\\[A-Z0-9]{2,4}"),
        ],
    )
    def test_creation_of_instrument_specific_regex(self, input_symbol, expected_regex_pattern):
        # Setup - none
        # Exercise
        generated_regex = wcg.create_specific_instrument_regex(input_symbol)
        # Verify
        assert generated_regex == expected_regex_pattern
        # Cleanup - none


class TestCreateInstrumentLevelPattern:
    def test_creation_of_instrument_level_regex(self):
        # Setup
        instrument_names = ['F:FBTP\\*', 'F:FDAX\\M21', 'F:FESX\\*']
        # Exercise
        generated_instrument_regexes = wcg.create_instrument_level_pattern(instrument_names)
        # Verify
        expected_instrument_regexes = (
            r'(F:FBTP\\[A-Z][0-9]{2,4}|F:FDAX\\M21|F:FESX\\[A-Z][0-9]{2,4})'
        )
        assert generated_instrument_regexes == expected_instrument_regexes
        # Cleanup - none


class TestCreateDCMessageLevelPattern:
    def test_creation_of_dc_message_level_pattern(self):
        # Setup
        source_id = "207"
        instrument_names = ['F:FBTP\\*', 'F:FDAX\\M21', 'F:FESX\\*']
        # Exercise
        generated_regex = wcg.create_dc_message_level_pattern(source_id, instrument_names)
        # Verify
        expected_dc_level_regex = (
            r"^DC\|207\|(F:FBTP\\[A-Z][0-9]{2,4}|F:FDAX\\M21|F:FESX\\[A-Z][0-9]{2,4})"
        )
        assert generated_regex == expected_dc_level_regex
        # Cleanup - none


class TestCombineMultipleRegexes:
    def test_combination_of_regexes(self):
        # Setup
        regexes = [r'F2:ES\\[A-Z][0-9]{2,4}', r'F2:NQ\\[A-Z][0-9]{2,4}']
        # Exercise
        generated_combination_of_regexes = wcg.combine_multiple_regexes(regexes)
        # Verify
        expected_combination_of_regexes = "F2:ES\\\\[A-Z][0-9]{2,4}|F2:NQ\\\\[A-Z][0-9]{2,4}"
        assert generated_combination_of_regexes.pattern == expected_combination_of_regexes
        # Cleanup - none


class TestRetrieveSourceSymbolPairs:
    def test_retrieval_of_source_name_pairs(self):
        # Setup
        path_to_reference_data_file = (
            pathlib.Path(__file__).resolve().parent / "static_data" / "mock_data_dir" /
            "2020" / "10" / "16" / "S207" / "CORE" / "COREREF_207_20201016.txt.bz2"
        )
        instrument_level_regex = (
            r"(F:FDAX\\[A-Z][0-9]{2,4}|F:FESX\\[A-Z][0-9]{2,4}|F:FBTP\\[A-Z][0-9]{2,4}|"
            r"F:FBTS\\[A-Z][0-9]{2,4})"
        )
        message_level_regex = (
            r"^DC\|207\|(F:FDAX\\[A-Z][0-9]{2,4}|F:FESX\\[A-Z][0-9]{2}|F:FBTP\\[A-Z][0-9]{2,4}|"
            r"F:FBTS\\[A-Z][0-9]{2,4})"
        )
        # Exercise
        retrieved_source_name_pairs = wcg.retrieve_source_symbol_pairs(
            path_to_reference_data_file, message_level_regex, instrument_level_regex
        )
        # Verify
        expected_source_name_pairs = [
            ('207', 'F:FBTP\\H21'), ('207', 'F:FBTP\\M21'), ('207', 'F:FBTP\\Z20'),
            ('207', 'F:FBTS\\H21'), ('207', 'F:FBTS\\M21'), ('207', 'F:FBTS\\Z20'),
            ('207', 'F:FDAX\\H21'), ('207', 'F:FDAX\\M21'), ('207', 'F:FDAX\\Z20'),
            ('207', 'F:FESX\\H21'), ('207', 'F:FESX\\H22'), ('207', 'F:FESX\\M21'),
            ('207', 'F:FESX\\M22'), ('207', 'F:FESX\\U21'), ('207', 'F:FESX\\U22'),
            ('207', 'F:FESX\\Z20'), ('207', 'F:FESX\\Z21')
        ]
        assert retrieved_source_name_pairs == expected_source_name_pairs
        # Cleanup - none

    def test_retrieval_of_source_name_pairs_with_selected_contracts_only(self):
        # Setup
        path_to_reference_data_file = (
            pathlib.Path(__file__).resolve().parent / "static_data" / "mock_data_dir" /
            "2020" / "10" / "16" / "S207" / "CORE" / "COREREF_207_20201016.txt.bz2"
        )
        instrument_level_regex = r"(F:FDAX\\Z20|F:FESX\\H22|F:FBTP\\H21|F:FBTS\\M21)"

        message_level_regex = r"^DC\|207\|(F:FDAX\\Z20|F:FESX\\H22|F:FBTP\\H21|F:FBTS\\M21)"

        # Exercise
        retrieved_source_name_pairs = wcg.retrieve_source_symbol_pairs(
            path_to_reference_data_file, message_level_regex, instrument_level_regex
        )
        # Verify
        expected_source_name_pairs = [
            ('207', 'F:FBTP\\H21'), ('207', 'F:FBTS\\M21'), ('207', 'F:FDAX\\Z20'),
            ('207', 'F:FESX\\H22'),
        ]
        assert retrieved_source_name_pairs == expected_source_name_pairs
        # Cleanup - none

    def test_retrieval_of_source_name_pairs_when_one_contract_are_not_in_file(self):
        # Setup
        path_to_reference_data_file = (
            pathlib.Path(__file__).resolve().parent / "static_data" / "mock_data_dir" /
            "2020" / "10" / "16" / "S207" / "CORE" / "COREREF_207_20201016.txt.bz2"
        )
        instrument_level_regex = r"(F:FDAX\\Z21|F:FESX\\H22|F:FBTP\\H21|F:FBTS\\M21)"

        message_level_regex = r"^DC\|207\|(F:FDAX\\Z21|F:FESX\\H22|F:FBTP\\H21|F:FBTS\\M21)"

        # Exercise
        retrieved_source_name_pairs = wcg.retrieve_source_symbol_pairs(
            path_to_reference_data_file, message_level_regex, instrument_level_regex
        )
        # Verify
        expected_source_name_pairs = [
            ('207', 'F:FBTP\\H21'), ('207', 'F:FBTS\\M21'), ('207', 'F:FESX\\H22'),
        ]
        assert retrieved_source_name_pairs == expected_source_name_pairs
        # Cleanup - none

    def test_retrieval_of_source_name_pairs_when_all_contracts_are_not_in_file(self):
        # Setup
        path_to_reference_data_file = (
            pathlib.Path(__file__).resolve().parent / "static_data" / "mock_data_dir" /
            "2020" / "10" / "16" / "S207" / "CORE" / "COREREF_207_20201016.txt.bz2"
        )
        instrument_level_regex = r"(F:FDAX\\Z21|F:FESX\\H22|F:FBTP\\H21|F:FBTS\\M21)"

        message_level_regex = r"^DC\|207\|(F:FDAX\\Z21|F:FESX\\Z22|F:FBTP\\H22|F:FBTS\\M22)"

        # Exercise
        retrieved_source_name_pairs = wcg.retrieve_source_symbol_pairs(
            path_to_reference_data_file, message_level_regex, instrument_level_regex
        )
        # Verify
        expected_source_name_pairs = []
        assert retrieved_source_name_pairs == expected_source_name_pairs
        # Cleanup - none

    def test_system_exit(self):
        # Setup
        path_to_coreref_file = pathlib.Path(__file__).resolve().parent.joinpath(
            'static_data', 'COREREF_673_20201016.txt',
        )
        message_level_pattern = r"^DC\|673\|(F2:ES\\[A-Z][0-9]{2,4}|F2:NQ\\[A-Z][0-9]{2,4})"
        instrument_level_pattern = r"(F2:ES\\[A-Z][0-9]{2,4}|F2:NQ\\[A-Z][0-9]{2,4})"
        # Exercise
        with pytest.raises(SystemExit) as system_exit:
            wcg.retrieve_source_symbol_pairs(
                path_to_coreref_file, message_level_pattern, instrument_level_pattern,
            )
        # Verify
        assert system_exit.type == SystemExit
        # Cleanup - none

    def test_system_exit_message(self):
        # Setup
        path_to_coreref_file = pathlib.Path(__file__).resolve().parent.joinpath(
            'static_data', 'COREREF_673_20201016.txt',
        )
        message_level_pattern = r"^DC\|673\|(F2:ES\\[A-Z][0-9]{2,4}|F2:NQ\\[A-Z][0-9]{2,4})"
        instrument_level_pattern = r"(F2:ES\\[A-Z][0-9]{2,4}|F2:NQ\\[A-Z][0-9]{2,4})"
        # Exercise
        with pytest.raises(SystemExit) as system_exit:
            wcg.retrieve_source_symbol_pairs(
                path_to_coreref_file, message_level_pattern, instrument_level_pattern,
            )
        # Verify
        expected_exit_message = (
            f"Process finished with exit code 1\n"
            f"Attempted to process: {path_to_coreref_file.as_posix()}\n"
            f"The file has extension:'.txt'. Expected:'.bz2'"
        )
        assert system_exit.value.code == expected_exit_message
        # Cleanup - none


class TestProcessCorerefFile:
    def test_discovery_of_contract_symbols_with_specific_contracts(self, get_source_symbols_dict):
        # Setup
        file_to_process = pathlib.Path(__file__).resolve().parent.joinpath(
                'static_data', 'mock_data_dir', '2020', '10', '16', 'S673', 'CORE',
                'COREREF_673_20201016.txt.bz2'
                )
        dictionary_of_symbols = {"673": ["F2:ES\\H21", "F2:ES\\Z20", "F2:NQ\\H21", "F2:NQ\\Z20"]}
        # Exercise
        discovered_contract_symbols = wcg.process_coreref_file(
            file_to_process, dictionary_of_symbols
        )
        # Verify
        expected_symbols = [
            ('673', 'F2:ES\\H21'), ('673', 'F2:ES\\Z20'),
            ('673', 'F2:NQ\\H21'), ('673', 'F2:NQ\\Z20'),
        ]
        assert discovered_contract_symbols == expected_symbols
        # Cleanup - none

    def test_discovery_of_contract_symbols_with_wildcards(self, get_source_symbols_dict):
        # Setup
        file_to_process = pathlib.Path(__file__).resolve().parent.joinpath(
                'static_data', 'mock_data_dir', '2020', '10', '16', 'S673', 'CORE',
                'COREREF_673_20201016.txt.bz2'
                )
        dictionary_of_symbols = {"673": ["F2:ES*", "F2:NQ*"]}
        # Exercise
        discovered_contract_symbols = wcg.process_coreref_file(
            file_to_process, dictionary_of_symbols
        )
        # Verify
        expected_symbols = [
             ('673', 'F2:ES\\H21'), ('673', 'F2:ES\\M21'), ('673', 'F2:ES\\U21'),
             ('673', 'F2:ES\\Z20'), ('673', 'F2:ES\\Z21'), ('673', 'F2:NQ\\H21'),
             ('673', 'F2:NQ\\M21'), ('673', 'F2:NQ\\U21'), ('673', 'F2:NQ\\Z20'),
             ('673', 'F2:NQ\\Z21')
        ]
        assert discovered_contract_symbols == expected_symbols
        # Cleanup - none

    def test_discovery_of_contract_symbols_with_mix_of_contracts_and_wildcards(self):
        # Setup
        file_to_process = pathlib.Path(__file__).resolve().parent.joinpath(
                'static_data', 'mock_data_dir', '2020', '10', '16', 'S673', 'CORE',
                'COREREF_673_20201016.txt.bz2'
                )
        dictionary_of_symbols = {"673": ["F2:ES\\H21", "F2:ES\\Z20", "F2:NQ*"]}
        # Exercise
        discovered_contract_symbols = wcg.process_coreref_file(
            file_to_process, dictionary_of_symbols
        )
        # Verify
        expected_symbols = [
             ('673', 'F2:ES\\H21'), ('673', 'F2:ES\\Z20'), ('673', 'F2:NQ\\H21'),
             ('673', 'F2:NQ\\M21'), ('673', 'F2:NQ\\U21'), ('673', 'F2:NQ\\Z20'),
             ('673', 'F2:NQ\\Z21')
        ]
        assert discovered_contract_symbols == expected_symbols
        # Cleanup - none

    def test_discovery_of_symbols_within_equity_coreref_file(self):
        # Setup
        file_to_process = pathlib.Path(__file__).resolve().parent.joinpath(
            'static_data', 'mock_data_dir', '2020', '03', '16', 'S794', 'CORE',
            'COREREF_794_20200316.txt.bz2'
        )
        dictionary_of_symbols = {"794": ["E:ADA", "E:BNPP", "E:PHIAA", "E:RDSAA"]}
        # Exercise
        discovered_contract_symbols = wcg.process_coreref_file(
            file_to_process, dictionary_of_symbols
        )
        # Verify
        expected_symbols = [
            ('794', 'E:ADA'), ('794', 'E:BNPP'), ('794', 'E:PHIAA'), ('794', 'E:RDSAA'),
        ]
        assert discovered_contract_symbols == expected_symbols
        # Cleanup - none


class TestProcessAllCorerefFiles:
    def test_discovery_of_all_symbols(self):
        # Setup
        files_to_process = [
            pathlib.Path(__file__).resolve().parent.joinpath(
                'static_data', 'mock_data_dir', '2020', '10', '16', 'S367', 'CORE',
                'COREREF_367_20201016.txt.bz2'
            ),
            pathlib.Path(__file__).resolve().parent.joinpath(
                'static_data', 'mock_data_dir', '2020', '10', '16', 'S673', 'CORE',
                'COREREF_673_20201016.txt.bz2'
                ),
        ]
        dictionary_of_symbols = {
            "367": ["F2:TN*", "F2:UB*", "F2:ZB*", "F2:ZF*", "F2:ZN*", "F2:ZT*"],
            "673": ["F2:ES*", "F2:NQ*"]
        }
        # Exercise
        discovered_symbols = wcg.process_all_coreref_files(
            files_to_process, dictionary_of_symbols
        )
        # Verify
        expected_symbols = [
            ('367', 'F2:TN\\H21'), ('367', 'F2:TN\\M21'), ('367', 'F2:TN\\Z20'),
            ('367', 'F2:UB\\H21'), ('367', 'F2:UB\\M21'), ('367', 'F2:UB\\Z20'),
            ('367', 'F2:ZB\\H21'), ('367', 'F2:ZB\\M21'), ('367', 'F2:ZB\\Z20'),
            ('367', 'F2:ZF\\H21'), ('367', 'F2:ZF\\M21'), ('367', 'F2:ZF\\U20'),
            ('367', 'F2:ZF\\Z20'), ('367', 'F2:ZN\\H21'), ('367', 'F2:ZN\\M21'),
            ('367', 'F2:ZN\\Z20'), ('367', 'F2:ZT\\H21'), ('367', 'F2:ZT\\M21'),
            ('367', 'F2:ZT\\U20'), ('367', 'F2:ZT\\Z20'), ('673', 'F2:ES\\H21'),
            ('673', 'F2:ES\\M21'), ('673', 'F2:ES\\U21'), ('673', 'F2:ES\\Z20'),
            ('673', 'F2:ES\\Z21'), ('673', 'F2:NQ\\H21'), ('673', 'F2:NQ\\M21'),
            ('673', 'F2:NQ\\U21'), ('673', 'F2:NQ\\Z20'), ('673', 'F2:NQ\\Z21')
        ]
        assert discovered_symbols == expected_symbols
        # Cleanup - none

    def test_mixed_discovery_of_symbols_and_contracts(self):
        # Setup
        files_to_process = [
            pathlib.Path(__file__).resolve().parent.joinpath(
                'static_data', 'mock_data_dir', '2020', '10', '16', 'S367', 'CORE',
                'COREREF_367_20201016.txt.bz2'
            ),
            pathlib.Path(__file__).resolve().parent.joinpath(
                'static_data', 'mock_data_dir', '2020', '10', '16', 'S673', 'CORE',
                'COREREF_673_20201016.txt.bz2'
                ),
        ]
        dictionary_of_symbols = {
            "367": [
                "F2:TN\\Z20", "F2:TN\\H21", "F2:UB\\Z20", "F2:UB\\H21",
                "F2:ZB\\Z20", "F2:ZB\\H21", "F2:ZF*", "F2:ZN*", "F2:ZT*",
            ],
            "673": ["F2:ES*", "F2:NQ*"]
        }
        # Exercise
        discovered_symbols = wcg.process_all_coreref_files(
            files_to_process, dictionary_of_symbols
        )
        # Verify
        expected_symbols = [
            ('367', 'F2:TN\\H21'), ('367', 'F2:TN\\Z20'), ('367', 'F2:UB\\H21'),
            ('367', 'F2:UB\\Z20'), ('367', 'F2:ZB\\H21'), ('367', 'F2:ZB\\Z20'),
            ('367', 'F2:ZF\\H21'), ('367', 'F2:ZF\\M21'), ('367', 'F2:ZF\\U20'),
            ('367', 'F2:ZF\\Z20'), ('367', 'F2:ZN\\H21'), ('367', 'F2:ZN\\M21'),
            ('367', 'F2:ZN\\Z20'), ('367', 'F2:ZT\\H21'), ('367', 'F2:ZT\\M21'),
            ('367', 'F2:ZT\\U20'), ('367', 'F2:ZT\\Z20'), ('673', 'F2:ES\\H21'),
            ('673', 'F2:ES\\M21'), ('673', 'F2:ES\\U21'), ('673', 'F2:ES\\Z20'),
            ('673', 'F2:ES\\Z21'), ('673', 'F2:NQ\\H21'), ('673', 'F2:NQ\\M21'),
            ('673', 'F2:NQ\\U21'), ('673', 'F2:NQ\\Z20'), ('673', 'F2:NQ\\Z21')
        ]
        assert discovered_symbols == expected_symbols
        # Cleanup - none


class TestGenerateConfigFilePath:
    def test_generation_of_file_path(self):
        # Setup
        target_directory = "C:/Users/some_user/config_files"
        # Exercise
        generated_file_path = wcg.generate_config_file_path(target_directory)
        # Verify
        expected_file_path = pathlib.Path(target_directory).joinpath(
            f"watchlist_config_{datetime.datetime.utcnow().strftime('%Y%m%d')}.csv")
        assert generated_file_path.as_posix() == expected_file_path.as_posix()
        # Cleanup - none


class TestConfigFileWriter:
    def test_csv_file_is_created(self):
        # Setup
        target_directory = pathlib.Path(__file__).resolve().parent / "static_data"
        source_symbol_pairs = [
            ('367', 'F2:TN\\H21')
        ]
        # Exercise
        wcg.config_file_writer(target_directory.as_posix(), source_symbol_pairs)
        # Verify
        expected_file_path = (
            pathlib.Path(__file__).resolve().parent / "static_data" /
            f"watchlist_config_{datetime.datetime.utcnow().strftime('%Y%m%d')}.csv"
        )
        assert expected_file_path.is_file() is True
        # Cleanup
        target_directory.joinpath(expected_file_path).unlink(missing_ok=True)

    def test_written_file_has_proper_name(self):
        # Setup
        target_directory = pathlib.Path(__file__).resolve().parent / "static_data"
        source_symbol_pairs = [
            ('367', 'F2:TN\\H21'), ('367', 'F2:TN\\M21'), ('367', 'F2:TN\\Z20'),
            ('367', 'F2:UB\\H21'), ('367', 'F2:UB\\M21'), ('367', 'F2:UB\\Z20'),
            ('367', 'F2:ZB\\H21'), ('367', 'F2:ZB\\M21'), ('367', 'F2:ZB\\Z20'),
            ('367', 'F2:ZF\\H21'), ('367', 'F2:ZF\\M21'), ('367', 'F2:ZF\\U20'),
            ('367', 'F2:ZF\\Z20'), ('367', 'F2:ZN\\H21'), ('367', 'F2:ZN\\M21'),
            ('367', 'F2:ZN\\Z20'), ('367', 'F2:ZT\\H21'), ('367', 'F2:ZT\\M21'),
            ('367', 'F2:ZT\\U20'), ('367', 'F2:ZT\\Z20')
        ]
        # Exercise
        wcg.config_file_writer(target_directory.as_posix(), source_symbol_pairs)
        file_name = list(target_directory.glob("watchlist_config*.csv"))[0].name
        # Verify
        expected_file_name = f"watchlist_config_{datetime.datetime.utcnow().strftime('%Y%m%d')}.csv"
        assert file_name == expected_file_name
        # Cleanup
        target_directory.joinpath(expected_file_name).unlink(missing_ok=True)

    def test_file_has_proper_header(self):
        # Setup
        target_directory = pathlib.Path(__file__).resolve().parent / "static_data"
        source_symbol_pairs = []
        # Exercise
        wcg.config_file_writer(target_directory.as_posix(), source_symbol_pairs)
        # Verify
        expected_header = "sourceId,RTSsymbol"
        path_to_file = (
            pathlib.Path(__file__).resolve().parent / "static_data" /
            f"watchlist_config_{datetime.datetime.utcnow().strftime('%Y%m%d')}.csv"
        )
        with path_to_file.open('r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for index, row in enumerate(csv_reader):
                if index == 0:
                    file_header = ','.join(row)
        assert file_header == expected_header
        # Cleanup
        path_to_file.unlink(missing_ok=True)

    def test_file_has_expected_content(self):
        # Setup
        target_directory = pathlib.Path(__file__).resolve().parent / "static_data"
        source_symbol_pairs = [
            ('207', 'F:FBTP\\H21'), ('207', 'F:FBTP\\M21'), ('207', 'F:FBTP\\Z20'),
            ('207', 'F:FBTS\\H21'), ('207', 'F:FBTS\\M21'), ('207', 'F:FBTS\\Z20')
        ]
        # Exercise
        wcg.config_file_writer(target_directory.as_posix(), source_symbol_pairs)
        # Verify
        path_to_file = (
            pathlib.Path(__file__).resolve().parent / "static_data" /
            f"watchlist_config_{datetime.datetime.utcnow().strftime('%Y%m%d')}.csv"
        )
        expected_file_content = (
            "sourceId,RTSsymbol\n"
            "207,F:FBTP\\H21\n"
            "207,F:FBTP\\M21\n"
            "207,F:FBTP\\Z20\n"
            "207,F:FBTS\\H21\n"
            "207,F:FBTS\\M21\n"
            "207,F:FBTS\\Z20"
        )
        with path_to_file.open('r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            rows = [','.join(row) for row in csv_reader]
            file_content = '\n'.join(rows)
        assert file_content == expected_file_content
        # Cleanup
        path_to_file.unlink(missing_ok=True)

    def test_return_the_expected_summary(self):
        # Setup
        target_directory = pathlib.Path(__file__).resolve().parent / "static_data"
        source_symbol_pairs = [
            ('673', 'F2:ES\\H21'), ('673', 'F2:ES\\M21'), ('673', 'F2:ES\\U21'),
            ('673', 'F2:ES\\Z20'), ('673', 'F2:ES\\Z21'), ('673', 'F2:NQ\\H21'),
            ('673', 'F2:NQ\\M21'), ('673', 'F2:NQ\\U21'), ('673', 'F2:NQ\\Z20'),
            ('673', 'F2:NQ\\Z21')
        ]
        # Exercise
        generated_summary = wcg.config_file_writer(target_directory.as_posix(), source_symbol_pairs)
        # Verify
        expected_summary = ("Configuration file successfully written.\n"
                            "10 symbols were added to the file.")
        assert generated_summary == expected_summary
        # Cleanup
        path_to_file = (
            pathlib.Path(__file__).resolve().parent / "static_data" /
            f"watchlist_config_{datetime.datetime.utcnow().strftime('%Y%m%d')}.csv"
        )
        path_to_file.unlink(missing_ok=True)

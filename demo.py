from datetime import datetime

from class_parser import JsonFileParser, CsvFileParser


def test_json_parser():
    json_parser = JsonFileParser(file="static_data\\config.json")
    # APPLY PARSER TO GET DATETIME OBJECT
    assert (datetime(2019, 4, 3) == json_parser.date_parser("date_input", fmt="%d/%m/%Y"))
    # APPLY PARSER TO GET DATETIME OBJECT WITH UNKNOWN FMT
    assert (datetime(2019, 4, 3) == json_parser.date_util_parser("date_input"))
    # APPLY PARSER TO GET BOOLEAN FROM STRING
    assert (True == json_parser.boolean_string_parser("boolean_string_input"))
    # APPLY PARSER TO GET BOOLEAN FROM STRING
    assert ("ABCDEF" == json_parser.string_parser("string_case_input", case="upper"))
    # APPLY PARSER TO GET INT
    assert (3 == json_parser.int_parser("integer_input"))
    # APPLY PARSER TO GET FLOAT
    assert (4.2 == json_parser.float_parser("float_input"))
    # APPLY PARSER TO LIST
    assert ([datetime(2019, 4, 3), datetime(2019, 4, 4)] == json_parser.date_parser("date_list_input", fmt="%d/%m/%Y"))
    # APPLY PARSER TO NESTED FIELD AND RETURNS SUBKEY
    assert ({'bottom_1': ['ABC', 'CDE'], 'bottom_2': ['FGH', 'ILM']} == json_parser.string_parser("nested_field",
                                                                                                  case="upper"))
    # APPLY PARSER ONLY TO SPECIFIC SUBKEY
    assert ("AbCdEf" == json_parser.string_parser("super_nested_field", "nested_2", "nested_3"))
    # RAISE ERROR IF KEY IS MISSING
    try:
        json_parser.boolean_string_parser("not_existent_key")
    except Exception as e:
        assert type(e) == KeyError
    else:
        assert False
    # DEFAULT TO PASSED VALUE IF RAISE ERROR == FALSE
    assert ("AAA" == json_parser.string_parser("not_existent_field", raise_error=False, default="AAA"))
    # GET ROW VALUE
    assert (['03/04/2019', '04/04/2019'] == json_parser.get("date_list_input", raise_error=True))
    # DEFAULT TO PASSED VALUE IF RAISE ERROR == FALSE
    assert ("QWY" == json_parser.get("not_existent_field", raise_error=False, default="QWY"))
    # APPLY FUNCTION TO NESTED FIELD
    assert ({'nested_1': [True, False], 'nested_2': {'nested_3': True}} == (
        json_parser.apply_to_nested_dict("super_nested_field", fun=lambda x: "Ab" in x)))


def test_csv_parser():
    csv_parser = CsvFileParser(file="static_data\\config.csv")

    # APPLY PARSER TO GET DATETIME OBJECT
    assert (datetime(2019, 4, 3) == csv_parser.date_parser("date_input", fmt="%d/%m/%Y"))
    # APPLY PARSER TO GET DATETIME OBJECT WITH UNKNOWN FMT
    assert (datetime(2019, 4, 3) == csv_parser.date_util_parser("date_input"))
    # APPLY PARSER TO GET BOOLEAN FROM STRING
    assert (True == csv_parser.boolean_string_parser("boolean_input"))
    # APPLY PARSER TO GET BOOLEAN FROM STRING
    assert ("ABCDEFGHI" == csv_parser.string_parser("string_case_input", case="upper"))
    # APPLY PARSER TO GET INT
    assert (5 == csv_parser.int_parser("integer_input"))
    # APPLY PARSER TO GET FLOAT
    assert (0.5 == csv_parser.float_parser("float_input"))
    # OTHERWISE GET RAW DATA
    assert ("0.5" == csv_parser.get("float_input"))


if __name__ == "__main__":
    test_json_parser()
    test_csv_parser()

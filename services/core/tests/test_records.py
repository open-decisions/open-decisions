from governmental_core.records import all_record_files, check_file


def test_all_records_valid():
    failures = {str(f): check_file(f) for f in all_record_files() if check_file(f)}
    assert failures == {}

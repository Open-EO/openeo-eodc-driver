import os


def test_complete_to_public_path(file_service, user_folder, user_id):
    test_path = os.path.join(user_folder, 'files', 'some-file.txt')
    actual_public_path = file_service.complete_to_public_path(user_id=user_id, complete_path=test_path)
    assert actual_public_path == 'files/some-file.txt'


def test_authorize_file(file_service, user_folder, user_id):
    test_path = 'some-folder/some-file.txt'
    worked, error_dict, complete_path = file_service.authorize_file(user_id=user_id, path=test_path)
    assert worked
    assert error_dict is None
    assert complete_path == os.path.join(user_folder, 'files', test_path)


def test_authorize_file_dir(file_service, user_folder, user_id):
    test_folder = 'somefolder.txt'
    ref_folder = os.path.join(user_folder, 'files', test_folder)
    if not os.path.isdir(ref_folder):
        os.mkdir(ref_folder)

    worked, error_dict, complete_path = file_service.authorize_file(user_id=user_id, path=test_folder)
    assert not worked
    assert complete_path is None
    assert error_dict == {
        'status': 'error',
        'service': 'files',
        'code': 400,
        'user_id': 'test-user',
        'msg': 'somefolder.txt: Must be a file, no directory.',
        'internal': False,
        'links': []}


def test_authorize_file_path(file_service, user_folder, user_id):
    test_file = 'somefile_without_extension'

    worked, error_dict, complete_path = file_service.authorize_file(user_id=user_id, path=test_file)
    assert not worked
    assert complete_path is None
    print(error_dict)
    assert error_dict == {
        'status': 'error',
        'service': 'files',
        'code': 401,
        'user_id': 'test-user',
        'msg': 'somefile_without_extension: This path is not valid.',
        'internal': False,
        'links': []}


def test_authorize_existing_file_missing(file_service, user_folder, user_id):
    test_file = 'somefile.txt'
    worked, error_dict, complete_path = file_service.authorize_existing_file(user_id=user_id, path=test_file)
    assert not worked
    assert complete_path is None
    assert error_dict == {
        'status': 'error',
        'service': 'files',
        'code': 404,
        'user_id': 'test-user',
        'msg': 'somefile.txt: No such file or directory.',
        'internal': False,
        'links': []}


def test_authorize_exsiting_file(file_service, user_folder, user_id):
    test_file = 'somefile.txt'
    ref_path = os.path.join(user_folder, 'files', test_file)
    open(ref_path, 'a').close()
    worked, error_dict, complete_path = file_service.authorize_existing_file(user_id=user_id, path=test_file)
    assert worked
    assert error_dict is None
    assert complete_path == ref_path


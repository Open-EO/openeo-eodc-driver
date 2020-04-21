import os
import shutil


def test_upload(file_service, user_folder, user_id, input_folder, tmp_folder):
    shutil.copyfile(os.path.join(input_folder, 'upload.txt'), os.path.join(tmp_folder, 'upload.txt'))
    ref_path = 'final.txt'
    result = file_service.upload(user_id=user_id, tmp_path=tmp_folder, path=ref_path)
    assert result == {
        'code': 200,
        'data': {
            'path': 'files/final.txt',
            'size': '4.0KiB'
        },
        'status': 'success'}


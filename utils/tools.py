import functools

from utils import exceptions


class UploadFileUtils:
    def __init__(self, file_obj):
        if not file_obj:
            raise exceptions.UploadFileError("文件不存在，请添加文件!")
        self.file_obj = file_obj

    def _check_mime_type(self, correct_mime_type):
        # 限制文件MIME Type
        if self.file_obj.content_type not in correct_mime_type:
            raise exceptions.UploadFileError("文件类型错误, 请上传正确格式!")

    def _check_file_name(self, end_rule=None):
        # 限制文件后缀
        if end_rule:
            file_name = self.file_obj.name.strip('"')
            if not file_name.endswith(end_rule):
                raise exceptions.UploadFileError("文件类型错误, 请上传正确格式!")

    def file_receiving(self):
        """接收文件"""
        upload_file = b""
        for chunk in self.file_obj.chunks():
            upload_file += chunk
        return upload_file

    def py_file_check(self):
        """py文件检查"""
        # self._check_mime_type(["application/xml", "text/xml"])
        self._check_file_name(end_rule="py")

    def image_file_check(self):
        self._check_mime_type(["image/png", "image/jpeg"])
        self._check_file_name(end_rule=("jpg", "jpeg", "png", "svg"))


def build_default_dict(name, key, value):
    """构建基础字典"""
    return dict(name=name, key=key, value=value)


class combomethod(object):
    def __init__(self, method):
        self.method = method

    def __get__(self, obj=None, objtype=None):
        @functools.wraps(self.method)
        def _wrapper(*args, **kwargs):
            if obj is not None:
                return self.method(obj, *args, **kwargs)
            else:
                return self.method(objtype, *args, **kwargs)

        return _wrapper

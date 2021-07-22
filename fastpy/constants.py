import pathlib

INDENT = ' ' * 4
SPACER = '-' * 10
NAMESPACE_SEP = "::"
def JOIN_NAMESPACE (*parts: str) -> str: return NAMESPACE_SEP.join (parts)

LIB_NAME = "libfastpy"
INCL_FOLDER = pathlib.Path (__file__).parent.parent / "include"
print (INCL_FOLDER)
INCL_FLAG = f"-I{INCL_FOLDER}"

COMMONS_FOLDER_FORMAT_STRING = f"{LIB_NAME}/common/{{file}}"

PATH_TO_BASE_H = COMMONS_FOLDER_FORMAT_STRING.format (file = "base.hpp")
BASE_NAMESPACE = JOIN_NAMESPACE (LIB_NAME)

WRAPPER_CLASS = JOIN_NAMESPACE (BASE_NAMESPACE, "Ref")
def WRAP_CLASS (_class: str): return f"{WRAPPER_CLASS} <{_class}>"

PATH_TO_BUILTINS_H = COMMONS_FOLDER_FORMAT_STRING.format (file = "functions.hpp")
BUILTINS_NAMESPACE = JOIN_NAMESPACE (BASE_NAMESPACE, "functions")
IMPLEMENTED_BUILTINS = {
    "print": {
        "signature": {
            "args": [{
                "starred": True,
                "name": "objects",
                "type": {
                    "templated": True
                }
            }],
            "kwargs": [{
                "starred": False,
                "name": "sep",
                "type": {
                    "templated": False,
                    "python": str
                },
                "default": " "
            }, {
                "starred": False,
                "name": "end",
                "type": {
                    "templated": False,
                    "python": str
                },
                "default": "\n"
            }],
            "dst_ordering": ["objects", "sep", "end"]
        }
    }
}

PATH_TO_TYPES_H = COMMONS_FOLDER_FORMAT_STRING.format (file = "types.hpp")
TYPES_NAMESPACE = JOIN_NAMESPACE (BASE_NAMESPACE, "types")
TYPES_MAPPING = {
    str: "String",
    int: "Int"
}

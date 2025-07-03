from clang import cindex
from .definition import TapeType
import typing

class Context:
    def __init__(self, file_path:str):
        self._buffer = dict()
        self._file_path = file_path
        self._handlers = dict()
        self._handlers[TapeType.TCLASS.name] = ClassHandler(self, TapeType.TCLASS.name)
        self._handlers[TapeType.TFUNCTION.name] = FunctionHandler(self, TapeType.TFUNCTION.name)

    @property
    def database(self)->dict:
        return self._buffer

    @property
    def handlers(self)->dict:
        return self._handlers
    
    @property
    def file_path(self)->dict:
        return self._file_path
    
    def __str__(self):
        return '{}: {}'.format(self._file_path, str(self._buffer))

class CursorProxy:
    def __init__(self, cursor:cindex.Cursor, location:cindex.SourceLocation, handler = None):
        self._key = location.line << 20 | location.column
        self._cursor = cursor
        self._handler = handler
        self.childrens = list()
    @property
    def key(self):
        return self._key
    
    @property
    def cursor(self)->cindex.Cursor:
        return self._cursor
    
    @property
    def handler(self):
        return self._handler
    
    def __gt__(self, other):
        return self._key > other._key
    
    def __lt__(self, other):
        return self._key < other._key
    
    def add_child(self, children):
        self.childrens.append(children)

class Handler:
    def __init__(self, parent:Context, key_word):
        self._key_word:str = key_word
        self._parent:Context = parent

    @property
    def key_word(self):
        return self._key_word
    
    def meta_info_filter(self, key_words:list, cursor:cindex.Cursor) ->dict:
        token_str = ""
        for token in cursor.get_tokens():
            token_str = token_str + token.spelling
        token_str = token_str.replace(self._key_word, "dict")
        meta_info = eval("{}".format(token_str))
        real_meta_info = dict()
        for key in key_words:
            real_meta_info[key] = meta_info.get(key, "")
        return real_meta_info
    
    def match(self, proxy:CursorProxy, children:typing.Iterator)->bool:
        pass

def collection_metadata(context:Context, root:cindex.Cursor):
    cursor_list:list[CursorProxy] = []
    cursor:cindex.Cursor
    for cursor in root.get_children():
        location:cindex.SourceLocation = cursor.location
        if location.file is None:
            continue
        if location.file.name != context.file_path:
            continue
        if cursor.kind == cindex.CursorKind.MACRO_INSTANTIATION:
            handle = context.handlers.get(cursor.spelling)
            if handle:
                cursor_list.append(CursorProxy(cursor, location, handle))
        elif cursor.kind == cindex.CursorKind.CLASS_DECL or cursor.kind == cindex.CursorKind.STRUCT_DECL:
            proxy = CursorProxy(cursor, location)
            cursor_list.append(proxy)
            for child_cursor in cursor.get_children():
                if child_cursor.kind == cindex.CursorKind.CXX_METHOD:
                    cursor_list.append(CursorProxy(child_cursor, child_cursor.location))
                elif child_cursor.kind == cindex.CursorKind.CONSTRUCTOR:
                    if child_cursor.access_specifier == cindex.AccessSpecifier.PUBLIC:
                        proxy.add_child(CursorProxy(child_cursor, child_cursor.location))
    cursor_list.sort()
    # for proxy in cursor_list:
    #     print("reslut {} {} {} {}".format(proxy.cursor.kind, 
    #                                         proxy.cursor.spelling, 
    #                                         proxy.cursor.location.line, 
    #                                         proxy.cursor.location.column))
    ref_iter = iter(cursor_list)
    proxy:CursorProxy
    while True:
        try:
            proxy = next(ref_iter)
        except StopIteration:
            return
        
        handler:Handler = proxy.handler
        if handler:
            handler.match(proxy, ref_iter)

def ananlysis_file(file_path, compile_args):
    index = cindex.Index.create()
    _parse = index.parse(file_path, compile_args, None, 1)
    context = Context(file_path)
    collection_metadata(context, _parse.cursor)
    if len(context._buffer.keys()) > 0:
        return context._buffer

class ClassHandler(Handler):
    key_words = [
        "commont",
    "is_singleton",
    ]
    def __init__(self, parent, key_word):
        super().__init__(parent, key_word)
    
    def match(self, proxy:CursorProxy, children:typing.Iterator)->bool:
        current_proxy:CursorProxy
        for current_proxy in children:
            if current_proxy.cursor.kind == cindex.CursorKind.CLASS_DECL or current_proxy.cursor.kind == cindex.CursorKind.STRUCT_DECL:
                real_meta_info = self.meta_info_filter(ClassHandler.key_words, proxy.cursor)
                clz_info = dict(meta_info = real_meta_info, funcs = [], constructors = [])
                self._parent.database[current_proxy.cursor.spelling] = clz_info
                for children in current_proxy.childrens:
                    arg_type_list = []
                    for arg in children.cursor.get_arguments():
                        arg_type_list.append(arg.type.spelling)
                    if len(arg_type_list) > 0:
                        clz_info['constructors'].append(arg_type_list)
                return
class FunctionHandler(Handler):
    key_words = [
        "commont",
        "singleton_method",
    ]
    def __init__(self, parent, key_word):
        super().__init__(parent, key_word)
    
    def match(self, proxy:CursorProxy, children:typing.Iterator)->bool:
        current_proxy:CursorProxy
        for current_proxy in children:
            if current_proxy.cursor.kind != cindex.CursorKind.CXX_METHOD:
                continue
            semantic_parent = current_proxy.cursor.semantic_parent
            if semantic_parent is None:
                continue

            clz = semantic_parent.spelling
            if self._parent.database.get(clz) is None:
                continue

            real_meta_info = self.meta_info_filter(FunctionHandler.key_words, proxy.cursor)
            
            singleton_method = real_meta_info.get('singleton_method', 0)
            name = current_proxy.cursor.spelling
            if singleton_method == 1:
                is_ponter = current_proxy.cursor.type.get_result().kind == cindex.TypeKind.POINTER and 1 or 0
                self._parent.database[clz]['singleton_method'] = dict(
                    name = name,
                    is_pointer = is_ponter
                )
            else:
                is_static = current_proxy.cursor.storage_class == cindex.StorageClass.STATIC
                self._parent.database[clz]['funcs'].append(dict(name = name,
                                                            meta_info = real_meta_info, is_static = is_static))
            return
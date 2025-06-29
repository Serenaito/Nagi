import os
from .definition import Debug, Path
from .handler import ananlysis_file
from multiprocessing import Pool
class Parser:
    def __init__(self, parallel = True):
        self._compile_args:list[str] = list()
        self._bind_file:list[Path] = list()
        self.parallel = parallel

    def recursive_listdir(self, directory_path, path):
        files = os.listdir(path)
        for file in files:
            file_path = os.path.join(path, file)
            if os.path.isfile(file_path):
                self._bind_file.append(Path(directory_path, file, file_path))
            elif os.path.isdir(file_path):
                self.recursive_listdir(file, file_path)

    def add_bind_directory(self, directory_path:str) -> bool:
        path = os.path.abspath(directory_path)
        self.recursive_listdir(directory_path, path)

    def add_bind_file(self, file_path:str) -> bool:
        os.path.basename(file_path)
        self._bind_file.append(file_path)

    def ananlysis(self):
        metadatas = list()
        if self.parallel:
            with Pool(6) as pool:
                results = []
                for path in self._bind_file:
                    results.append(dict(path = path, buffer = pool.apply_async(func=ananlysis_file, args=(path.abs_path, self._compile_args))))
                pool.close()
                pool.join()
                for result in results:
                    buffer =  result['buffer'].get()
                    if buffer:
                        metadatas.append(dict(path = result['path'], data = result['buffer'].get()))
        else:
            for path in self._bind_file:
                buffer = ananlysis_file(path.abs_path, self._compile_args)
                if buffer:
                    metadatas.append(dict(path = path, data = buffer))
        self.metadatas = metadatas

    def add_definition(self, definition:str):
        self._compile_args.append('-D{}'.format(definition))

    def add_include_directories(self, include_directories):
        self._compile_args.append('-I{}'.format(include_directories))
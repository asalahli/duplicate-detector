import collections
import hashlib
import pathlib
import sys


CHUNK_SIZE = 10 * 1024 * 1024


FileInfo = collections.namedtuple("FileInfo", ["original", "duplicates"])


def empty_callback(path):
    pass


class Application(object):
    def __init__(self, root):
        self.root = pathlib.Path(root)
        self.file_map = {}
        self.duplicate_files = []
        self.folder_count = 0
        self.file_count = 0

        self.processed_file_count = 0
        self.duplicate_file_count = 0


    def run(self):
        if not self.root.exists():
            sys.exit("Path doesn't exist")

        if not self.root.is_dir():
            sys.exit("%s is not a directory" % self.root)

        self.traverse(
            path=self.root,
            folder_callback=self.increase_folder_counter,
            file_callback=self.increase_file_counter
        )

        print("%s folders and %s files found" % (self.folder_count, self.file_count))
        print()

        self.traverse(
            path=self.root,
            file_callback=self.analyze_file
        )

        print()
        print()
        
        for file_hash in self.file_map:
            file_info = self.file_map[file_hash]
            if len(file_info.duplicates) > 0:
                print(file_info.original)
                for duplicate_file_path in file_info.duplicates:
                    print("    ", duplicate_file_path)
                print()


    def increase_folder_counter(self, file_path):
        self.folder_count += 1


    def increase_file_counter(self, file_path):
        self.file_count += 1


    def analyze_file(self, file_path):
        file_hash = self.calculate_file_hash(file_path)

        if file_hash in self.file_map:
            self.file_map[file_hash].duplicates.append(file_path)
            self.duplicate_file_count += 1
        else:
            self.file_map[file_hash] = FileInfo(original=file_path, duplicates=[])

        self.processed_file_count += 1

        print("\r                                                                                ", end="")
        print(
            "\r%s of %s files analyzed, %s duplicates found." % 
            (self.processed_file_count, self.file_count, self.duplicate_file_count),
            end=""
        )


    def calculate_file_hash(self, file_path):
        m = hashlib.sha256()

        with file_path.open(mode='rb') as f:
            while True:
                data = f.read(CHUNK_SIZE)
                if len(data) == 0: break
                m.update(data)

        return m.hexdigest()


    def traverse(self, path, folder_callback=empty_callback, file_callback=empty_callback):
        for child in path.iterdir():
            if child.is_dir():
                folder_callback(child)
                self.traverse(child, folder_callback, file_callback)
            else:
                file_callback(child)



if __name__ == "__main__":
    app = Application(sys.argv[1])
    app.run()

import re
from pathlib import Path
from shutil import copy


def replace_all(text: str, replacements: dict):
    for key, val in replacements.items():
        text = text.replace(f"<{key}>", val)
    return text


class PatternMatcher:
    def __init__(self, pattern: str) -> None:
        self.pattern = pattern
        self.regex = re.compile('<(.*?)>')
        self.parts = self.regex.findall(self.pattern)
        self.variables = {}
        self._create_variables()

    def _create_variables(self):
        for part in self.parts:
            var_name, idxs = part.split('@')
            start_idx, end_idx = idxs.split(':')

            if start_idx:
                _start = int(start_idx) - 1
            else:
                _start = 0

            if end_idx:
                _end = int(end_idx)
            else:
                _end = None

            self.variables[var_name] = {'start': _start,
                                        'end': _end}

    def match(self, text):
        values = {}
        for var in self.variables:
            s = self.variables[var]['start']
            e = self.variables[var]['end']
            if e is None:
                values[var] = text[s:]
            else:
                values[var] = text[s:e]

        return values


class PatternCopy:
    def __init__(self,
                 src: str,
                 dst: str,
                 pattern: PatternMatcher,
                 folder_pattern: str) -> None:
        self.src = Path(src)
        self.dst = Path(dst)
        self.pattern = pattern
        self.folder_pattern = folder_pattern

    def copy_files(self, match=str):
        for p in self.src.glob(match):
            parts = self.pattern.match(p.stem)
            sub_dst = replace_all(self.folder_pattern, parts)
            _dst = self.dst.joinpath(sub_dst)
            _dst.mkdir(parents=True, exist_ok=True)
            copy(p, _dst)


if __name__ == "__main__":
    src = "D:/Google Drive/Azna/Docs/Κτηματολόγιο Κιλκίς/Γιαγιά"
    dst = "D:/.temp/copy_tests"

    name_pattern = "<ota@3:7><tomeas@8:9><enotita@10:11><gt@12:14>"
    folder_pattern = "<ota>/<tomeas>"

    pm = PatternMatcher(pattern=name_pattern)
    pc = PatternCopy(src=src, dst=dst, pattern=pm,
                     folder_pattern=folder_pattern)

    pc.copy_files('K*.pdf')

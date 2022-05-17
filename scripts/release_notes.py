import os
from typing import List

TAG = os.environ["TAG"][1:]


def get_change_log_notes() -> str:
    in_current_section = False
    current_section_notes: List[str] = []
    with open("HISTORY.rst") as changelog:
        for line in changelog:
            if line.startswith(TAG):
                in_current_section = True
                continue
            if in_current_section:
                if line.startswith("* "):
                    current_section_notes.append(line)
                elif line.startswith("++") or line.startswith("\n"):
                    continue
                else:
                    break
    assert current_section_notes
    return "".join(current_section_notes).strip() + "\n"


def main():
    print(get_change_log_notes())


if __name__ == "__main__":
    main()

"""Create Markdown wrappers around the project's example .py files."""
from pathlib import Path

top = "# <put filename here>\n```python\n"

bottom = """```
"""

raw_top = "# <put filename here>\n~~~\n"

raw_bottom = """~~~
"""

text_bottom = """~~~
"""


def nag():
    print("If a new file...")
    print("Consider adding a test case to test_wrapped_python_files.py.")
    print("And add to examples.rst")
    print()


def prompt_to_write_file(outfile_name, text):
    if input("ok to write " + outfile_name + " [Y/n]? >> ") == "Y":
        print("writing", outfile_name)
        _ = Path(outfile_name).write_text(text, encoding="utf-8")


def wrap_one_file(name, outname=None):
    text = top.replace("<put filename here>", name)
    text += Path(name).read_text(encoding="utf-8")
    text += bottom
    if outname is not None:
        outfile_name = outname
    else:
        outfile_name = name.replace(".py", "_py.md")
    prompt_to_write_file(outfile_name, text)


def main():
    nag()
    # also add a test case to tests/test_wrapped_python_files.py
    wrap_one_file("src/phmutest/fixture.py", outname="docs/fixture_py.md")
    wrap_one_file("docs/fix/code/globdemo.py")
    wrap_one_file("docs/fix/code/chdir.py")
    wrap_one_file("docs/fix/repl/drink.py")
    wrap_one_file(
        "tests/py/generated_project.py", outname="docs/generated_project_py.md"
    )
    wrap_one_file(
        "tests/py/generated_sharedemo.py", outname="docs/generated_share_demo_py.md"
    )


if __name__ == "__main__":
    main()

"""Copy .md files to prepare to run mkdocs. Recopy if modified.

When called with the command line arg --start-server
- mkdocs serve is started
- updates to the watched project files are copied to the destination
- enter Ctrl-C to discontinue watching and shut down the mkdocs server
Suggest adding the mkdocs.yml docs_dir to .gitignore.
"""
import subprocess
import sys
from multiprocessing import Process
from pathlib import Path
from time import sleep


class Watched:
    """A source file and its copy (dest) to be kept up to date."""

    def __init__(self, source: Path, dest: Path):
        self.source = source
        self.dest = dest

    def ismodified(self) -> bool:
        """True if dest file is no longer up to date."""
        return self.source.stat().st_mtime > self.dest.stat().st_mtime

    def update(self):
        """Copy source file to dest file, create needed dirs."""
        text = self.source.read_text(encoding="utf-8")
        parentdir = self.dest.parent
        parentdir.mkdir(mode=0o700, parents=True, exist_ok=True)
        _ = self.dest.write_text(text, encoding="utf-8")

    def __repr__(self):
        return f"{self.source}, {self.dest}"


class Updater:
    """Keep files in the dest folder up to date."""

    def __init__(self, dest: Path):
        self.dest = dest
        self.watching = []

    def addglob(self, glob: str):
        """Add existing files by Path glob expression to keep up to date in dest."""
        for p in Path().glob(glob):
            self.watching.append(Watched(p, self.dest / p))

    def show_obsolete(self, remove=False):
        """Files in dest that are now un-watched. They are deleted when remove==True."""
        old_destfiles_and_dirs = self.dest.glob("**/*")
        # Exclude directories. Won't detect obsolete empty directories.
        old_destfiles = [f for f in old_destfiles_and_dirs if not f.is_dir()]
        new_destfiles = [w.dest for w in self.watching]
        for obsolete in set(old_destfiles) - set(new_destfiles):
            if remove:
                assert isinstance(obsolete, Path)
                print(f"removing obsolete file {obsolete}")
                obsolete.unlink()
            else:
                print(f"detected obsolete file {obsolete}")

    def update(self):
        """Detect modifications to the added files. Create/update the dest files."""
        for w in self.watching:
            if not w.dest.exists():
                print(f"creating {w.dest}")
                w.update()
            else:
                if w.ismodified():
                    print(f"updating {w.dest}")
                    w.update()

    def __repr__(self):
        lines = [str(w) for w in self.watching]
        return "\n".join(lines)


def start_mkdocs_serve():
    """Launch subprocess running mkdocs server."""
    print("starting mkdocs serve...")
    _ = subprocess.run(["mkdocs", "serve"])


def mainloop(updater: Updater):
    """Copy files. Continuously run the Updater until Ctrl-C."""
    print(f"{sys.argv[0]}")
    print(f"destination= {updater.dest}")
    print(f"number of files= {len(updater.watching)}")
    updater.update()
    updater.show_obsolete(remove="--clean" in sys.argv)
    if "--start-server" in sys.argv:
        p = Process(target=start_mkdocs_serve)
        p.start()
        print("Ctrl-C to quit watching and mkdocs serve")
        try:
            while True:
                sleep(1)
                updater.update()
        except KeyboardInterrupt:
            pass
        print("\nno longer watching\n")
        p.terminate()
        p.join()
        p.close()


def main():
    """Create and run the documentation file updater."""
    ud = Updater(Path("_mkdocsin"))
    ud.addglob("CONTRIBUTING.md")
    ud.addglob("README.md")
    ud.addglob("tests/md/project.md")
    ud.addglob("docs/**/*.md")
    mainloop(ud)


if __name__ == "__main__":
    main()

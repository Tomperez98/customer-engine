from pathlib import Path
from urllib.parse import urlencode
import webbrowser
import toml


def main() -> None:
    cwd = Path()
    pyproject_data = toml.loads(cwd.joinpath("pyproject.toml").read_text())["project"]
    version = pyproject_data["version"]
    repo_url = pyproject_data["urls"]["Source"]
    params = urlencode(
        query={
            "title": f"v{version}",
            "tag": f"v{version}",
            "prereleased": 1,
        },
    )
    webbrowser.open_new_tab(url=f"{repo_url}/releases/new?{params}")


if __name__ == "__main__":
    main()

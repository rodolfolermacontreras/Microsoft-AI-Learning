"""
Environment exploration script.

Run this inside the container to verify all expected packages are installed
and show their versions. Also shows container environment details.
"""

import sys
import platform
import os
import importlib
from typing import Optional


PACKAGES_TO_CHECK = [
    "pandas",
    "numpy",
    "sklearn",
    "xgboost",
    "lightgbm",
    "scipy",
    "statsmodels",
    "matplotlib",
    "seaborn",
    "plotly",
    "tqdm",
    "joblib",
]


def get_version(package_name: str) -> Optional[str]:
    """Get the version string for an installed package."""
    try:
        mod = importlib.import_module(package_name)
        return getattr(mod, "__version__", "installed (no __version__)")
    except ImportError:
        return None


def print_section(title: str) -> None:
    """Print a section header."""
    print(f"\n{'=' * 55}")
    print(f"  {title}")
    print("=" * 55)


def main() -> None:
    """Check and display environment details."""

    print_section("Python Environment")
    print(f"Python version : {sys.version}")
    print(f"Executable     : {sys.executable}")
    print(f"Platform       : {platform.system()} {platform.release()}")
    print(f"Architecture   : {platform.machine()}")
    print(f"Working dir    : {os.getcwd()}")
    print(f"User           : {os.getenv('USER', os.getenv('USERNAME', 'unknown'))}")

    print_section("Installed DS Packages")
    all_ok = True
    for pkg in PACKAGES_TO_CHECK:
        version = get_version(pkg)
        if version is not None:
            status = "OK"
            print(f"  {status:4s}  {pkg:<20s}  {version}")
        else:
            status = "MISSING"
            all_ok = False
            print(f"  {status:4s}  {pkg:<20s}  NOT INSTALLED")

    print_section("Environment Variables")
    relevant_vars = ["PYTHONUNBUFFERED", "PYTHONDONTWRITEBYTECODE", "PATH"]
    for var in relevant_vars:
        value = os.environ.get(var, "not set")
        if var == "PATH":
            # PATH can be very long, truncate it
            value = value[:80] + "..." if len(value) > 80 else value
        print(f"  {var}: {value}")

    print_section("Summary")
    if all_ok:
        print("  All expected packages are installed.")
    else:
        print("  Some packages are missing. Check requirements.txt and rebuild.")
    print()


if __name__ == "__main__":
    main()

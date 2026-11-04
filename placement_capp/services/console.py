"""Console helpers: banners, prompts, pickers."""
from data.dummy_data import COMPANIES, STUDENTS

W = 78  # banner width


def bar(ch="="):
    print(ch * W)


def banner(title, subtitle=None):
    bar()
    print(title.center(W).rstrip())
    if subtitle:
        print(subtitle.center(W).rstrip())
    bar()


def section(title):
    print()
    print(f"--- {title} ".ljust(W, "-"))


def pause():
    try:
        input("\nPress Enter to return to the menu...")
    except EOFError:
        pass


def ask_int(prompt, lo, hi, default):
    try:
        raw = input(f"{prompt} [{lo}-{hi}, Enter = {default}]: ").strip()
    except EOFError:
        return default
    if raw == "":
        return default
    try:
        val = int(raw)
    except ValueError:
        print(f"  Not a number, using {default}.")
        return default
    if not lo <= val <= hi:
        print(f"  Out of range, using {default}.")
        return default
    return val


def pick_student(default=0):
    return STUDENTS[ask_int("Student id", 0, len(STUDENTS) - 1, default)]


def pick_company(default=1):
    print("  Companies: " + ", ".join(f"{i + 1}={c['name']}" for i, c in enumerate(COMPANIES)))
    return COMPANIES[ask_int("Company number", 1, len(COMPANIES), default) - 1]

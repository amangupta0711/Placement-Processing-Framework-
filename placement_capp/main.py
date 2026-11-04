"""
PLACEMENT PROCESSING FRAMEWORK - CAPP TERMINAL PROTOTYPE
Course: Computer Architecture and Parallel Processing (CCSE0304) | Group 2 | SDG 4

Run:  python main.py
"""
from services.console import banner
from services.demos import (demo_booth, demo_cache, demo_control_unit, demo_instruction_cycle,
                            demo_parallel, demo_pipeline, view_data)
from services.integration import demo_integrated_batch, demo_integrated_single


MENU = [
    ("View student records and company criteria", view_data),
    ("ALU: Booth signed multiplication (eligibility score)", demo_booth),
    ("Control unit: hardwired vs micro-programmed", demo_control_unit),
    ("Instruction cycle: mini-CPU fetch/decode/execute", demo_instruction_cycle),
    ("Pipeline: 5-stage timing + automatic hazard detection", demo_pipeline),
    ("Cache memory: direct-mapped vs 4-way (hit ratio, EAT)", demo_cache),
    ("Parallel processing: SISD / SIMD / MIMD (Flynn)", demo_parallel),
    ("Integrated flow: one application, all CAPP parts", demo_integrated_single),
    ("Integrated batch: 200 students x 4 companies", demo_integrated_batch),
]


def main():
    while True:
        print()
        banner("PLACEMENT PROCESSING FRAMEWORK", "CAPP TERMINAL MENU")
        for i, (label, _) in enumerate(MENU, 1):
            print(f"{i}. {label}")
        print(f"{len(MENU) + 1}. Exit")
        try:
            choice = input(f"\nChoose an option (1-{len(MENU) + 1}): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            return
        if choice == str(len(MENU) + 1):
            print("Goodbye.")
            return
        if choice.isdigit() and 1 <= int(choice) <= len(MENU):
            print()
            MENU[int(choice) - 1][1]()
        else:
            print("Invalid choice, please enter a number from the menu.")


if __name__ == "__main__":
    main()

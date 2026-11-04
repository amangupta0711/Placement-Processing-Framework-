# Placement Processing Framework - CAPP Terminal Prototype

Course: Computer Architecture and Parallel Processing (CCSE0304) | Group 2 | SDG 4 - Quality Education

A terminal-based, pure-Python (3.8+) prototype. Every menu option shows a different CAPP
concept on the same placement workflow. All data is dummy data (200 students, 4 companies).

## Run in VS Code
1. File > Open Folder... > select `placement_capp`
2. Open the terminal (Ctrl + `) and run:
   ```
   python main.py
   ```
   (use `python3 main.py` on Mac/Linux). No `pip install` needed.
3. Run the tests: `python -m unittest discover -s tests -v`

(`__pycache__/` is created automatically the first time you run the program.)

## Folder structure
```
placement_capp/
|-- main.py                  menu / entry point
|-- models.py                constants (stages, cache size, tc, tm) + plain-Python eligibility rule
|-- README.md
|-- capp/                    the CAPP concepts (one file each)
|   |-- alu.py               Booth signed multiplication
|   |-- control_unit.py      hardwired signals + micro-programmed control memory
|   |-- cpu.py               mini CPU: assembler + instruction cycle
|   |-- pipeline.py          5-stage pipeline + automatic hazard detection
|   |-- cache.py             direct-mapped / 4-way LRU cache, EAT
|   `-- parallel.py          SIMD and MIMD
|-- data/
|   `-- dummy_data.py        200 dummy students + company criteria
|-- services/
|   |-- console.py           banners, prompts
|   |-- demos.py             menu demos for options 1-7
|   `-- integration.py       options 8-9: all parts joined end to end
`-- tests/
    `-- test_capp.py         unit tests
```

## Menu -> concept
| # | Option | CAPP concept |
|---|--------|--------------|
| 1 | View records and criteria | dummy data |
| 2 | Booth multiplication | ALU, signed arithmetic |
| 3 | Hardwired vs micro-programmed | control unit |
| 4 | Mini-CPU trace | instruction cycle (fetch/decode/execute) |
| 5 | Pipeline timing | 5-stage pipeline, hazards, stalls, k+(n-1) |
| 6 | Cache comparison | cache memory, hit ratio, EAT |
| 7 | SISD / SIMD / MIMD | parallel processing (Flynn) |
| 8 | One application end to end | integration |
| 9 | All students x all companies | integration + shortlist + performance summary |

Eligibility score = 2 x CGPA + 5 x skills + (-10) x backlogs (CGPA kept as integer, 8.2 -> 82).

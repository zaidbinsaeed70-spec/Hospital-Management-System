# CEP-2 Hospital Patient Management & Scheduling System

## Overview
Menu-driven CLI that manages patient registrations, visit histories, emergency triage, and appointment scheduling while explicitly implementing the mandated CEP-2 data structures (hash table, linked list, priority queue, BST). All operations persist to `records.json`, so workflows survive restarts without relying on Python `dict`, `list`, or `heapq` as substitutes.

## Architecture
```
+-----------+
|  main.py  |  CLI, validation, persistence orchestration
+-----+-----+
      |
      +--> Hash Table (registry) ----------> Patient objects
      +--> Linked List (visit history) ----> Patient.visit_history
      +--> Priority Queue (triage queue) --> Emergency payloads
      +--> BST (appointment schedule) -----> Appointment objects
```
- `main.py` wires menu options to the data structures and handles persistence.
- `src/hash_table.py`, `src/linked_list.py`, `src/priority_queue.py`, and `src/tree.py` expose custom implementations that satisfy CEP-2's academic constraints (explicit nodes, no built-in containers as substitutes).
- `src/storage.py` serializes/deserializes state without leaking built-in containers into runtime logic.

## Module Responsibilities
| Module | Purpose |
| --- | --- |
| `src/hash_table.py` | Chained hash table (ctypes bucket array) keyed by patient ID for O(1) average lookup. |
| `src/linked_list.py` | Singly linked list storing each patient's visit history and appointment log with traversal helpers. |
| `src/priority_queue.py` | Severity-based triage queue implemented as a sorted linked list to guarantee highest-priority dequeue. |
| `src/tree.py` | Pointer-based BST storing appointments in chronological order (timestamp + sequence key). |
| `src/patient.py` | Patient entity plus serialization helpers tied to the linked-list history. |
| `src/appointment.py` | Appointment entity limited to patient ID, datetime, and 5-character scheduling code. |
| `src/storage.py` | JSON persistence for registry, triage queue, appointment tree, and sequence counter. |
| `main.py` | CLI, validation, persistence triggers, human-friendly appointment codes, and menu workflow. |

## Data Structure Mapping
| Requirement | Data Structure | Rationale |
| --- | --- | --- |
| Patient registration & lookup | Hash Table | Achieves expected O(1) average lookups; custom chaining avoids built-ins. |
| Emergency triage | Priority Queue | Sorted linked list ensures severity ordering without Python heaps. |
| Appointment schedule | BST | Maintains chronological ordering and supports in-order traversal for reports. |
| Historical records | Linked List | Explicit nodes satisfy the "no list storage" constraint while enabling linear traversal. |

## Core Operations
1. **Register / Lookup Patients** - store demographic info, access via hash table (`choice 1/2`).
2. **Visit History Maintenance** - append textual entries per patient using linked lists (`choice 3/4`).
3. **Emergency Intake** - severity-scored enqueue/dequeue via priority queue (`choice 5/6`), with inline registration when needed.
4. **Appointment Scheduling** - insert into BST, auto-generate 5-character code, visit-history logging (`choice 7`).
5. **Cancellation & Rescheduling** - keyed by appointment code; operations update BST and visit history (`choice 8/9`).
6. **Chronological Reporting** - in-order traversal dumps upcoming appointments with codes (`choice 10`).
7. **Persistence** - `records.json` is updated after every successful mutation and loaded on startup.

## CSV Mirror
- `records.csv` mirrors the JSON state so you can edit patients in a spreadsheet and let the CLI pick them up automatically.
- The CSV exposes these columns: `patient_id`, `name`, `age`, `gender` (M/F/O), `phone`, `medical_notes`. Only rows with valid values are imported.
- On startup the CLI loads `records.json`, then reads `records.csv`, inserting any patient IDs that are not already registered. When import happens the CLI prints `INFO: Imported X patient(s) from records.csv.` and immediately persists the merged state back to both JSON and CSV.
- Manual edits should avoid duplicate `patient_id` rows (existing IDs are skipped) and keep `age` as an integer between 0-130; invalid rows are ignored silently.

## Complexity Summary
| Operation | Complexity |
| --- | --- |
| Insert/lookup patient | Average O(1) (hash table chaining). |
| Enqueue/dequeue emergency | Enqueue O(n) (linked insertion), dequeue O(1). |
| Insert/find/delete appointment | Average O(log n) for balanced data, worst O(n) (BST). |
| Visit history append/traverse | Append O(1), traversal O(k) for k records. |
| Persistence read/write | O(n) over serialized entities (patients + triage + appointments). |

## Running the CLI
```powershell
python -m venv venv
venv\Scripts\activate
python main.py
```
Follow the numbered prompts. Data is saved to `records.json` automatically; delete the file to reset the system.

## Sample Session
```
=== CEP-2 Hospital Patient Management & Scheduling ===
1) Register Patient ... 0) Exit
Select: 1
Patient ID (unique): P001
Name: John Doe
Age: 30
Gender (M/F/O): M
Phone: 555-0000
Medical notes (optional):
OK: Registered: Patient[P001] John Doe, 30, M, 555-0000

Select: 7
Patient ID: P001
Appointment Date (YYYY-MM-DD HH:MM): 2026-02-01 10:00
OK: scheduled: Appt[00002] 2026-02-01 10:00 pid=P001
Appointment code: 00002

Select: 10
--- Appointments (Chronological) ---
CODE=00002  Appt[00002] 2026-02-01 10:00 pid=P001
```

## Testing & Validation
- Interactive testing via CLI ensures each menu action exercises the appropriate data structure.
- Because the CLI runs under a `try/except` loop, invalid inputs surface friendly errors without crashing.
- For automated validation, script the CLI using piped input sequences (examples in issue history) to assert persistence and workflow correctness.

## Future Enhancements
- Surface persistence errors (currently ignored for UX simplicity).
- Optional BST rebalancing or AVL upgrade for worst-case guarantees.
- Automated regression harness to replay sample sessions.

The current codebase satisfies the CEP-2 academic constraints: every required data structure is custom-built, permanently wired into the CLI workflow, and justified by the runtime behavior outlined above.

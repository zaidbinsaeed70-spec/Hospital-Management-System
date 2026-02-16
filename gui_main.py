import tkinter as tk
from tkinter import ttk, messagebox
from SRC.appointment import Appointment
from SRC.hash_table import HashTable
from SRC.priority_queue import PriorityQueue
from SRC.storage import load_state, save_state
from SRC.tree import BST

APPT_CODE_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


class HospitalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CEP-2 Hospital Management System")
        self.root.geometry("1000x600")  # Made slightly wider

        # Load Data
        self.registry, self.triage, self.schedule, self.appt_seq, self.imported_count = load_state()

        if self.registry is None: self.registry = HashTable()
        if self.triage is None: self.triage = PriorityQueue()
        if self.schedule is None: self.schedule = BST()
        if not isinstance(self.appt_seq, int) or self.appt_seq < 0: self.appt_seq = 0

        self.code_index = self.rebuild_code_index()
        self.create_tabs()

    def rebuild_code_index(self):
        idx = HashTable()
        for key, appt in self.schedule.items():
            code = getattr(appt, "code", None)
            if not code:
                code = self.generate_appt_code()
                self.appt_seq += 1
                appt.code = code
            idx.put(code, key)
        return idx

    def generate_appt_code(self):
        counter = self.appt_seq
        if counter < 0: counter = 0
        base = len(APPT_CODE_CHARS)
        if counter == 0:
            code = "0"
        else:
            code = ""
            n = counter
            while n > 0:
                n, rem = divmod(n, base)
                code = APPT_CODE_CHARS[rem] + code
        return code.rjust(5, "0")[-5:]

    def save_data(self):
        save_state(self.registry, self.triage, self.schedule, self.appt_seq)

    def on_closing(self):
        self.save_data()
        self.root.destroy()

    def create_tabs(self):
        tab_control = ttk.Notebook(self.root)
        self.tab_patients = ttk.Frame(tab_control)
        self.tab_appointments = ttk.Frame(tab_control)
        self.tab_emergency = ttk.Frame(tab_control)

        tab_control.add(self.tab_patients, text='Patients')
        tab_control.add(self.tab_appointments, text='Appointments')
        tab_control.add(self.tab_emergency, text='Emergency / Triage')
        tab_control.pack(expand=1, fill="both")

        self.build_patient_tab()
        self.build_appointment_tab()
        self.build_emergency_tab()

    # --- TAB 1: PATIENTS (UPDATED WITH DELETE) ---
    def build_patient_tab(self):
        frame = ttk.Frame(self.tab_patients, padding=10)
        frame.pack(fill="both", expand=True)

        # Controls
        ctrl_frame = ttk.Frame(frame)
        ctrl_frame.pack(fill="x", pady=5)

        ttk.Label(ctrl_frame, text="Search By:").pack(side="left")
        self.search_var = tk.StringVar(value="Name")
        search_combo = ttk.Combobox(ctrl_frame, textvariable=self.search_var, values=["Name", "ID", "Blood Group"],
                                    width=10)
        search_combo.pack(side="left", padx=5)

        self.search_entry = ttk.Entry(ctrl_frame, width=20)
        self.search_entry.pack(side="left", padx=5)
        ttk.Button(ctrl_frame, text="Search", command=self.search_patients).pack(side="left")
        ttk.Button(ctrl_frame, text="Refresh", command=self.refresh_patient_list).pack(side="left", padx=5)

        # --- NEW BUTTONS ---
        ttk.Button(ctrl_frame, text="+ Register", command=self.popup_register).pack(side="right", padx=5)
        ttk.Button(ctrl_frame, text="X Delete Selected", command=self.delete_patient).pack(side="right", padx=5)

        # Table
        cols = ("ID", "Name", "Age", "Gender", "Phone", "Notes")
        self.p_tree = ttk.Treeview(frame, columns=cols, show='headings')
        for col in cols:
            self.p_tree.heading(col, text=col)
            self.p_tree.column(col, width=100)

        self.p_tree.pack(fill="both", expand=True, pady=10)
        self.refresh_patient_list()

    def delete_patient(self):
        # 1. Check if a row is selected
        selected_item = self.p_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a patient to delete.")
            return

        # 2. Get the Patient ID from the selected row
        item_data = self.p_tree.item(selected_item[0])
        patient_id = str(item_data['values'][0])  # Column 0 is ID

        # 3. Confirm with User
        confirm = messagebox.askyesno("Confirm Delete",
                                      f"Are you sure you want to delete Patient ID: {patient_id}?\n\nThis will remove them from the Excel file and system.")
        if not confirm:
            return

        # 4. Remove from Hash Table
        success = self.registry.remove(patient_id)

        if success:
            # 5. Save changes (this updates JSON and rewrites Excel without this patient)
            self.save_data()
            self.refresh_patient_list()
            messagebox.showinfo("Deleted", f"Patient {patient_id} removed successfully.")
        else:
            messagebox.showerror("Error", "Could not remove patient from registry.")

    def refresh_patient_list(self):
        for i in self.p_tree.get_children():
            self.p_tree.delete(i)
        patients = []
        for _, p in self.registry.items():
            patients.append(p)
        patients.sort(key=lambda x: x.name)
        for p in patients:
            self.p_tree.insert("", "end", values=(p.patient_id, p.name, p.age, p.gender, p.phone, p.medical_notes))

    def search_patients(self):
        query = self.search_entry.get().lower()
        mode = self.search_var.get()
        for i in self.p_tree.get_children():
            self.p_tree.delete(i)
        for _, p in self.registry.items():
            match = False
            if mode == "Name" and query in p.name.lower():
                match = True
            elif mode == "ID" and query in p.patient_id.lower():
                match = True
            elif mode == "Blood Group" and p.medical_notes and query.upper() in p.medical_notes.upper():
                match = True
            if match:
                self.p_tree.insert("", "end", values=(p.patient_id, p.name, p.age, p.gender, p.phone, p.medical_notes))

    def popup_register(self):
        top = tk.Toplevel(self.root)
        top.title("Register Patient")
        top.geometry("300x400")
        fields = ["ID", "Name", "Age", "Gender (M/F)", "Phone", "Notes"]
        entries = {}
        for field in fields:
            row = ttk.Frame(top)
            row.pack(fill="x", padx=5, pady=5)
            ttk.Label(row, text=field, width=15).pack(side="left")
            e = ttk.Entry(row)
            e.pack(side="right", expand=True, fill="x")
            entries[field] = e

        def submit():
            data = {f: entries[f].get().strip() for f in fields}
            if not data["ID"] or not data["Name"]:
                messagebox.showerror("Error", "ID and Name are required.")
                return
            if self.registry.contains(data["ID"]):
                messagebox.showerror("Error", "Patient ID already exists.")
                return
            try:
                age = int(data["Age"])
                p = Patient(data["ID"], data["Name"], age, data["Gender (M/F)"].upper(), data["Phone"], data["Notes"])
                self.registry.put(p.patient_id, p)
                self.save_data()
                self.refresh_patient_list()
                top.destroy()
                messagebox.showinfo("Success", "Patient Registered!")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(top, text="Save", command=submit).pack(pady=10)

    # --- TAB 2: APPOINTMENTS ---
    def build_appointment_tab(self):
        frame = ttk.Frame(self.tab_appointments, padding=10)
        frame.pack(fill="both", expand=True)
        ctrl = ttk.Frame(frame)
        ctrl.pack(fill="x", pady=5)
        ttk.Label(ctrl, text="Patient ID:").pack(side="left")
        self.appt_pid = ttk.Entry(ctrl, width=15)
        self.appt_pid.pack(side="left", padx=5)
        ttk.Label(ctrl, text="Date (YYYY-MM-DD HH:MM):").pack(side="left")
        self.appt_date = ttk.Entry(ctrl, width=20)
        self.appt_date.pack(side="left", padx=5)
        ttk.Button(ctrl, text="Schedule", command=self.schedule_appt).pack(side="left", padx=10)
        ttk.Button(ctrl, text="Refresh", command=self.refresh_appt_list).pack(side="right")
        cols = ("Code", "Time", "Patient ID", "Patient Name")
        self.appt_tree = ttk.Treeview(frame, columns=cols, show='headings')
        for c in cols: self.appt_tree.heading(c, text=c)
        self.appt_tree.pack(fill="both", expand=True, pady=10)
        ttk.Button(frame, text="Cancel Selected", command=self.cancel_appt).pack(side="bottom", pady=5)
        self.refresh_appt_list()

    def refresh_appt_list(self):
        for i in self.appt_tree.get_children(): self.appt_tree.delete(i)

        def traverse(node):
            if not node: return
            traverse(node.left)
            appt = node.value
            p = self.registry.get(appt.patient_id)
            p_name = p.name if p else "Unknown"
            self.appt_tree.insert("", "end", values=(appt.code, appt.datetime_str(), appt.patient_id, p_name))
            traverse(node.right)

        traverse(self.schedule.root)

    def schedule_appt(self):
        pid = self.appt_pid.get().strip()
        dt = self.appt_date.get().strip()
        if not pid or not dt:
            messagebox.showerror("Error", "Patient ID and Date required.")
            return
        p = self.registry.get(pid)
        if not p:
            resp = messagebox.askyesno("Not Found", "Patient not found. Register them first?")
            if resp: self.popup_register()
            return
        try:
            appt = Appointment(pid, dt)
            appt.code = self.generate_appt_code()
            key = appt.key_minutes() * 1000 + self.appt_seq
            self.appt_seq += 1
            self.schedule.insert(key, appt)
            self.code_index.put(appt.code, key)
            p.add_visit(f"APPT SCHEDULED [{appt.code}] -> {appt}")
            self.save_data()
            self.refresh_appt_list()
            messagebox.showinfo("Success", f"Scheduled! Code: {appt.code}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def cancel_appt(self):
        sel = self.appt_tree.selection()
        if not sel: return
        item = self.appt_tree.item(sel[0])
        code = item['values'][0]
        key = self.code_index.get(str(code))
        if key:
            self.schedule.delete(key)
            self.code_index.remove(str(code))
            self.save_data()
            self.refresh_appt_list()
            messagebox.showinfo("Cancelled", f"Appointment {code} cancelled.")

    # --- TAB 3: EMERGENCY ---
    def build_emergency_tab(self):
        frame = ttk.Frame(self.tab_emergency, padding=10)
        frame.pack(fill="both", expand=True)
        form = ttk.LabelFrame(frame, text="Admit Emergency Patient")
        form.pack(fill="x", pady=10)
        ttk.Label(form, text="Patient ID:").pack(side="left", padx=5)
        self.em_pid = ttk.Entry(form, width=10)
        self.em_pid.pack(side="left")
        ttk.Label(form, text="Severity (1-10):").pack(side="left", padx=5)
        self.em_sev = ttk.Entry(form, width=5)
        self.em_sev.pack(side="left")
        ttk.Label(form, text="Complaint:").pack(side="left", padx=5)
        self.em_issue = ttk.Entry(form, width=20)
        self.em_issue.pack(side="left")
        ttk.Button(form, text="Admit", command=self.admit_emergency).pack(side="left", padx=10)
        ttk.Label(frame, text="Current Triage Queue:").pack(anchor="w")
        cols = ("Priority", "Details")
        self.em_tree = ttk.Treeview(frame, columns=cols, show='headings')
        self.em_tree.heading("Priority", text="Priority")
        self.em_tree.heading("Details", text="Patient Details")
        self.em_tree.pack(fill="both", expand=True)
        ttk.Button(frame, text="Treat Next", command=self.treat_next).pack(pady=10)
        self.refresh_triage()

    def admit_emergency(self):
        pid = self.em_pid.get().strip()
        sev_str = self.em_sev.get().strip()
        issue = self.em_issue.get().strip()
        p = self.registry.get(pid)
        if not p:
            messagebox.showerror("Error", "Patient ID not found. Register first.")
            return
        try:
            sev = int(sev_str)
            payload = f"EMERGENCY pid={pid} name={p.name} sev={sev} issue={issue}"
            self.triage.enqueue(sev, payload)
            self.save_data()
            self.refresh_triage()
            self.em_pid.delete(0, 'end')
            self.em_issue.delete(0, 'end')
        except ValueError:
            messagebox.showerror("Error", "Severity must be a number.")

    def treat_next(self):
        item = self.triage.dequeue()
        if item:
            self.save_data()
            self.refresh_triage()
            messagebox.showinfo("Treating", f"Now Treating:\n{item}")
        else:
            messagebox.showinfo("Empty", "No patients in triage.")

    def refresh_triage(self):
        for i in self.em_tree.get_children(): self.em_tree.delete(i)
        items = self.triage.to_list()
        for item in items:
            self.em_tree.insert("", "end", values=(item['priority'], item['payload']))


if __name__ == "__main__":
    root = tk.Tk()
    app = HospitalApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
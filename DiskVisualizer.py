import psutil
import tkinter as tk
from colorsys import hsv_to_rgb
import platform

class DiskUsageApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Disk Usage Visualization")
        self.master.configure(background='black')

        self.frame = tk.Frame(master, background='black')
        self.frame.pack()

        self.disks = self.get_usable_disks()
        self.disk_labels = []
        self.disk_canvases = []
        self.usage_bars = []

        self.init_disk_visualization()
        self.update_loop()

    def get_usable_disks(self):
        # Filter for usable disks only
        disks = []
        for disk in psutil.disk_partitions():
            if disk.fstype and ('cdrom' not in disk.opts) and (platform.system() != 'Windows' or 'removable' not in disk.opts):
                try:
                    # Check if we can access disk usage data
                    psutil.disk_usage(disk.mountpoint)
                    disks.append(disk)
                except (PermissionError, FileNotFoundError):
                    continue  # Skip inaccessible disks
        return disks

    def calculate_color(self, percentage):
        hue = (1 - percentage / 100) * 0.33
        r, g, b = hsv_to_rgb(hue, 1, 1)
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

    def init_disk_visualization(self):
        for i, disk in enumerate(self.disks):
            label = tk.Label(self.frame, text="", fg='white', bg='black')
            label.grid(row=i, column=0, sticky="w")
            self.disk_labels.append(label)

            canvas = tk.Canvas(self.frame, width=300, height=20, bd=1, relief='solid', bg='black')
            canvas.grid(row=i, column=1)
            usage_bar = canvas.create_rectangle(0, 0, 0, 20, fill='grey')
            self.disk_canvases.append(canvas)
            self.usage_bars.append(usage_bar)

    def update_disk_visualization(self):
        for i, disk in enumerate(self.disks):
            try:
                usage = psutil.disk_usage(disk.mountpoint)
            except (PermissionError, FileNotFoundError):
                continue  # Skip if we don't have permission or the disk is unavailable

            total_gb = usage.total / (1024 ** 3)
            free_gb = usage.free / (1024 ** 3)
            used_percent = (usage.used / usage.total) * 100
            free_percent = (usage.free / usage.total) * 100
            color = self.calculate_color(used_percent)

            label_text = f"{disk.device} ({disk.mountpoint}) - Used: {used_percent:.2f}%, Free: {free_percent:.2f}% | Total: {total_gb:.1f}GB, Free: {free_gb:.1f}GB"
            self.disk_labels[i].config(text=label_text)
            self.disk_canvases[i].coords(self.usage_bars[i], 0, 0, used_percent * 3, 20)
            self.disk_canvases[i].itemconfig(self.usage_bars[i], fill=color)

    def update_loop(self):
        self.update_disk_visualization()
        self.master.after(1000, self.update_loop)  # Update every second

def main():
    root = tk.Tk()
    app = DiskUsageApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

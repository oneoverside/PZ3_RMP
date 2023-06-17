import tkinter as tk
from datetime import datetime

import paho.mqtt.client as mqttclient


class App:
    def __init__(self, master):
        self.client = None
        self.master = master
        self.master.title("IoT Project")
        self.master.geometry("500x400")
        self.counter = 0
        self.max_value = 50
        self.state = False
        self.m = 5
        self.events = []

        # Counter Label
        self.counter_label = tk.Label(self.master, text="Counter: {}".format(self.counter))
        self.counter_label.pack()

        # State Label
        self.state_label = tk.Label(self.master, text="State: {}".format(self.state), bg="green")
        self.state_label.pack()

        # Button
        self.button = tk.Button(self.master, text="Click me!", command=self.button_click)
        self.button.pack()

        # Entry Field
        self.entry_label = tk.Label(self.master, text="Change M Value: ")
        self.entry_label.pack()
        self.entry = tk.Entry(self.master)
        self.entry.pack()
        self.entry.bind("<Return>", self.entry_update)

        # Scale Widget
        self.scale_label = tk.Label(self.master, text="Change Counter Value: ")
        self.scale_label.pack()
        self.scale = tk.Scale(self.master, from_=0, to=self.max_value, orient=tk.HORIZONTAL)
        self.scale.set(self.counter)
        self.scale.bind("<ButtonRelease-1>", self.scale_update)
        self.scale.pack()

        # Listbox Widget
        self.listbox_label = tk.Label(self.master, text="History of Events: ")
        self.listbox_label.pack()
        self.listbox = tk.Listbox(self.master)
        self.listbox.pack()
        self.connect_to_hub()

    def button_click(self):
        self.counter += 1
        self.events.append((self.counter, datetime.now().strftime("%H:%M:%S")))
        self.counter_label.config(text="Counter: {}".format(self.counter))
        self.state = not self.state
        self.state_label.config(text="State: {}".format(self.state))
        if self.counter >= self.m:
            self.state_label.config(bg="red")
        else:
            self.state_label.config(bg="green")
        self.listbox_update()
        self.publish()

    def entry_update(self, _):
        try:
            self.m = int(self.entry.get())
            if self.counter >= self.m:
                self.state_label.config(bg="red")
            else:
                self.state_label.config(bg="green")
        except ValueError:
            pass

    def scale_update(self, _):
        self.counter = int(self.scale.get())
        self.counter_label.config(text="Counter: {}".format(self.counter))
        self.events.append((self.counter, datetime.now().strftime("%H:%M:%S")))
        self.listbox_update()
        self.publish()
        if self.counter >= self.m:
            self.state_label.config(bg="red")
        else:
            self.state_label.config(bg="green")

    def listbox_update(self):
        self.listbox.delete(0, tk.END)
        for event in self.events:
            self.listbox.insert(tk.END, "Counter={}: {}".format(event[0], event[1]))

    def on_message(self, client, userdata, msg):
        if msg.payload:
            self.counter = int(msg.payload)
            self.counter_label.config(text="Counter: {}".format(self.counter))
            self.events.append((self.counter, datetime.now().strftime("%H:%M:%S")))
            self.listbox_update()
            print(f"Отримано повідомленя за топіком: {msg.topic} з QoS {msg.qos}: {msg.payload}")
        else:
            print("Empty payload received on topic", msg.topic)

    def on_connect(self, client, userdata, flags, rc):
        print(f"Підключення до серверу створенно успішно {rc}")

    def publish(self):
        self.client.publish("Counter", str(self.counter))

    def connect_to_hub(self):
        broker_address = "node02.myqtthub.com"
        port = 1883
        user = "dalakoz"
        password = "_"

        self.client = mqttclient.Client(client_id="test-client", clean_session=False)
        self.client.username_pw_set(user, password=password)
        self.client.connect(broker_address, port=port)
        self.client.subscribe("Counter")
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect

        self.client.loop_start()


root = tk.Tk()
app = App(root)
root.mainloop()

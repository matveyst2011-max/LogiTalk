import threading
from socket import *
from customtkinter import *




class MainWindow(CTk):
   def __init__(self):
       super().__init__()
       self.geometry('400x300')
       self.title('Чат')
       set_appearance_mode('dark')


       self.label = None
       self.username = 'Artem'


       # menu frame
       self.menu_width = 0
       self.max_menu_width = 200
       self.menu_frame = CTkFrame(self, width=0, height=300)
       self.menu_frame.pack_propagate(False)
       self.menu_frame.place(x=0, y=0)
       self.is_show_menu = False
       self.speed_animate_menu = -20
       self.anim_id = None


       # віджети меню (створюються один раз)
       self.label = CTkLabel(self.menu_frame, text='Ваше Ім`я')
       self.label.pack(pady=30)
       self.entry = CTkEntry(self.menu_frame)
       self.entry.insert(0, self.username)
       self.entry.pack()
       self.label_theme = CTkOptionMenu(self.menu_frame, values=['Темна', 'Світла'],
                                        command=self.change_theme)
       self.label_theme.pack(side='bottom', pady=20)


       self.btn = CTkButton(self, text='▶', command=self.toggle_show_menu, width=30)
       self.btn.place(x=0, y=0)


       # main
       self.chat_field = CTkTextbox(self, font=('Arial', 14, 'bold'), state='disable')
       self.chat_field.place(x=0, y=30)
       self.message_entry = CTkEntry(self, placeholder_text='Введіть повідомлення:', height=40)
       self.message_entry.place(x=0, y=250)
       self.message_entry.bind('<Return>', lambda event: self.send_message())
       self.send_button = CTkButton(self, text='▶', width=50, height=40, command=self.send_message)
       self.send_button.place(x=350, y=250)


       try:
           self.sock = socket(AF_INET, SOCK_STREAM)
           self.sock.connect(('2.tcp.eu.ngrok.io', 25075))
           hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
           self.sock.send(hello.encode('utf-8'))
           threading.Thread(target=self.recv_message, daemon=True).start()
       except Exception as e:
           self.add_message(f"Не вдалося підключитися до сервера: {e}")


       self.adaptive_ui()


   def toggle_show_menu(self):
       # зупиняємо попередню анімацію, щоб вони не накладались
       if self.anim_id is not None:
           self.after_cancel(self.anim_id)
           self.anim_id = None


       if self.is_show_menu:
           self.is_show_menu = False
           self.speed_animate_menu = -abs(self.speed_animate_menu)
           self.btn.configure(text='▶')
       else:
           self.is_show_menu = True
           self.speed_animate_menu = abs(self.speed_animate_menu)
           self.btn.configure(text='◀')
       self.show_menu()


   def show_menu(self):
       self.menu_width += self.speed_animate_menu
       self.menu_width = max(0, min(self.max_menu_width, self.menu_width))


       self.menu_frame.configure(width=self.menu_width, height=self.winfo_height())
       # кнопка розтягується разом із меню
       self.btn.configure(width=max(30, self.menu_width))


       if self.is_show_menu and self.menu_width < self.max_menu_width:
           self.anim_id = self.after(20, self.show_menu)
       elif not self.is_show_menu and self.menu_width > 0:
           self.anim_id = self.after(20, self.show_menu)
       else:
           self.anim_id = None


   def change_theme(self, value):
       if value == 'Темна':
           set_appearance_mode('dark')
       else:
           set_appearance_mode('light')


   def adaptive_ui(self):
       win_w = self.winfo_width()
       win_h = self.winfo_height()
       menu_w = self.menu_width
       input_h = self.message_entry.winfo_height()
       send_w = self.send_button.winfo_width()
       send_h = self.send_button.winfo_height()


       self.menu_frame.configure(height=win_h)


       self.chat_field.place(x=menu_w, y=30)
       self.chat_field.configure(width=win_w - menu_w, height=win_h - input_h - 30)


       self.message_entry.configure(width=win_w - menu_w - send_w)
       self.message_entry.place(x=menu_w, y=win_h - input_h)


       self.send_button.place(x=win_w - send_w, y=win_h - send_h)


       self.after(20, self.adaptive_ui)


   def add_message(self, text):
       self.chat_field.configure(state="normal")
       self.chat_field.insert(END, text + '\n')
       self.chat_field.configure(state="disable")
       self.chat_field.see(END)


   def get_username(self):
       name = self.entry.get().strip()
       return name if name else self.username


   def send_message(self):
       message = self.message_entry.get()
       if message:
           self.username = self.get_username()
           self.add_message(f'{self.username}: {message}')
           try:
               data = f"TEXT@{self.username}@{message}\n"
               self.sock.sendall(data.encode('utf-8'))
           except Exception as e:
               self.add_message(f"Помилка відправки: {e}")
       self.message_entry.delete(0, END)


   def recv_message(self):
       buffer = ""
       while True:
           try:
               chunk = self.sock.recv(4096)
               if not chunk:
                   break
               buffer += chunk.decode('utf-8')


               while "\n" in buffer:
                   line, buffer = buffer.split('\n', 1)
                   self.handle_line(line.strip())
           except:
               break
       self.sock.close()


   def handle_line(self, line):
       if not line:
           return
       parts = line.split("@", 2)
       msg_type = parts[0]


       if msg_type == "TEXT":
           if len(parts) >= 3:
               author = parts[1]
               message = parts[2]
               self.after(0, self.add_message, f"{author}: {message}")
       elif msg_type == "IMAGE":
           if len(parts) >= 3:
               author = parts[1]
               filename = parts[2]
               self.after(0, self.add_message, f"{author}: надіслав зображення {filename}")
       else:
           self.after(0, self.add_message, line)




win = MainWindow()
win.mainloop()

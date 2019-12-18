import tkinter as tk
from twython import Twython
from twython.exceptions import TwythonError
import webbrowser
from os import path
from keys import APP_KEY, APP_SECRET
import csv
from time import sleep, strftime

class PinEntry(tk.Frame):
	def __init__(self, callback, master=None):
		super().__init__(master)
		self.master = master
		self.callback = callback
		self.create_widgets()
		self.pack(padx=5, pady=5)
		
	def create_widgets(self):
		self.winfo_toplevel().title("Get Followers")
		self.pin_label = tk.Label(self, text="Enter PIN:")
		self.pin_entry = tk.Entry(self)
		self.pin_entry.insert(tk.END, "PIN")
		self.ok_button = tk.Button(self, text="OK")
		self.ok_button["command"] = self.return_pin
		
		self.pin_label.pack(side="left", padx=5, pady=5)
		self.ok_button.pack(side="right", padx=5, pady=5)
		self.pin_entry.pack(side="right", padx=5, pady=5)
	
	def return_pin(self):
		pin = self.pin_entry.get()
		self.callback(pin)

class FollowerGetter(tk.Frame):
	def __init__(self, api, master=None):
		super().__init__(master)
		self.master = master
		self.api = api
		self.create_widgets()
		self.pack()
	
	def create_widgets(self):
		self.winfo_toplevel().title("Get Followers")
		username = self.api.verify_credentials()["screen_name"]
		
		self.user_label = tk.Label(self, text="Signed in as @{}".format(username))
		self.target_label = tk.Label(self, text="Enter target account:")
		self.target_entry = tk.Entry(self)
		self.target_entry.insert(tk.END, "@MoggMentum")
		self.pages_label = tk.Label(self, text="Enter page count:")
		self.pages_entry = tk.Entry(self)
		self.pages_entry.insert(tk.END, "15")
		self.get_button = tk.Button(self, text="Download followers", command=self.download_followers)
		
		# self.user_label.grid(row=0, column=0)
		# self.target_label.grid(row=1, column=0)
		# self.target_entry.grid(row=1, column=1)
		# self.pages_label.grid(row=2, column=0)
		# self.pages_entry.grid(row=2, column=1)
		# self.get_button.grid(row=3, column=1)
		
		self.user_label.pack(padx=5, pady=5)
		self.target_label.pack(padx=5, pady=5)
		self.target_entry.pack(padx=5, pady=5)
		self.pages_label.pack(padx=5, pady=5)
		self.pages_entry.pack(padx=5, pady=5)
		self.get_button.pack(padx=5, pady=5)
	
	def download_followers(self):
		target_account = self.target_entry.get()
		pages = int(self.pages_entry.get())
		self.get_followers(pages, target_account)
	
	def rate_limit_wait(self):
		while True:
			rate_limit_context = self.api.get_application_rate_limit_status(resources='followers')
			rlc_fl = rate_limit_context['resources']['followers']['/followers/list']
			if rlc_fl['remaining'] > 0:
				return rlc_fl['remaining']
			else:
				print('API rate limit reached. Sleeping for 5 minutes...')
				sleep(5*60)
	
	def user_format_final(self, user):
		keys = ('screen_name', 'id_str')
		return [user[key] for key in keys]
	
	def user_format_evaluate(self, user):
		keys = ('screen_name', 'id_str', 'name', 'created_at',
                'location', 'description',
                'followers_count', 'friends_count', 'statuses_count')
		return [user[key] for key in keys]
	
	def get_followers(self, pages, target):
		all_followers = []
		cursor = -1
		remaining_calls = 0
		for i in range(pages):
			if remaining_calls <= 0:
				print('Checking API rate limit...')
				remaining_calls = self.rate_limit_wait()
			page = self.api.get_followers_list(
				screen_name=target, skip_status='true',
				count=200, cursor=cursor)
			print('Page retrieved.')
			cursor = page['next_cursor_str']
			all_followers.extend(self.user_format_evaluate(user) for user in page['users'])
		print("{} followers downloaded from {}".format(len(all_followers), target))
		dt = strftime('%y.%m.%d %H.%M.%S')
		output_filename = 'user_details_{}_{}.csv'.format(target, dt)
		with open(output_filename, 'w', encoding='utf-8', newline='') as file:
			w = csv.writer(file, dialect='excel')
			for follower in all_followers:
				w.writerow(follower)
		print("{} followers written to {}".format(len(all_followers), output_filename))
		

class Application(tk.Frame):
	def __init__(self, master=None):
		super().__init__(master)
		self.master = master
		self.create_widgets()
		self.pack(padx=5, pady=5)
	
	def init_twitter(self):
		self.twitter = Twython(APP_KEY, APP_SECRET)

	def create_widgets(self):
		self.winfo_toplevel().title("Get Followers")
		self.auth_button = tk.Button(self)
		self.siwt_image = tk.PhotoImage(file = "sign-in-with-twitter-gray.png") 
		self.auth_button["image"] = self.siwt_image
		self.auth_button["command"] = self.open_auth_page
		self.auth_button.pack(side="top", padx=5, pady=5)

		self.quit = tk.Button(self, text="Exit",
							  command=self.master.destroy)
		self.quit.pack(side="bottom", padx=5, pady=5)
	
	def begin_auth(self):
		self.init_twitter()
		self.auth = self.twitter.get_authentication_tokens()
	
	def open_auth_page(self):
		self.begin_auth()
		webbrowser.open_new_tab(self.auth['auth_url'])
		self.pin_tl = tk.Toplevel(self)
		self.pin_tl.grab_set()
		self.enter_pin = PinEntry(master=self.pin_tl, callback=self.receieve_pin)
	
	def open_follower_getter(self):
		self.follower_tl = tk.Toplevel(self)
		self.follower_tl.grab_set()
		self.follower_getter = FollowerGetter(master=self.follower_tl, api=self.twitter)
		
	def receieve_pin(self, pin):
		self.pin = pin
		self.pin_tl.destroy()
		self.finish_auth()
		
	def finish_auth(self):
		OAUTH_TOKEN = self.auth['oauth_token']
		OAUTH_TOKEN_SECRET = self.auth['oauth_token_secret']
		self.twitter = Twython(
			APP_KEY, APP_SECRET,
			OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
		try:
			final_step = self.twitter.get_authorized_tokens(self.pin)
		except TwythonError:
			print("Incorrect PIN or API keys, please try again.")
			self.init_twitter()
			return
		OAUTH_TOKEN = final_step['oauth_token']
		OAUTH_TOKEN_SECRET = final_step['oauth_token_secret']
		self.twitter = Twython(
				APP_KEY, APP_SECRET,
				OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
		self.user = self.twitter.verify_credentials()
		print("Signed in as @{}".format(self.user["screen_name"]))
		self.open_follower_getter()

if __name__ == '__main__':
	root = tk.Tk()
	app = Application(master=root)
	app.mainloop()

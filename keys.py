with open('secret', 'r') as f:
	APP_KEY, APP_SECRET = f.read().strip().split('\n')
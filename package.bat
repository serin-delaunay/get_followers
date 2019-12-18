pyinstaller get_followers_tk.py --clean -F --exclude-module setuptools --exclude-module dist-utils --exclude-module sqlite3  --exclude-module multiprocessing --exclude-module decimal
xcopy readme.txt dist\ /Y
xcopy sign-in-with-twitter-gray.png dist\ /Y
xcopy secret dist\ /Y
cd dist
del get_followers.zip
"C:\Program Files\7-Zip\7z.exe" a get_followers.zip *
cd ..
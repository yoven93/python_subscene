To start daemon thread: python3 app.py start language path_to_movie_folders

To stop daemon thread: python3 app.py stop


Note:
Testing on macOS caused an error:URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:581)>
To solve this error, I had to execute /Applications/Python\ 3.6/Install\ Certificates.command on the terminal
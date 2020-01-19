# course-seat-selector

This is a python script that refreshes the webpage of a given course automatically to sign up once there's seat in the course. once given a username, password, and course number, 


## Installing

### Mac

First clone the project and `cd`:

```sh
git clone https://github.com/zscc/course-selector.git
cd course-selector
```
Then [create a virtual environment by following this tutorial](https://docs.python.org/3/tutorial/venv.html). 
Then install the dependencies via
```sh
pip install --upgrade -r requirements.txt
```

from the project root directory. 

The default browser engine this script uses is Firefox, make Firefox driver is install. If not, run 
```sh
brew install geckodriver
```
If you installed the driver without homebrew, remember to add the executable to the system path. Add the below line to your bash config file (e.g., `~/.bashrc`)
```sh
export PATH=$PATH:/path/to/geckodriver
```


## Running

To run, go into the firefox folder, and launch the script

```sh
cd firefox
python3 beta.py
```

When prompted, put in your username, password, the course you want to get into, and how frequently do you want your browser to refresh to get the seat, and voilà!

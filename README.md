
# Stay Set

___URL for the Web App http://35.200.179.153___

___Check the Linux Server Configuration [here](https://github.com/shrutisheoran/linux-server-setup)___

___This project is a shopping web app which uses third party user authentication and also implements user authorisation___

1. **It displays a list of corners**
2. **Each corner has a list of subcategories**
3. **Each subcategory have a list of items**
4. **A user logged in can**
	* add a corner
	* add an item
	* add a subcategory if he created the corner

5. **A user which created the corner/subcategory/item can**
	* edit corner/subcategory/item
	* remove corner/subcategory/item

## Configure virtual machine using vagrant
* Download vagrant from [here](https://www.vagrantup.com/downloads.html)
* Download configuration files from [here](https://d17h27t6h515a5.cloudfront.net/topher/2017/August/59822701_fsnd-virtual-machine/fsnd-virtual-machine.zip)
* Extract those files in a folder then open git bash in the folder.
* Run `vagarant up` in git bash.
* Then run `winpty vagrant ssh` or `vagrant ssh` to login.
* Now you have up and running postgresql in your system with python3 and newly created database **_news_**.

## To run the web app in your computer
1. Run command `su postgres` and then run `psql`.
2. Write `CREATE DATABASE shoppingsite;` and press enter.
3. Press `ctrl + d` and then run `su vagrant`.
4. Clone or download the zip file of the repository.
5. Open the terminal in the downloaded folder.
6. Run the command `python database_setup.py` in the terminal.
7. Run the command `python populate_database.py` in the terminal.
8. Run the command `python project.py` in the terminal.
9. Open your browser and enter the url `localhost:8000`.
10. You have a up and running shopping web application.

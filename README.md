# Item-Catalog

The **Item-Catalog** is a project written for **Udacity's Full Stack Developer Nanodegree Program**. 

In this project, the webpage will display a menu and an item pane populated with food items with its representative food category. You have the option of adding new items to a particular food category, and edit/delete food items if you are the creator of that object (or have admin privileges). To create/edit/delete a category, you must have admin privileges. For the purpose of this evaluation, I have created a function to allow you to alternate your privilege status (See Usage.)

## Requirments

Please ensure your system contains the following software prior to using this project:

* Virtual Box
* Custom Vagrant file from Udacity.com

## Download

To obtain a copy of this project download the entire contents of this repository in a `.zip` file onto your desktop or folder of choice and unzip it to your vagrant folder. Below are also the required links that you will need to download and install for the requirements.

* [Vagrant](https://www.vagrantup.com/downloads.html)
* [Vagrant Configuration File](https://d17h27t6h515a5.cloudfront.net/topher/2017/August/59822701_fsnd-virtual-machine/fsnd-virtual-machine.zip)

## Usage

1) Open terminal or command prompt and navigate to your Vagrant folder.

2) Enter `vagrant up` to initially set up your virtual machine.

3) Once Vagrant has finished setting up, enter `vagrant ssh`. 

4) Navigate to your vagrant folder inside vagrant using `cd /vagrant/`.

5) This project has already been setup with a database. If you want to delete the database and recreate it, move `main.db` to the trash. Run `python database_setup.py` for a clean database or `python addDB.py` for a populated database.

6) Enter `python /vagrant/main.py` to run the server.

7) To view the webpage, visit: [localhost:5000].

[localhost:5000]: localhost:5000

8) To alternate between user and admin privileges, please sign into your Google Account first, then after successful completion visit: [localhost:5000/status/]

[localhost:5000/status/]: localhost:5000/status/

9) To serialize data visit:
- categories: `localhost:5000/main/JSON`
- items: `localhost:5000/main/<int:category_id>/item/JSON`
- specific item: `localhost:5000/main/<int:category_id>/item/<int:item_id>/JSON`
- users: `localhost:5000/user/JSON`

## Source

## Disclaimer

Please use this project at your own risk. I, _J. Ye._, am not responsible for any damage(s) that the end-user's computer may experience while using this project.

## License


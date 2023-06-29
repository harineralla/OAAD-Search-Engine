# OAAD-Search-Engine
As aspiring and future system and software developers, our team is excited to undertake the development of Cyberminer,
an ingenious web search engine. Leveraging our expertise in Object-Oriented Analysis and Design, we will plan and
design a prototype using Object-Oriented Programming techniques. By collaborating closely and harnessing our passion
for innovation, we aim to create a search engine that demonstrates our skills and potential as future developers

# Getting Started

Activate the virtualenv for your project.
    
Install project dependencies:

    $ pip install -r requirements/local.txt
    
    
Then simply apply the migrations:

    $ python manage.py makemigrations adminapp

    $ python manage.py migrate
    

You can now run the development server:

    $ python manage.py runserver

You can check admin tables as well:

    $ python manage.py runserver 
    and navigate to localhost url + /admin

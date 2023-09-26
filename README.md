#flask run

# for external connection

#flask run --host=0.0.0.0

# run in different port

#flask run -p 5001

flask run --debug

# To remove all packages from pip

pip freeze | xargs pip uninstall -y

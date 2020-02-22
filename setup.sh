#!/bin/bash


###
#setup script to install and initi py envirnoments

echo -e "Running setup script \n ------------------------------------------"
WORK_DIR=$(pwd)

usage='''
Setup script for python environment \n
takes one argument: dir To place python env \n
defaults to:  __py_env__ \n
'''
py_dir='__py_env__'


if [ -z $@ ]
then
    echo No input args
    echo -e $usage
else 
    $py_dir = $1
fi

echo -e "Seting up pyton env, dir = $py_dir"

#mkdir $py_dir
python3 -m venv $py_dir
echo -e 'Activate env'
source $WORK_DIR/$py_dir/bin/activate
echo 'installing requirements.txt'
pip3 install -r $WORK_DIR/requirements.txt
echo 'Instaled, deactivating py env'
deactivate
echo -e 'Deactivated env'

echo "adding $py_dir to .gitignore"
echo $py_dir >> .gitignore


echo "DONE"


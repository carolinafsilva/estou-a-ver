brew install python3
ln -s /usr/local/Cellar//python/3.7.5/Frameworks/Python.framework/Versions/3.7/include/python3.7m/* /usr/local/include/
pip3 install -r requirements.txt
python3 setup.py build
python3 setup.py install

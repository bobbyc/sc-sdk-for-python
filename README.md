# SecureCloud Management SDK for python

python interface SDK for SecureCloud Management API

## Prerequisites
- PyCrypto >= 2.6
	- https://pypi.python.org/pypi/pycrypto
	- For windows pre-compiled version at http://www.voidspace.org.uk/python/modules.shtml#pycrypto

## Install SCLIB

Install sclib package into python library folder

	> python setup.py install --record files.txt

If successfully install package, files.txt will log installed files list for further audit.

## Uninstall SCLIB

Please make sure you already install pip - a tool for installing and managing Python packages.

	> sudo pip uninstall sclib

## SCLIB Configuration

- There are 2 way to configure sclib parameter, the file name should be `.sclib.config`
	- /etc/.sclib.config
	- put .sclib.config file in your home folder
		- ~/.sclib.config (for Linux)
		- c:\Users\ `<user name>` \ .sclib.config (for Windows)

###Config sample:

	[connection]
	MS_HOST = https://ms.securecloud.com/broker/API.svc/v3.5
	MS_BROKER_NAME = <your broker name>
	MS_BROKER_PASSPHASE = <your passphase>
	SSL_VALIDATION = <Enable/Disable>
	SSL_CERTIFICATE = <cert file name>

	[authentication]
	AUTH_NAME = <your account(email)>
	AUTH_PASSWORD = <your password>
	
###Configuration Parameters:
	
- **MS_HOST** (MUST)

	URL for the SecureCloud Management API entry point

- **MS_BROKER_NAME** (MUST)

	Broker name. Please get this broker from Administrator

- **MS_BROKER_PASSPHASE** (MUST)

	Password of broker name. Please get this from Administrator

- **SSL_VALIDATION** (OPTIONAL)

	**Enable**/**Disable** SSL validation. When disabled, SDK will bypass HTTPS (SSL) certificate checking.

- **SSL_CERTIFICATE** (OPTIONAL)

	Specify file name. This parameter will search certificate in **/cacert** folder.


- **AUTH_NAME** (MUST)

- **AUTH_PASSWORD** (MUST)

## Unit Test

### Testing Path
Configure testing path with environment valuable `PYTHONPATH`

	> export PYTHONPATH=<sc-sdk-for-python>

### Running tests:

Run simple connection test with following commands

	> cd <sc-sdk-for-python>/tests/unit/
	> python test_connection.py

More tests
	
	> cd <sc-sdk-for-python>/tests/unit/sc
	> python -m unittest discovery 

or test in group tests, for example:

	> cd <sc-sdk-for-python>/tests/unit/sc
	> python test_instance.py 

or 

	> cd <sc-sdk-for-python>/tests/unit/sc
	> python test_instance.py SCVirtualMachineTest.testVMAllDevices

	


### Unit Test Result:

Default result folder:

    <sc-sdk-for-python>/tests/unit/result/

Naming Convention:

    Request Message: <result>/<TestClassName>.<TestMethod>/[Request]-<method> <api>.xml
    Response message: <result>/<TestClassName>.<TestMethod>/[Response]-<method> <api>.xml

## Server Certificate Validation

Default certificate file:

    <sc-sdk-for-python>/sclib/cacerts/cacert.pem
	
NOTE:

	Replace cacert.pem file if HTTPS (SSL) certificate is your own certificate.
    

# data-navi-gatr

#### If I ever use angle brackets (<>) that means that is a value that you enter. Make sure you change that to apply to your system before you run the commands.

## Before you setup the app you need to do 1 of the following:
##### From Windows CMD, SSH into your Ubuntu Server
```
ssh <your-ubuntu-username>@<server ip>
```
-----
### Option 1, disable password requirment for the change ownership command for your user.
```
sudo visudo
```
##### Go to the very bottom of the page where it says "See sudoers(5) for more information on "@inlude" directives:"
##### Add the following text at the bottom to remove password requirement for chown. After you have added that click "'ctrl' x" and then click "'y'" and then "'enter'"
```
<you-ubuntu-username> ALL=(ALL:ALL) NOPASSWD: /bin/chown
```
##### You can now exit out of you Ubuntu Server but you will want to keep cmd open
### Option 2, enable the root user and root user ssh.
##### Create a password for the root user
```
sudo passwd root
```
##### Enable ssh login for the root user, by editing the sshd_config file
```
sudo nano /etc/ssh/sshd_config
```
##### Find the line the that looks like this:
```
#PermitRootLogin no
```
##### Change it to this
```
PermitRootLogin yes
```
##### Restart the SSh service:
```
sudo service ssh restart
```
-----
### Download and install Data Navi Gatr
##### On the github page click the green dropdown button named ****"Code"**** and then click **"Download ZIP"**. Once it is downloaded go ahead and right click on the zip file and extract the contents. **Set the extract location to the C drive** (other wise you will have to copy the files to the C drive or change the commands below.).
-----
#### There are two different ways to deploy the application, one is to create an exe file and the other is to create a bat file. If you do choose to deploy the app as an exe with pyinstaller then windows security may delete the app because it thinks its malware.
-----
### Option 1, Deploy app as an exe:
##### First install Python 3.12, this can be found in the Microsoft store
##### Open CMD and install the necessary packages for the application.
```
pip install babel tkcalendar paramiko pyinstaller
```
##### Once those packages are installed use CMD to navigate to the directory where you saved the "Data Navi Gatr" folder.
```
cd "C:\data-navi-gatr-main"
```
##### Once you are in the Data Navi Gatr folder run the following command:
```
python -m PyInstaller --onefile --noconsole --hidden-import=babel.numbers "Data Navi Gatr.py"
```
##### once that is all done with no errors then you have successfully created the application. if you want to make a Desktop shortcut for the application you can right click on your desktop and select new and then shortcut, then navigate to the "Data Navi Gatr" directory then the "dist" folder then select the main.exe, You can then create a name for your shortcut and the click finish, and now you have a desktop shortcut.
### Option 2, Deploy app as a bat:
##### First install Python 3.12, this can be found in the Microsoft store
##### Open CMD and install the necessary packages for the application.
```
pip install tkcalendar paramiko
```
#####
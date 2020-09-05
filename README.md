# exportMDL
Python script to export drama lists from MyDramaList.com without the need for an API key.

# Table of Contents

* [Setup](#setup)
    * [General installation](#installation)
* [Documentation](#documentation)
    * [Exporting](#exporting-your-drama-list)
        * [Example](#examples)
    * [Configuration](#configuration)
* [Importing](#importing-export-file)
    * [Excel](#using-microsoft-excel)
    * [Google Sheets](#using-google-sheets)
    * [LibreOffice Calc](#using-libreoffice-calc)
* [First-time Users](#first-time-users)
    * [Download Python](#download)
    * [Install Python](#install)
    * [Start terminal](#start-terminal)
    * [Input the codes](#input-the-codes)
    * [Edit configuration file](#edit-the-configuration-file)
    * [Special consideration for Windows users](#special-consideration-for-windows-users)
    



## Setup
### Requirements
Python >3.6 (Jump to [First-time Users](#first-time-users) for a more detailed guide)


### Installation
Installation can be done either by downloading the files directly from GitHub (Code -> Download ZIP) or by cloning it
    
    git clone https://github.com/arifer612/exportMDL
    
After cloning the source files, you may want to make sure that the required dependencies have been installed with
    
    pip3 install -r requirements.txt

## Documentation
### Exporting your drama list

    python3 exportMDL.py
    
Optional arguments you may use:
    
    -f --filename <filename>                    Specifies the filename for the export file
    
    -o --only <category1,category2...>          Specifies list category. Categories MUST be separated by a comma without spaces
    -e --exceptions <excption1,exception2...>   Specifies list category exceptions. Exceptions MUST be separated by a comma without spaces.
                                                
                The available category options are: (watching, completed, hold, drop, plan_to_watch, not_interested)
                                                    
    -h --help                                   Shows the help pages
    
#### Examples

    python3 exportMDL.py -f ShowsWatched -o watching,completed
Saves the 'Currently Watching' and 'Completed' lists as ShowsWatched.tsv

    python3 exportMDL.py -f MainDramaList -e not_interested
Saves everything on your drama list except for those that are marked under the 'Not Interested' list as MainDramaList.tsv
    

### Configuration
Set the save directory for the export file in _config.conf_ as in the following manner:

    log = C:\Desktop
    
Set login details in _config.conf_ as in the following manner:
    
    username = user@email.com
    password = P@sSw0rd

You may opt to leave these blank. 

## Importing export file
The drama list will be exported as a _.tsv_ file. You may choose to import the files onto your local data management
software such as Excel, LibreOffice Calc, or Google Sheets.

### Using Microsoft Excel
When importing into Microsoft Excel, I highly recommend that you do not use the default import manager. Instead, start
with a fresh sheet and under the Data Ribbon, choose to import "From Text/CSV". An import manager will pop up, just
okay it and you're done.

![Microsoft Excel Ribbon](https://i.imgur.com/xTB1qzp.png "Microsoft Excel Example")

### Using Google Sheets
When importing into Google Sheets, the import manager will pop up to query the necessary import rules. You can import it
with the default rules:

![Google Sheets](https://i.imgur.com/NSxQFsX.png "Google Sheets Example")

### Using LibreOffice Calc
When importing using LibreOffice Calc, the import manager will pop up to query the necessary import rules. Use the
following rules:

![LibreOffice Calc](https://i.imgur.com/2rTOl29.png "LibreOffice Calc Example")

## First-time Users
If this is your first time using Python, I recommend you follow the following steps.

#### Download
Download the latest version of Python here(https://www.python.org/downloads/)

#### Install
Start the installation and make sure to check the checkbox "Add Python 3.x to PATH" if you are on Windows. Mac and Linux-based users do not need to worry about this

#### Start terminal
Go into the folder where you have saved the project

* For Windows users, go into the project folder, hold shift and right click. You will see the following menu. Click on "Open Powershell window here" or "Open Terminal here" ![Windows](https://i.imgur.com/nOAuaM8.png)
* For Mac users, right click on the project folder and click on "New terminal at folder"
* For Linux-based users, cd into the project folder

#### Input the codes
Once the Powershell/terminal/bash has started, you can start using the codes above. On Windows, it should look something like these:
![pip](https://i.imgur.com/RCTwY3u.png)
![python](https://i.imgur.com/RCTwY3u.png)

If you have not set your login details in the configuration file (you can do so through [here](#edit-the-configuration-file)), you will be prompted to key in your login details like this. Do note that you cannot copy and paste your password into the terminal on Windows and it will not show any asterisks or symbols as you type your password.
![login](https://i.imgur.com/kNfQMIy.png)

#### Edit the configuration file
To edit _config.conf_ open the file using an editing software such as Notepad for Windows, TextEdit on MacOS, nano on Linux distros

### Special consideration for Windows Users
One key point to note that if you are on Windows and only have 1 version of Python installed, you should omit any occurences of '3' in the codes above. For example:

    pip install -r requirements.txt
    python exportMDL.py

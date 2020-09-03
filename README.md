# exportMDL
Python script to export drama lists from MyDramaList.com without the need for an API key.

## Setup
### Requirements
Python >3.6


### Installation
Installation can be done either by downloading the files directly from GitHub (Code -> Download ZIP) or by cloning it
    
    git clone https://github.com/arifer612/exportMDL
    
After cloning the source files, you may want to make sure that the required dependencies have been installed with
    
    pip3 install -r requirements.txt

## Documentation
#### Exporting your drama list

    python3 exportMDL.py
    
Optional arguments you may use:
    
    -f --filename <filename>                    Specifies the filename for the export file
    
    -o --only <category1,category2...>          Specifies list category. Categories MUST be separated by a comma without spaces
    -e --exceptions <excption1,exception2...>   Specifies list category exceptions. Exceptions MUST be separated by a comma without spaces.
                                                
                The available category options are: (watching, complete, hold, drop, plan_to_watch, not_interested)
                                                    
    -h --help                                   Shows the help pages
    
##### Examples

    python3 exportMDL.py -f ShowsWatched -o watching,completed
Saves the 'Currently Watching' and 'Completed' lists as ShowsWatched.tsv

    python3 exportMDL.py -f MainDramaList -e not_interested
Saves everything on your drama list except for those that are marked under the 'Not Interested' list as MainDramaList.tsv
    

#### Configuration
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
Simply drag and drop the .tsv file Microsoft Excel and it will automatically import the data.

### Using Google Sheets
When importing into Google Sheets, the import manager will pop up to query the necessary import rules. Use the 
following rules:

![Google Sheets](https://i.imgur.com/EDTnqGe.png "Google Sheets Example")

### Using LibreOffice Calc
When importing using LibreOffice Calc, the import manager will pop up to query the necessary import rules. Use the
following rules:

![LibreOffice Calc](https://i.imgur.com/2rTOl29.png "LibreOffice Calc Example")

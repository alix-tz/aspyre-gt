[![MIT License](https://img.shields.io/static/v1?style=plastic&label=license&message=MIT&color=brightgreen)](LICENSE) [![Version](https://img.shields.io/static/v1?style=plastic&label=version&message=0.2.4&color=blue)]()

# ASPYRE GT

A pipeline to transfer ground truth from [Transkribus](https://transkribus.eu/Transkribus/) to [eScriptorium](https://escriptorium.fr/).

![Mascot Aspyre](static/image/aspyre_mini.png)



## SUMMARY 
1. [How to use Aspyre](#how-to-use-aspyre)
2. [Configuring the export from Transkribus](#configuring-the-export-from-transkribus) 
3. [Reporting Errors](#reporting-errors) 
4. [Wiki](#wiki)


## How to use Aspyre
- [As a library](#as-a-library)
- [As a CLI](#as-a-cli)
- [As a service online (GUI)](#as-a-service-online)


### As a library
Aspyre is now a library. To install it, simply download `aspyrelib/` and make sure to install the dependencies! Use `from aspyrelib import aspyre` to import it in your program.


#### `aspyre.main(orig_source, orig_destination, talktome)`
- `aspyre.main() is... the main function in Aspyre. It will take a path to a directory or a zip structured the same way as an archive exported from Transkribus (it must contain references to images and ALTO 2 XML files), and will create new XML files conform to ALTO 4 in a new directory. Additionnally, it will save all these new files into a ZIP that you load onto eScriptorium.

  - **`src`** (str): a path to a directory or a zip containing ALTO XML files in a "alto" subdirectory and a "mets.xml" file.
  - **`dest`** (str): a path to the location where resulting files should be stored (and zipped). If not path is provided, the new files will be created in a directory named "alto_escriptorium/" within the source directory.
  - **`talktome`** (bool): if True, will display highlighted messages; if False, Aspyre will only show information, warning and error messages.


### As a CLI

A legacy script from earlier stage enables you to use Aspyre as a CLI fairly easily.

#### Step by step
- Export the transcriptions and the images from Transkribus; you now have a zip file
- ~~Unzip the file to a directory you will serve to Aspyre as the location of the sources~~ *(unnecessary with Aspyre 0.2.4!)*
- Create a virtual environment based on Python 3 and install dependencies (cf. *requirements.txt*)
- Run *aspyre/run.py* (`python3 aspyre/run.py`) with the fitting options
- See the CLI's options with *--help** (`python3 aspyre/run.py --help`)
- Aspyre will create a new ZIP that can be loaded onto eScriptorium

#### Example 

``` python
$ virtualenv venv -p python3
$ source venv/bin/activate
(venv)$ pip install -r requirements.txt 
(venv)$ python3 aspyre/run.py -i /path/to/exported/documents
```

### As a service online

You can now access Aspyre as a service online (GUI)! :arrow_right: [**`go to Aspyre GUI`**](https://aspyre-gui.herokuapp.com/)

#### Step by step

- Export the transcriptions and the images from Transkribus; you now have a zip file
- If your archive weighs more than 500 MB, remove the images from the zip file (unzip the archive and rezip it keeping only the alto/ directory and the 'mets.xml' file)
- Load the zip file onto the application and download the returned zip file
- You can now directly load this new ZIP onto eScriptorium

---

## Configuring the export from Transkribus
Export your data checking the “Transkribus Document” format option and checking the **“Export ALTO”** and **“Export Image”** sub-options.

> ![Transkribus Export Parameters](static/image/tkb_export_options.png)


---

## Reporting Errors

If you notice unexpected errors or bugs or if you wish to add more complexity to the way Aspyre transforms the ALTO XML files, please [create an issue](https://github.com/alix-tz/aspyre-gt/issues/new) and contribute!

---

## Wiki
- [What was the problem?](https://github.com/alix-tz/aspyre-gt/wiki/What-was-the-problem%3F)
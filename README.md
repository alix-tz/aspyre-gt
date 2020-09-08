# Aspyre GT

A pipeline to transfer ground truth from [Transkribus](https://transkribus.eu/Transkribus/) to [eScriptorium](https://escriptorium.fr/).

![Mascot Aspyre](static/image/aspyre_mini.png)


## ASPYRE GUI

You can now access Aspyre as a service online!

:arrow_right: [**`go to Aspyre GUI`**](https://aspyre-gui.herokuapp.com/)


## SUMMARY 
1. [Instructions](#instructions)
2. [Reporting Errors](#reporting-errors) 
3. [What was the problem?](#what-was-the-problem)
4. [Developping notes](#developping-notes)
5. [Diagram](#diagram)


## Instructions
- [ ] Export ground truth from Transkribus as 'Transkribus Document' using the **Export ALTO** option
> You can also export the images while you are at it
>
> ![Transkribus Export Parameters](static/image/tkb_export_options.png)
> 
> If you use the **Server export** option, unzip the archive before proceeding to the next steps

- [ ] Set a Python 3 environment and install dependencies (cf. `requirements.txt`)
> ``` bash
> $ virtualenv venv -p python3
> $ source venv/bin/activate
> (venv)$ pip install -r requirements.txt 
>```
> You can also use a conda environment. I would actually gladly add a `environment.yml` file to this repository, just sayin'!

- [ ] Run `aspyre/main.py`, providing the location to the ground truth exported from Transkribus
> `python3 main.py -i path/to/TKB/archive [-o path/to/output/directory] [--talktome]`
> ``` bash 
> -i SOURCE, --source SOURCE
>                           Location of the TRP Export directory
> -o DESTINATION, --destination DESTINATION
>                           Location where processing result should be stored
>                           (path to an existing directory)
> -t, --talktome            Will display highlighted messages if activated 
> ```


- [ ] If transforming multiple ALTO XML files, zip all new ALTO XML in a single `.zip` archive
> You can also load each ALTO XML file one by one but, well, it might take a while!  

- [ ] Provided that the names of the image files are identical to the ones loaded on eScriptorium, hit the 'Import Transcription (XML)' button and go with the flow! 🤙
> Note that you have to have uploaded the images before you can upload the transcription.  
> You don't need to select which image is associated with the transcription, the ALTO XML file already contains that information.


---

## Reporting Errors

If you notice unexpected errors or bugs or if you wish to add more complexity to the way Aspyre transforms the ALTO XML files, please create an issue and contribute!

---

## What was the problem?

**`eScriptorium`** allows users to import a document's segmentation and transcription using XML ALTO as a pivot format. 

The [`imports specifications`](https://gitlab.inria.fr/scripta/escriptorium/-/blob/master/app/apps/imports/README.md) describe the expected format as follows:

> Upload a valid [ALTO XML](https://en.wikipedia.org/wiki/ALTO_(XML)) file for segmentation and transcriptions.
The file is strictly validated against ALTO v4 (http://www.loc.gov/standards/alto/ns-v4#), if it's not valid an error message will (perhaps) help you fix the issue.
Each `<Page>` in the file will correspond to a selected card in the same order.
The 'name' field is the name of the transcription in which the text content will be stored (you can select it above the transcription panel). It is possible to import content from different files in the same transcription this way.
By defaults the segmentation for the selected images, both regions and lines, will be deleted. You can disable this behavior by unchecking 'Override existing segmentation.', in which case the system will try to match the lines and regions by their `ID` attribute. The old content for matching lines is then stored in its history and new lines/regions are created when no matching existing element are found.
> 
> Here is the most basic example, 2 pages with 2 lines each.
Other tags (description, glyphs) are ignored for now.
> ```xml
> <?xml version="1.0" encoding="UTF-8"?>
> <alto xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
> 	  xmlns="http://www.loc.gov/standards/alto/ns-v4#"
> 	  xsi:schemaLocation="http://www.loc.gov/standards/alto/ns-v4# http://www.loc.gov/standards/alto/v4/alto-4-0.xsd">
>  <Layout>
>     <Page WIDTH="850" HEIGHT="1083" PHYSICAL_IMG_NR="0" ID="page_0">
>       <PrintSpace HPOS="0" VPOS="0" WIDTH="850" HEIGHT="1083">
> 	<TextBlock HPOS="0" VPOS="0" ID="textblock_0" WIDTH="850" HEIGHT="1083">
> 	  <TextLine ID="line_0" HPOS="160" VPOS="771" WIDTH="0" HEIGHT="28">
> 	    <String ID="segment_0" CONTENT="This is an example" HPOS="160" VPOS="771" WIDTH="0" HEIGHT="28" WC="0.9995"></String>
>           </TextLine>
>         </TextBlock>
>       </PrintSpace>
>     </Page>
>     <Page WIDTH="850" HEIGHT="1083" PHYSICAL_IMG_NR="0" ID="page_1">
>       <PrintSpace HPOS="0" VPOS="0" WIDTH="850" HEIGHT="1083">
> 	<TextBlock HPOS="0" VPOS="0" ID="textblock_1" WIDTH="850" HEIGHT="1083">
> 	  <TextLine ID="line_1" HPOS="160" VPOS="771" WIDTH="0" HEIGHT="28">
> 	    <String ID="segment_1" CONTENT="This is also an example" HPOS="160" VPOS="771" WIDTH="0" HEIGHT="28" WC="0.9995"></String>
> 	  </TextLine>
>         </TextBlock>
>       </PrintSpace>
>     </Page>
>   </Layout>
> </alto>`
> ```

Therefore *eScriptorium* expects **ALTO-4**.

**`Transkribus`** on the other hand allows the users to export the result of segmentation and/or transcription in XML ALTO.

The user is given two options : 
> - [x] Export ALTO
> - [ ] ~~Export ALTO (Split Lines Into Words)~~

Because we have no interest at the moment in working at *word* level, we only focus on the format exported thanks to the `Export ALTO` option. 

The resulting XML file is similar to the following example: 

> ``` xml
> <?xml version="1.0" encoding="UTF-8"?>
> <alto xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
>       xmlns="http://www.loc.gov/standards/alto/ns-v2#"
>       xmlns:page="http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"
>       xsi:schemaLocation="http://www.loc.gov/standards/alto/ns-v2# http://www.loc.gov/standards/alto/alto.xsd">
>    <Description>
>       <MeasurementUnit>pixel</MeasurementUnit>
>       <OCRProcessing ID="IdOcr">
>          <ocrProcessingStep>
>             <processingDateTime>2020-08-26T14:51:12.802+02:00</processingDateTime>
>             <processingSoftware>
>                <softwareCreator>READ COOP</softwareCreator>
>                <softwareName>Transkribus</softwareName>
>             </processingSoftware>
>          </ocrProcessingStep>
>       </OCRProcessing>
>    </Description>
>    <Layout>
>       <Page ID="Page1" PHYSICAL_IMG_NR="1" HEIGHT="439" WIDTH="1010">
>          <TopMargin HEIGHT="0" WIDTH="1010" VPOS="0" HPOS="0"/>
>          <LeftMargin HEIGHT="439" WIDTH="0" VPOS="0" HPOS="0"/>
>          <RightMargin HEIGHT="439" WIDTH="0" VPOS="0" HPOS="1010"/>
>          <BottomMargin HEIGHT="0" WIDTH="1010" VPOS="439" HPOS="0"/>
>          <PrintSpace HEIGHT="439" WIDTH="1010" VPOS="0" HPOS="0">
>             <TextBlock ID="region_1598445725038_6" HEIGHT="51" WIDTH="290" VPOS="61" HPOS="271">
>                <Shape>
>                   <Polygon POINTS="271,61 271,112 561,112 561,61"/>
>                </Shape>
>                <TextLine ID="line_1598445725074_9" BASELINE="112" HEIGHT="51" WIDTH="290" VPOS="61" HPOS="271">
>                   <String ID="string_line_1598445725074_9" HEIGHT="51" WIDTH="290" VPOS="61" HPOS="271" CONTENT="What is Lorem Ipsum"/>
>                </TextLine>
>             </TextBlock>
>          </PrintSpace>
>       </Page>
>    </Layout>
> </alto>
> ```

For each image in a given document, *Transkribus* produces an **ALTO-2** XML file. 

🙄 **In conclusion, the ALTO files exported from Transkribus are not compatible with the import module in eScriptorium. We want to change this.**


## Developping notes
1. [Known "import errors" in eScriptorium](https://gitlab.inria.fr/dh-projects/aspyre-gt/-/issues/3)
2. [Extrapolation of baseline coordinates](https://gitlab.inria.fr/dh-projects/aspyre-gt/-/issues/4)
3. [Working directly from a Transrkibus export](https://gitlab.inria.fr/dh-projects/aspyre-gt/-/issues/5)
4. [Document issues raised when switching to eScriptorium-flavored ALTO 4](https://gitlab.inria.fr/dh-projects/aspyre-gt/-/issues/9)

---

## Diagram

![commented diagram describing the program](static/image/diagram.png)

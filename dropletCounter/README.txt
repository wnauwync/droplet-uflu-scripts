
#############################################
########    dropletCounter README    ########
#############################################



1. Copy dropletCounter.py and the requirements.txt file in directory that contains other directories with droplet image data
2. open terminal in directory
3. Start python
4. if dependencies in requirements.txt are not yet installed, install using pip:
------:> pip install -r requirements.txt --no-index --find-links file:///tmp/packages
5. Import dropletCounter
6. Analyse data by running dropletCounter function
7. Plot data by running plotData



----------------------------------------------------------------------------------------------------
FUNCTION dropletCounter:
Takes INPUTS:
1) directory:
2) flowrate: in uL/hr
3) newTxt: if True, generates new tsv file in dir dropletData. If False adds data to most recent tsv file in dir dropletData.
4) newGif: False by default since takes some time to generate, if True, creates a Gif from transformed images. Good for 
troubleshooting

Creates OUTPUT:
1) dirs dropletData and imageData if not yet presen in dir
2) tsv file in dropletData if specified using newTxt
3) gif file in imageData if specified using newGif

----------------------------------------------------------------------------------------------------
FUNCTION plotData:
Takes INPUTS:
1) fileName: by default no input necessary, will take most recently generated tsv file in directory dropletData.
If specified, give fileName of tsv

Creates OUTPUT:
1) 2D plot of droplet frequency vs time. Time is derived from time drople analysis is run.
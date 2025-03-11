# HR Evaluation Steps 

## Process Sat info 

There is a routine `hr-eval/makeprocsatsubmit.py` that is a python script that generates multiple submit scripts that will process each satelite for the dates requested in the routine. This is still a hard-coded script, but can be modified for others needs.   The configuration files that are used to process each satelite is in `hr-eval/configs`

#TODO
Add info on how this step can and should be checked

The output of this step can be found: 

| Machine | Directory Location |
|:------------------:|:-----------------|
| orion | `/work/noaa/marine/jmeixner/Data/processedsatdata/Altimeter_${SATELITE}_HR${SEASON}.nc` | 


## Interpolate model to statelite track 

The first step here is to create the jobs that will need to be created.  There are three python scripts that will create these jobs: 
`hr-eval/InterpModel2Sat/makesubmitinterpgfsv16.py` `hr-eval/InterpModel2Sat/makesubmitinterpHR.py` `hr-eval/InterpModel2Sat/makesubmitinterpmulti1.py`

This file is currently hard-coded to use output files on orion and the rootdir at the top of each of these would need to be changed to write into someone's directory.   The makesubmitinterpHR needs to be run for each HR experiment. 

Since there are quite a few jobs to submit, there are also python scripts to create simply jobs to submit different batches of jobs.  These can be found in: 
`hr-eval/InterpModel2Sat/makebatchgfs.py` `hr-eval/InterpModel2Sat/makebatchHR.py` `hr-eval/InterpModel2Sat/makebatchmulti1.py`

There is a check script to ensure that all output is created from the interpolation. These are the `hr-eval/InterpModel2Sat/check*.py` scripts.  Also, there should be checks on file size and examining of logs to ensure all files are created. 

The output of this step can be found: 

| Machine | Directory Location |
|:------------------:|:-----------------|
| hera | `/scratch1/NCEPDEV/climate/Jessica.Meixner/processsatdata/outinterp/${MODEL}/${MODEL}_${GRID}_${SEASON}_${ICDATE}_${SATELITE}.nc`|
| orion | `/work2/noaa/marine/jmeixner/processsatdata/outinterp/${MODEL}/${MODEL}_${GRID}_${SEASON}_${ICDATE}_${SATELITE}.nc`|

Note that GFSv16 and Multi1 do not have "seasons" in their naming conventions.   



#TODO 

Then you can plot the output as an additional check of the output to ensure files are as correct 

## Combine output of interpolated model to satelite track 

The previous step is completed for each forecast hour and for multi-grid scenarios, each grid.  This step combines the output 
by season for each model for each satelite, taking into account multi-grids for Multi1 and GFSv16.  For each model the following
is run: 

``` python CombineSatInterpOut.py -m $MODEL -o $OUTDIR ```

where MODEL=multi1, GFSv16, HR1, HR2, HR3a, HR3b and OUTDIR is the desired output directory. 

The output is a series of files 
`combined_${MODEL}_${SEASON}_${SATELITE}.nc`
for the combined output and then `combined_day${DAY}_${MODEL}_${SEASON}_${SATELITE}.nc` for the model output for each day. 

To check this, we need to make sure that we have all of the expected files exist and that they all are of non-zero size, 
in addition to checking that there were not errors in the log files from the jobs. 
Note, the size of the mutli1 files are smaller because it does not have the same length of forecast and the hurricane 
output for GFSv16 is lareger than HR runs as it goes out to 16, not 7 days. 

The number of expected output files is: 

| Number of Files | Model | Calculation | 
|:------------------:|:-----------------:|:----------------------:|
| 96 |  multi1  | ( (7 days + 1 combined) x ( 3 seasons ) x (4 satelites) ) | 
|  100 |  GFSv16  | ( (7 days + 1 combined) x (1 hurricane season) x (4 satelites) + (16 days + 1 combined) x (1 summer season) x (4 satelites) ) |
|  168 |  HR experiements |  ( (7 days + 1 combined) x (1 hurricane season) x (4 satelites) + (16 days + 1 combined) x (2 summer/winter season) x (4 satelites )) |

This steps output can be found: 

| Machine | Output Locations  | 
|:------------------:|:-----------------|
| hera | `/scratch1/NCEPDEV/climate/Jessica.Meixner/processsatdata/combineout/combined_${MODEL}_${SEASON}_${SATELITE}.nc` `/scratch1/NCEPDEV/climate/Jessica.Meixner/processsatdata/combineout/combined_day${DAY}_${MODEL}_${SEASON}_${SATELITE}.nc`|
| orion |  `/work2/noaa/marine/jmeixner/processsatdata/combineout/combined_${MODEL}_${SEASON}_${SATELITE}.nc` `/work2/noaa/marine/jmeixner/processsatdata/combineout/combined_day${DAY}_${MODEL}_${SEASON}_${SATELITE}.nc` |

#TODO 
A previous way of combining scripts was using time-f.py which required the config.json. Do we keep these as is or move to a foler or remove?  


## Scripts used to create the plots: 

2- Then I used the eval.py to plot them. for plotting them you need to call pvalstats.py. The script is (eval.py). This is an automated process. In order to run the code you have to define the evalsumconfig.json. In this file you have to define the directory , filename, satellite name and then you can run the code.It accepts multiple pathes and filenames.

3- for the statistcal analysis I used the code and called mvalstats.py to calculate the statistcs. (stat.py)It created the spreadsheets with this format ({folder}_stats.csv)

4- plotstat.py, in this code you can plot the outputs of the stat.py. In the code, there is a switch that you can define if you want to consider all the vlues for all the models or the amount that covers all of them. when this value ()
is False,it plots the full range and when it is true it only plots up to values that is covered by all of the inputs.


## Note from Jessica 
most of the last parts of the creating and making plots is not well documented (yet).  The stats file i used as been moved to: /scratch1/NCEPDEV/climate/Jessica.Meixner/processsatdata/statshr3.nc
 

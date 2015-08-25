These scripts use the resukting files from the DataOrganization -> Raster scripts. They are used in two ways: statistics in RStudio and spatial consistency with python and arcpy

Statistics:

To ready the files for summary statstics, the order of scripts used matters:
1. "census_averages" takes the resulting files mentioned above and uses the raster tif files and a specified shapefiles of some boundary, in this case census tracts. It computes averages of the pixels in each census tract and exports a csv with the averages and the GISJOIN information from the shapefile.
2. "merge_csv_shapefile" takes the csvs created in Step 1 and merges them into a new shapefile for each csv, editing the attribute table information.

R scripts for statistics:
This order does not matter, as these scripts calculate independant statics with teh csvs created above.
1. "chi_squared" computes a schi squared contingency analysis for counts of extreme heat days and produces a table of proportions as well as the statstics of the analysis.
2. "anovas" separately computes anovas for month-to-month within a season for day and night and comments show the resulting statsitics as well as the results from post-hoc testing. These may be done in a loop, but for clarity within the script to see each individual test, each ANOVA was run separately.
3. ac_regressions" shows the regression models we tested for AC use using survey data and Census Bureau data. The script details how to run the regression, how to interpret the results, how to put the coefficients in 'odds' rather than the default 'log odds', how to talk about the results, and how to create a predicted probability sequence for potential visualization.
4. "final_figures_example" just shows some example code for some of the fugures we created in RStudio.

GIS Spatial Consistency:

This only uses the "python_arc_model_builder" script and requires arcpy. Code comments detail what parameters are necessary to make the code run.

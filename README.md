## Maize_Phenotype_Map ![](https://img.shields.io/badge/Release-v1.0.1-blue.svg)![](https://img.shields.io/pypi/l/Django.svg)
All of four scripts were written in Python to process RGB and hyperspectral image data. These scripts were run under command line of Linux Mint 17.2 System with dependencies of OpenCV module 2.4.8, Numpy >1.5, CMake > 2.6, GCC > 4.4.x and Scipy 0.13.X. 

Note: Please ignore warning messages produced during the image analysis, which are caused by tiny or no size of interested areas, or image generations. But the whole extraction process can go forwards without interruption. Corresponding error files are created to keep information of which image produces warning messages.

## Citation:
Please cite the paper "Zhikai Liang, Piyush Pandey, Vincent Stoerger, Yuhang Xu, Yumou Qiu, Yufeng Ge, James C. Schnable; Conventional and hyperspectral time-series imaging of maize lines widely used in field trials, GigaScience, gix117, https://doi.org/10.1093/gigascience/gix117" when use codes in this repository.
 
### 1) Numeric values extracted from RGB images. 

RGB_extraction_maize_diversity.py

Extracting numeric values of plant height, width, area in RGB images in pixel counts.

Data Structure: folder name -> Genotype ID -> Plant ID -> Camera Types -> RGB Image in Day

Demo: Python RGB_extraction_maize_diversity.py folder_name

Output file is RGB_extraction.csv

### 2) Numeric values extracted from stalk only area of plants in hyperspectral images. 

HYP_onlystem_reflectance.py

Extracting median reflectance value of pixels in the plant stem area through segmenting stem part of plants.

Data Structure: folder name -> Genotype ID -> Plant ID -> Camera Types (HYP) -> Day folders -> Image in 243 wavelengths

Demo: Python HYP_onlystem_reflectance.py folder_name

Output file is HYP_onlystem_reflectance_maize_diversity.txt

### 3) Numeric values extracted from leaf areas without stalk of plants in hyperspectral images. 

HYP_nostem_reflectance.py

Extracting median reflectance value of pixels in the plant area without stem through segmenting from hyperspectral image.

Data Structure: folder name -> Genotype ID -> Plant ID -> Camera Types (HYP) -> Day folders -> Image in 243 wavelengths

Demo: Python HYP_nostem_reflectance.py

Output file is HYP_nostem_reflectance_maize_diversity.txt

### 4) PCA analysis of plant pixels in hyperspectral images.

hyperspectral_PCA_visualization.py

Restoring and visualizing the entire plant area by consiering first three PC coefficients generated from PCA analysis of all pixels in all analyzed plants. Choose a day you want to analyze as the demo code. The first plot shows the PCA results based on first two PCs and the second plot shows the visualized and restored plants based on PCA results.

Data Structure: folder name -> Plant ID -> Camera Types (HYP) -> Day folders -> Image in 243 wavelengths

Demo: Python hyperspectral_PCA_visualization.py folder_name Day_030

### 5) Numeric values extracted from fluorescent images. 

FLUO_extraction_maize_diversity.py

Extracting average and sum of fluorescence intensity in side views and top view

Demo: Python FLUO_extraction_maize_diversity.py folder_name

Output file is Fluo_extraction.csv

### 6) The file to correspond band number with actual wavelength. 

wavelength_foldid.txt

The file corresponds each image file in hyperspectral folder to each specific wavelength.

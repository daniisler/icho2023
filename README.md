# Scripts used for IChO2023

## Logistics & Allocations

## Printing & Scanning


```
pip3 install -r requirements.txt
pip3 install zbarlight
```

## Ranking & Statistics

All scripts for this section are located in the folder `rankings_statistics`. They are written in python3 and require the packages defined in requirements.txt. To install them, run

```
pip3 install -r requirements.txt
```

The scripts were not written in a very general way and are more thought to give insight on what can be done with the data. They are not very well documented, but should be easy to understand. If you have any questions, feel free to contact me. You should definitely try them out well in advance to make sure they work with your particular case.

### Preparation of Exported Markings

Once all delegations have signed off their students marks, the export of the markings can be started from oly-exams. This can take about 15 minutes, so sit back and relax. A csv file is generated, containing for each student: All markings from the organizers, mentors and final (set after arbitration and signed off by mentors) of each subtask. In the column headers the maximum reachable values are specified in brackets behind the question title. If there were tasks with negative points, it will say (0.00), which needs to be manually replaced by the absolute value of the maximum possible negative score.

After this was done, the markings for the two exams need to be saved in two different csv files, while copying the first five rows to both of them. From here on the scripts will take over.

### Formatting of Markings

First a few variables have to be defined:
```
infile = os.path.join('/home/daniel/Downloads', f'markings_{exam_type}_{version}.csv') # Files from the step above that provide the marks for all subtasks
outfile_let = os.path.join('/home/daniel/Downloads', f'markings_let{exam_type}_{version}.csv') # Filename for the file which will contain the fraction of points reached for each subtask
outfile = os.path.join('/home/daniel/Downloads', f'markings_percentage{exam_type}_{version}.csv') # Filename for the file which will the fraction of total score (maximum 100% over both exams) reached for each subtask
outfile_org = os.path.join('/home/daniel/Downloads', f'markings{exam_type}_{version}_filter.csv') # Filename for the file which will contain the number of points achieved by each subtask (probably not needed, but nice to have)
fill_random = False # Set True if you want to fill an empty marking export with random testdata

# List of weighting factors for each task (as percentage)
if exam_type == 'Theory':
    weighting_factors = [5,5,6,6,7,7,7,5,6,6] # Percent score awarded for each subtask in theoretical exam
if exam_type == 'Practical':
    weighting_factors = [16, 13, 11, 100] # Percent score awarded for each subtaks in practial exam
```

After everything is prepared, running the script

```
python3 markings_format.py
```

will generate the above defined csv files, which can be used for statistics and to do the final ranking.

### Statistics on the Individual Exams Scores

These scripts provide plots on the students performance in the practical and theoretical exams per question individually (histograms of the fraction of points reached) and per weighted score reached for the full exams (histogram of the fraction of total score reached).

Again a few variables have to be defined (all in the top few lines of the script):
```
version = 'Final'
os.makedirs(f'/home/daniel/Downloads/markings_plots_theory_{version}/', exist_ok=True)


exam_type = 'Theory' # 'Theory'
num_questions = 3 if exam_type=='Practical' else 10

df_markings_org = pd.read_csv(f'/home/daniel/Downloads/markings{exam_type}_{version}_filter.csv')
if exam_type == 'Theory':
    max_points = [22,33,29,34,34.5,32,34,31,29,39]
    weights_array = [5,5,6,6,7,7,7,5,6,6]
else:
    max_points = [70,90,59]
    weights_array = [16,13,11]
```


The scripts are run by

```
python3 markings_statistics_theory.py
python3 markings_statistics_practical.py
```

### Ranking

To define the ranking, the above scripts need to have been run first, since they generate csv files with the weighted total scores for the individual exams. Again a few variables should be defined:

```
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
debug = 0
version = 'Final'
theory_df = pd.read_csv(f'/home/daniel/Downloads/markingsTheory_{version}_filter_totals.csv')
practical_df = pd.read_csv(f'/home/daniel/Downloads/markingsPractical_{version}_filter_totals.csv')
```

The script is run by

```
python3 ranking_sort.py
```

### Statistics on Arbitration

This script provides plots on what the effect of the arbitration was on the students scores. For this you need to generate the csv files with the markings before and after arbitration by running the script `markings_format.py` with the variable version modified:

```
version = 'Final' -> version = 'Organizer'
```

and line 41 modified as:

```
# Only take final marking
if row['Version'] == 'F': -> if row['Version'] == 'O':
```

Then repeat the process described in the sections above with all keeping the variable version set to 'Organizer'. After this is done, the script `markings_statistics_arbitration.py` can be run to generate the plots also shown in the final report.

```
python3 markings_statistics_arbitration.py
```

## OlyExams Additions

All scripts for this section are located in the folder `oly-exams_additions`. These scripts served to take off some tedious work in oly-exams. They are written in python3 and require the packages defined in requirements.txt. To install them, run

```
pip3 install -r requirements.txt
```

Some IT-knowledge is required to run them properly and they should only be run by someone feeling confident with them.

### Preparation of secret.py

The script `secret.py` contains the login information for the oly-exams web-service. It is not included in the repository for obvious reasons. It should be placed in the same folder as the other scripts and contain the information shown in the template `secret_template.py`.

### Bulk download exam

The script `bulk_download_exam.py` downloads all compiled pdf questions, answer-sheets and solutions (id's need to be specified in `secret.py`) from an exam from the oly-exams web-service and collates them into a single pdf document. For authentication you need to login to the web-service in your browser and copy the cookie information into `secret.py`. Further a fer variables need to be specified at the beginning of the script:

```
# Env
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
tmp_dir = os.path.join(PROJECT_DIR, 'exam_pdfs')
os.makedirs(tmp_dir, exist_ok=True)
os.makedirs(os.path.join(PROJECT_DIR, 'merged_exam'), exist_ok=True)
debug=1

download_latest_versions = True
build_exam = True
exam_type = 'Theory' # 'Practical' or 'Theory'
max_version_general_inst = []
general_inst_files = []
if exam_type == 'Practical':
    # For practical problems (question id, answer id, solution id, question number)
    problem_id_array = [(6,9,7,1), #OC problem (P1)
                        (11,14,12,2), #Titration tango (P2)
                        (18,21,16,3) #Beauty in simplicity (P3)
                        ] 
    general_inst_id = [2,3]
if exam_type == 'Theory':
    # For theory problems
    problem_id_array=[(4,8,5,1),(13,15,10,2),(17,20,19,3),(22,25,23,4), (26,28,27,5), (30,31,29,6), (33,34,32,7), (35,37,36,8), (39,40,38,9), (41,43,42,10)]
    general_inst_id = [1]

base_domain = 'icho2023.oly-exams.org'
```

### Color Points in Solutions

This script was used to highlight the given points for a solution in blue color and use a consistent format. This is to show, that such bulk changes can also be done automatically. As the script will (hopefully) not be needed again, it's just here to show what can be done.

### Insert questions into Answer Sheets

This script was used to insert the questions into the answer sheets. It is not very general and was only used for the practical exam. It is just here to show what can be done.



## Mass Mailing

These scripts are used to send out mass mails to all delegations. They serve as an idea base on what can be done, but for each application they need to be rewritten (at least partially). Also the script should first be tested by sending an email to your own email adress, to make sure you don't send out 300 faulty emails. The scripts are located in the folder `auto_mailing`.

They are written in python3 and require the packages defined in requirements.txt. To install them, run

```
pip3 install -r requirements.txt
```

### Preparation of the Mailing Credentials

First you need to provide the credentials for the mail account from which the mails will be sent. This is done in the file `secret.py`. An example is provided in `secret_template.py`. Further, if you want to send out large files, you might need to upload them to google drive and provide the link in the mail. For this you need to setup an api and define the credentials in `client_secrets.json`. An example is provided in `client_secrets_template.json`. How to setup the api is described [here](https://console.cloud.google.com/apis/dashboard). This is quite advanced and should only be done if you feel confident with it.

### Preparation of the Mailing List

First the mail addresses to all mentors/observers/guests of all delegations needs to be provided in some way. In our case this was an excel file with one row per delegation, in the first column the country code, continued by the stuents contact details and then the mentors/observers/guests details. You need to adapt the scripts according to the format in which you provide this data. This part is the same for all scripts in this section.

### Preparation of the Mail

To prepare a mass mail for a certain purpose, you need to have a csv file with the data you wish to send out (for example oly-exams credentials or the delegations students results). Then write some code that reads in the csv file and generates the mail. This part is different for each application, so you need to write it yourself. The scripts in this section are only meant to give you an idea on how to do it.

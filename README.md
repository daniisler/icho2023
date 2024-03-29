# Scripts used for IChO2023

## Environment Setup

Our scripts have been written in Python 3 and depend on several modules that need to be installed first by running 

```
pip3 install -r requirements.txt
```

or equivalent. To complete the setup, run

```
binlink.sh
source env.sh
```

which creates links to some top-level executables in the `bin` directory and modifies the `$PATH` and `$PYTHONPATH`
environment variables. You may want to add the contents of `env.sh` to your `.bashrc` file; otherwise, make
sure you `source env.sh` every time you start a new terminal session to run our student allocation scripts.

## Logistics & Allocations

To generate seating plans for the practical and theoretical exams we use a simulated annealing algorithm that minimizes
a penalty function. This function is defined in `icho2023/seating/interactions.py`, and a detailed explanation of
how it works is given in the docstring. In order to perform the simulation, we need to tell the function how many
students are attending the Olympiad and how different delegations "interact" - i.e., are there factors that 
disfavour seating students from any two given delegations next to each other. As such, we've considered
languages spoken by a delegation, geographical proximity, and "other" (geopolitical) factors. How these
are documented is described in the next section.

### Delegation Data

The directory `data` contains the following data files that you shouldn't have to modify:

  * `iso3166.csv`: list of country codes and the corresponding 2- and 3-letter codes from ISO 3166

  * `borders.csv`: list of country land borders (data available from <https://www.geodatasource.com>).
  
...and the following files that you will likely have to change:

  * `invitees.csv`: comma-separated file with columns 'Country', 'Students', 'Language 1', 'Language 2', 
  and 'Language 3'. The 'Country' column should list a name that matches one of the entries in `iso3166.csv`.
  The 'Students' column lists the number of students in the delegation. The 'Language' columns list the
  languages spoken fluently by members of the delegation, as indicated upon registration. You may want
  to redact 'English' so as not to overload the algorithm.

  * `aliases.json`: some countries were barred from participating at IChO 2023 and had instead sent
  individual participants; individual participants were assigned custom three-letter codes taken
  from the reserved 'QMA' to 'QZZ' range, as defined in this file.

  * `extra_borders.json`: only land borders are included in `borders.csv`; you may want to add
  additional sea borders to be considered under the geographical proximity criterion.

  * `other.json`: apart from proximity and spoken languages, other considerations might come into play;
  our example is based on https://www.cfr.org/global-conlict-tracker/ as of May 2023. This is not an
  expression of a political opinion and must not be treated as such.

### Seating Allocation and Signing Sheets

First, we have to generate a list of student codes. To do so, go to `examples/` and execute `./run.sh`.
Once you have done that, you can also run

```
python make_signing_sheets.py students.csv
```

This will compile two signing sheets, ordered by delegation code and signing code, using XeTeX. 

Next, you need the floorplans for the examination halls, stored as CSV files. Available seating is 
indicated with `XXX-0`, and everything else is designated by an empty string. Floorplans used by
IChO 2023 are stored in `data/theory_floorplans` and `data/practical_floorplans`.

For examples using our `icholocator` program, go to `examples/theory_allocation/` or `examples/practical_allocation/`
and execute `./run.sh`. The script should take about one minute to run and will produce CSV files with proposed
student seating, PDFs showing changes of the penalty function over the course of the simulation (`annealed_energy.pdf`)
and final inter-student interaction (`residuals.pdf`), as well as a pickle file `SIM.pkl` which can
be used by advanced users to restart the simulation. Feel free to modify the penalties defined in
`params.json` to see how that affects the final result and rate of convergence. NOTE: the length of the simulation
(number of MC steps in `run.sh`) is set to a low value so that the example runs quickly. For a final allocation
we recommend setting the number of steps to around 1'000'000, in which case the allocation may take a couple of
hours, but will result in a lower energy configuration.

### Post-processing and Logistics

It was convenient to split all students into 16 groups for each exam in order to set up and invigilate the
exam venues. Most labs constituted a single group except for E376 and E394, which were split into halves.
Group assignment for theory was more involved and can be deduced from the source code of the corresponding
script. To assign students to their exam groups and to produce a human-readable CSV file documenting
the assignment, go to the `examples` directory after running the examples from the previous section
and execute the following sequence of commands:

```
cd practical_allocation/
python split_labs.py        # split the big labs into two
# create a dataframe stored as a pickle file with each student code assigned a lab group
python parse_practical.py seated_students.pkl   
cd ../theory_allocation/
python add_labels.py        # creates "marked" CSV seating plans with explicit row and column labels
# update the dataframe from before with theory groups
python parse_theory.py --data ../practical_allocation/seated_students.pkl seated_students.pkl
cd ../
# create a CSV listing group assignments in a more readable form
python export_to_csv.py theory_allocation/seated_students.pkl seated_students.csv
```

Having constructed the database of seats, you can now produce documents that draw on this information, 
such as instructions sheets for lab inspection. For this, go to `examples/lab_inspection/` and
run `lab_covers.py template.tex ../practical_allocation/seated_students.pkl`. This will produce
`lab_covers.pdf` with the three-letter delegation code positioned so that it is visible through the address window of a
standard C4 envelope, as well as table listing the labs allocated to each student in that particular delegation. For
more information, run `lab_covers.py -h` and feel free to examine `template.tex`.

## Printing & Scanning

Because some extra functionalities were needed for printing and scanning, some scripts were used to handle this. They are located in the folder `printing-scanning_scripts`.

### Printing of Labstock Labels

The script `labels_gen_pdf.py` is used to print the labels for the labstock. It takes a csv file as input, which contains the information on the student code and amount of chemical contained in the vial. These were used to mark the vials with the samples for the analytic tasks in the practical exam.

### Reprinting Answer Sheets for Markers

Our markers requested to mark the students answers on prinouts. This has been done by api queries to oly-exams and then getting the files via ftp. This is an advanced process and should only be done after extensive testing and understanding. The script should e monitored during the whole scanning process.

For the process the script `as_reprint_api.py` was used. It queries the oly-exams api for successful scans; for this you need to add the api key in `secret.py`, which you can find [here](https://icho2023.oly-exams.org/exam/admin/api_keys) (if you don't have access you might need to ask the developers). Further the oly-exams ftp-folder needs to be mounted in your filesystem and you need to provide the path in one of the variables in the beginning.

The script will then query the api every three minutes and check if there are new scans. If there are, it will download the corresponding answer sheets, collate them in pdfs per task with cover-sheets (the number of students per batch can be defined as a variable). It also features telegram notifications for unsuccessful scans, which can be enabled by providing the bot token and chat id in the beginning of the script. See [here](https://core.telegram.org/bots#6-botfather) for more information on how to create a telegram bot.

### Reprinting Answer Sheets for Delegations

Although we encouraged the delegations to mark their students answers electronically, many requested printouts. To provide these on time, we used a similar process as for the markers.

The script `gen_delegations_answers_pdf.py` is used to reprint the answer sheets for the delegations. This works only if the script mentioned above is running/was running because it uses the files provided by that. It will collect the answer sheets of the students of each delegation mentioned in a csv file, collate them in a pdf with cover sheet and upload the result to google drive where printing volunteers can access them.

Before running the script for the first time, you need to have created a google drive api key and downloaded the credentials file. See [here](https://developers.google.com/drive/api/v3/quickstart/python) for more information on how to do this. You need to provide the path to the credentials file in the beginning of the script. The script will then ask you to authenticate with your google account. This will create a token file, which will be used for future authentication. The script will also ask you to provide the path to the folder where the pdfs should be uploaded to. This folder needs to be shared with the service account created for the api key.

### Final Version for TakeHome

We offered the delegations a take-home package with their translations of the exam, the official english version and the solutions. As an addition we also scanned the marked answer sheets. The qr-codes were then evaluated again using the script `marked_exams_sorted.py`, which takes pdf files fresh from scanning as inputs and sorts them into folders for each delegation. All pages where no qr-code was detected are collated into another pdf, where one could manually search for missing pages. Note that pages can also go missing if the scanner pulls multiple pages at once and therefore this process is not 100% reliable.

After this, the script `exam_final_integrate_polybox.py` was run to also integrate the electronically marked exams that were provided via a cloud called polybox.

When everything was collected, the script `exam_final_version.py` was used to collate all the files into one pdf per student in a folder per delegation. Missing pages were replaced by the original scan (not marked). Note this was the first try of such a thing and we achieved to get about 99% of all pages. This was treated as good enough.


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

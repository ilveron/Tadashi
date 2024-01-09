# README

# Intro

***Tadashi*** (from *tadashii*, Japanese for *******correct*******), is a correctness suite designed for [I-DLV-sr](https://github.com/DeMaCS-UNICAL/I-DLV-sr) disjunctive programs.

Its goal is to check automatically whether the results of given encodings in I-DLV-sr are between the optimal solutions provided by the solver included in it ([I²-DLV](https://github.com/DeMaCS-UNICAL/I-DLV/wiki/Incremental-IDLV)) and, hence correct.

---

# Architecture

The suite is structured into three logical phases, based on a pipeline architecture. Here's how it works:

- **Phase 1**: The workspace is created and relevant I-DLV-sr execution files are collected. These files include reasoner inputs, static ASP rewritings, and I-DLV-sr results in JSON format.
- **Phase 2**: The static ASP rewritings are executed using DLV2, and the resulting Answer Sets are stored.
- **Phase 3**: The obtained results are compared, and the final report(s) are drafted.

*NOTE: All actions mentioned are taken for every timepoint, for every encoding in test*

![*Tadashi’s architecture*](https://i.imgur.com/udFpUFF.png)

*Tadashi’s architecture*

---

# Usage

### Preliminary steps

Before you start the suite you shall create and fill the following three directories with the appropriate files in the same directory as the scripts `phase_1.py` `phase_2.py` `phase_3.py`:

- `idlvsr_encodings`: containing all I-DLV-sr encodings (`idlvsr` file extension) you want to be tested;
- `input_logs`: containing all the log files (`log` file extension) related to the encodings having the same filename;
- `external_definition`: containing the Python scripts (`py` file extension) which carry the external definitions for the related encoding.

<p float="left">
  <img src="https://i.imgur.com/pMJKB8b.png" width="250" />
  <img src="https://i.imgur.com/V53ZQt8.png" width="250" /> 
  <img src="https://i.imgur.com/vUBfhzn.png" width="250" />
</p>

<!-- ![idlvsr_encodings.png](https://i.imgur.com/pMJKB8b.png)

![input_logs.png](https://i.imgur.com/V53ZQt8.png)

![external_definition.png](https://i.imgur.com/vUBfhzn.png) -->

*An example of the previously mentioned directories’ structure*

I-DLV-sr is needed during the `phase_1.py` script, so make sure to download [the latest release from the official repository](https://github.com/DeMaCS-UNICAL/I-DLV-sr/releases) and extract `I-DLV-sr-v2.0.0.jar` and the `reasoner` directory to the same directory as the scripts and the previously created directories.

DLV2 (*without support to Python*) is needed during the `phase_2.py` script, so make sure to download [the latest release from the official site](https://dlv.demacs.unical.it/home) and copy it to the same directory, rename it to `dlv2` and give the file execution permission (via `chmod u+x <filename>`).

Do the exact same for DLV2 **with support to python** if you need to test encodings having external definitions in it (renaming it `dlv2-python`).

### Run the suite

You can alternatively execute the three Python scripts separately via the commands:

```bash
# Please run them in the following order
./phase_1.py
./phase_2.py
./phase_3.py
```

Or you can just run the handy shortcut script: 

```bash
./run_suite.sh
```

which if used with the option `-v`, is going to run the suite in verbose mode, providing another report which is  definitely more accurate (namely `verbose_report.txt`).

*NOTE: Make sure to give all the scripts execution permission first via `sudo chmod u+x <filename>`*

### Results

![*Content of the “**tadashi**” directory at the end of the execution of the scripts*](https://i.imgur.com/qZhgyFk.png)

*Content of the “**tadashi**” directory at the end of the execution of the scripts*

Once the execution finishes, you will find (in the same directory as the scripts) a freshly created directory named `tadashi` (which is the designated workspace), containing a directory for each encoding tested (which in turn contains all the files used by the suite to do the various checks), and the `report.txt` file, which tells the user, for each encoding tested, whether it is correct or not.

For example, the `report.txt` file is expected to be as follows:	

```
mon_cost1                            CORRECT
mon_ext2                             CORRECT
mon_inconsistent_1                   CORRECT
t52                                  CORRECT
t54                                  CORRECT
t55                                  CORRECT
```

This means that all tested encodings results turned out to be correct (*great!*)

If we chose to run the one-shot script in verbose mode (`-v` option), we would also have the `verbose_report.txt` in the `tadashi` directory with the base report.

The verbose report for this example is available [at this link](https://pastebin.com/NpLnfSDZ)

***What if some results are not correct?***

Let’s say that I-DLV-sr computed a wrong result in some timepoints of t52, *how would we notice*?

In the report file, all the timepoints where anomalies were detected will be marked (on the line of the specific encoding), so that they can be noticed.

```
mon_cost1                            CORRECT
mon_ext2                             CORRECT
mon_inconsistent_1                   CORRECT
t52                                  NOT CORRECT(['2019-01-16T10:00:02', '2019-01-16T10:00:06'])
t54                                  CORRECT
t55                                  CORRECT
```

Once the timepoints are noticed, the user can alternatively run that encoding manually and check where the results are not correct. Or (*preferably*) run the suite in verbose mode and check that timepoint in the `verbose_report.txt`.

---

# Contact info

**Alessandro Monetti** (*developer*): alessandromonetti@outlook.it

You can contact me for any further info on the Tadashi project.

Please report any bugs regarding this tool by opening a GitHub Issue and assigning it to me ([@ilveron](https://github.com/ilveron)).
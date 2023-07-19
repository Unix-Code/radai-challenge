## Setup
There are no required third-party dependencies to actually run the main script.
In order to run tests, `pytest` and `pytest-mock` are required. The easiest way to install these 
packages is to run:
```
$ pip install -r requirements-dev.txt
```

## How To Run
1. You must either have properly set up the `PYTHONPATH` to include `main.py` and the rest of
   the challenge code module, or have the current working directory set to the challenge code 
   directory
2. Run the following command (subsitute `python` with the correct local alias for or path to a python executable): 
   ```
   $ python main.py <arg>
   ```
    a. `<arg>` can either be empty (use STDIN) or a path to a file (use file) or `--help` 
       (display usage instructions)
    b. To use STDIN, it will be necessary to redirect some content like so:
       Unix:
       ```
       $ python main.py < "foobar.txt"
       ```
       Windows (System used to develop challenge) PowerShell:
       ```
       $ type "foobar.txt" | python main.py
       ```
3. View Output in STDOUT

## Time Taken

2.5 hours of total development time

## Possible Improvements

* The design used for this code challenge is purposely generic and extensible 
  (mainly for subsequent challenge questions). If these extension points were identified as being
  unnecessary, ie due to never needing alternate/additional scoring metrics, then they can be
  removed and the related code refactored in order to make things more concise.
* The base assumption was that there wouldn't be enough matches in a "season" (set of match
  results used for ranking) that linearly parsing the matches would become a bottleneck. If this
  assumption is incorrect, and we expect an arbitrarily large number of matches to use for ranking
  (and also potentially a large number of unique metrics to use for the ranking), then it would be
  best to improve performance
  * One option is to add batched concurrency. STDIN may not be easily seekable, but in the file use-case, 
    with some additional complexity, the file could be chopped up into rough batches to be 
    read + parsed concurrently (ie using a `ThreadPoolExecutor`). 
    This isn't trivial due to varying line sizes, but one way to try is to
    extend the batch (forwards and/or backwards) to a new line character before parsing.
  * If the biggest bottleneck is simply reading all the data from the file, then we
    could:
    * Use threading/concurrency to read the whole file before parsing at all
    * Use memory-mapped files to load file contents to pages of memory. (Requires a PC with lots of RAM)
    * Use an open-source library designed around loading large data sets (ie Polars)
* If this was going to be maintained as a long-term project, then I would also suggest:
  * Setting up linting using flake8/ruff (and also potentially typechecking using a preferred library)
  * Setting up CI/CD using Github Actions (or an alternative - ie Gitlab)
  * Writing a more sophisticated & multi-platform method of packaging up and deploying this tool. Options include:
    * Using a library like PyInstaller
    * Building the project into an installable package (if it's to be composed in other systems), ie using Poetry
    * Writing a Dockerfile to create a reusable Docker image

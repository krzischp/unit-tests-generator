# unit-tests-generator  

## Python unit tests generator
  
*Note this is an experimental script. It is going to be extended and improved soon.*  

Generate pytest unit tests folders and files structure.  

Use the following command line in the directory located one level higher than your project root directory:  
`python gen_unit_tests.py <project directory name> <your src directory> tests`
  
You will then have all the unit test classes initialized in the same folder structure as in your **src** directory.  
  
You can build you classes docstrings with the **Visual Studio** plugin **Python Docstring Generator**.
If you correctly set the type of each inputs in all of your functions docstrings, you can then run the following command line to generate the test classes with the initialized functions inputs:  
`python gen_unit_tests.py <project directory name> <your src directory> tests True`

compatipede2-client
===================

These scripts are for testing a distributed service for site compatibility diagnosis. 

This service can be used both in "exploratory" mode and to check if known bugs are still present in web sites. The current client script and data focuses on the "known bugs/regression testing" part.

To test: pull this project, edit compatipedelib.py to add the URL for the service (_init_url variable), then simply do 

    python run_tests_from_data.py

It is also possible to run a specific test only by giving it a bug ID:

    python run_tests_from_data.py -b webcompat-173

will thus run the test for issue #173 on webcompat.com

# Production release

* Create git flow release branch
* Push version number in setup.py
* Push version number in src/atraxiflow/\_\_init\_\_.py
* Create entry in CHANGES.md
* Push release branch and check Travis CI for errors
* Close git flow release branch and push changes, remove release branch on github
* Create pip package
* Check that the correct version of the packages have been created in dist (there is no way back after publishing it to PyPi)
* Publish the new version to PyPi
* Check that the documentation has been created properly

A few hours later...

* Check that the pip-badge is updated properly
* Check lgtm.com for errors and hints 

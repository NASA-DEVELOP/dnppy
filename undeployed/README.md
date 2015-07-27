This folder holds code that is packaged with dnppy for good record keeping, but is NOT installed with the module. The code in this directory should be distinct from dnppy, but cannot be treated as such due to limitations imposed by NASA open source software release protocols. There are a few different categories that code like this falls within, and it is organized as such. 

####/proj_code
NASA DEVELOP project teams contribute specialized code to this directory for access by project partners. Project code is evaluated for its generality and moved up to the subjects folder, then into dnppy if some generalization is possible. Code in this directory may have a very narrow focus on the needs of the project partners and lack scalability, but could potentially be generalized and scaled. Code in this directory may be in any programming language.

####/subjects
This repository is filled with unstructured code for a general purpose that could be useful to refactor and add to the dnppy framework in the near future.

####/legacy
This is old code from before our days of configuration management that might have very useful snippets to pull into dnppy_install.



For `git_frequency_monitoring.ipynb`:
insert the GitHub token 
```
token = "YOUR_TOKEN_HERE"  # Replace with your GitHub token
```
before executing the notebook. 

```
# Clone the repository
!git clone https://github.com/ursa-mikail/toolings.git

# Change directory to the location of the notebook
%cd toolings/python/git

# Convert and run the Jupyter notebook
!jupyter nbconvert --to script git_frequency_monitoring.ipynb
!python3 git_frequency_monitoring.py

# Alternatively, execute the notebook directly
# !jupyter nbconvert --to notebook --execute git_frequency_monitoring.ipynb
```
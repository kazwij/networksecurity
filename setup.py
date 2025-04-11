'''
For packaging and distributing Python Projects. include metadata, dependancies,and more

'''

from setuptools import find_packages,setup 
from typing import List

def get_requirements()->List[str]:
    '''
    This fuction will return list of requirements
    '''
    requirement_lst:List[str]=[]
    try:
        with open('requirements.txt','r') as file:
            #read lines from the file
            lines = file.readlines()
            # process each line
            for line in lines:
                requirement = line.strip() # this will remove leading and tail white spaces in a line
                # ignore empty lines and -e . 
                if requirement and requirement !='-e .':
                    requirement_lst.append(requirement)
    except FileExistsError:
        print("requirements.txt file not found")

    return requirement_lst


setup(

name="NetworkSecurity",
version="0.0.1",
author="Kasun Perumbuli",
author_email="kperumbuli91@gmail.com",
packages=find_packages(),
install_requires = get_requirements()

)

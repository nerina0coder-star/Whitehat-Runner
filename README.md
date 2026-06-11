<!-- badges -->
<!-- Versioning - Alpha -> Beta -> Experimental -> Release -->
![Author Mail](https://img.shields.io/badge/Email-github.py.coder%40gmail.com.-red?logo=github)
![Version](https://img.shields.io/badge/Version-v0.0.1--Alpha-red?logo=github)
![License](https://img.shields.io/badge/License-MIT-red?logo=github)
![Usablity](https://img.shields.io/badge/Usablity-Low-orange)

<h1 style='font-size: 3rem'>
WARNING: THIS BRANCH IS IN DEVELOPMENT, YOU MAY TEST BUT PLEASE DO NOT USE THIS IN ANY REAL-WORLD CONTEXT.
THAT IS THE REASON THE REPOSITORY HAS NO TAGS YET.
</h1>

# This project currently has many issues as it has been build at Jun 10 3AM. I plan to spend only 1 hour daily on this project.

# As I can dedicate at most 1 hour to this project, until version v0.0.1 is released, no tags will be given to this repository.

# This is my first time using pybind11 and c++, so it may take a few months for version v0.0.1 to be released with the expected features.

# Until version v0.0.1-Beta, no files except README.md, [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), [CONTRIBUTING.md](CONTRIBUTING.md), [LICENSE.md](LICENSE.md) and of course [LOGS.md](LOGS.md) will be put in this repository.

## Quick look
- Here is a minimal version of the project.
```python
from WhitehatRunner import Function, Whitelist, Runner
def sum(num1: int, num2: int):
    return num1 + num2
funcs = []
funcs.append(Function('sum', { 'num1' : int, 'num2' : int}, sum)) # passes name('sum') params('num1' is an int, 'num2' is another int) and the actual made function(sum - don't call it)
whitelist = Whitelist(funcs)
runner = Runner(whitelist)
runner.run("[[ sum(num1=9, num2=11) ]]", run_here=True)
```
## What it is?
- A sandbox to run filtered python code from, filtering and running code using a whitelist mechanism and iterating thru the given code from a c++ function.
- A connection creator between files and the running python process.

## Expected new release time - September 10 2026
Necessary 

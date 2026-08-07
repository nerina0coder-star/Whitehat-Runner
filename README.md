<!-- badges -->
<!-- Versioning - Alpha -> Beta -> Experimental -> Release -->
![Author Mail](https://img.shields.io/badge/Email-github.py.coder%40gmail.com.-red?logo=github)
![Version](https://img.shields.io/badge/Version-v0.0.1--Beta-orange?logo=github)
![License](https://img.shields.io/badge/License-MIT-red?logo=github)
![Usablity](https://img.shields.io/badge/Usablity-Medium-orange)

<h1 style='font-size: 3rem'>
WARNING: THIS BRANCH IS IN DEVELOPMENT, YOU MAY TEST BUT PLEASE DO NOT USE THIS IN ANY REAL-WORLD CONTEXT UNTIL VERSION 0.0.1 Release.
IF YOU ARE GOING TO USE THE GIVEN CODE, YOU CAN USE IT WITH DOCKER ON TRUSTED USER INPUT.
RELEASE IS NEAR.
</h1>


# Whitehat Runner
## Quick look
- Here is a minimal version of the project.
```python
from WhitehatRunner import *
func = Function(lambda: 1 + 2, explicit_name="func")
whitelist = Whitelist(func)
runner = Runner(whitelist)
answer = "Nothing"
stop = False
while not stop:
    try:
        for function in runner.runny(raw=f"[start[ {input('write a function to parse...\n')} ]end]"):
            answer = function(doeval=True)()
    except Exception as e:
        answer = "\n" + str(e)
    print(f'Function answered with {answer}')
    if input('Continue? (y/n) ').lower() == 'n':
        stop = True
func = Function(print)
whitelist = Whitelist(func)
runner = Runner(whitelist)
runner.runner(raw="[start[ print('Hello!') ]end]", output_path='output.py', max_cpu=10, max_cpu_cores=1, max_ram=200)
```
## What it is?
- A sandbox to run filtered python code from, filtering and running code using a whitelist mechanism.
- A connection creator between files and the running python process.
- A fast way to run functions from external files safely.

## What changed?
- ASTSecure became greedy, but fast!

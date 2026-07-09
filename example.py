from WhitehatRunner import *
func = Function(lambda: 1 + 2, explicit_name="func")
whitelist = Whitelist(func)
runner = Runner(whitelist)
answer = "Nothing"
stop = False
while not stop:
    try:
        for function in runner.runny(raw=f"[start[ {input('write a function to parse...\n')} ]end]"):
            answer = function(doeval=True)
    except Exception as e:
        answer = "\n" + str(e)
    print(f'Function answered with {answer}')
    if input('Continue? (y/n) ').lower() == 'n':
        stop = True
func = Function(print)
whitelist = Whitelist(func)
runner = Runner(whitelist)
runner.runner(raw="[start[ print('Hello!') ]end]", output_path='output.py', max_cpu=10, max_cpu_cores=1, max_ram=200)
import typeguard

from WhitehatRunner import Whitelist, Function, Runner
def test1():
    func = Function(lambda: 1 + 2, explicit_name="func")
    whitelist = Whitelist(func)
    runner = Runner(whitelist)
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

def test2():
    @Function.define()
    def func():
        return 10
    whitelist = Whitelist(func)
    runner = Runner(whitelist)
    whitelist.whitelist_imports('typeguard', 'typechecked', 'tc')
    calls = list(runner.runny(raw="[start[ from typeguard import typechecked as tc ]end]"))
    calls[0](doeval=False)
    print(whitelist._whitelisted_globals.get('tc') is typeguard.typechecked)

def test3():
    pass

if __name__ == "__main__":
    test1()
    test2()
    test3()
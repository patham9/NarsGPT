import NarsGPT as NAR

def AddInput(inp):
    ret = NAR.AddInput(inp, Print=False, PrintInputSentenceOverride=True, PrintInputSentenceOverrideValue=True)
    if inp.endswith("?"):
        print(ret["GPT_Answer"])

def question():
    ret = NAR.AddInput("Raise a question about me, not addressed by any existing memory item?", Print=False, PrintInputSentenceOverride=True, PrintInputSentenceOverrideValue=False)
    print(ret["GPT_Answer"].split("?")[0] + "?")
question()

while True:
    try:
        inp = input().rstrip("\n").strip()
    except:
        exit(0)
    AddInput(inp)
    question()

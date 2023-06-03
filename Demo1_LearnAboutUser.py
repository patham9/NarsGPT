import NarsGPT as NAR

LearnMoreAbout = "me" #"the router"
UseLastQuestionInContext = True

lastquestion = ""
def AddInput(inp):
    if not inp.endswith("?") and not inp.startswith("*") and UseLastQuestionInContext:
        inp = lastquestion + " " + inp
    ret = NAR.AddInput(inp, Print=False, PrintInputSentenceOverride=True, PrintInputSentenceOverrideValue=True)
    if inp.endswith("?"):
        print(ret["GPT_Answer"])

def RaiseQuestion():
    global lastquestion
    ret = NAR.AddInput(f"Raise a question about {LearnMoreAbout}, not addressed by any existing memory item?", Print=False, PrintInputSentenceOverride=True, PrintInputSentenceOverrideValue=False)
    ret["GPT_Answer"] = ret["GPT_Answer"].split("?")[0] + "?"
    print(ret["GPT_Answer"])
    NAR.I_You_Exchange(ret)
    lastquestion = ret["GPT_Answer"]
RaiseQuestion()

while True:
    try:
        inp = input().rstrip("\n").strip()
    except:
        exit(0)
    AddInput(inp)
    RaiseQuestion()

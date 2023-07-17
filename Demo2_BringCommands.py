import NarsGPT as NAR
import openai
import time

prompt="""
The task: __TASK__
To solve it, ask a question about information you need.
Alternatively generate a bring(thing, source_location, target_location) command to solve the task if Q&A history indicates object, source_location, target_location are concrete objects and not memory indices!
Never use memory items or indices as command arguments, only issue a command when the needed information is mentioned in the Q&A history!
"""
RECENT_QA_TUPLES = []

def build_prompt(task):
    prompt_temp = prompt.replace("__TASK__", task)
    if RECENT_QA_TUPLES:
        prompt_temp += "\Q&A history:"
        for qa in RECENT_QA_TUPLES:
            prompt_temp += qa[0] + " ANSWER: " + qa[1] + "\n"
    else:
        prompt_temp += "\Q&A history: EMPTY"
    return prompt_temp

def query(task):
    prompt = build_prompt(task)
    while True:
        try:
            response = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=[ {"role": "user", "content": prompt}], max_tokens=200, temperature=0)
            ret = response['choices'][0]['message']['content']
            return ret
        except Exception as e:
            print("Error: API call failed, will try repeating it in 10 seconds!", str(e))
            time.sleep(10) #wait 10 seconds

def parseOutput(LM_output):
    if "(" not in LM_output:
        if not LM_output.endswith("?"):
            print("ERROR: NOT VALID QUESTION: ", LM_output)
            exit(0)
        return NAR.AddInput(LM_output, PrintAnswer=False, Print=False, PrintInputSentenceOverride=True, PrintInputSentenceOverrideValue=False)["GPT_Answer"]
    return None

task = input()
while True:
    LM_output = query(task).strip()
    NARS_output = parseOutput(LM_output)
    print(LM_output, NARS_output, "\n")
    if NARS_output is not None:
        RECENT_QA_TUPLES.append((LM_output, NARS_output))
    else:
        break
    

    

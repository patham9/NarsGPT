from NAL import *

def Memory_attention_buffer(memory, attention_buffer_size):
    attention_buf=[]
    relevant_item_list = list(memory.items())
    #find attention_buf_target_size/2 newest items:
    relevant_item_list.sort(key=lambda x: -x[1][0])
    attention_buf += reversed(relevant_item_list[0:int(attention_buffer_size/2)]) #newer comes later in prompt
    #find additional attention_buf_target_size/2 useful items which were not already part of the newest
    relevant_item_list.sort(key=lambda x: -x[1][1])
    for x in attention_buf:
        if x in relevant_item_list:
            relevant_item_list.remove(x) #so we won't select it as it is already part of mem
    i = 0
    while len(attention_buf) < attention_buffer_size and i < len(relevant_item_list):
        attention_buf = [relevant_item_list[i]] + attention_buf
        i += 1
    return attention_buf

def Memory_generate_prompt(memory, prompt_start, prompt_end, attention_buffer_size):
    prompt_memory = ""
    buf = Memory_attention_buffer(memory, attention_buffer_size)
    if len(buf) == 0:
        prompt_memory = "EMPTY!"
    for i,x in enumerate(buf):
        (f,c) = x[1][2]
        flags = []
        if c < 0.5:
            flags.append("hypothetically")
        else:
            flags.append("knowingly")
        if f < 0.3:
            flags.append("False")
        elif f > 0.7:
            flags.append("True")
        else:
            flags.append("Contradictory")
        certainty = Truth_Expectation((f,c))
        truthtype = '"' + " ".join(flags) + '"'
        prompt_memory += f"i={i}: {x[0]}. truthtype={truthtype} certainty={certainty}\n"
    return prompt_start + prompt_memory + prompt_end

def Memory_digest_sentence(memory, sentence, truth, stamp, currentTime, PrintMemoryUpdates):
    if sentence not in memory:
        memory[sentence] = (0, 0, (0.5, 0.0), [])
    if sentence in memory:
        lastUsed, useCount, truth_existing, stamp_existing = memory[sentence]
        truth_updated, stamp_updated = NAL_Revision_And_Choice(truth, stamp, truth_existing, stamp_existing)
        memory[sentence] = (currentTime, useCount+1, truth_updated, stamp_updated)
        if PrintMemoryUpdates: print("//UPDATED", sentence, memory[sentence])
